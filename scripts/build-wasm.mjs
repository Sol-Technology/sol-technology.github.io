// Publishes the AvroConvert Online engine (tools/avroconvert-wasm, .NET WebAssembly) into
// public/avroconvert/online/_framework, where the tool pages load it from. Requires the .NET 10 SDK.
// GitHub Pages compresses on the fly, so the precompressed .br/.gz copies are left out.
import { execFileSync } from "node:child_process";
import { cpSync, mkdirSync, rmSync } from "node:fs";

const publishDir = ".wasm-publish";
const target = "public/avroconvert/online/_framework";

rmSync(publishDir, { recursive: true, force: true });
execFileSync("dotnet", ["publish", "tools/avroconvert-wasm/AvroConvertWasm.csproj", "-c", "Release", "-o", publishDir, "--nologo"], { stdio: "inherit" });

rmSync(target, { recursive: true, force: true });
mkdirSync(target, { recursive: true });
cpSync(`${publishDir}/wwwroot/_framework`, target, { recursive: true, filter: (src) => !/\.(br|gz)$/.test(src) });
rmSync(publishDir, { recursive: true, force: true });
console.log(`AvroConvert Online engine published to ${target}`);
