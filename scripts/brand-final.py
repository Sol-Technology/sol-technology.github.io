#!/usr/bin/env python3
"""Final SolTechnology brand assets (concept BB: 7 chevrons + ring core, G6 geometry, C1 colors).
Writes SVG into public/brand/ and, if Chrome is available, PNG rasters."""
from pathlib import Path
import math, subprocess, shutil

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "public" / "brand"
OUT.mkdir(parents=True, exist_ok=True)

SOLAR = "#F59E0B"
INK = "#0B1F33"
WHITE = "#FFFFFF"
FONT = "Inter, 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif"

N, R_IN, R_OUT, HALF, SW, CORE = 7, 31, 44, 13, 7.5, 11


def pt(cx, cy, r, deg):
    a = math.radians(deg)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def mark_body(chev, core, *, filled_core=False, sw=SW, ids=False, anim=False):
    out = []
    for k in range(N):
        ang = -90 + k * 360 / N
        ax, ay = pt(50, 50, R_IN, ang - HALF)
        bx, by = pt(50, 50, R_OUT, ang)
        cx, cy = pt(50, 50, R_IN, ang + HALF)
        extra = ""
        if anim:
            extra = (f'<animate attributeName="stroke" values="{chev};{core};{chev}" keyTimes="0;0.5;1" '
                     f'dur="2.1s" begin="{k*0.3:.1f}s" repeatCount="indefinite"/>')
        out.append(f'<polyline points="{ax:.2f},{ay:.2f} {bx:.2f},{by:.2f} {cx:.2f},{cy:.2f}" fill="none" '
                   f'stroke="{chev}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">{extra}</polyline>')
    if filled_core:
        out.append(f'<circle cx="50" cy="50" r="{CORE+2}" fill="{core}"/>')
    else:
        out.append(f'<circle cx="50" cy="50" r="{CORE}" fill="none" stroke="{core}" stroke-width="{sw}"/>')
    return "\n  ".join(out)


def svg(w, h, body, vb=None):
    vb = vb or f"0 0 {w} {h}"
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{w}" height="{h}">\n  {body}\n</svg>\n'


def wordmark(x, y, size, sol, tech):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="700" '
            f'letter-spacing="{-size*0.03:.2f}" fill="{sol}">sol<tspan font-weight="400" fill="{tech}">technology</tspan></text>')


def write(name, content):
    (OUT / name).write_text(content, encoding="utf-8")


# marks
write("mark.svg", svg(100, 100, mark_body(INK, SOLAR)))
write("mark-dark.svg", svg(100, 100, mark_body(WHITE, SOLAR)))
write("mark-mono.svg", svg(100, 100, mark_body("currentColor", "currentColor")))
write("mark-small.svg", svg(100, 100, mark_body(INK, SOLAR, filled_core=True, sw=9)))      # ≤32 px
write("mark-small-dark.svg", svg(100, 100, mark_body(WHITE, SOLAR, filled_core=True, sw=9)))
write("mark-animated.svg", svg(100, 100, mark_body(INK, SOLAR, anim=True)))
write("mark-animated-dark.svg", svg(100, 100, mark_body(WHITE, SOLAR, anim=True)))
# favicons switch chevrons to white on dark browser chrome (tab bars), where navy would vanish
FAVICON_DARK = "<style>@media (prefers-color-scheme: dark) { polyline { stroke: #FFFFFF; } }</style>
  "
write("favicon.svg", svg(100, 100, FAVICON_DARK + mark_body(INK, SOLAR, filled_core=True, sw=9)))

# logos
write("logo-horizontal.svg", svg(640, 120,
      f'<g transform="translate(10,10)">{mark_body(INK, SOLAR)}</g>\n  {wordmark(130, 84, 64, SOLAR, INK)}'))
write("logo-horizontal-dark.svg", svg(640, 120,
      f'<g transform="translate(10,10)">{mark_body(WHITE, SOLAR)}</g>\n  {wordmark(130, 84, 64, SOLAR, WHITE)}'))
write("logo-stacked.svg", svg(520, 300,
      f'<g transform="translate(190,20) scale(1.4)">{mark_body(INK, SOLAR)}</g>\n  '
      f'<text x="260" y="260" text-anchor="middle" font-family="{FONT}" font-size="64" font-weight="700" letter-spacing="-1.9" fill="{SOLAR}">sol<tspan font-weight="400" fill="{INK}">technology</tspan></text>'))
write("lockup-avroconvert.svg", svg(760, 120,
      f'<g transform="translate(10,10)">{mark_body(INK, SOLAR)}</g>\n  '
      f'<text x="130" y="66" font-family="{FONT}" font-size="44" font-weight="700" letter-spacing="-1.3" fill="{SOLAR}">sol<tspan font-weight="400" fill="{INK}">technology</tspan></text>\n  '
      f'<text x="130" y="100" font-family="{FONT}" font-size="26" font-weight="500" fill="#5B6B7B">/ AvroConvert</text>'))

# app icon tile (navy tile, white chevrons, solar ring)
write("app-icon.svg", svg(512, 512,
      f'<rect width="512" height="512" rx="112" fill="{INK}"/>\n  <g transform="translate(76,76) scale(3.6)">{mark_body(WHITE, SOLAR, sw=8)}</g>'))

# og image 1200x630
write("og-image.svg", svg(1200, 630,
      f'<rect width="1200" height="630" fill="{INK}"/>\n  '
      f'<g transform="translate(120,165) scale(3)">{mark_body(WHITE, SOLAR)}</g>\n  '
      f'<text x="480" y="315" font-family="{FONT}" font-size="96" font-weight="700" letter-spacing="-2.9" fill="{SOLAR}">sol<tspan font-weight="400" fill="{WHITE}">technology</tspan></text>\n  '
      f'<text x="482" y="380" font-family="{FONT}" font-size="30" fill="#9FB0C0">High-performance .NET libraries</text>\n  '
      f'<text x="482" y="560" font-family="{FONT}" font-size="26" fill="#7F91A3">soltechnology.dev</text>'))

# rasters
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


# ---------- AvroConvert product mark (chevrons + outline paper plane) ----------

def plane_outline(col, *, scale=1.6, rot=-32, sw=2.6, filled=False):
    d = "M2 21 L23 12 L2 3 L2 10 L17 12 L2 14 Z"
    fill = col if filled else "none"
    stroke = "none" if filled else col
    return (f'<g transform="translate(50,50) rotate({rot}) scale({scale}) translate(-12.5,-12)">'
            f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/></g>')


def chev_only(chev, sw=SW):
    body = mark_body(chev, chev, sw=sw)
    return body.rsplit("\n  <circle", 1)[0]   # drop the core ring


def product_mark(chev, glyph, *, small=False):
    if small:
        return chev_only(chev, sw=9) + "\n  " + plane_outline(glyph, scale=1.45, filled=True)
    return chev_only(chev) + "\n  " + plane_outline(glyph)


write("avroconvert-mark.svg", svg(100, 100, product_mark(INK, SOLAR)))
write("avroconvert-mark-dark.svg", svg(100, 100, product_mark(WHITE, SOLAR)))
write("avroconvert-mark-mono.svg", svg(100, 100, product_mark("currentColor", "currentColor")))
write("avroconvert-mark-small.svg", svg(100, 100, product_mark(INK, SOLAR, small=True)))
write("avroconvert-mark-small-dark.svg", svg(100, 100, product_mark(WHITE, SOLAR, small=True)))
write("avroconvert-favicon.svg", svg(100, 100, FAVICON_DARK + product_mark(INK, SOLAR, small=True)))
write("avroconvert-logo-horizontal.svg", svg(760, 120,
      f'<g transform="translate(10,10)">{product_mark(INK, SOLAR)}</g>\n  '
      f'<text x="130" y="66" font-family="{FONT}" font-size="44" font-weight="700" letter-spacing="-1.3" fill="{SOLAR}">sol<tspan font-weight="400" fill="{INK}">technology</tspan></text>\n  '
      f'<text x="130" y="100" font-family="{FONT}" font-size="26" font-weight="500" fill="#5B6B7B">/ AvroConvert</text>'))
write("avroconvert-logo-horizontal-dark.svg", svg(760, 120,
      f'<g transform="translate(10,10)">{product_mark(WHITE, SOLAR)}</g>\n  '
      f'<text x="130" y="66" font-family="{FONT}" font-size="44" font-weight="700" letter-spacing="-1.3" fill="{SOLAR}">sol<tspan font-weight="400" fill="{WHITE}">technology</tspan></text>\n  '
      f'<text x="130" y="100" font-family="{FONT}" font-size="26" font-weight="500" fill="#9FB0C0">/ AvroConvert</text>'))
write("avroconvert-app-icon.svg", svg(512, 512,
      f'<rect width="512" height="512" rx="112" fill="{INK}"/>\n  <g transform="translate(76,76) scale(3.6)">{product_mark(WHITE, SOLAR)}</g>'))
write("avroconvert-og-image.svg", svg(1200, 630,
      f'<rect width="1200" height="630" fill="{INK}"/>\n  '
      f'<g transform="translate(120,165) scale(3)">{product_mark(WHITE, SOLAR)}</g>\n  '
      f'<text x="480" y="290" font-family="{FONT}" font-size="96" font-weight="700" letter-spacing="-2.9" fill="{WHITE}">AvroConvert</text>\n  '
      f'<text x="484" y="345" font-family="{FONT}" font-size="30" fill="#9FB0C0">Rapid Apache Avro serializer for .NET</text>\n  '
      f'<text x="484" y="560" font-family="{FONT}" font-size="26" font-weight="700" fill="{SOLAR}">sol<tspan font-weight="400" fill="#9FB0C0">technology</tspan><tspan fill="#7F91A3">.dev</tspan></text>'))
if Path(CHROME).exists():
    def shot(src, dst, w, h):
        cmd = [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--default-background-color=00000000",
               f"--window-size={w},{h}", f"--screenshot={dst}", (OUT / src).resolve().as_uri()]
        for attempt in range(3):   # headless Chrome occasionally exits 2 when launched back-to-back
            if subprocess.run(cmd, capture_output=True).returncode == 0 and Path(dst).exists():
                return
        raise RuntimeError(f"screenshot failed: {dst}")
    # size-specific wrappers so the SVG fills the viewport exactly
    for name, size, src in (("favicon-16.png", 16, "mark-small.svg"), ("favicon-32.png", 32, "mark-small.svg"),
                            ("favicon-48.png", 48, "mark-small.svg"), ("apple-touch-icon.png", 180, "app-icon.svg"),
                            ("icon-192.png", 192, "app-icon.svg"), ("icon-512.png", 512, "app-icon.svg"),
                            ("avroconvert-favicon-16.png", 16, "avroconvert-mark-small.svg"),
                            ("avroconvert-favicon-32.png", 32, "avroconvert-mark-small.svg"),
                            ("avroconvert-favicon-48.png", 48, "avroconvert-mark-small.svg"),
                            ("favicon-dark-16.png", 16, "mark-small-dark.svg"), ("favicon-dark-32.png", 32, "mark-small-dark.svg"),
                            ("favicon-dark-48.png", 48, "mark-small-dark.svg"),
                            ("avroconvert-favicon-dark-16.png", 16, "avroconvert-mark-small-dark.svg"),
                            ("avroconvert-favicon-dark-32.png", 32, "avroconvert-mark-small-dark.svg"),
                            ("avroconvert-favicon-dark-48.png", 48, "avroconvert-mark-small-dark.svg"),
                            ("avroconvert-nuget-128.png", 128, "avroconvert-app-icon.svg"),
                            ("avroconvert-icon-512.png", 512, "avroconvert-app-icon.svg")):
        tmp = f"_tmp_{size}.svg"
        body = (OUT / src).read_text().split("\n", 1)[1].rsplit("</svg>", 1)[0]
        vb = "0 0 512 512" if "app-icon" in src else "0 0 100 100"
        write(tmp, f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{size}" height="{size}">{body}</svg>')
        shot(tmp, OUT / name, size, size)
        (OUT / tmp).unlink()
    shot("og-image.svg", OUT / "og-image.png", 1200, 630)
    shot("avroconvert-og-image.svg", OUT / "avroconvert-og-image.png", 1200, 630)
    # GitHub / NuGet avatars: full-bleed square (platform applies its own rounding/circle crop), mark inside the safe circle
    for name, body in (("github-avatar.svg", mark_body(WHITE, SOLAR, sw=8)),
                       ("avroconvert-avatar.svg", product_mark(WHITE, SOLAR))):
        write(name, svg(1024, 1024, f'<rect width="1024" height="1024" fill="{INK}"/>\n  <g transform="translate(192,192) scale(6.4)">{body}</g>'))
        shot(name, OUT / name.replace(".svg", ".png"), 1024, 1024)
    # transparent high-res marks
    for name, src in (("mark-1024.png", "mark.svg"), ("mark-dark-1024.png", "mark-dark.svg"),
                      ("avroconvert-mark-1024.png", "avroconvert-mark.svg"), ("avroconvert-mark-dark-1024.png", "avroconvert-mark-dark.svg")):
        body = (OUT / src).read_text().split("\n", 1)[1].rsplit("</svg>", 1)[0]
        write("_tmp.svg", f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="1024" height="1024">{body}</svg>')
        shot("_tmp.svg", OUT / name, 1024, 1024)
        (OUT / "_tmp.svg").unlink()
    # ICO from PNGs (no PIL dependency): plain ICO container with PNG entries
    import struct
    for prefix in ("", "avroconvert-"):
        sizes = (16, 32, 48)
        pngs = [(OUT / f"{prefix}favicon-{s}.png").read_bytes() for s in sizes]
        hdr = struct.pack("<HHH", 0, 1, len(pngs))
        off = 6 + 16 * len(pngs)
        entries, data = b"", b""
        for s, b in zip(sizes, pngs):
            entries += struct.pack("<BBBBHHII", s % 256, s % 256, 0, 0, 1, 32, len(b), off + len(data))
            data += b
        (OUT / f"{prefix}favicon.ico").write_bytes(hdr + entries + data)
    print("rasters ok")

print("ok", OUT)
