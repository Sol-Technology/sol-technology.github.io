import { readFileSync } from "node:fs";
import { join } from "node:path";

/** The AvroConvert version the Online engine is built with, read from its project file at build time. */
export const engineVersion: string =
  readFileSync(join(process.cwd(), "tools/avroconvert-wasm/AvroConvertWasm.csproj"), "utf8").match(
    /Include="AvroConvert" Version="([^"]+)"/,
  )?.[1] ?? "";
