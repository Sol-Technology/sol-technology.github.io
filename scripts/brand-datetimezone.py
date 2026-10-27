#!/usr/bin/env python3
"""SolTechnology.DateTimeZone product mark: SolTechnology chevrons outside, clock-globe (solar) inside.
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


def hands(col, sw, hour_len=8.5, minute_len=12.5, hour=21, minute=37, dot=True):
    hour_deg = -90 + ((hour % 12) + minute / 60) * 30
    minute_deg = -90 + minute * 6
    hx, hy = pt(50, 50, hour_len, hour_deg)
    mx, my = pt(50, 50, minute_len, minute_deg)
    out = (f'<polyline points="{hx:.2f},{hy:.2f} 50,50 {mx:.2f},{my:.2f}" fill="none" stroke="{col}" '
           f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>')
    if dot:
        out += f'\n  <circle cx="50" cy="50" r="{sw*0.7:.2f}" fill="{col}"/>'
    return out


def clock(col, *, r=17, sw=GLYPH_SW):
    """Plain clock dial. A globe grid and a continent were tried and dropped: unreadable below 48 px."""
    return f'<circle cx="50" cy="50" r="{r}" fill="none" stroke="{col}" stroke-width="{sw}"/>\n  ' + hands(col, sw)


def product_mark(chev, glyph, *, small=False):
    if small:
        return chevrons(chev, sw=9) + "\n  " + clock(glyph, r=16, sw=6)
    return chevrons(chev) + "\n  " + clock(glyph)


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
            f'<text x="{x}" y="{y+34}" font-family="{FONT}" font-size="26" font-weight="500" fill="{sub}">/ DateTimeZone</text>')


FAVICON_DARK = "<style>@media (prefers-color-scheme: dark) { polyline { stroke: #FFFFFF; } }</style>\n  "

write("datetimezone-mark.svg", svg(product_mark(INK, SOLAR)))
write("datetimezone-mark-dark.svg", svg(product_mark(WHITE, SOLAR)))
write("datetimezone-mark-mono.svg", svg(product_mark("currentColor", "currentColor")))
write("datetimezone-mark-small.svg", svg(product_mark(INK, SOLAR, small=True)))
write("datetimezone-mark-small-dark.svg", svg(product_mark(WHITE, SOLAR, small=True)))
write("datetimezone-favicon.svg", svg(FAVICON_DARK + product_mark(INK, SOLAR, small=True)))
# canvas cropped to the content (mark + wordmark end at ~450), so the PNG centres in a README
LOGO_W = 460
write("datetimezone-logo-horizontal.svg", svg(f'<g transform="translate(10,10)">{product_mark(INK, SOLAR)}</g>\n  {wordmark(130, 66, INK, "#5B6B7B")}', LOGO_W, 120, f"0 0 {LOGO_W} 120"))
write("datetimezone-logo-horizontal-dark.svg", svg(f'<g transform="translate(10,10)">{product_mark(WHITE, SOLAR)}</g>\n  {wordmark(130, 66, WHITE, "#9FB0C0")}', LOGO_W, 120, f"0 0 {LOGO_W} 120"))
write("datetimezone-app-icon.svg", svg(f'<rect width="512" height="512" rx="112" fill="{INK}"/>\n  <g transform="translate(76,76) scale(3.6)">{product_mark(WHITE, SOLAR)}</g>', 512, 512, "0 0 512 512"))
write("datetimezone-og-image.svg", svg(
    f'<rect width="1200" height="630" fill="{INK}"/>\n  '
    f'<g transform="translate(120,165) scale(3)">{product_mark(WHITE, SOLAR)}</g>\n  '
    f'<text x="480" y="290" font-family="{FONT}" font-size="96" font-weight="700" letter-spacing="-2.9" fill="{WHITE}">DateTimeZone</text>\n  '
    f'<text x="484" y="345" font-family="{FONT}" font-size="30" fill="#9FB0C0">A point in time, together with the time zone it is seen in</text>\n  '
    f'<text x="484" y="560" font-family="{FONT}" font-size="26" font-weight="700" fill="{SOLAR}">sol<tspan font-weight="400" fill="#9FB0C0">technology</tspan><tspan fill="#7F91A3">.dev</tspan></text>',
    1200, 630, "0 0 1200 630"))

if Path(CHROME).exists():
    def raster(name, src, size, vb):
        body = (OUT / src).read_text().split("\n", 1)[1].rsplit("</svg>", 1)[0]
        tmp = OUT / f"_tmp_{size}.svg"
        tmp.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{size}" height="{size}">{body}</svg>')
        shot(tmp, OUT / name, size, size)
        tmp.unlink()
    for name, size, src in (("datetimezone-favicon-16.png", 16, "datetimezone-mark-small.svg"),
                            ("datetimezone-favicon-32.png", 32, "datetimezone-mark-small.svg"),
                            ("datetimezone-favicon-48.png", 48, "datetimezone-mark-small.svg"),
                            ("datetimezone-favicon-dark-16.png", 16, "datetimezone-mark-small-dark.svg"),
                            ("datetimezone-favicon-dark-32.png", 32, "datetimezone-mark-small-dark.svg"),
                            ("datetimezone-favicon-dark-48.png", 48, "datetimezone-mark-small-dark.svg"),
                            ("datetimezone-mark-1024.png", 1024, "datetimezone-mark.svg"),
                            ("datetimezone-mark-dark-1024.png", 1024, "datetimezone-mark-dark.svg")):
        raster(name, src, size, "0 0 100 100")
    for name, size in (("datetimezone-nuget-128.png", 128), ("datetimezone-icon-512.png", 512)):
        raster(name, "datetimezone-app-icon.svg", size, "0 0 512 512")
    shot(OUT / "datetimezone-og-image.svg", OUT / "datetimezone-og-image.png", 1200, 630)
    # GitHub / NuGet avatar: full-bleed square, the platform rounds it
    write("datetimezone-avatar.svg", svg(f'<rect width="1024" height="1024" fill="{INK}"/>\n  <g transform="translate(192,192) scale(6.4)">{product_mark(WHITE, SOLAR)}</g>', 1024, 1024, "0 0 1024 1024"))
    shot(OUT / "datetimezone-avatar.svg", OUT / "datetimezone-avatar.png", 1024, 1024)
    # white avatar and NuGet icon (decision 27.10.2026: white backgrounds on GitHub, NuGet, Polar)
    white = f'<rect width="1024" height="1024" fill="{WHITE}"/>\n  <g transform="translate(192,192) scale(6.4)">{product_mark(INK, SOLAR)}</g>'
    write("datetimezone-avatar-white.svg", svg(white, 1024, 1024, "0 0 1024 1024"))
    shot(OUT / "datetimezone-avatar-white.svg", OUT / "datetimezone-avatar-white.png", 1024, 1024)
    tmp = OUT / "_tmp.svg"
    tmp.write_text(svg(white, 128, 128, "0 0 1024 1024"))
    shot(tmp, OUT / "datetimezone-nuget-128-white.png", 128, 128)
    tmp.unlink()
    # opaque white logo with wordmark (2x) for READMEs that cannot rely on SVG fonts
    body = (OUT / "datetimezone-logo-horizontal.svg").read_text().split("\n", 1)[1].rsplit("</svg>", 1)[0]
    tmp = OUT / "_tmp.svg"
    tmp.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {LOGO_W} 120" width="{LOGO_W*2}" height="240"><rect width="{LOGO_W}" height="120" fill="{WHITE}"/>{body}</svg>')
    shot(tmp, OUT / "datetimezone-logo-horizontal-white.png", LOGO_W * 2, 240)
    # transparent 2x dark logo for README <picture> on GitHub dark theme
    body = (OUT / "datetimezone-logo-horizontal-dark.svg").read_text().split("\n", 1)[1].rsplit("</svg>", 1)[0]
    tmp.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {LOGO_W} 120" width="{LOGO_W*2}" height="240">{body}</svg>')
    shot(tmp, OUT / "datetimezone-logo-horizontal-dark.png", LOGO_W * 2, 240)
    tmp.unlink()
    import struct
    pngs = [(OUT / f"datetimezone-favicon-{n}.png").read_bytes() for n in (16, 32, 48)]
    ico = struct.pack("<HHH", 0, 1, len(pngs))
    offset = 6 + 16 * len(pngs)
    for n, data in zip((16, 32, 48), pngs):
        ico += struct.pack("<BBBBHHII", n, n, 0, 0, 1, 32, len(data), offset)
        offset += len(data)
    (OUT / "datetimezone-favicon.ico").write_bytes(ico + b"".join(pngs))
print("ok")
