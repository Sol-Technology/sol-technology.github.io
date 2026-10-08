export const site = {
  name: "SolTechnology",
  domain: "soltechnology.dev",
  url: "https://soltechnology.dev",
  tagline: "High-performance .NET libraries with commercial licences for companies",
  contactEmail: "contact@soltechnology.dev",
  supportEmail: "support@soltechnology.dev",
  github: "https://github.com/sol-technology",
  // Legal entity shown in Terms (Paddle Domain Review requires the sole proprietor's legal name)
  legalName: "Adrian Strugala SolTechnology",
  legalAddress: "Młodych Techników 4/38, 53-646 Wrocław, Poland",
  legalTaxId: "NIP 8971889807",
};

// Paddle Billing. Leave token empty until the Paddle account is live; buttons fall back to e-mail.
export const paddle = {
  environment: "production" as "sandbox" | "production",
  clientToken: "live_ec07c55527f273e2c7442ad3eaf",
  prices: {
    avroconvertBusiness: "pri_01m4brjga04ft4m98zxaz848tg",
    avroconvertEnterprise: "pri_01m4brm8gex8ahxrepqefgc7jm",
  },
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
      for: "Companies above the Community threshold",
      bullets: [
        "Commercial licence for production use",
        "Unlimited developers, applications and deployments",
        "Perpetual fallback: versions released during your subscription stay licensed forever",
        "Priority issue triage on GitHub",
      ],
      cta: { label: "Buy Business licence", paddlePrice: "avroconvertBusiness" },
      license: "SolTechnology Commercial Licence",
      highlight: true,
    },
    {
      id: "enterprise",
      name: "Enterprise",
      price: 1499,
      period: "per organisation / year",
      for: "Support with response times, procurement-friendly purchasing",
      bullets: [
        "Everything in Business",
        "E-mail support, 2 business-day response target",
        "Invoice / purchase order / bank transfer via Paddle",
        "Signed licence agreement on request",
      ],
      cta: { label: "Buy Enterprise licence", paddlePrice: "avroconvertEnterprise" },
      license: "SolTechnology Commercial Licence",
    },
  ],
};
