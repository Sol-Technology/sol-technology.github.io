export const site = {
  name: "SolTechnology",
  domain: "soltechnology.dev",
  url: "https://soltechnology.dev",
  tagline: ".NET libraries and engineering services: cloud migrations, system analysis, high-performance data",
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
    avroconvertTeam: "",
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
      id: "team",
      name: "Team",
      price: 199,
      period: "per organisation / year",
      for: "Companies above the Community threshold, up to 10 developers",
      bullets: [
        "Commercial licence for production use",
        "Up to 10 developers in the organisation",
        "Perpetual fallback: versions released during your subscription stay licensed forever",
        "Community support on GitHub",
      ],
      cta: { label: "Buy Team licence", paddlePrice: "avroconvertTeam" },
      license: "SolTechnology Commercial Licence",
    },
    {
      id: "business",
      name: "Business",
      price: 499,
      period: "per organisation / year",
      for: "Unlimited developers, priority triage",
      bullets: [
        "Commercial licence for production use",
        "Unlimited developers in the organisation",
        "Perpetual fallback on all versions released during the subscription",
        "Priority issue triage",
      ],
      cta: { label: "Buy Business licence", paddlePrice: "avroconvertBusiness" },
      license: "SolTechnology Commercial Licence",
      highlight: true,
    },
    {
      id: "enterprise",
      name: "Enterprise",
      price: 1490,
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
