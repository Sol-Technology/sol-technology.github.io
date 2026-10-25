// AvroConvert compiled to WebAssembly (tools/avroconvert-wasm). Loaded on first use, once per page.
export interface AvroEngine {
  Version(): string;
  GenerateModel(schema: string): string;
  GenerateModelFromAvro(avro: Uint8Array): string;
  FormatSchema(schema: string): string;
  InspectAvro(avro: Uint8Array, maxRecords: number): string;
  AvroToJson(avro: Uint8Array): string;
  AvroToJsonEncoding(avro: Uint8Array): string;
  InferSchema(json: string): string;
  JsonToAvro(json: string, codec: string): Uint8Array;
  CompareSizes(json: string): string;
  CheckCompatibility(previous: string, next: string, mode: string): string;
  Fingerprints(schema: string): string;
  DecodeKafkaMessage(message: Uint8Array, schema: string, confluentFraming: boolean): string;
}

const frameworkUrl = "/avroconvert/online/_framework/dotnet.js";
let engine: Promise<AvroEngine> | undefined;

export function loadEngine(): Promise<AvroEngine> {
  engine ??= (async () => {
    const { dotnet } = await import(/* @vite-ignore */ frameworkUrl);
    const runtime = await dotnet.create();
    const exports = await runtime.getAssemblyExports(runtime.getConfig().mainAssemblyName);
    return exports.Engine as AvroEngine;
  })();
  return engine;
}

/** Wires the status line of the tool layout to the engine and returns the engine. */
export async function startEngine(): Promise<AvroEngine> {
  const status = document.querySelector<HTMLElement>("[data-engine-status]");
  try {
    const started = performance.now();
    const e = await loadEngine();
    if (status) {
      status.dataset.state = "ready";
      status.textContent = `AvroConvert ${e.Version()} running in your browser (WebAssembly, started in ${Math.round(performance.now() - started)} ms)`;
    }
    return e;
  } catch (error) {
    if (status) {
      status.dataset.state = "error";
      status.textContent = `AvroConvert could not start in this browser: ${(error as Error).message}`;
    }
    throw error;
  }
}

/** Runs an engine call and turns .NET exceptions into a message without the stack trace. */
export function attempt<T>(call: () => T): { value?: T; error?: string } {
  try {
    return { value: call() };
  } catch (error) {
    const message = (error as Error).message ?? String(error);
    return { error: message.split("\n   at ")[0].replace(/^Error: /, "") };
  }
}
