export const site = {
  name: "SolTechnology",
  domain: "soltechnology.dev",
  url: "https://soltechnology.dev",
  tagline: "Rapid .NET libraries",
  contactEmail: "contact@soltechnology.dev",
  supportEmail: "support@soltechnology.dev",
  github: "https://github.com/sol-technology",
  // Legal entity shown in Terms (Paddle Domain Review requires the sole proprietor's legal name)
  legalName: "SolTechnology Adrian Strugała",
  legalAddress: "[Street, Postal code City], Poland",
  legalTaxId: "NIP [●]",
};

// Paddle Billing. Leave token empty until the Paddle account is live; buttons fall back to e-mail.
export const paddle = {
  environment: "sandbox" as "sandbox" | "production",
  clientToken: "",
  prices: {
    avroconvertBusiness: "",
    avroconvertEnterprise: "",
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
        "Noncommercial use",
        "Commercial use by organisations under 100 people and under USD 1M annual revenue",
        "Community support on GitHub",
      ],
      cta: { label: "Install from NuGet", href: "https://www.nuget.org/packages/AvroConvert" },
      license: "PolyForm Noncommercial 1.0.0 / PolyForm Small Business 1.0.0",
    },
    {
      id: "business",
      name: "Business",
      price: 599,
      period: "per organisation / year",
      for: "Organisations above the Community threshold, up to 25 developers",
      bullets: [
        "Commercial licence for production use",
        "Up to 25 developers in the organisation",
        "Perpetual fallback: versions released during your subscription stay licensed forever",
        "Priority issue triage",
      ],
      cta: { label: "Buy Business licence", paddlePrice: "avroconvertBusiness" },
      license: "SolTechnology Commercial Licence",
      highlight: true,
    },
    {
      id: "enterprise",
      name: "Enterprise",
      price: 2499,
      period: "per organisation / year",
      for: "Unlimited developers, support with response times",
      bullets: [
        "Unlimited developers in the organisation",
        "E-mail support, 2 business-day response target",
        "Perpetual fallback on all versions released during the subscription",
        "Invoice / bank transfer purchasing via Paddle",
      ],
      cta: { label: "Buy Enterprise licence", paddlePrice: "avroconvertEnterprise" },
      license: "SolTechnology Commercial Licence",
    },
  ],
};
