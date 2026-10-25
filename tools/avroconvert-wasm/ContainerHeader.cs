using System.Text;

/// <summary>
/// Reads the header of an Avro object container file and walks its blocks without decoding them: the metadata map,
/// the codec and the number of records come from the framing alone, so they are available for files of any size.
/// </summary>
internal sealed class ContainerHeader
{
    private static readonly byte[] Magic = { (byte)'O', (byte)'b', (byte)'j', 1 };

    public required Dictionary<string, byte[]> Metadata { get; init; }

    public string Schema => Encoding.UTF8.GetString(Metadata["avro.schema"]);

    public string Codec => Metadata.TryGetValue("avro.codec", out var codec) ? Encoding.UTF8.GetString(codec) : "null";

    public long Records { get; private set; }

    public long Blocks { get; private set; }

    /// <summary>Bytes before the first block: magic, metadata (including the schema) and sync marker.</summary>
    public int HeaderBytes { get; private set; }

    public static ContainerHeader Read(byte[] data)
    {
        if (data.Length < Magic.Length || !data.AsSpan(0, Magic.Length).SequenceEqual(Magic))
        {
            throw new InvalidDataException("Not an Avro object container file: it does not start with 'Obj' 0x01. Headless Avro (e.g. a Kafka message) needs its schema – use the Kafka message decoder.");
        }

        var position = Magic.Length;
        var metadata = new Dictionary<string, byte[]>();
        while (true)
        {
            var count = ReadLong(data, ref position);
            if (count == 0)
            {
                break;
            }

            if (count < 0)
            {
                count = -count;
                ReadLong(data, ref position); // block size in bytes
            }

            for (var i = 0; i < count; i++)
            {
                var key = Encoding.UTF8.GetString(ReadBytes(data, ref position));
                metadata[key] = ReadBytes(data, ref position);
            }
        }

        if (!metadata.ContainsKey("avro.schema"))
        {
            throw new InvalidDataException("The file header has no avro.schema entry.");
        }

        position += 16; // sync marker
        var header = new ContainerHeader { Metadata = metadata, HeaderBytes = position };
        while (position < data.Length)
        {
            header.Records += ReadLong(data, ref position);
            var size = ReadLong(data, ref position);
            position = checked((int)(position + size + 16));
            header.Blocks++;
        }

        return header;
    }

    private static byte[] ReadBytes(byte[] data, ref int position)
    {
        var length = checked((int)ReadLong(data, ref position));
        var bytes = data.AsSpan(position, length).ToArray();
        position += length;
        return bytes;
    }

    /// <summary>Zig-zag encoded variable-length long, as in the Avro binary encoding.</summary>
    private static long ReadLong(byte[] data, ref int position)
    {
        ulong value = 0;
        var shift = 0;
        byte b;
        do
        {
            if (position >= data.Length)
            {
                throw new InvalidDataException("The file ends in the middle of the header or of a block.");
            }

            b = data[position++];
            value |= (ulong)(b & 0x7F) << shift;
            shift += 7;
        }
        while ((b & 0x80) != 0);

        return (long)(value >> 1) ^ -(long)(value & 1);
    }
}
