#!/usr/bin/env python3
"""SolTechnology.DataLake product mark: SolTechnology chevrons outside, waves (solar) inside.
Writes SVG into public/brand/ and, if Chrome is available, PNG rasters.
Run after brand-final.py; the geometry and colours are the same."""
from pathlib import Path
import math, subprocess, sys

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "public" / "brand"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

SOLAR, INK, WHITE = "#F59E0B", "#0B1F33", "#FFFFFF"
FONT = "Inter, 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif"
N, R_IN, R_OUT, HALF, SW = 7, 31, 44, 13, 7.5
GLYPH_SW = 4.2   # same visual weight as the AvroConvert plane outline (2.6 × 1.6)


def pt(cx, cy, r, deg):
    a = math.radians(deg)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def chevrons(col, sw=SW):
    out = []
    for k in range(N):
        ang = -90 + k * 360 / N
        ax, ay = pt(50, 50, R_IN, ang - HALF)
        bx, by = pt(50, 50, R_OUT, ang)
        cx, cy = pt(50, 50, R_IN, ang + HALF)
        out.append(f'<polyline points="{ax:.2f},{ay:.2f} {bx:.2f},{by:.2f} {cx:.2f},{cy:.2f}" fill="none" stroke="{col}" '
                   f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>')
    return "\n  ".join(out)


def layers(col, *, sw=GLYPH_SW):
    """Stacked layers: a table built from files and snapshots. Waves were tried and dropped: they read as the sea."""
    a = f'fill="none" stroke="{col}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"'
    return (f'<polygon points="50,35 66,43 50,51 34,43" {a}/>\n  '
            f'<polyline points="34,51 50,59 66,51" {a}/>\n  '
            f'<polyline points="34,59 50,67 66,59" {a}/>')


def product_mark(chev, glyph, *, small=False):
    if small:
        return chevrons(chev, sw=9) + "\n  " + layers(glyph, sw=5.5)
    return chevrons(chev) + "\n  " + layers(glyph)


def svg(body, w=100, h=100, vb="0 0 100 100"):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{w}" height="{h}">\n  {body}\n</svg>\n'


def write(name, content):
    (OUT / name).write_text(content, encoding="utf-8")


def shot(src, dst, w, h):
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--default-background-color=00000000",
           f"--window-size={w},{h}", f"--screenshot={dst}", Path(src).resolve().as_uri()]
    for _ in range(3):   # headless Chrome occasionally exits 2 when launched back-to-back
        if subprocess.run(cmd, capture_output=True).returncode == 0 and Path(dst).exists():
            return
    raise RuntimeError(f"screenshot failed: {dst}")


def wordmark(x, y, fg, sub):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="44" font-weight="700" letter-spacing="-1.3" fill="{SOLAR}">sol'
            f'<tspan font-weight="400" fill="{fg}">technology</tspan></text>\n  '
            f'<text x="{x}" y="{y+34}" font-family="{FONT}" font-size="26" font-weight="500" fill="{sub}">/ DataLake</text>')


FAVICON_DARK = "<style>@media (prefers-color-scheme: dark) { polyline { stroke: #FFFFFF; } }</style>\n  "

write("datalake-mark.svg", svg(product_mark(INK, SOLAR)))
write("datalake-mark-dark.svg", svg(product_mark(WHITE, SOLAR)))
write("datalake-mark-mono.svg", svg(product_mark("currentColor", "currentColor")))
write("datalake-mark-small.svg", svg(product_mark(INK, SOLAR, small=True)))
write("datalake-mark-small-dark.svg", svg(product_mark(WHITE, SOLAR, small=True)))
write("datalake-favicon.svg", svg(FAVICON_DARK + product_mark(INK, SOLAR, small=True)))
# canvas cropped to the content (mark + wordmark end at ~450), so the PNG centres in a README
LOGO_W = 460
write("datalake-logo-horizontal.svg", svg(f'<g transform="translate(10,10)">{product_mark(INK, SOLAR)}</g>\n  {wordmark(130, 66, INK, "#5B6B7B")}', LOGO_W, 120, f"0 0 {LOGO_W} 120"))
write("datalake-logo-horizontal-dark.svg", svg(f'<g transform="translate(10,10)">{product_mark(WHITE, SOLAR)}</g>\n  {wordmark(130, 66, WHITE, "#9FB0C0")}', LOGO_W, 120, f"0 0 {LOGO_W} 120"))
write("datalake-app-icon.svg", svg(f'<rect width="512" height="512" rx="112" fill="{INK}"/>\n  <g transform="translate(76,76) scale(3.6)">{product_mark(WHITE, SOLAR)}</g>', 512, 512, "0 0 512 512"))
write("datalake-og-image.svg", svg(
    f'<rect width="1200" height="630" fill="{INK}"/>\n  '
    f'<g transform="translate(120,165) scale(3)">{product_mark(WHITE, SOLAR)}</g>\n  '
    f'<text x="480" y="290" font-family="{FONT}" font-size="96" font-weight="700" letter-spacing="-2.9" fill="{WHITE}">DataLake</text>\n  '
    f'<text x="484" y="345" font-family="{FONT}" font-size="30" fill="#9FB0C0">Iceberg tables and Parquet datasets in .NET</text>\n  '
    f'<text x="484" y="560" font-family="{FONT}" font-size="26" font-weight="700" fill="{SOLAR}">sol<tspan font-weight="400" fill="#9FB0C0">technology</tspan><tspan fill="#7F91A3">.dev</tspan></text>',
    1200, 630, "0 0 1200 630"))

if Path(CHROME).exists():
    def raster(name, src, size, vb):
        body = (OUT / src).read_text().split("\n", 1)[1].rsplit("</svg>", 1)[0]
        tmp = OUT / f"_tmp_{size}.svg"
        tmp.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{size}" height="{size}">{body}</svg>')
        shot(tmp, OUT / name, size, size)
        tmp.unlink()
    for name, size, src in (("datalake-favicon-16.png", 16, "datalake-mark-small.svg"),
                            ("datalake-favicon-32.png", 32, "datalake-mark-small.svg"),
                            ("datalake-favicon-48.png", 48, "datalake-mark-small.svg"),
                            ("datalake-favicon-dark-16.png", 16, "datalake-mark-small-dark.svg"),
                            ("datalake-favicon-dark-32.png", 32, "datalake-mark-small-dark.svg"),
                            ("datalake-favicon-dark-48.png", 48, "datalake-mark-small-dark.svg"),
                            ("datalake-mark-1024.png", 1024, "datalake-mark.svg"),
                            ("datalake-mark-dark-1024.png", 1024, "datalake-mark-dark.svg")):
        raster(name, src, size, "0 0 100 100")
    for name, size in (("datalake-nuget-128.png", 128), ("datalake-icon-512.png", 512)):
        raster(name, "datalake-app-icon.svg", size, "0 0 512 512")
    shot(OUT / "datalake-og-image.svg", OUT / "datalake-og-image.png", 1200, 630)
    # GitHub / NuGet avatar: full-bleed square, the platform rounds it
    write("datalake-avatar.svg", svg(f'<rect width="1024" height="1024" fill="{INK}"/>\n  <g transform="translate(192,192) scale(6.4)">{product_mark(WHITE, SOLAR)}</g>', 1024, 1024, "0 0 1024 1024"))
    shot(OUT / "datalake-avatar.svg", OUT / "datalake-avatar.png", 1024, 1024)
    # NuGet package icon: dark, full bleed, same framing as AvroConvert, DateTimeZone and Core (decision 25.11.2026)
    write("datalake-nuget-512.svg", svg(f'<rect width="512" height="512" fill="{INK}"/>\n  <g transform="translate(21,31) scale(4.7)">{product_mark(WHITE, SOLAR)}</g>', 512, 512, "0 0 512 512"))
    shot(OUT / "datalake-nuget-512.svg", OUT / "datalake-nuget-512.png", 512, 512)
    # white avatar for GitHub and Polar (decision 27.10.2026); the white NuGet icon is kept but packages use the navy tile
    white = f'<rect width="1024" height="1024" fill="{WHITE}"/>\n  <g transform="translate(192,192) scale(6.4)">{product_mark(INK, SOLAR)}</g>'
    write("datalake-avatar-white.svg", svg(white, 1024, 1024, "0 0 1024 1024"))
    shot(OUT / "datalake-avatar-white.svg", OUT / "datalake-avatar-white.png", 1024, 1024)
    tmp = OUT / "_tmp.svg"
    tmp.write_text(svg(white, 128, 128, "0 0 1024 1024"))
    shot(tmp, OUT / "datalake-nuget-128-white.png", 128, 128)
    tmp.unlink()
    # opaque white logo with wordmark (2x) for READMEs that cannot rely on SVG fonts
    body = (OUT / "datalake-logo-horizontal.svg").read_text().split("\n", 1)[1].rsplit("</svg>", 1)[0]
    tmp = OUT / "_tmp.svg"
    tmp.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {LOGO_W} 120" width="{LOGO_W*2}" height="240"><rect width="{LOGO_W}" height="120" fill="{WHITE}"/>{body}</svg>')
    shot(tmp, OUT / "datalake-logo-horizontal-white.png", LOGO_W * 2, 240)
    # transparent 2x dark logo for README <picture> on GitHub dark theme
    body = (OUT / "datalake-logo-horizontal-dark.svg").read_text().split("\n", 1)[1].rsplit("</svg>", 1)[0]
    tmp.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {LOGO_W} 120" width="{LOGO_W*2}" height="240">{body}</svg>')
    shot(tmp, OUT / "datalake-logo-horizontal-dark.png", LOGO_W * 2, 240)
    tmp.unlink()
    import struct
    pngs = [(OUT / f"datalake-favicon-{n}.png").read_bytes() for n in (16, 32, 48)]
    ico = struct.pack("<HHH", 0, 1, len(pngs))
    offset = 6 + 16 * len(pngs)
    for n, data in zip((16, 32, 48), pngs):
        ico += struct.pack("<BBBBHHII", n, n, 0, 0, 1, 32, len(data), offset)
        offset += len(data)
    (OUT / "datalake-favicon.ico").write_bytes(ico + b"".join(pngs))
print("ok")
