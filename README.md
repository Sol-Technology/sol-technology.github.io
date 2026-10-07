# soltechnology.dev

Marketing and licensing site for SolTechnology libraries. Built with [Astro](https://astro.build) and Tailwind CSS, deployed to GitHub Pages at [soltechnology.dev](https://soltechnology.dev).

```sh
npm install
npm run dev      # http://localhost:4321
npm run build    # dist/
```

- `src/config.ts` – site metadata, legal entity, products, pricing, Paddle configuration.
- `src/pages/*.md` – legal documents (Terms, Refund Policy, Privacy Policy).
- `public/brand/` – brand assets; regenerate with `python3 scripts/brand-final.py` (requires Google Chrome for PNG rasters).
- `scripts/brand-concepts.py`, `scripts/brand-product.py` – exploration boards (not deployed; output goes to `public/brand/concepts/`, which is git-ignored).
