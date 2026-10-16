#!/usr/bin/env python3
"""NuGet radar: popular packages that look abandoned, single-maintainer or commercially licensed.

Usage: python3 nuget-radar.py [--top 1500] [--stale-days 365] [--out radar.md]
Reads only public nuget.org APIs. Takes a few minutes for 1500 packages.
"""
import argparse
import concurrent.futures as cf
import json
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone

SEARCH = "https://azuresearch-usnc.nuget.org/query"
REG = "https://api.nuget.org/v3/registration5-gz-semver2/{id}/index.json"

SKIP_PREFIXES = (
    "microsoft.", "system.", "runtime.", "netstandard", "mono.", "xamarin.", "aspnet", "azure.", "google.",
    "aws", "amazon.", "grpc.", "nunit", "xunit", "mstest", "coverlet", "humanizer.core.", "nuget.", "roslyn",
    "fsharp.", "libuv", "sqlitepclraw", "entityframework", "dotnet-", "stylecop", "sonaranalyzer", "oracle.",
    "mysql.", "npgsql", "newtonsoft", "castle.", "antlr", "jetbrains", "nerdbank", "mediatr.contracts",
    "stripe", "twilio", "sendgrid", "serilog.sinks.", "opentelemetry.", "automapper.extensions", "hangfire.",
    "polly.", "swashbuckle.", "identitymodel", "bouncycastle", "k4os", "mimekit", "mailkit", "sharpziplib",
)

COMMERCIAL_LICENSES = re.compile(r"polyform|rpl|commercial|proprietary|license\.txt|licence\.txt|LicenseRef", re.I)


def get(url, retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "soltechnology-radar/1.0", "Accept-Encoding": "gzip"})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
                if r.headers.get("Content-Encoding") == "gzip":
                    import gzip
                    data = gzip.decompress(data)
                return json.loads(data)
        except Exception as e:  # noqa: BLE001
            if i == retries - 1:
                return {"_error": str(e)}
            time.sleep(1.5 * (i + 1))


def search_top(n):
    out = []
    skip = 0
    while len(out) < n:
        take = min(100, n - len(out))
        res = get(f"{SEARCH}?q=&prerelease=false&skip={skip}&take={take}")
        data = res.get("data", [])
        if not data:
            break
        out.extend(data)
        skip += take
    return out


def is_pre(v):
    return "-" in v


def latest_stable_published(pkg_id):
    idx = get(REG.format(id=pkg_id.lower()))
    if "_error" in idx or not idx.get("items"):
        return None, None
    pages = idx["items"]
    # walk pages from newest; fetch page body if not inlined
    for page in reversed(pages):
        items = page.get("items")
        if items is None:
            page = get(page["@id"])
            items = page.get("items", [])
        for leaf in reversed(items):
            ce = leaf.get("catalogEntry", {})
            v = ce.get("version", "")
            if not v or is_pre(v):
                continue
            if ce.get("listed") is False:
                continue
            pub = ce.get("published")
            if not pub or pub.startswith("1900"):
                continue
            dep = bool(ce.get("deprecation"))
            return datetime.fromisoformat(pub.replace("Z", "+00:00")), dep
    return None, None


def analyse(pkg, stale_days):
    pid = pkg["id"]
    pub, deprecated = latest_stable_published(pid)
    now = datetime.now(timezone.utc)
    age = (now - pub).days if pub else None
    owners = pkg.get("owners") or []
    lic = pkg.get("licenseExpression") or pkg.get("licenseUrl") or ""
    flags = []
    if age is not None and age > stale_days:
        flags.append(f"stale {age // 30}m")
    if len(owners) == 1:
        flags.append("1 owner")
    if deprecated:
        flags.append("deprecated")
    if COMMERCIAL_LICENSES.search(lic):
        flags.append("non-OSS licence")
    return {
        "id": pid,
        "downloads": pkg.get("totalDownloads", 0),
        "owners": ",".join(owners),
        "licence": lic.replace("https://", "").replace("http://", "")[:40],
        "last_stable": pub.date().isoformat() if pub else "?",
        "age_days": age,
        "flags": flags,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=1500)
    ap.add_argument("--stale-days", type=int, default=365)
    ap.add_argument("--out", default="nuget-radar.md")
    ap.add_argument("--workers", type=int, default=12)
    args = ap.parse_args()

    print(f"fetching top {args.top} by downloads...", file=sys.stderr)
    top = search_top(args.top)
    cands = [p for p in top if not p["id"].lower().startswith(SKIP_PREFIXES)]
    print(f"{len(top)} fetched, {len(cands)} after prefix filter; resolving release dates...", file=sys.stderr)

    rows = []
    with cf.ThreadPoolExecutor(args.workers) as ex:
        for i, r in enumerate(ex.map(lambda p: analyse(p, args.stale_days), cands), 1):
            rows.append(r)
            if i % 100 == 0:
                print(f"  {i}/{len(cands)}", file=sys.stderr)

    flagged = [r for r in rows if r["flags"]]
    flagged.sort(key=lambda r: -r["downloads"])

    with open(args.out, "w") as f:
        f.write(f"# NuGet radar – {datetime.now().date()} – top {args.top} by total downloads, stale > {args.stale_days} days\n\n")
        f.write(f"{len(rows)} packages checked after excluding Microsoft/System/runtime; {len(flagged)} flagged.\n\n")
        f.write("| # | Package | Total downloads | Last stable | Owners | Licence | Flags |\n|---|---|---|---|---|---|---|\n")
        for i, r in enumerate(flagged, 1):
            f.write(f"| {i} | {r['id']} | {r['downloads']:,} | {r['last_stable']} | {r['owners']} | {r['licence']} | {', '.join(r['flags'])} |\n")
    print(f"wrote {args.out}: {len(flagged)} flagged of {len(rows)}", file=sys.stderr)


if __name__ == "__main__":
    main()
