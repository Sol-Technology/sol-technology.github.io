using System.IO.Compression;
using System.Reflection;
using System.Runtime.InteropServices.JavaScript;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;
using Newtonsoft.Json;
using SolTechnology.Avro;

/// <summary>
/// Functions called by the AvroConvert Online pages. Inputs and outputs are strings, bytes or JSON documents;
/// exceptions surface in JavaScript as errors with the AvroConvert message.
/// </summary>
public static partial class Engine
{
    private static readonly JsonSerializerOptions Indented = new() { WriteIndented = true };

    [JSExport]
    public static string Version() =>
        typeof(AvroConvert).Assembly.GetCustomAttribute<AssemblyInformationalVersionAttribute>()?.InformationalVersion.Split('+')[0]
        ?? typeof(AvroConvert).Assembly.GetName().Version!.ToString();

    // ---- Schema → C# ------------------------------------------------------------------------------------------------

    [JSExport]
    public static string GenerateModel(string schema) => AvroConvert.GenerateModel(AvroSchema.Parse(schema));

    [JSExport]
    public static string GenerateModelFromAvro(byte[] avro) => AvroConvert.GenerateModel(avro);

    [JSExport]
    public static string FormatSchema(string schema)
    {
        AvroSchema.Parse(schema);
        return Pretty(schema);
    }

    // ---- Avro file viewer --------------------------------------------------------------------------------------------

    /// <summary>Header, block statistics and the first <paramref name="maxRecords"/> records of an Avro object container file.</summary>
    [JSExport]
    public static string InspectAvro(byte[] avro, int maxRecords)
    {
        var header = ContainerHeader.Read(avro);
        var preview = new List<object?>();
        using (var stream = new MemoryStream(avro, writable: false))
        using (var reader = AvroConvert.OpenDeserializer<dynamic>(stream))
        {
            while (preview.Count < maxRecords && reader.HasNext())
            {
                preview.Add(reader.ReadNext());
            }
        }

        var metadata = new JsonObject();
        foreach (var (key, value) in header.Metadata.Where(m => m.Key != "avro.schema"))
        {
            metadata[key] = Encoding.UTF8.GetString(value);
        }

        return new JsonObject
        {
            ["schema"] = Pretty(header.Schema),
            ["codec"] = header.Codec,
            ["metadata"] = metadata,
            ["records"] = header.Records,
            ["blocks"] = header.Blocks,
            ["bytes"] = avro.Length,
            ["preview"] = JsonConvert.SerializeObject(preview, Formatting.Indented),
            ["previewCount"] = preview.Count
        }.ToJsonString();
    }

    /// <summary>All records as JSON (one array).</summary>
    [JSExport]
    public static string AvroToJson(byte[] avro) => AvroConvert.Avro2Json(avro);

    /// <summary>All records in the Avro specification's JSON encoding (avro-tools <c>tojson</c> format), one per line.</summary>
    [JSExport]
    public static string AvroToJsonEncoding(byte[] avro) => AvroConvert.Avro2JsonEncoding(avro);

    // ---- JSON → Avro -------------------------------------------------------------------------------------------------

    [JSExport]
    public static string InferSchema(string json) => Pretty(AvroSchema.InferFromJson(json).Json);

    /// <summary>JSON data to an Avro object container file with an inferred schema.</summary>
    [JSExport]
    public static byte[] JsonToAvro(string json, string codec) => AvroConvert.Json2Avro(json, ParseCodec(codec));

    /// <summary>Size of the data as JSON, gzipped JSON and Avro with every codec that works in the browser.</summary>
    [JSExport]
    public static string CompareSizes(string json)
    {
        // Minified, so indentation in the input does not count against JSON.
        var jsonBytes = Encoding.UTF8.GetBytes(JsonNode.Parse(json)!.ToJsonString());
        var sizes = new JsonObject
        {
            ["json"] = jsonBytes.Length,
            ["jsonGzip"] = Gzip(jsonBytes)
        };
        var avro = new JsonObject();
        var plain = AvroConvert.Json2Avro(json, CodecType.Null);
        sizes["avroHeader"] = ContainerHeader.Read(plain).HeaderBytes;
        foreach (var codec in new[] { CodecType.Null, CodecType.Deflate, CodecType.Snappy, CodecType.Zstandard, CodecType.GZip, CodecType.Brotli })
        {
            try
            {
                avro[codec.ToString()] = AvroConvert.Json2Avro(json, codec).Length;
            }
            catch (Exception)
            {
                // A codec that needs a native library the browser runtime does not have.
            }
        }

        sizes["avro"] = avro;
        return sizes.ToJsonString();
    }

    // ---- Schema compatibility ----------------------------------------------------------------------------------------

    [JSExport]
    public static string CheckCompatibility(string previous, string next, string mode)
    {
        var compatibilityMode = Enum.Parse<AvroCompatibilityMode>(mode, ignoreCase: true);
        var previousSchema = AvroSchema.Parse(previous);
        var nextSchema = AvroSchema.Parse(next);
        var result = AvroSchema.CheckCompatibility(previousSchema, nextSchema, compatibilityMode);

        // Every difference in both directions, so the page can explain non-breaking changes too.
        var backward = AvroSchema.Compare(previousSchema, nextSchema);
        var forward = AvroSchema.Compare(nextSchema, previousSchema);

        return new JsonObject
        {
            ["mode"] = compatibilityMode.ToString(),
            ["compatible"] = result.IsCompatible,
            ["equivalent"] = backward.AreEquivalent,
            ["incompatibilities"] = Differences(result.Incompatibilities),
            ["newReadsOld"] = Differences(backward.Differences),
            ["oldReadsNew"] = Differences(forward.Differences)
        }.ToJsonString();
    }

    [JSExport]
    public static string Fingerprints(string schema)
    {
        var parsed = AvroSchema.Parse(schema);
        return new JsonObject
        {
            ["canonicalForm"] = parsed.CanonicalForm,
            ["crc64"] = Convert.ToHexStringLower(parsed.GetFingerprint(AvroFingerprintAlgorithm.Crc64Avro)),
            ["crc64Long"] = parsed.Fingerprint.ToString(),
            // MD5 is not available in .NET on WebAssembly.
            ["sha256"] = Convert.ToHexStringLower(parsed.GetFingerprint(AvroFingerprintAlgorithm.Sha256))
        }.ToJsonString();
    }

    // ---- Kafka message decoder ---------------------------------------------------------------------------------------

    /// <summary>
    /// Splits a Kafka message in the Confluent Schema Registry wire format (magic byte 0, 4-byte big-endian schema id,
    /// Avro binary) and, when <paramref name="schema"/> is given, decodes the payload.
    /// </summary>
    [JSExport]
    public static string DecodeKafkaMessage(byte[] message, string schema, bool confluentFraming)
    {
        var result = new JsonObject { ["bytes"] = message.Length };
        var payload = message;
        if (confluentFraming)
        {
            // Magic byte 0: 4-byte big-endian schema id. Magic byte 1 (Confluent clients 2.11+): 16-byte big-endian schema GUID.
            if (message.Length >= 5 && message[0] == 0)
            {
                result["magicByte"] = 0;
                result["schemaId"] = (message[1] << 24) | (message[2] << 16) | (message[3] << 8) | message[4];
                payload = message[5..];
            }
            else if (message.Length >= 17 && message[0] == 1)
            {
                result["magicByte"] = 1;
                result["schemaGuid"] = new Guid(message.AsSpan(1, 16), bigEndian: true).ToString();
                payload = message[17..];
            }
            else
            {
                throw new InvalidDataException($"Not the Confluent wire format: expected magic byte 0 with a 4-byte schema id or 1 with a 16-byte schema GUID, got {(message.Length == 0 ? "no data" : $"0x{message[0]:x2} as the first byte and {message.Length} bytes")}.");
            }
        }

        result["payloadBytes"] = payload.Length;
        if (!string.IsNullOrWhiteSpace(schema))
        {
            var writerSchema = AvroSchema.Parse(schema);
            result["json"] = JsonConvert.SerializeObject(AvroConvert.DeserializeHeadless<dynamic>(payload, schema), Formatting.Indented);
            result["jsonEncoding"] = AvroConvert.Avro2JsonEncoding(payload, writerSchema);
        }

        return result.ToJsonString();
    }

    // ---- helpers -----------------------------------------------------------------------------------------------------

    private static JsonArray Differences(IEnumerable<SchemaDifference> differences) =>
        new(differences.Select(d => (JsonNode)new JsonObject
        {
            ["path"] = d.Path,
            ["kind"] = d.Kind.ToString(),
            ["breaking"] = d.IsBreaking,
            ["description"] = d.Description
        }).ToArray());

    private static string Pretty(string json) =>
        JsonNode.Parse(json)!.ToJsonString(Indented);

    private static CodecType ParseCodec(string codec) =>
        string.IsNullOrEmpty(codec) ? CodecType.Null : Enum.Parse<CodecType>(codec, ignoreCase: true);

    private static int Gzip(byte[] data)
    {
        using var output = new MemoryStream();
        using (var gzip = new GZipStream(output, CompressionLevel.Optimal, leaveOpen: true))
        {
            gzip.Write(data);
        }

        return (int)output.Length;
    }
}
