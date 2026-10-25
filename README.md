# soltechnology.dev

Marketing and licensing site for SolTechnology libraries. Built with [Astro](https://astro.build) and Tailwind CSS, deployed to GitHub Pages at [soltechnology.dev](https://soltechnology.dev).

```sh
npm install
npm run dev      # http://localhost:4321
npm run build    # dist/
npm run build:wasm   # AvroConvert Online engine (needs the .NET 10 SDK); run once before dev/build
```

- `src/config.ts` – site metadata, legal entity, products, pricing, Polar checkout links.
- `src/pages/*.md` – legal documents (Terms, Refund Policy, Privacy Policy).
- `src/pages/avroconvert/online/` – AvroConvert Online tools. They call AvroConvert compiled to WebAssembly from `tools/avroconvert-wasm` (the AvroConvert NuGet package + `[JSExport]` functions in `Engine.cs`); `npm run build:wasm` publishes it into `public/avroconvert/online/_framework` (git-ignored, built in CI). To move the tools to a new AvroConvert release, change the package version in `AvroConvertWasm.csproj`.
- `public/brand/` – brand assets; regenerate with `python3 scripts/brand-final.py` (requires Google Chrome for PNG rasters).
- `scripts/brand-concepts.py`, `scripts/brand-product.py` – exploration boards (not deployed; output goes to `public/brand/concepts/`, which is git-ignored).
