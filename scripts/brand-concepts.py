#!/usr/bin/env python3
"""Generates SolTechnology logo concept boards (SVG) into public/brand/concepts/."""
from pathlib import Path
import math

OUT = Path(__file__).resolve().parent.parent / "public" / "brand" / "concepts"
OUT.mkdir(parents=True, exist_ok=True)

AMBER = "#F59E0B"
NAVY = "#0B1F33"
SKY = "#38BDF8"
DEEP = "#1E3A5F"   # mid navy, readable on white
FONT = "Inter, 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif"

# palette per board: primary, accent, (sol, technology) on light, (sol, technology) on dark
DEFAULT_PAL = dict(p=AMBER, a=SKY, l1=NAVY, l2=NAVY, d1="#FFFFFF", d2="#FFFFFF")
NAVY_PAL = dict(p=NAVY, a=AMBER, l1=AMBER, l2=NAVY, d1=AMBER, d2="#FFFFFF")
AMBER_PAL = dict(p=AMBER, a=NAVY, l1=AMBER, l2=NAVY, d1=AMBER, d2=SKY)
DEEP_PAL = dict(p=DEEP, a=AMBER, l1=AMBER, l2=DEEP, d1=AMBER, d2=SKY)


def pt(cx, cy, r, deg):
    a = math.radians(deg)
    return cx + r * math.cos(a), cy + r * math.sin(a)


# ---------- marks (each in a 100x100 box) ----------

def mark_a(primary, accent, mono=False):
    """A. Sun & Bit – one disc, one pixel."""
    bit = primary if mono else accent
    hole = "#FFFFFF" if mono else bit
    return f'''
    <circle cx="50" cy="50" r="40" fill="{primary}"/>
    <rect x="58" y="26" width="16" height="16" rx="2" fill="{hole}"/>'''


def mark_b(primary, accent, mono=False):
    """B. Pixel Sun – 3x3 grid, corners as short rays."""
    core = primary if mono else accent
    cells = []
    pos = [5, 37, 69]
    for i, y in enumerate(pos):
        for j, x in enumerate(pos):
            if i == 1 and j == 1:
                cells.append(f'<rect x="{x}" y="{y}" width="26" height="26" rx="7" fill="{core}"/>')
            elif i == 1 or j == 1:
                cells.append(f'<rect x="{x}" y="{y}" width="26" height="26" rx="7" fill="{primary}"/>')
            else:
                cells.append(f'<rect x="{x+5}" y="{y+5}" width="16" height="16" rx="5" fill="{primary}"/>')
    return "\n    ".join(cells)


def mark_c(primary, accent, mono=False):
    """C. Segmented Ring – six arcs (data blocks), one active, blue core."""
    arcs = []
    for k in range(6):
        c = -90 + k * 60
        x0, y0 = pt(50, 50, 36, c - 22)
        x1, y1 = pt(50, 50, 36, c + 22)
        color = (primary if mono else accent) if k == 1 else primary
        arcs.append(f'<path d="M {x0:.2f} {y0:.2f} A 36 36 0 0 1 {x1:.2f} {y1:.2f}" stroke="{color}" stroke-width="12" fill="none"/>')
    core = primary if mono else accent
    arcs.append(f'<circle cx="50" cy="50" r="9" fill="{core}"/>')
    return "\n    ".join(arcs)


def mark_d(primary, accent, mono=False):
    """D. S-Orbit – monogram S from two 3/4 arcs + satellite dot."""
    dot = primary if mono else accent
    r = 16
    tx, ty = 50, 34
    bx, by = 50, 66
    sx, sy = pt(tx, ty, r, -25)
    ex, ey = pt(bx, by, r, 155)
    return f'''
    <path d="M {sx:.2f} {sy:.2f} A {r} {r} 0 1 0 {tx} {ty + r} A {r} {r} 0 1 1 {ex:.2f} {ey:.2f}" stroke="{primary}" stroke-width="12" stroke-linecap="round" fill="none"/>
    <circle cx="74" cy="74" r="7" fill="{dot}"/>'''


MARKS = {
    "a-sun-bit": ("Sun &amp; Bit", mark_a, "Simple Twist: jedna bryła, jeden ownable detal (bit)"),
    "b-pixel-sun": ("Pixel Sun", mark_b, "Pixel Sharp: siatka 3×3, czytelna od 16 px"),
    "c-segmented-ring": ("Segmented Ring", mark_c, "Ewolucja pierścieni: 6 bloków danych, jeden aktywny"),
    "d-s-orbit": ("S-Orbit", mark_d, "Monogram S + satelita; litera jako znak"),
}


# ---------- sun family (close to the original 7 rings + 7 dots) ----------

def ring_dots(primary, accent, mono, n=6, R=36, r_ring=10, sw=7, R_in=14, r_dot=4.5,
              core=None, filled=False, highlight=None):
    out = []
    for k in range(n):
        x, y = pt(50, 50, R, -90 + k * 360 / n)
        col = primary
        if highlight is not None and k == highlight and not mono:
            col = accent
        if filled:
            out.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r_ring}" fill="{col}"/>')
        else:
            out.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r_ring}" fill="none" stroke="{col}" stroke-width="{sw}"/>')
    if R_in:
        for k in range(n):
            x, y = pt(50, 50, R_in, -90 + k * 360 / n + (180 / n if n % 2 == 0 else 0))
            out.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r_dot}" fill="{primary if mono else accent}"/>')
    if core:
        out.append(f'<circle cx="50" cy="50" r="{core}" fill="{primary if mono else accent}"/>')
    return "\n    ".join(out)


def mark_e(p, a, mono=False):
    """E. Six Suns – oryginał odchudzony: 6 pełnych dysków + 6 kropek, bez konturów."""
    return ring_dots(p, a, mono, n=6, R=35, r_ring=12, R_in=14, r_dot=4.5, filled=True)


def mark_f(p, a, mono=False):
    """F. Corona – 6 pierścieni (bold) + jeden niebieski rdzeń zamiast 6 kropek."""
    return ring_dots(p, a, mono, n=6, R=35, r_ring=11, sw=8, R_in=0, core=11)


def mark_g(p, a, mono=False):
    """G. Dawn – pierścienie wokół, jeden 'wschodzący' dysk w błękicie."""
    return ring_dots(p, a, mono, n=6, R=35, r_ring=12, R_in=0, filled=True, highlight=0, core=8)


def mark_h(p, a, mono=False):
    """H. Halo – jeden gruby pierścień-słońce z 6 kropkami na orbicie."""
    inner = p if mono else a
    dots = []
    for k in range(6):
        x, y = pt(50, 50, 44, -90 + k * 60)
        dots.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="5.5" fill="{p}"/>')
    return f'''<circle cx="50" cy="50" r="22" fill="none" stroke="{p}" stroke-width="12"/>
    <circle cx="50" cy="50" r="6" fill="{inner}"/>
    ''' + "\n    ".join(dots)


def mark_i(p, a, mono=False):
    """I. Node Sun – 6 kropek połączonych z rdzeniem (graf danych)."""
    core = p if mono else a
    parts = []
    for k in range(6):
        x, y = pt(50, 50, 36, -90 + k * 60)
        parts.append(f'<line x1="50" y1="50" x2="{x:.2f}" y2="{y:.2f}" stroke="{p}" stroke-width="5" stroke-linecap="round"/>')
        parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="9" fill="{p}"/>')
    parts.append(f'<circle cx="50" cy="50" r="13" fill="{core}"/>')
    return "\n    ".join(parts)


def mark_j(p, a, mono=False):
    """J. Seven – wierne 7 elementów z oryginału, ale pełne dyski malejące ku środkowi (głębia)."""
    core = p if mono else a
    parts = []
    for k in range(7):
        x, y = pt(50, 50, 36, -90 + k * 360 / 7)
        parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="11" fill="{p}"/>')
    for k in range(7):
        x, y = pt(50, 50, 15, -90 + k * 360 / 7 + 180 / 7)
        parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4" fill="{core}"/>')
    return "\n    ".join(parts)


MARKS.update({
    "e-six-suns": ("Six Suns", mark_e, "Oryginał odchudzony: 6 pełnych dysków + 6 kropek, bez konturów"),
    "f-corona": ("Corona", mark_f, "6 bold pierścieni + jeden rdzeń; 1 kolor dominujący, 1 akcent"),
    "g-dawn": ("Dawn", mark_g, "Pierścienie + jeden 'wschodzący' dysk w błękicie (pattern break)"),
    "h-halo": ("Halo", mark_h, "Jeden gruby pierścień-słońce, 6 kropek na orbicie"),
    "i-node-sun": ("Node Sun", mark_i, "Słońce jako graf: 6 węzłów połączonych z rdzeniem"),
    "j-seven": ("Seven", mark_j, "Wierne 7+7 z oryginału, pełne dyski, kontrast skali"),
})


def wordmark(x, y, size, c1, c2):
    return f'''<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="700" letter-spacing="-{size*0.03:.1f}" fill="{c1}">sol<tspan font-weight="400" fill="{c2}">technology</tspan></text>'''


def board(key, title, fn, note, pal=DEFAULT_PAL):
    P, A = pal["p"], pal["a"]
    W, H = 1400, 820
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{FONT}">']
    s.append(f'<rect width="{W}" height="{H}" fill="#F6F7F9"/>')
    s.append(f'<text x="60" y="70" font-size="22" font-weight="600" fill="{NAVY}">Koncept {key.split("-")[0].upper()} — {title}</text>')
    s.append(f'<text x="60" y="100" font-size="16" fill="#5B6B7B">{note}</text>')

    # light panel
    s.append(f'<rect x="60" y="130" width="620" height="420" rx="18" fill="#FFFFFF" stroke="#E3E7EC"/>')
    s.append(f'<g transform="translate(110,190) scale(1.6)">{fn(P, A)}</g>')
    s.append(wordmark(300, 290, 60, pal["l1"], pal["l2"]))
    s.append(f'<text x="300" y="325" font-size="15" fill="#5B6B7B">soltechnology.dev</text>')
    # favicon row on light
    s.append(f'<text x="110" y="420" font-size="13" fill="#8A97A6">64 / 32 / 16 px</text>')
    s.append(f'<g transform="translate(110,440) scale(0.64)">{fn(P, A)}</g>')
    s.append(f'<g transform="translate(190,456) scale(0.32)">{fn(P, A)}</g>')
    s.append(f'<g transform="translate(236,464) scale(0.16)">{fn(P, A)}</g>')
    # mono on light
    s.append(f'<text x="420" y="420" font-size="13" fill="#8A97A6">mono</text>')
    s.append(f'<g transform="translate(420,440) scale(0.64)">{fn(NAVY, NAVY, mono=True)}</g>')
    s.append(f'<g transform="translate(500,456) scale(0.32)">{fn(NAVY, NAVY, mono=True)}</g>')

    # dark panel
    s.append(f'<rect x="720" y="130" width="620" height="420" rx="18" fill="{NAVY}"/>')
    dp = "#FFFFFF" if P == NAVY or P == DEEP else P
    s.append(f'<g transform="translate(770,190) scale(1.6)">{fn(dp, A if A != NAVY else SKY)}</g>')
    s.append(wordmark(960, 290, 60, pal["d1"], pal["d2"]))
    s.append(f'<text x="960" y="325" font-size="15" fill="#9FB0C0">dark mode</text>')
    s.append(f'<text x="770" y="420" font-size="13" fill="#7F91A3">mono (white)</text>')
    s.append(f'<g transform="translate(770,440) scale(0.64)">{fn("#FFFFFF", "#FFFFFF", mono=True)}</g>')
    s.append(f'<g transform="translate(850,456) scale(0.32)">{fn("#FFFFFF", "#FFFFFF", mono=True)}</g>')
    # app icon tile
    tile = AMBER if P in (NAVY, DEEP) else NAVY
    s.append(f'<rect x="1080" y="400" width="120" height="120" rx="28" fill="{tile}"/>')
    s.append(f'<g transform="translate(1100,420) scale(0.8)">{fn(P if tile == AMBER else AMBER, A if tile == AMBER else SKY)}</g>')
    s.append(f'<text x="1080" y="540" font-size="13" fill="#7F91A3">app icon</text>')

    # product lockup
    s.append(f'<rect x="60" y="580" width="1280" height="180" rx="18" fill="#FFFFFF" stroke="#E3E7EC"/>')
    s.append(f'<g transform="translate(100,620) scale(1.0)">{fn(P, A)}</g>')
    s.append(f'<text x="230" y="665" font-size="34" font-weight="700" fill="{pal["l1"]}" letter-spacing="-1">sol<tspan font-weight="400" fill="{pal["l2"]}">technology</tspan></text>')
    s.append(f'<text x="230" y="700" font-size="20" fill="#5B6B7B">/ AvroConvert</text>')
    s.append(f'<text x="700" y="650" font-size="14" fill="#8A97A6">Paleta</text>')
    for i, (c, n) in enumerate([(AMBER, "Solar  #F59E0B"), (NAVY, "Ink  #0B1F33"), (DEEP, "Deep  #1E3A5F"), (SKY, "Signal  #38BDF8")]):
        y = 665 + i * 24
        s.append(f'<rect x="700" y="{y-14}" width="18" height="18" rx="5" fill="{c}" stroke="#E3E7EC"/>')
        s.append(f'<text x="728" y="{y}" font-size="13" fill="{NAVY}">{n}</text>')
    s.append(f'<text x="1000" y="650" font-size="14" fill="#8A97A6">Typografia</text>')
    s.append(f'<text x="1000" y="680" font-size="14" fill="{NAVY}">Inter / Space Grotesk — 700 + 400</text>')
    s.append(f'<text x="1000" y="705" font-size="14" fill="{NAVY}">lowercase, tracking −3 %</text>')
    s.append('</svg>')
    (OUT / f"{key}.svg").write_text("\n".join(s), encoding="utf-8")

    # standalone mark
    (OUT / f"{key}-mark.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">{fn(P, A)}</svg>',
        encoding="utf-8")


# ---------- seven family: 7 as the signature, navy-led ----------

def seven(p, a, mono, R=36, r=11, R_in=15, r_dot=4, rings=False, sw=7, apex=None, core=None):
    out = []
    for k in range(7):
        x, y = pt(50, 50, R, -90 + k * 360 / 7)
        col = (a if (apex is not None and k == apex and not mono) else p)
        if rings:
            out.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r}" fill="none" stroke="{col}" stroke-width="{sw}"/>')
        else:
            out.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r}" fill="{col}"/>')
    if R_in:
        for k in range(7):
            x, y = pt(50, 50, R_in, -90 + k * 360 / 7 + 180 / 7)
            out.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r_dot}" fill="{p if mono else a}"/>')
    if core:
        out.append(f'<circle cx="50" cy="50" r="{core}" fill="{p if mono else a}"/>')
    return "\n    ".join(out)


def mark_k(p, a, mono=False):
    """K. Seven Ink – 7 granatowych dysków + 7 żółtych iskier."""
    return seven(p, a, mono, r=11, R_in=15, r_dot=4.2)


def mark_l(p, a, mono=False):
    """L. Apex – 7 dysków, wierzchołek w żółci, rdzeń zamiast kropek."""
    return seven(p, a, mono, r=11.5, R_in=0, apex=0, core=10)


def mark_m(p, a, mono=False):
    """M. Seven Rings – wierne pierścienie z oryginału w granacie, żółte kropki."""
    return seven(p, a, mono, r=10, rings=True, sw=7, R_in=15, r_dot=4.2)


def mark_n(p, a, mono=False):
    """N. Eclipse – 7 granatowych pierścieni, jeden żółty pełny dysk na szczycie."""
    out = []
    for k in range(7):
        x, y = pt(50, 50, 36, -90 + k * 360 / 7)
        if k == 0:
            out.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="13" fill="{p if mono else a}"/>')
        else:
            out.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="10" fill="none" stroke="{p}" stroke-width="7"/>')
    out.append(f'<circle cx="50" cy="50" r="8" fill="{p}"/>')
    return "\n    ".join(out)


def mark_o(p, a, mono=False):
    """O. Solar Gear – 7 żółtych dysków stykających się z granatowym rdzeniem (mocny kontrast)."""
    out = [f'<circle cx="50" cy="50" r="24" fill="{p if mono else a}"/>']
    for k in range(7):
        x, y = pt(50, 50, 34, -90 + k * 360 / 7)
        out.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="12" fill="{p}"/>')
    return "\n    ".join(out)


SEVEN = {
    "k-seven-ink": ("Seven Ink", mark_k, "7 granatowych dysków + 7 żółtych iskier; granat prowadzi, żółć akcentuje", NAVY_PAL),
    "l-apex": ("Apex", mark_l, "7 = jeden element na szczycie; wierzchołek w żółci, żółty rdzeń", NAVY_PAL),
    "m-seven-rings": ("Seven Rings", mark_m, "Pierścienie z oryginału, bez konturu, w granacie; żółte kropki", DEEP_PAL),
    "n-eclipse": ("Eclipse", mark_n, "6 granatowych pierścieni + 1 pełne żółte słońce na szczycie", NAVY_PAL),
    "o-solar-gear": ("Solar Gear", mark_o, "7 żółtych dysków na granatowym rdzeniu; najmocniejszy kontrast", AMBER_PAL),
}


# ---------- tech sun: rays, segments, angles ----------

def rays(p, a, mono, n=7, r1=20, r2=42, sw=9, apex=None, core=0, taper=False):
    out = []
    for k in range(n):
        ang = -90 + k * 360 / n
        x1, y1 = pt(50, 50, r1, ang)
        x2, y2 = pt(50, 50, r2, ang)
        col = a if (apex is not None and k == apex and not mono) else p
        w = sw if not taper else sw
        out.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>')
    if core:
        out.append(f'<circle cx="50" cy="50" r="{core}" fill="{p if mono else a}"/>')
    return "\n    ".join(out)


def mark_p(p, a, mono=False):
    """P. Rays – 7 promieni, pusty środek (słońce domyślne), wierzchołek żółty."""
    return rays(p, a, mono, n=7, r1=22, r2=44, sw=10, apex=0)


def mark_q(p, a, mono=False):
    """Q. Core Rays – żółty rdzeń + 7 granatowych promieni (spinner/kompilacja)."""
    return rays(p, a, mono, n=7, r1=26, r2=44, sw=9, core=14)


def mark_r(p, a, mono=False):
    """R. Heptagon – zaokrąglony siedmiokąt + 7 żółtych ticków na wierzchołkach."""
    pts = [pt(50, 50, 24, -90 + k * 360 / 7) for k in range(7)]
    poly = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
    out = [f'<polygon points="{poly}" fill="{p}" stroke="{p}" stroke-width="8" stroke-linejoin="round"/>']
    for k in range(7):
        ang = -90 + k * 360 / 7
        x1, y1 = pt(50, 50, 33, ang)
        x2, y2 = pt(50, 50, 45, ang)
        out.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{p if mono else a}" stroke-width="7" stroke-linecap="round"/>')
    return "\n    ".join(out)


def mark_s(p, a, mono=False):
    """S. Radar – dwa pierścienie pocięte na 7 segmentów, przesunięte; żółty rdzeń."""
    out = []
    for R, sw, off, gap in ((38, 9, 0, 14), (24, 8, 180 / 7, 18)):
        for k in range(7):
            c = -90 + off + k * 360 / 7
            half = 360 / 14 - gap / 2
            x0, y0 = pt(50, 50, R, c - half)
            x1, y1 = pt(50, 50, R, c + half)
            out.append(f'<path d="M {x0:.2f} {y0:.2f} A {R} {R} 0 0 1 {x1:.2f} {y1:.2f}" stroke="{p}" stroke-width="{sw}" fill="none" stroke-linecap="round"/>')
    out.append(f'<circle cx="50" cy="50" r="7" fill="{p if mono else a}"/>')
    return "\n    ".join(out)


def mark_t(p, a, mono=False):
    """T. Horizon – słońce wschodzące nad linią: półdysk + 5 promieni + pozioma kreska."""
    core = p if mono else a
    out = [f'<path d="M 24 58 A 26 26 0 0 1 76 58 Z" fill="{core}"/>',
           f'<rect x="10" y="62" width="80" height="9" rx="4.5" fill="{p}"/>']
    for ang in (-150, -120, -90, -60, -30):
        x1, y1 = pt(50, 58, 34, ang)
        x2, y2 = pt(50, 58, 46, ang)
        out.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{p}" stroke-width="8" stroke-linecap="round"/>')
    return "\n    ".join(out)


def mark_u(p, a, mono=False):
    """U. Bits – granatowy dysk + 7 kwadratowych bitów na orbicie, jeden żółty."""
    out = [f'<circle cx="50" cy="50" r="20" fill="{p}"/>']
    for k in range(7):
        ang = -90 + k * 360 / 7
        x, y = pt(50, 50, 38, ang)
        col = (a if (k == 0 and not mono) else p)
        out.append(f'<rect x="{x-6.5:.2f}" y="{y-6.5:.2f}" width="13" height="13" rx="3" fill="{col}" transform="rotate({ang+90:.1f} {x:.2f} {y:.2f})"/>')
    return "\n    ".join(out)


SEVEN.update({
    "p-rays": ("Rays", mark_p, "7 promieni, pusty środek – słońce domyślne; wierzchołek żółty", NAVY_PAL),
    "q-core-rays": ("Core Rays", mark_q, "Żółty rdzeń + 7 granatowych promieni; czyta się jak spinner/kompilacja", NAVY_PAL),
    "r-heptagon": ("Heptagon", mark_r, "Siedmiokąt (rzadki = charakterystyczny) + 7 żółtych ticków", NAVY_PAL),
    "s-radar": ("Radar", mark_s, "Dwa pierścienie po 7 segmentów, przesunięte; żółty rdzeń", NAVY_PAL),
    "t-horizon": ("Horizon", mark_t, "Wschód: żółty półdysk nad granatową linią + 5 promieni", NAVY_PAL),
    "u-bits": ("Bits", mark_u, "Dysk + 7 kwadratowych bitów na orbicie, jeden żółty", NAVY_PAL),
})


# ---------- conceptual suns ----------

_mask_id = [0]


def mark_w(p, a, mono=False):
    """W. Sunburst chart – 7 promieni różnej długości (radialny wykres), żółty rdzeń."""
    lens = [46, 33, 41, 29, 44, 35, 38]
    out = []
    for k, L in enumerate(lens):
        ang = -90 + k * 360 / 7
        x1, y1 = pt(50, 50, 21, ang)
        x2, y2 = pt(50, 50, L, ang)
        out.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{p}" stroke-width="9" stroke-linecap="round"/>')
    out.append(f'<circle cx="50" cy="50" r="12" fill="{p if mono else a}"/>')
    return "\n    ".join(out)


def mark_x(p, a, mono=False):
    """X. Binary S – 8 promieni długi/krótki = 01010011 ('S' w ASCII), żółty rdzeń."""
    code = "01010011"
    out = []
    for k, b in enumerate(code):
        ang = -90 + k * 45
        x1, y1 = pt(50, 50, 23, ang)
        x2, y2 = pt(50, 50, 46 if b == "1" else 33, ang)
        out.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{p}" stroke-width="9" stroke-linecap="round"/>')
    out.append(f'<circle cx="50" cy="50" r="13" fill="{p if mono else a}"/>')
    return "\n    ".join(out)


def mark_y(p, a, mono=False):
    """Y. Phyllotaxis – kropki po złotym kącie (137,5°), rosną na zewnątrz; środek żółty."""
    out = [f'<circle cx="50" cy="50" r="9" fill="{p if mono else a}"/>']
    for k in range(1, 13):
        ang = k * 137.508
        r = 10.8 * math.sqrt(k)
        x, y = pt(50, 50, r, ang)
        out.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{2.6 + k * 0.42:.2f}" fill="{p}"/>')
    return "\n    ".join(out)


def mark_z(p, a, mono=False):
    """Z. Orbit – Sol jako gwiazda: żółty dysk, granatowa orbita, błękitna planeta (produkt)."""
    planet = p if mono else SKY
    t = math.radians(200)
    px, py = 42 * math.cos(t), 15 * math.sin(t)
    rot = -28
    return f'''<circle cx="50" cy="50" r="17" fill="{p if mono else a}"/>
    <g transform="rotate({rot} 50 50)">
      <ellipse cx="50" cy="50" rx="42" ry="15" fill="none" stroke="{p}" stroke-width="6"/>
      <circle cx="{50+px:.2f}" cy="{50+py:.2f}" r="7" fill="{planet}"/>
    </g>'''


def mark_aa(p, a, mono=False):
    """AA. Tile – słońce wycięte w negatywie z żółtego kafelka (app-icon first)."""
    _mask_id[0] += 1
    mid = f"m{_mask_id[0]}"
    cuts = [f'<circle cx="50" cy="50" r="19" fill="#000"/>']
    for k in range(7):
        ang = -90 + k * 360 / 7
        x1, y1 = pt(50, 50, 28, ang)
        x2, y2 = pt(50, 50, 40, ang)
        cuts.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="#000" stroke-width="8" stroke-linecap="round"/>')
    tile = p if mono else a
    return f'''<defs><mask id="{mid}"><rect width="100" height="100" fill="#fff"/>{"".join(cuts)}</mask></defs>
    <rect x="4" y="4" width="92" height="92" rx="24" fill="{tile}" mask="url(#{mid})"/>'''


def mark_bb(p, a, mono=False):
    """BB. Chevrons – 7 znaków '>' promieniście (kod + promienie), żółty rdzeń."""
    out = []
    for k in range(7):
        ang = -90 + k * 360 / 7
        ax, ay = pt(50, 50, 31, ang - 13)
        bx, by = pt(50, 50, 44, ang)
        cx, cy = pt(50, 50, 31, ang + 13)
        out.append(f'<polyline points="{ax:.2f},{ay:.2f} {bx:.2f},{by:.2f} {cx:.2f},{cy:.2f}" fill="none" stroke="{p}" stroke-width="7.5" stroke-linecap="round" stroke-linejoin="round"/>')
    out.append(f'<circle cx="50" cy="50" r="12" fill="{p if mono else a}"/>')
    return "\n    ".join(out)


SEVEN.update({
    "w-sunburst": ("Sunburst", mark_w, "Słońce = wykres sunburst: 7 promieni różnej długości (dane), żółty rdzeń", NAVY_PAL),
    "x-binary-s": ("Binary S", mark_x, "8 promieni długi/krótki = 01010011 = 'S' w ASCII; historia do opowiedzenia", NAVY_PAL),
    "y-phyllotaxis": ("Phyllotaxis", mark_y, "Kropki po złotym kącie 137,5° – natura słońca zapisana algorytmem", NAVY_PAL),
    "z-orbit": ("Orbit", mark_z, "Sol jako gwiazda: żółty dysk, orbita, błękitna planeta = produkt", NAVY_PAL),
    "aa-tile": ("Tile", mark_aa, "Słońce wycięte w negatywie z żółtego kafelka – app icon first", NAVY_PAL),
    "bb-chevrons": ("Chevrons", mark_bb, "7 znaków '>' promieniście: kod + promienie", NAVY_PAL),
})


for key, (title, fn, note) in MARKS.items():
    board(key, title, fn, note)
for key, (title, fn, note, pal) in SEVEN.items():
    board(key, title, fn, note, pal)
MARKS.update({k: v[:3] for k, v in SEVEN.items()})


# ---------- U colorways ----------

def bits(disk, bit, hi):
    out = [f'<circle cx="50" cy="50" r="20" fill="{disk}"/>']
    for k in range(7):
        ang = -90 + k * 360 / 7
        x, y = pt(50, 50, 38, ang)
        col = hi if k == 0 else bit
        out.append(f'<rect x="{x-6.5:.2f}" y="{y-6.5:.2f}" width="13" height="13" rx="3" fill="{col}" transform="rotate({ang+90:.1f} {x:.2f} {y:.2f})"/>')
    return "\n    ".join(out)


WHITE = "#FFFFFF"
# (name, light: disk,bit,hi, sol,tech ; dark: disk,bit,hi, sol,tech)
U_WAYS = [
    ("U1 Ink / Solar",        (NAVY, NAVY, AMBER, AMBER, NAVY),   (WHITE, WHITE, AMBER, AMBER, WHITE)),
    ("U2 Solar / Ink",        (AMBER, NAVY, SKY, AMBER, NAVY),    (AMBER, WHITE, SKY, AMBER, WHITE)),
    ("U3 Ink / Solar bits",   (NAVY, AMBER, SKY, AMBER, NAVY),    (WHITE, AMBER, SKY, AMBER, WHITE)),
    ("U4 Sky / Ink",          (SKY, NAVY, AMBER, SKY, NAVY),      (SKY, WHITE, AMBER, SKY, WHITE)),
    ("U5 Ink / Sky bits",     (NAVY, SKY, AMBER, AMBER, NAVY),    (WHITE, SKY, AMBER, AMBER, WHITE)),
    ("U6 Solar mono + Ink",   (AMBER, AMBER, NAVY, AMBER, NAVY),  (AMBER, AMBER, WHITE, AMBER, WHITE)),
    ("U7 Deep / Solar",       (DEEP, DEEP, AMBER, AMBER, DEEP),   (SKY, SKY, AMBER, AMBER, SKY)),
    ("U8 Tri",                (NAVY, SKY, AMBER, AMBER, SKY),     (WHITE, SKY, AMBER, AMBER, SKY)),
]


def board_u(ways=U_WAYS, name="u-colorways", title="Koncept U — Bits: warianty kolorystyczne"):
    W, H = 1400, 110 + len(ways) * 200 + 20
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{FONT}">',
         f'<rect width="{W}" height="{H}" fill="#F6F7F9"/>',
         f'<text x="60" y="60" font-size="22" font-weight="600" fill="{NAVY}">{title}</text>',
         f'<text x="60" y="88" font-size="15" fill="#5B6B7B">lewa kolumna: tło jasne · prawa: tło granatowe · pod znakiem 32 px i mono</text>']
    for i, (nm, L, D) in enumerate(ways):
        y = 110 + i * 200
        for col, (x, bg, c, fg) in enumerate(((60, WHITE, L, NAVY), (720, NAVY, D, WHITE))):
            disk, bit, hi, sol, tech = c
            s.append(f'<rect x="{x}" y="{y}" width="620" height="180" rx="16" fill="{bg}" stroke="#E3E7EC"/>')
            s.append(f'<g transform="translate({x+30},{y+30}) scale(1.2)">{bits(disk, bit, hi)}</g>')
            s.append(f'<text x="{x+190}" y="{y+95}" font-size="46" font-weight="700" letter-spacing="-1.4" fill="{sol}">sol<tspan font-weight="400" fill="{tech}">technology</tspan></text>')
            s.append(f'<text x="{x+190}" y="{y+125}" font-size="13" fill="{"#8A97A6" if bg == WHITE else "#9FB0C0"}">{nm}</text>')
            s.append(f'<g transform="translate({x+520},{y+40}) scale(0.32)">{bits(disk, bit, hi)}</g>')
            s.append(f'<g transform="translate({x+560},{y+40}) scale(0.32)">{bits(fg, fg, fg)}</g>')
            s.append(f'<g transform="translate({x+540},{y+100}) scale(0.16)">{bits(disk, bit, hi)}</g>')
    s.append('</svg>')
    (OUT / f"{name}.svg").write_text("\n".join(s), encoding="utf-8")


SKY_DEEP = "#0EA5E9"   # darker sky, holds on white
V_WAYS = [
    ("V1 Solar / Sky — równe bity",          (AMBER, SKY, SKY, AMBER, NAVY),        (AMBER, SKY, SKY, AMBER, WHITE)),
    ("V2 Solar / Sky — bit Ink",             (AMBER, SKY, NAVY, AMBER, NAVY),       (AMBER, SKY, WHITE, AMBER, WHITE)),
    ("V3 Solar / Sky — bit Solar",           (AMBER, SKY, AMBER, AMBER, NAVY),      (AMBER, SKY, AMBER, AMBER, WHITE)),
    ("V4 Solar / Sky-deep — równe bity",     (AMBER, SKY_DEEP, SKY_DEEP, AMBER, SKY_DEEP), (AMBER, SKY, SKY, AMBER, SKY)),
    ("V5 Solar / Sky-deep — bit Ink, tech Ink", (AMBER, SKY_DEEP, NAVY, AMBER, NAVY), (AMBER, SKY, WHITE, AMBER, WHITE)),
    ("V6 Solar / Sky — technology Sky",      (AMBER, SKY, SKY, AMBER, SKY_DEEP),    (AMBER, SKY, SKY, AMBER, SKY)),
]


board_u()
board_u(V_WAYS, "v-solar-sky", "Koncept U — żółty środek, błękitne bity")


# ---------- BB refinement ----------

def chev(p, a, mono=False, n=7, r_in=31, r_out=44, half=13, sw=7.5, core=12, apex=None, core_ring=False):
    out = []
    for k in range(n):
        ang = -90 + k * 360 / n
        ax, ay = pt(50, 50, r_in, ang - half)
        bx, by = pt(50, 50, r_out, ang)
        cx, cy = pt(50, 50, r_in, ang + half)
        col = apex if (k == 0 and apex and not mono) else p
        out.append(f'<polyline points="{ax:.2f},{ay:.2f} {bx:.2f},{by:.2f} {cx:.2f},{cy:.2f}" fill="none" stroke="{col}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>')
    cc = p if mono else a
    if core_ring:
        out.append(f'<circle cx="50" cy="50" r="{core}" fill="none" stroke="{cc}" stroke-width="{sw}"/>')
    elif core:
        out.append(f'<circle cx="50" cy="50" r="{core}" fill="{cc}"/>')
    return "\n    ".join(out)


BB_GEOM = [
    ("G1 baza", dict()),
    ("G2 grubiej (sw 9, core 13)", dict(sw=9, core=13, r_in=30, r_out=45)),
    ("G3 szerzej rozwarte (half 17)", dict(half=17, sw=8, core=12)),
    ("G4 ciaśniej (half 10, sw 8.5)", dict(half=10, sw=8.5, r_in=32, core=12)),
    ("G5 duży rdzeń (core 16, r_in 34)", dict(core=16, r_in=34, r_out=46, sw=8)),
    ("G6 rdzeń pierścień", dict(core=11, core_ring=True, sw=7.5)),
    ("G7 bez rdzenia", dict(core=0, r_in=28, r_out=44, sw=8.5)),
    ("G8 6 chevronów", dict(n=6, sw=8.5, half=14, core=13)),
]

BB_COLOR = [
    ("C1 Ink chevrony / Solar rdzeń", (NAVY, AMBER, None), (WHITE, AMBER, None)),
    ("C2 Solar chevrony / Ink rdzeń", (AMBER, NAVY, None), (AMBER, WHITE, None)),
    ("C3 Ink / Solar + wierzchołek Sky", (NAVY, AMBER, SKY), (WHITE, AMBER, SKY)),
    ("C4 Ink / Solar + wierzchołek Solar", (NAVY, AMBER, AMBER), (WHITE, AMBER, AMBER)),
    ("C5 Deep chevrony / Solar rdzeń", (DEEP, AMBER, None), (SKY, AMBER, None)),
    ("C6 Sky chevrony / Solar rdzeń", (SKY_DEEP, AMBER, None), (SKY, AMBER, None)),
]


def board_bb():
    W = 1400
    rowh = 150
    H = 120 + len(BB_GEOM) * rowh + 60 + len(BB_COLOR) * 200 + 40
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{FONT}">',
         f'<rect width="{W}" height="{H}" fill="#F6F7F9"/>',
         f'<text x="60" y="60" font-size="22" font-weight="600" fill="{NAVY}">BB — Chevrons: geometria</text>',
         f'<text x="60" y="88" font-size="15" fill="#5B6B7B">każdy wiersz: 100 px · 48 · 32 · 16 · mono 48 · na granacie 48 i 16</text>']
    y0 = 110
    for i, (nm, kw) in enumerate(BB_GEOM):
        y = y0 + i * rowh
        s.append(f'<rect x="60" y="{y}" width="1280" height="{rowh-12}" rx="14" fill="#FFFFFF" stroke="#E3E7EC"/>')
        s.append(f'<text x="80" y="{y+30}" font-size="14" font-weight="600" fill="{NAVY}">{nm}</text>')
        s.append(f'<g transform="translate(80,{y+36}) scale(1.0)">{chev(NAVY, AMBER, **kw)}</g>')
        s.append(f'<g transform="translate(220,{y+62}) scale(0.48)">{chev(NAVY, AMBER, **kw)}</g>')
        s.append(f'<g transform="translate(290,{y+70}) scale(0.32)">{chev(NAVY, AMBER, **kw)}</g>')
        s.append(f'<g transform="translate(340,{y+78}) scale(0.16)">{chev(NAVY, AMBER, **kw)}</g>')
        s.append(f'<g transform="translate(400,{y+62}) scale(0.48)">{chev(NAVY, NAVY, mono=True, **kw)}</g>')
        s.append(f'<rect x="480" y="{y+40}" width="130" height="80" rx="10" fill="{NAVY}"/>')
        s.append(f'<g transform="translate(500,{y+56}) scale(0.48)">{chev(WHITE, AMBER, **kw)}</g>')
        s.append(f'<g transform="translate(570,{y+72}) scale(0.16)">{chev(WHITE, AMBER, **kw)}</g>')
        s.append(f'<text x="660" y="{y+70}" font-size="40" font-weight="700" letter-spacing="-1.2" fill="{AMBER}">sol<tspan font-weight="400" fill="{NAVY}">technology</tspan></text>')
        s.append(f'<g transform="translate(1010,{y+50}) scale(0.5)">{chev(NAVY, AMBER, **kw)}</g>')
        s.append(f'<text x="1075" y="{y+82}" font-size="22" font-weight="700" fill="{AMBER}">sol<tspan font-weight="400" fill="{NAVY}">technology</tspan><tspan font-weight="400" fill="#5B6B7B"> / AvroConvert</tspan></text>')
    y0 = y0 + len(BB_GEOM) * rowh + 20
    s.append(f'<text x="60" y="{y0+20}" font-size="22" font-weight="600" fill="{NAVY}">BB — Chevrons: kolor (geometria G1)</text>')
    y0 += 50
    for i, (nm, L, D) in enumerate(BB_COLOR):
        y = y0 + i * 200
        for x, bg, (p, a, ap), fg in ((60, WHITE, L, NAVY), (720, NAVY, D, WHITE)):
            s.append(f'<rect x="{x}" y="{y}" width="620" height="180" rx="16" fill="{bg}" stroke="#E3E7EC"/>')
            s.append(f'<g transform="translate({x+30},{y+30}) scale(1.2)">{chev(p, a, apex=ap)}</g>')
            sol = AMBER
            tech = NAVY if bg == WHITE else WHITE
            s.append(f'<text x="{x+190}" y="{y+95}" font-size="46" font-weight="700" letter-spacing="-1.4" fill="{sol}">sol<tspan font-weight="400" fill="{tech}">technology</tspan></text>')
            s.append(f'<text x="{x+190}" y="{y+125}" font-size="13" fill="{"#8A97A6" if bg == WHITE else "#9FB0C0"}">{nm}</text>')
            s.append(f'<g transform="translate({x+520},{y+40}) scale(0.32)">{chev(p, a, apex=ap)}</g>')
            s.append(f'<g transform="translate({x+560},{y+40}) scale(0.32)">{chev(fg, fg, mono=True)}</g>')
            s.append(f'<g transform="translate({x+540},{y+100}) scale(0.16)">{chev(p, a, apex=ap)}</g>')
    s.append('</svg>')
    (OUT / "bb-refine.svg").write_text("\n".join(s), encoding="utf-8")
    return H


BB_H = board_bb()
print("ok", OUT, "bb_h", BB_H)

# PNG previews via headless Chrome (QuickLook rescales and crops wide boards)
import subprocess, shutil, sys
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PREVIEW = Path(sys.argv[1]) if len(sys.argv) > 1 else None
if PREVIEW and Path(CHROME).exists():
    PREVIEW.mkdir(parents=True, exist_ok=True)
    for key in MARKS:
        src = OUT / f"{key}.svg"
        dst = PREVIEW / f"{key}.png"
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        "--window-size=1400,820", f"--screenshot={dst}", src.as_uri()],
                       check=True, capture_output=True)
    print("previews", PREVIEW)
