#!/usr/bin/env python3
"""Draw the 18 November 2026 world-news front page (1024x1024 PNG).

Every element is drawn with PIL primitives: no photos, no copied art.
Palette is a newspaper front page: warm paper, dark ink, one red accent.
"""
import math
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (248, 244, 233)
INK = (24, 26, 32)
RED = (178, 34, 34)
NAVY = (31, 58, 95)
TEAL = (18, 96, 92)
SLATE = (84, 90, 102)
WHITE = (255, 255, 255)

def _find_font_dir():
    """Locate the DejaVu fonts across OSes (Debian/Ubuntu, Fedora, macOS, Windows)."""
    override = os.environ.get("FONT_DIR")
    candidates = [override] if override else []
    candidates += [
        "/usr/share/fonts/truetype/dejavu/",
        "/usr/share/fonts/dejavu/",
        "/usr/local/share/fonts/dejavu/",
        "/Library/Fonts/",
        "/System/Library/Fonts/",
        "C:/Windows/Fonts/",
    ]
    for d in candidates:
        if d and os.path.isfile(os.path.join(d, "DejaVuSans.ttf")):
            return d
    raise RuntimeError(
        "DejaVu fonts not found; set FONT_DIR to a folder holding "
        "DejaVuSans.ttf / DejaVuSans-Bold.ttf / DejaVuSerif-Bold.ttf")

FDIR = _find_font_dir()
def font(name, size):
    return ImageFont.truetype(os.path.join(FDIR, name), size)

SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

def wrap(text, fnt, width):
    """Greedy wrap by measured pixel width.

    Raises ValueError instead of silently overflowing: a single word
    wider than the box, or a caller that truncates lines, must fail
    loudly rather than print broken text.
    """
    words, lines, cur = text.split(), [], ""
    for w in words:
        if fnt.getlength(w) > width:
            raise ValueError(f"word too wide for its box: {w!r}")
        trial = (cur + " " + w).strip()
        if fnt.getlength(trial) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def balance_two_lines(lines, fnt, width):
    """If a headline wrapped to two lines with a lone word on line 2,
    move the last word of line 1 down so both lines read evenly.

    Re-checks the pixel width of the new line 2: moving a word down can
    make it overflow the panel, and that must fail loudly like wrap().
    """
    if len(lines) == 2:
        first, last = lines[0].split(), lines[1].split()
        if len(last) == 1 and len(first) > 1:
            new = [" ".join(first[:-1]), first[-1] + " " + lines[1]]
            if fnt.getlength(new[1]) > width:
                raise ValueError(f"balanced headline line 2 too wide: {new[1]!r}")
            return new
    return lines

def centred_text(x0, x1, y, text, fnt, fill=INK):
    w = fnt.getlength(text)
    d.text(((x0 + x1 - w) / 2, y), text, font=fnt, fill=fill)

def flag(drw, x, y, w, h, kind):
    """Tiny simplified flag: stripes / disc / stars, drawn, not copied."""
    if kind == "us":
        for i in range(7):
            drw.rectangle([x, y + i * h / 7, x + w, y + (i + 1) * h / 7],
                          fill=(178, 34, 52) if i % 2 == 0 else WHITE)
        drw.rectangle([x, y, x + w * 0.4, y + h * 4 / 7], fill=(30, 50, 110))
    elif kind == "cn":
        drw.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
        cx, cy = x + w * 0.22, y + h * 0.28
        for k in range(5):
            a = -math.pi / 2 + k * 2 * math.pi / 5
            r1, r2 = h * 0.16, h * 0.07
            pts = []
            for j in range(10):
                r = r1 if j % 2 == 0 else r2
                ang = a + j * math.pi / 5
                pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
            drw.polygon(pts, fill=(255, 222, 0))
    elif kind == "ru":
        for i, c in enumerate([(255, 255, 255), (0, 57, 166), (213, 0, 50)]):
            drw.rectangle([x, y + i * h / 3, x + w, y + (i + 1) * h / 3], fill=c)
    elif kind == "in":
        for i, c in enumerate([(255, 153, 51), WHITE, (19, 136, 8)]):
            drw.rectangle([x, y + i * h / 3, x + w, y + (i + 1) * h / 3], fill=c)
        drw.ellipse([x + w / 2 - h / 7, y + h / 2 - h / 7,
                     x + w / 2 + h / 7, y + h / 2 + h / 7],
                    outline=(0, 0, 128), width=2)
    elif kind == "jp":
        drw.rectangle([x, y, x + w, y + h], fill=WHITE)
        drw.ellipse([x + w / 2 - h / 5, y + h / 2 - h / 5,
                     x + w / 2 + h / 5, y + h / 2 + h / 5], fill=(188, 0, 45))
    elif kind == "au":
        drw.rectangle([x, y, x + w, y + h], fill=(0, 47, 108))
        # Union Jack canton (top-left quarter), simplified at this size.
        cx0, cy0, cw, ch = x, y, w * 0.5, h * 0.5
        drw.line([cx0, cy0, cx0 + cw, cy0 + ch], fill=WHITE, width=2)
        drw.line([cx0 + cw, cy0, cx0, cy0 + ch], fill=WHITE, width=2)
        drw.line([cx0, cy0, cx0 + cw, cy0 + ch], fill=(200, 16, 46), width=1)
        drw.line([cx0 + cw, cy0, cx0, cy0 + ch], fill=(200, 16, 46), width=1)
        drw.line([cx0 + cw / 2, cy0, cx0 + cw / 2, cy0 + ch], fill=WHITE, width=3)
        drw.line([cx0, cy0 + ch / 2, cx0 + cw, cy0 + ch / 2], fill=WHITE, width=3)
        drw.line([cx0 + cw / 2, cy0, cx0 + cw / 2, cy0 + ch], fill=(200, 16, 46), width=1)
        drw.line([cx0, cy0 + ch / 2, cx0 + cw, cy0 + ch / 2], fill=(200, 16, 46), width=1)
        # Southern Cross: four white stars on the fly.
        for sx, sy in [(0.72, 0.28), (0.86, 0.38), (0.68, 0.62), (0.84, 0.78)]:
            px, py = x + w * sx, y + h * sy
            drw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=WHITE)
    drw.rectangle([x, y, x + w, y + h], outline=INK, width=1)

# ---------------------------------------------------------------- masthead
d.rectangle([0, 0, W, 6], fill=RED)
centred_text(0, W, 26, "THE WORLD IN ONE DAY", SERIF_B(52))
centred_text(0, W, 92, "One day's world news, in one picture", SANS(17), fill=SLATE)
d.line([60, 128, W - 60, 128], fill=INK, width=2)
d.line([60, 133, W - 60, 133], fill=INK, width=1)
centred_text(0, W, 142, "WEDNESDAY  ·  18 NOVEMBER 2026", SANS_B(34), fill=RED)
d.line([60, 192, W - 60, 192], fill=INK, width=2)

# ---------------------------------------------------------------- icons
def icon_skyline(x, y, w, h):
    """Shenzhen skyline at dusk with three flags."""
    d.rectangle([x, y, x + w, y + h], fill=(253, 214, 130))
    d.ellipse([x + 106, y + 2, x + 126, y + 22], fill=(240, 120, 40))
    base = y + h
    for bx, bw, bh in [(0, 34, 62), (38, 26, 88), (68, 40, 52),
                       (112, 30, 96), (146, 36, 66), (186, 28, 84),
                       (218, 42, 58), (264, 30, 78)]:
        d.rectangle([x + bx, base - bh, x + bx + bw, base], fill=NAVY)
        for wy in range(base - bh + 8, base - 6, 14):
            for wx in range(x + bx + 6, x + bx + bw - 4, 12):
                d.rectangle([wx, wy, wx + 5, wy + 6], fill=(253, 214, 130))
    d.rectangle([x, y + h - 4, x + w, y + h], fill=INK)
    flag(d, x + 14, y + 6, 46, 26, "us")
    flag(d, x + w // 2 - 23, y + 6, 46, 26, "cn")
    flag(d, x + w - 60, y + 6, 46, 26, "ru")

def icon_bridge(x, y, w, h):
    """Broken bridge arch over water, with a blast star."""
    d.rectangle([x, y, x + w, y + h], fill=(183, 214, 232))
    d.rectangle([x, y + h - 26, x + w, y + h], fill=(46, 110, 160))
    for i in range(5):
        d.arc([x + 8 + i * 58, y + h - 34, x + 52 + i * 58, y + h - 10],
              180, 360, fill=(255, 255, 255), width=3)
    d.rectangle([x + 10, y + 52, x + w // 2 - 26, y + 66], fill=(90, 90, 96))
    d.rectangle([x + w // 2 + 26, y + 52, x + w - 10, y + 66], fill=(90, 90, 96))
    # Broken arch: two segments with a gap at the top centre, where the
    # road span fell. Both feet stay inside the icon box (y + 60 < y + h).
    d.arc([x + w // 2 - 78, y + 28, x + w // 2 + 78, y + 92],
          180, 255, fill=(90, 90, 96), width=8)
    d.arc([x + w // 2 - 78, y + 28, x + w // 2 + 78, y + 92],
          285, 360, fill=(90, 90, 96), width=8)
    for k in range(8):
        a = k * math.pi / 4
        r1 = 26
        x1 = x + w // 2 + r1 * math.cos(a)
        y1 = y + 44 + r1 * math.sin(a)
        d.line([x + w // 2, y + 44, x1, y1], fill=(255, 170, 0), width=5)
    d.ellipse([x + w // 2 - 12, y + 32, x + w // 2 + 12, y + 56],
              fill=(255, 120, 0))
    d.line([x + 18, y + 52, x + 18, y + 66], fill=INK, width=3)
    d.line([x + w - 18, y + 52, x + w - 18, y + 66], fill=INK, width=3)

def icon_radar(x, y, w, h):
    """Radar dish sweeping, with an intercepted drone."""
    d.rectangle([x, y, x + w, y + h], fill=(24, 40, 58))
    cx, cy = x + w // 2, y + 56
    for r in (40, 28, 16):
        d.ellipse([cx - r, cy - r, cx + r, cy + r],
                  outline=(90, 200, 120), width=2)
    d.pieslice([cx - 40, cy - 40, cx + 40, cy + 40],
               205, 250, fill=(90, 200, 120))
    # Sweep line stays inside the green sector (205-250 deg): its tip is
    # the midpoint direction, 227 deg, at radius 40.
    d.line([cx, cy, cx - 29, cy - 27], fill=(140, 230, 160), width=3)
    d.ellipse([cx - 37, cy - 35, cx - 21, cy - 19], fill=(255, 220, 60))
    d.line([x + w - 92, y + 26, x + w - 52, y + 26], fill=(220, 220, 220), width=4)
    d.ellipse([x + w - 74, y + 18, x + w - 58, y + 34], fill=(220, 220, 220))
    d.line([x + w - 92, y + 20, x + w - 104, y + 12], fill=(220, 220, 220), width=3)
    d.line([x + w - 52, y + 20, x + w - 40, y + 12], fill=(220, 220, 220), width=3)
    # Target crosshair (a red ring with ticks), not a medical cross.
    tx, ty = x + w - 74, y + 72
    d.ellipse([tx - 11, ty - 11, tx + 11, ty + 11],
              outline=(255, 90, 60), width=3)
    d.ellipse([tx - 2, ty - 2, tx + 2, ty + 2], fill=(255, 90, 60))
    d.line([tx, ty - 17, tx, ty - 12], fill=(255, 90, 60), width=2)
    d.line([tx, ty + 12, tx, ty + 17], fill=(255, 90, 60), width=2)
    d.line([tx - 17, ty, tx - 12, ty], fill=(255, 90, 60), width=2)
    d.line([tx + 12, ty, tx + 17, ty], fill=(255, 90, 60), width=2)

def icon_cyclone(x, y, w, h):
    """Spiral storm over a coastline."""
    d.rectangle([x, y, x + w, y + h], fill=(200, 222, 238))
    d.rectangle([x, y + h - 22, x + w, y + h], fill=(232, 196, 120))
    d.polygon([(x + 18, y + h - 22), (x + 60, y + h - 52), (x + 110, y + h - 22)],
              fill=(120, 160, 90))
    d.polygon([(x + w - 120, y + h - 22), (x + w - 70, y + h - 44),
               (x + w - 16, y + h - 22)], fill=(120, 160, 90))
    cx, cy = x + w // 2, y + h // 2 - 6
    for turn in range(3):
        r0 = 8 + turn * 13
        for a in range(0, 360, 6):
            a1 = math.radians(a + turn * 360)
            a2 = math.radians(a + 6 + turn * 360)
            r1 = r0 + (a / 360.0) * 13
            r2 = r0 + ((a + 6) / 360.0) * 13
            d.line([cx + r1 * math.cos(a1), cy + r1 * math.sin(a1),
                    cx + r2 * math.cos(a2), cy + r2 * math.sin(a2)],
                   fill=(31, 58, 95), width=5)
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(31, 58, 95))

def icon_chip(x, y, w, h):
    """Computer chip with a rising chart arrow."""
    d.rectangle([x, y, x + w, y + h], fill=(226, 238, 226))
    cx, cy = x + 62, y + h // 2 + 8
    for px in (-34, -12, 12, 34):
        d.line([cx + px, cy - 34, cx + px, cy - 48], fill=(31, 58, 95), width=4)
        d.line([cx + px, cy + 34, cx + px, cy + 48], fill=(31, 58, 95), width=4)
    for py in (-22, 0, 22):
        d.line([cx - 34, cy + py, cx - 48, cy + py], fill=(31, 58, 95), width=4)
        d.line([cx + 34, cy + py, cx + 48, cy + py], fill=(31, 58, 95), width=4)
    d.rectangle([cx - 34, cy - 34, cx + 34, cy + 34], fill=(31, 58, 95))
    d.rectangle([cx - 18, cy - 18, cx + 18, cy + 18], fill=(118, 185, 0))
    d.text((cx - 9, cy - 13), "AI", font=SANS_B(20), fill=WHITE)
    pts = [(x + 150, y + h - 22), (x + 185, y + 62), (x + 212, y + 82),
           (x + 246, y + 34), (x + 272, y + 46), (x + 292, y + 18)]
    d.line(pts, fill=(178, 34, 34), width=5, joint="curve")
    d.polygon([(x + 292, y + 18), (x + 276, y + 14), (x + 288, y + 34)],
              fill=(178, 34, 34))

def icon_quad(x, y, w, h):
    """Four flags around a table."""
    d.rectangle([x, y, x + w, y + h], fill=(222, 232, 244))
    d.ellipse([x + w // 2 - 52, y + 52, x + w // 2 + 52, y + 92],
              fill=(139, 92, 42))
    d.ellipse([x + w // 2 - 52, y + 46, x + w // 2 + 52, y + 76],
              fill=(176, 124, 66))
    spots = [(x + 22, y + 8, "us"), (x + w - 68, y + 8, "in"),
             (x + 22, y + h - 38, "jp"), (x + w - 68, y + h - 38, "au")]
    for fx, fy, kind in spots:
        flag(d, fx, fy, 46, 26, kind)

def icon_game(x, y, w, h):
    """Night city skyline with a big VI."""
    d.rectangle([x, y, x + w, y + h], fill=(26, 18, 52))
    for sx, sy in [(20, 14), (70, 26), (130, 10), (200, 22), (260, 12), (290, 28)]:
        d.ellipse([x + sx, y + sy, x + sx + 4, y + sy + 4], fill=WHITE)
    base = y + h
    for bx, bw, bh, lit in [(0, 30, 46, True), (34, 24, 70, False),
                            (62, 36, 54, True), (102, 26, 52, False),
                            (132, 34, 48, True), (170, 28, 66, False),
                            (202, 38, 58, True), (244, 30, 76, False),
                            (278, 30, 50, True)]:
        d.rectangle([x + bx, base - bh, x + bx + bw, base], fill=(12, 8, 30))
        if lit:
            for wy in range(base - bh + 8, base - 6, 14):
                d.rectangle([x + bx + 6, wy, x + bx + 12, wy + 6],
                            fill=(255, 200, 60))
    _vi = SERIF_B(52)
    d.text((x + w // 2 - _vi.getlength("VI") / 2, y + 6), "VI", font=_vi,
           fill=(255, 90, 200), stroke_width=2, stroke_fill=(255, 255, 255))

# ---------------------------------------------------------------- lead story
LX, LY, LW, LH = 26, 204, 972, 184
d.rectangle([LX, LY, LX + LW, LY + LH], outline=INK, width=3, fill=WHITE)
icon_skyline(LX + 14, LY + 14, 330, LH - 28)
d.line([LX + 358, LY + 14, LX + 358, LY + LH - 14], fill=SLATE, width=1)
tx = LX + 378
d.text((tx, LY + 16), "LEAD  ·  ASIA-PACIFIC", font=SANS_B(16), fill=RED)
lines = wrap("APEC opens in Shenzhen", SANS_B(30), LW - 378 - 20)
yy = LY + 40
for ln in lines:
    d.text((tx, yy), ln, font=SANS_B(30), fill=INK)
    yy += 36
body = ("Xi Jinping opened the summit urging freer trade and "
        "investment. Officials said Donald Trump, Xi and Vladimir "
        "Putin plan a first three-way meeting on Thursday.")
lead_body_lines = wrap(body, SANS(18), LW - 378 - 20)
assert len(lead_body_lines) <= 4, "lead body too long for its box"
for ln in lead_body_lines:
    d.text((tx, yy), ln, font=SANS(18), fill=INK)
    yy += 24

# ---------------------------------------------------------------- grid panels
PANELS = [
    ("EUROPE  ·  WAR IN UKRAINE", "CRIMEA BRIDGE CRIPPLED",
     "Ukraine brought down the road arch of the 19-km Kerch "
     "bridge. Russia hit two Kyiv bridges in reply.", icon_bridge, NAVY),
    ("MIDDLE EAST  ·  GULF", "GULF SKIES ON ALERT",
     "Bahrain and Kuwait intercepted drone attacks, a "
     "day after the US hit a missile site on Qeshm Island.",
     icon_radar, TEAL),
    ("ASIA  ·  WEATHER", "CYCLONE AKVAN NEARS INDIA",
     "The storm over the Bay of Bengal is forecast to cross "
     "the Andhra coast on Friday, with winds up to 145 km/h.",
     icon_cyclone, (38, 96, 140)),
    ("BUSINESS  ·  TECH", "NVIDIA'S RECORD $115.8BN QUARTER",
     "Revenue more than doubled YoY in its first results since "
     "Huang resigned. The board ruled out his return.",
     icon_chip, (60, 90, 30)),
    ("ASIA-PACIFIC  ·  DIPLOMACY", "QUAD LEADERS MEET IN MANILA",
     "Trump arrived in Manila for talks with India, Japan and "
     "Australia, before heading to China.", icon_quad, (110, 60, 120)),
    ("CULTURE  ·  GAMES", "GTA VI UNLOCKS AT MIDNIGHT",
     "GTA VI goes on sale at midnight local time on 19 Nov "
     "for PS5 and Xbox. Pre-loads need up to 212 GB.",
     icon_game, (90, 30, 110)),
]

GX, GY = 26, 400
GW, GH = 316, 270
GAP = 12
for i, (kicker, head, body, icon, accent) in enumerate(PANELS):
    col, row = i % 3, i // 3
    px = GX + col * (GW + GAP)
    py = GY + row * (GH + GAP)
    d.rectangle([px, py, px + GW, py + GH], outline=INK, width=2, fill=WHITE)
    d.rectangle([px, py, px + GW, py + 8], fill=accent)
    icon(px + 8, py + 16, GW - 16, 100)
    d.text((px + 12, py + 122), kicker, font=SANS_B(13), fill=accent)
    yy = py + 142
    for ln in balance_two_lines(wrap(head, SANS_B(19), GW - 24), SANS_B(19), GW - 24):
        d.text((px + 12, yy), ln, font=SANS_B(19), fill=INK)
        yy += 23
    yy += 3
    body_lines = wrap(body, SANS(15), GW - 24)
    assert len(body_lines) <= 3, f"body too long for panel: {head}"
    for ln in body_lines:
        d.text((px + 12, yy), ln, font=SANS(15), fill=(40, 42, 50))
        yy += 19

# ---------------------------------------------------------------- footer
FY = 962
d.line([26, FY, W - 26, FY], fill=INK, width=2)
d.text((26, FY + 10), "ALSO TODAY", font=SANS_B(15), fill=RED)
_also = "Trump met Philippine President Marcos in Manila on the sidelines of his Asia trip."
assert SANS(15).getlength(_also) <= W - 150 - 26, "ALSO TODAY line too long"
d.text((150, FY + 10), _also, font=SANS(15), fill=INK)
d.text((26, FY + 34),
       "Sources: Reuters, CNBC, IMD, AAP  ·  Events of Wednesday 18 November 2026, as reported by 18 Nov, 11:00 WIB.",
       font=SANS(13), fill=SLATE)

OUT = Path(__file__).resolve().parent / "entry.png"
img.save(OUT, optimize=True)
print("saved entry.png")
