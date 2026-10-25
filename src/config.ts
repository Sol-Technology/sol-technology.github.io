export const site = {
  name: "SolTechnology",
  domain: "soltechnology.dev",
  url: "https://soltechnology.dev",
  tagline: "High-performance .NET libraries with commercial licences for companies",
  contactEmail: "contact@soltechnology.dev",
  supportEmail: "support@soltechnology.dev",
  github: "https://github.com/sol-technology",
  // Legal entity shown in Terms (the Merchant of Record's account review requires the sole proprietor's legal name). Keep in sync with terms.md / privacy.md.
  legalName: "Adrian Strugała Sol Technology",
  legalAddress: "Młodych Techników 4/38, 53-646 Wrocław, Poland",
  legalTaxId: "NIP 8971889807",
};

// Polar (polar.sh), reseller and Merchant of Record. One hosted Checkout Link per plan (Polar → Checkout Links → New Link,
// one product, return URL https://soltechnology.dev/avroconvert/#pricing). Production links live on buy.polar.sh; sandbox ones
// (for local tests, see licensing/ops/docs/MarketplaceChecklist.md) on sandbox-api.polar.sh. An empty link falls back to e-mail.
export const polar = {
  checkoutLinks: {
    avroconvertBusiness: "https://buy.polar.sh/polar_cl_mo815lurMHhc99B1R1CtS08tv3x0qmL5pqc4k0sKZnj",
    avroconvertEnterprise: "https://buy.polar.sh/polar_cl_DyVDhVWMuVWtQCTy7f5hWaVBkIKE3SicmR68h2ZO7lF",
  },
  // Shown on card statements; Polar's default descriptor is "POLAR* <organisation name>".
  statementDescriptor: "POLAR* SOLTECHNOLOGY",
};

export const products = [
  {
    slug: "avroconvert",
    name: "AvroConvert",
    short: "Rapid Apache Avro serializer for .NET",
    description:
      "Serialize .NET objects to Apache Avro and back with native support for C# types, schema generation, codecs and streaming.",
    nuget: "https://www.nuget.org/packages/AvroConvert",
    repo: "https://github.com/AdrianStrugala/AvroConvert",
    docs: "https://github.com/AdrianStrugala/AvroConvert/tree/master/docs",
    online: "/avroconvert/online/",
    mark: "/brand/avroconvert-mark.svg",
    markDark: "/brand/avroconvert-mark-dark.svg",
    stats: { downloads: "5.3M+", perDay: "4.4K", since: "2019" },
  },
];

export const pricing = {
  currency: "USD",
  tiers: [
    {
      id: "free",
      name: "Community",
      price: 0,
      period: "forever",
      for: "Individuals, open source, education and small businesses",
      bullets: [
        "Full library, no feature limits",
        "Companies under 100 people and under USD 1M annual revenue",
        "Personal, educational, research and nonprofit use",
        "Community support on GitHub",
      ],
      cta: { label: "Install from NuGet", href: "https://www.nuget.org/packages/AvroConvert" },
      license: "PolyForm Small Business 1.0.0 (noncommercial users also covered by PolyForm Noncommercial 1.0.0)",
    },
    {
      id: "business",
      name: "Business",
      price: 199,
      period: "per organisation / year",
      for: "Companies above the Community threshold with fewer than 1,000 people, not publicly listed, not public sector",
      bullets: [
        "Commercial licence for production use",
        "Unlimited developers, applications and deployments",
        "Covers your company and its wholly owned subsidiaries",
        "Also covers the 3.4.x maintenance releases for teams not yet on .NET 10",
        "Perpetual fallback: versions released during your subscription stay licensed forever",
        "Priority issue triage on GitHub",
      ],
      cta: { label: "Buy Business licence", checkoutLink: "avroconvertBusiness" },
      license: "SolTechnology Commercial Licence",
      highlight: true,
    },
    {
      id: "enterprise",
      name: "Enterprise",
      price: 1499,
      period: "per organisation / year",
      for: "Required for organisations with 1,000+ people, publicly listed companies and the public sector",
      bullets: [
        "Everything in Business",
        "Covers all affiliates worldwide, not only wholly owned subsidiaries",
        "E-mail support, 2 business-day response target",
        "Purchase order and bank transfer on request",
        "Signed licence agreement on request",
      ],
      cta: { label: "Buy Enterprise licence", checkoutLink: "avroconvertEnterprise" },
      license: "SolTechnology Commercial Licence",
    },
  ],
};

// AvroConvert Online: tools that run AvroConvert in the browser (.NET WebAssembly, tools/avroconvert-wasm).
export const onlineTools = [
  {
    slug: "",
    name: "Schema → C#",
    title: "Avro schema to C# class generator",
    description: "Paste an Apache Avro schema or drop an .avro file and get C# classes for AvroConvert. Runs in your browser.",
  },
  {
    slug: "avro-viewer",
    name: "Avro file viewer",
    title: "Avro file viewer",
    description: "Open an .avro file in the browser: schema, codec, metadata, record count and the records as JSON. Nothing is uploaded.",
  },
  {
    slug: "json-to-avro",
    name: "JSON → Avro",
    title: "JSON to Avro converter",
    description: "Infer an Avro schema from JSON, generate the C# model, compare sizes per codec and download the .avro file.",
  },
  {
    slug: "schema-compatibility",
    name: "Schema compatibility",
    title: "Avro schema compatibility checker",
    description: "Check two Avro schemas for backward, forward or full compatibility, see every breaking change, canonical form and fingerprints.",
  },
  {
    slug: "kafka-message-decoder",
    name: "Kafka message decoder",
    title: "Kafka Avro message decoder",
    description: "Decode a Confluent Schema Registry Kafka message: magic byte, schema id or GUID, and the Avro payload as JSON.",
  },
];
