#!/usr/bin/env python3
"""SolTechnology.Core package marks: SolTechnology chevrons outside, one glyph per package inside.
The base package uses the plain SolTechnology mark; testing kits reuse their parent's glyph with a
lab-flask badge. Writes the concept sheet to public/brand/concepts/core/ and, with Chrome, the
white NuGet icons to public/brand/core/<PackageId>-nuget-128-white.png."""
from pathlib import Path
import math, subprocess

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "public" / "brand" / "concepts" / "core"
FINAL = ROOT / "public" / "brand" / "core"
OUT.mkdir(parents=True, exist_ok=True)
FINAL.mkdir(parents=True, exist_ok=True)
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

SOLAR, INK, WHITE = "#F59E0B", "#0B1F33", "#FFFFFF"
FONT = "Inter, 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif"
N, R_IN, R_OUT, HALF, SW = 7, 31, 44, 13, 7.5
GLYPH_SW = 4.2   # same visual weight as the AvroConvert and DateTimeZone glyphs


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


def stroke(col, sw=GLYPH_SW):
    return f'fill="none" stroke="{col}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"'


# --- glyphs, drawn inside r≈18 around 50,50 ---

def result(c):      # success / failure as a value
    return f'<polyline points="38,51 46,59 62,41" {stroke(c, 5)}/>'


def cqrs(c):        # one request, two paths
    s = stroke(c)
    return (f'<polyline points="50,66 50,53 39,40" {s}/><polyline points="50,53 61,40" {s}/>'
            f'<polyline points="39,47 39,40 46,40" {s}/><polyline points="54,40 61,40 61,47" {s}/>')


def tale(c):        # open book
    s = stroke(c, 3.6)
    return (f'<path d="M50 40 C44 36 38 36 33 38 L33 62 C38 60 44 60 50 64 C56 60 62 60 67 62 L67 38 C62 36 56 36 50 40 Z" {s}/>'
            f'<line x1="50" y1="40" x2="50" y2="63" {s}/>')


def logging(c):     # log lines
    s = stroke(c)
    return "".join(f'<line x1="36" y1="{y}" x2="{x2}" y2="{y}" {s}/>' for y, x2 in ((40, 64), (50, 56), (60, 61)))


def http(c):        # globe
    s = stroke(c, 3.6)
    return (f'<circle cx="50" cy="50" r="16" {s}/><ellipse cx="50" cy="50" rx="7" ry="16" {s}/>'
            f'<line x1="34" y1="50" x2="66" y2="50" {s}/>')


def api(c):         # { }
    s = stroke(c)
    left = "M45 35 Q39 35 39 41 L39 46 Q39 50 35 50 Q39 50 39 54 L39 59 Q39 65 45 65"
    right = "M55 35 Q61 35 61 41 L61 46 Q61 50 65 50 Q61 50 61 54 L61 59 Q61 65 55 65"
    return f'<path d="{left}" {s}/><path d="{right}" {s}/>'


def auth(c):        # key
    s = stroke(c)
    return (f'<circle cx="41" cy="50" r="7" {s}/><polyline points="48,50 66,50" {s}/>'
            f'<polyline points="60,50 60,57" {s}/><polyline points="66,50 66,55" {s}/>')


def cache(c):       # lightning
    return f'<polygon points="54,33 39,53 49,53 46,67 61,46 51,46" fill="{c}" stroke="{c}" stroke-width="2" stroke-linejoin="round"/>'


def auid(c):        # #
    s = stroke(c)
    return (f'<line x1="46" y1="35" x2="42" y2="65" {s}/><line x1="59" y1="35" x2="55" y2="65" {s}/>'
            f'<line x1="36" y1="44" x2="65" y2="44" {s}/><line x1="35" y1="56" x2="64" y2="56" {s}/>')


def sql(c):         # database cylinder
    s = stroke(c, 3.6)
    return (f'<ellipse cx="50" cy="39" rx="13" ry="5" {s}/>'
            f'<path d="M37 39 L37 61 A13 5 0 0 0 63 61 L63 39" {s}/>'
            f'<path d="M37 50 A13 5 0 0 0 63 50" {s}/>')


def blob(c):        # cloud, narrower than the ring opening
    return (f'<g transform="translate(50,51) scale(0.86) translate(-50,-51)">'
            f'<path d="M38 61 A8 8 0 0 1 37 45 A11 11 0 0 1 58 41 A9 9 0 0 1 63 61 Z" {stroke(c)}/></g>')


def messagebus(c):  # envelope
    s = stroke(c)
    return f'<rect x="35" y="40" width="30" height="21" rx="2.5" {s}/><polyline points="36,42 50,52 64,42" {s}/>'


def hangfire(c):    # flame
    return (f'<path d="M50 34 C56 42 63 47 63 55 A13 12 0 0 1 37 55 C37 49 42 46 44 41 C46 46 48 48 51 49 '
            f'C51 44 50 39 50 34 Z" {stroke(c)}/>')


def flask(c, sw=GLYPH_SW):
    s = stroke(c, sw)
    return (f'<path d="M44 36 L44 47 L35 62 Q33 66 38 66 L62 66 Q67 66 65 62 L56 47 L56 36" {s}/>'
            f'<line x1="41" y1="36" x2="59" y2="36" {s}/><line x1="39" y1="57" x2="61" y2="57" {s}/>')


def sol(c):         # the plain SolTechnology mark: solar ring
    return f'<circle cx="50" cy="50" r="11" fill="none" stroke="{c}" stroke-width="7.5"/>'


def with_flask(parent):
    """Parent glyph shrunk to the upper left, flask badge in the lower right."""
    def glyph(c):
        badge = (f'<circle cx="62" cy="62" r="10" fill="{WHITE}"/>'
                 f'<g transform="translate(62,62) scale(0.42) translate(-50,-51)">{flask(INK, 6)}</g>')
        return f'<g transform="translate(46,46) scale(0.8) translate(-50,-50)">{parent(c)}</g>{badge}'
    return glyph


PACKAGES = [
    ("SolTechnology.Core", sol), ("CQRS", cqrs), ("Tale", tale), ("Logging", logging),
    ("HTTP", http), ("Api", api), ("Authentication", auth), ("Cache", cache),
    ("AUID", auid), ("SQL", sql), ("Blob", blob), ("MessageBus", messagebus),
    ("Hangfire", hangfire), ("Testing", flask), ("API.Testing", with_flask(api)),
    ("HTTP.Testing", with_flask(http)), ("SQL.Testing", with_flask(sql)),
    ("Redis.Testing", with_flask(cache)), ("ServiceBus.Testing", with_flask(messagebus)),
    ("Blob.Testing", with_flask(blob)),
]


def mark(glyph, chev=INK):
    return chevrons(chev) + "\n  " + glyph(SOLAR)


def svg(body, w, h, vb):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{w}" height="{h}">\n  {body}\n</svg>\n'


def shot(src, dst, w, h):
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--default-background-color=00000000",
           f"--window-size={w},{h}", f"--screenshot={dst}", Path(src).resolve().as_uri()]
    for _ in range(3):
        if subprocess.run(cmd, capture_output=True).returncode == 0 and Path(dst).exists():
            return
    raise RuntimeError(f"screenshot failed: {dst}")


COLS, TILE_W, TILE_H = 5, 240, 250
tiles = []
for i, (name, glyph) in enumerate(PACKAGES):
    x, y = (i % COLS) * TILE_W, (i // COLS) * TILE_H
    slug = name.replace("SolTechnology.", "").lower().replace(".", "-")
    (OUT / f"core-{slug}-mark.svg").write_text(svg(mark(glyph), 100, 100, "0 0 100 100"), encoding="utf-8")
    tiles.append(
        f'<g transform="translate({x},{y})">'
        f'<rect x="10" y="10" width="{TILE_W-20}" height="{TILE_H-20}" rx="18" fill="{WHITE}" stroke="#E2E8F0"/>'
        f'<g transform="translate(30,26) scale(1.4)">{mark(glyph)}</g>'
        f'<g transform="translate(176,26) scale(0.32)">{mark(glyph)}</g>'
        f'<g transform="translate(176,66) scale(0.16)">{mark(glyph)}</g>'
        f'<text x="{TILE_W/2}" y="{TILE_H-30}" text-anchor="middle" font-family="{FONT}" font-size="17" font-weight="600" fill="{INK}">{name}</text>'
        f'</g>')

rows = math.ceil(len(PACKAGES) / COLS)
W, H = COLS * TILE_W, rows * TILE_H + 70
sheet = svg(f'<rect width="{W}" height="{H}" fill="#F1F5F9"/>\n  '
            f'<text x="20" y="44" font-family="{FONT}" font-size="26" font-weight="700" fill="{SOLAR}">sol'
            f'<tspan font-weight="400" fill="{INK}">technology</tspan><tspan font-weight="500" fill="#5B6B7B"> / Core 2.0 package icons — concepts</tspan></text>\n  '
            f'<g transform="translate(0,60)">{"".join(tiles)}</g>', W, H, f"0 0 {W} {H}")
(OUT / "core-icons-sheet.svg").write_text(sheet, encoding="utf-8")
if Path(CHROME).exists():
    shot(OUT / "core-icons-sheet.svg", OUT / "core-icons-sheet.png", W, H)
    # white NuGet icon per package (decision 27.10.2026: white backgrounds on GitHub, NuGet, Polar)
    for name, glyph in PACKAGES:
        package_id = name if name.startswith("SolTechnology.") else f"SolTechnology.Core.{name}"
        white = f'<rect width="1024" height="1024" fill="{WHITE}"/>\n  <g transform="translate(192,192) scale(6.4)">{mark(glyph)}</g>'
        (FINAL / f"{package_id}-avatar-white.svg").write_text(svg(white, 1024, 1024, "0 0 1024 1024"), encoding="utf-8")
        tmp = FINAL / "_tmp.svg"
        tmp.write_text(svg(white, 128, 128, "0 0 1024 1024"))
        shot(tmp, FINAL / f"{package_id}-nuget-128-white.png", 128, 128)
        tmp.unlink()
print(f"{len(PACKAGES)} marks + sheet -> {OUT}; NuGet icons -> {FINAL}")
