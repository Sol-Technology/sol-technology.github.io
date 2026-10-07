#!/usr/bin/env python3
"""AvroConvert product mark: SolTechnology chevrons outside, Avro-inspired paper plane (solar) inside."""
from pathlib import Path
import math, subprocess, re

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "public" / "brand"
CONCEPTS = OUT / "concepts"
CONCEPTS.mkdir(parents=True, exist_ok=True)

SOLAR, INK, WHITE, SKY = "#F59E0B", "#0B1F33", "#FFFFFF", "#38BDF8"
FONT = "Inter, 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif"
N, R_IN, R_OUT, HALF, SW = 7, 31, 44, 13, 7.5


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
        out.append(f'<polyline points="{ax:.2f},{ay:.2f} {bx:.2f},{by:.2f} {cx:.2f},{cy:.2f}" fill="none" stroke="{col}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>')
    return "\n  ".join(out)


# --- inner glyphs (all drawn inside r≈21 around 50,50) ---

def official_avro(col):
    """Official Apache Avro paths, recolored. Reference only – ASF trademark."""
    src = (ROOT / "scripts" / "avro-logo-ref.svg").read_text()
    paths = re.findall(r'<path[^>]*d="([^"]+)"', src)
    body = "".join(f'<path fill="{col}" d="{d}"/>' for d in paths)
    # viewBox 2 2 35 30 → center (19.5,17), fit into ~40 px
    return f'<g transform="translate(50,50) scale(1.15) translate(-19.5,-17)">{body}</g>'


def plane(col, scale=1.55, rot=-32):
    """Own paper plane ('send' glyph), 24-box, tip right."""
    d = "M2 21 L23 12 L2 3 L2 10 L17 12 L2 14 Z"
    return f'<g transform="translate(50,50) rotate({rot}) scale({scale}) translate(-12.5,-12)"><path d="{d}" fill="{col}"/></g>'


def plane_splash(col, drops=SOLAR):
    """Own plane + three drops (nod to Avro splash)."""
    return plane(col, 1.45, -32) + "".join(
        f'<circle cx="{x}" cy="{y}" r="{r}" fill="{drops}"/>' for x, y, r in ((36, 33, 2.6), (44, 27, 2.0), (52, 25, 1.5)))


def plane_outline(col, scale=1.6, rot=-32):
    """Own plane as stroked outline (matches chevron line weight)."""
    d = "M2 21 L23 12 L2 3 L2 10 L17 12 L2 14 Z"
    return f'<g transform="translate(50,50) rotate({rot}) scale({scale}) translate(-12.5,-12)"><path d="{d}" fill="none" stroke="{col}" stroke-width="2.6" stroke-linejoin="round"/></g>'


VARIANTS = [
    ("P1 oficjalne logo Avro (ref.)", official_avro),
    ("P2 własny samolocik", plane),
    ("P3 samolocik + plusk", plane_splash),
    ("P4 samolocik kontur", plane_outline),
]


def svg(body, w=100, h=100):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="{w}" height="{h}">\n  {body}\n</svg>\n'


def board():
    rows = len(VARIANTS)
    H = 120 + rows * 200
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 {H}" width="1400" height="{H}" font-family="{FONT}">',
         f'<rect width="1400" height="{H}" fill="#F6F7F9"/>',
         f'<text x="60" y="60" font-size="22" font-weight="600" fill="{INK}">AvroConvert — znak produktu (chevrony SolTechnology + Avro w żółci)</text>',
         f'<text x="60" y="88" font-size="15" fill="#5B6B7B">P1 tylko do porównania: logo Apache Avro jest znakiem towarowym ASF i nie może być częścią logo produktu</text>']
    for i, (nm, fn) in enumerate(VARIANTS):
        y = 110 + i * 200
        for x, bg, chev, fg in ((60, WHITE, INK, INK), (720, INK, WHITE, WHITE)):
            s.append(f'<rect x="{x}" y="{y}" width="620" height="180" rx="16" fill="{bg}" stroke="#E3E7EC"/>')
            mark = chevrons(chev) + fn(SOLAR)
            s.append(f'<g transform="translate({x+30},{y+30}) scale(1.2)">{mark}</g>')
            s.append(f'<text x="{x+190}" y="{y+80}" font-size="40" font-weight="700" letter-spacing="-1.2" fill="{SOLAR}">sol<tspan font-weight="400" fill="{fg}">technology</tspan></text>')
            s.append(f'<text x="{x+190}" y="{y+112}" font-size="22" font-weight="500" fill="{"#5B6B7B" if bg == WHITE else "#9FB0C0"}">/ AvroConvert</text>')
            s.append(f'<text x="{x+190}" y="{y+150}" font-size="13" fill="{"#8A97A6" if bg == WHITE else "#9FB0C0"}">{nm}</text>')
            s.append(f'<g transform="translate({x+520},{y+40}) scale(0.48)">{mark}</g>')
            s.append(f'<g transform="translate({x+580},{y+56}) scale(0.32)">{mark}</g>')
            s.append(f'<g transform="translate({x+540},{y+110}) scale(0.16)">{mark}</g>')
            s.append(f'<g transform="translate({x+570},{y+100}) scale(0.32)">{chevrons(fg) + fn(fg)}</g>')
    s.append("</svg>")
    (CONCEPTS / "avroconvert-mark.svg").write_text("\n".join(s), encoding="utf-8")
    return H


H = board()
# standalone marks for P2–P4
for key, fn in (("p2", plane), ("p3", plane_splash), ("p4", plane_outline)):
    (CONCEPTS / f"avroconvert-{key}.svg").write_text(svg(chevrons(INK) + fn(SOLAR)), encoding="utf-8")
    (CONCEPTS / f"avroconvert-{key}-dark.svg").write_text(svg(chevrons(WHITE) + fn(SOLAR)), encoding="utf-8")

import sys
if len(sys.argv) > 1:
    dst = Path(sys.argv[1]); dst.mkdir(parents=True, exist_ok=True)
    subprocess.run(["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    f"--window-size=1400,{H}", f"--screenshot={dst/'avroconvert-mark.png'}", (CONCEPTS / "avroconvert-mark.svg").as_uri()],
                   check=True, capture_output=True)
print("ok")
