#!/usr/bin/env python3
"""Render the news-image-20261123 front page: one image, 38 stories, 9 regions.

Reads stories.json (verified stories for Monday 23 November 2026) and
draws a 1024x1024 newspaper front page with PIL. Deterministic: same
input gives byte-identical output (no timestamps, no randomness).
"""

import json
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "stories.json")
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024
PAPER = (246, 241, 229)
INK = (17, 17, 17)
RED = (179, 32, 44)
GRAY = (85, 85, 85)
RULE = (120, 115, 105)
OCEAN = (201, 223, 232)
LAND = (233, 220, 189)
LAND_EDGE = (185, 168, 106)
PIN = (192, 32, 44)

BADGES = {
    "CONFIRMED": (30, 122, 60),
    "REPORTED": (51, 51, 51),
    "CLAIMED": (179, 32, 44),
    "OFFICIAL": (31, 78, 156),
}

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    """Load a DejaVu font; fall back to PIL's default bitmap font."""
    try:
        return ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    except (OSError, IOError):
        return ImageFont.load_default()


def serif_b(size):
    return font("DejaVuSerif-Bold.ttf", size)


def serif(size):
    return font("DejaVuSerif.ttf", size)


def sans_b(size):
    return font("DejaVuSans-Bold.ttf", size)


def sans(size):
    return font("DejaVuSans.ttf", size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap of text to a pixel width; returns a list of lines."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines or [""]


def text_w(draw, text, fnt):
    return draw.textlength(text, font=fnt)


def fit_lines(draw, text, sizes, max_w, max_lines):
    """Pick the largest serif-bold size (from sizes, biggest first) whose
    wrap fits in max_lines; returns (font, lines)."""
    for size in sizes:
        fnt = serif_b(size)
        lines = wrap(draw, text, fnt, max_w)
        if len(lines) <= max_lines:
            return fnt, lines
    fnt = serif_b(sizes[-1])
    return fnt, wrap(draw, text, fnt, max_w)[:max_lines]


def badge(draw, x, y, label):
    """Draw a small coloured label pill; returns its width."""
    fnt = sans_b(9)
    tw = draw.textlength(label, font=fnt)
    w, h = int(tw) + 10, 13
    draw.rounded_rectangle([x, y, x + w, y + h], radius=3,
                           fill=BADGES.get(label, (51, 51, 51)))
    draw.text((x + 5, y + 2), label, font=fnt, fill=(255, 255, 255))
    return w


# ---------------------------------------------------------------- art panels

def art_cop31(draw, x, y, w, h):
    """Flat illustration: climate summit skyline at dusk, sun, flags."""
    draw.rectangle([x, y, x + w, y + h], fill=(38, 68, 104))
    # sun
    draw.ellipse([x + w - 62, y + 14, x + w - 18, y + 58], fill=(232, 196, 90))
    # skyline blocks
    base = y + h
    blocks = [(0, 52, 46), (48, 74, 30), (80, 44, 52), (134, 84, 34),
              (170, 60, 46), (218, 78, 30), (250, 50, 44), (296, 66, 26)]
    for bx, bh, bw in blocks:
        draw.rectangle([x + bx, base - bh, x + bx + bw, base],
                       fill=(22, 38, 64))
    # lit windows
    for wx in range(x + 8, x + w - 8, 16):
        for wy in range(y + h - 78, y + h - 8, 14):
            if (wx * 7 + wy * 13) % 5 == 0:
                draw.rectangle([wx, wy, wx + 5, wy + 7], fill=(232, 196, 90))
    # ground strip
    draw.rectangle([x, base - 10, x + w, base], fill=(196, 138, 52))
    # flag poles with small pennants
    for fx, col in [(x + 30, RED), (x + 110, (30, 122, 60)),
                    (x + 200, (232, 196, 90)), (x + 280, (31, 78, 156))]:
        draw.line([fx, base - 44, fx, base - 10], fill=(246, 241, 229), width=2)
        draw.polygon([(fx, base - 44), (fx + 16, base - 39), (fx, base - 34)],
                     fill=col)


def art_gulf(draw, x, y, w, h):
    """Flat illustration: night over the Gulf, radar arcs, city blocks."""
    draw.rectangle([x, y, x + w, y + h], fill=(16, 24, 46))
    # stars
    for sx, sy in [(20, 14), (70, 26), (130, 10), (190, 22), (250, 12),
                   (300, 28), (45, 40), (160, 38), (230, 44), (285, 8)]:
        draw.ellipse([x + sx, y + sy, x + sx + 3, y + sy + 3],
                     fill=(255, 255, 255))
    # moon
    draw.ellipse([x + w - 52, y + 10, x + w - 26, y + 36], fill=(235, 230, 210))
    # city blocks
    base = y + h
    for bx, bh, bw in [(0, 46, 58), (62, 62, 44), (110, 38, 66),
                       (180, 56, 50), (234, 42, 54), (292, 60, 30)]:
        draw.rectangle([x + bx, base - bh, x + bx + bw, base],
                       fill=(52, 64, 92))
        for wx in range(x + bx + 6, x + bx + bw - 6, 12):
            for wy in range(base - bh + 8, base - 6, 12):
                if (wx + wy) % 7 == 0:
                    draw.rectangle([wx, wy, wx + 4, wy + 5],
                                   fill=(232, 196, 90))
    # orange radar arcs over the city
    for cx, cy, r in [(x + 90, base - 30, 34), (x + 200, base - 26, 40),
                      (x + 280, base - 34, 28)]:
        draw.arc([cx - r, cy - r, cx + r, cy + r], start=180, end=360,
                 fill=(232, 130, 40), width=3)


def art_football(draw, x, y, w, h):
    """Flat illustration: floodlit pitch, centre circle, ball."""
    draw.rectangle([x, y, x + w, y + h], fill=(30, 110, 58))
    # mowing stripes
    for i in range(6):
        if i % 2 == 0:
            draw.rectangle([x, y + i * h // 6, x + w, y + (i + 1) * h // 6],
                           fill=(36, 122, 64))
    # halfway line and centre circle
    draw.line([x + w // 2, y, x + w // 2, y + h], fill=(255, 255, 255), width=2)
    draw.ellipse([x + w // 2 - 34, y + h // 2 - 34,
                  x + w // 2 + 34, y + h // 2 + 34],
                 outline=(255, 255, 255), width=2)
    # floodlight masts
    for mx in (x + 18, x + w - 18):
        draw.line([mx, y + 8, mx, y + 34], fill=(220, 220, 220), width=3)
        draw.ellipse([mx - 7, y + 2, mx + 7, y + 14], fill=(255, 244, 180))
    # ball on the spot
    bx, by = x + w // 2, y + h // 2
    draw.ellipse([bx - 11, by - 11, bx + 11, by + 11], fill=(255, 255, 255))
    draw.polygon([(bx, by - 6), (bx + 6, by - 2), (bx + 4, by + 6),
                  (bx - 4, by + 6), (bx - 6, by - 2)], fill=(17, 17, 17))


ART = {"cop31": art_cop31, "gulf": art_gulf, "football": art_football}

# ---------------------------------------------------------------- world map

# Rough continent outlines in (lon, lat); stylised, not survey-grade.
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-80, 73), (-75, 62),
     (-60, 55), (-55, 47), (-70, 42), (-75, 35), (-80, 32), (-85, 30),
     (-90, 21), (-97, 16), (-105, 20), (-110, 23), (-117, 33), (-125, 40),
     (-125, 49), (-135, 58), (-155, 58), (-165, 60)],
    # South America
    [(-80, 10), (-75, 5), (-60, 0), (-50, -5), (-40, -10), (-35, -20),
     (-40, -30), (-50, -35), (-60, -40), (-65, -50), (-70, -55),
     (-73, -40), (-75, -20), (-80, -5), (-82, 5)],
    # Europe
    [(-10, 36), (-5, 44), (0, 46), (5, 50), (8, 55), (10, 58), (18, 56),
     (21, 55), (24, 60), (30, 62), (35, 66), (40, 68), (35, 60), (30, 55),
     (25, 50), (20, 45), (15, 40), (10, 38), (5, 36), (0, 38), (-5, 36)],
    # Africa
    [(-10, 35), (0, 36), (10, 37), (20, 32), (30, 31), (35, 28), (40, 15),
     (48, 11), (51, 10), (45, 0), (40, -10), (35, -20), (30, -30),
     (20, -35), (15, -30), (12, -18), (10, -5), (8, 5), (0, 5), (-8, 5),
     (-15, 10), (-17, 15), (-15, 25), (-12, 30)],
    # Asia
    [(40, 68), (60, 70), (80, 73), (100, 77), (120, 73), (140, 72),
     (160, 70), (170, 66), (162, 60), (158, 52), (150, 45), (142, 40),
     (140, 35), (130, 33), (127, 35), (122, 30), (120, 25), (110, 20),
     (105, 10), (100, 8), (95, 15), (90, 22), (85, 20), (80, 15),
     (75, 10), (72, 20), (65, 25), (60, 25), (55, 28), (50, 30), (48, 30),
     (45, 35), (42, 40), (40, 45), (38, 50), (40, 55), (40, 60)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (120, -34), (125, -32), (130, -32),
     (135, -35), (140, -38), (145, -38), (150, -37), (153, -27), (150, -22),
     (146, -19), (142, -15), (142, -11), (137, -12), (135, -15), (132, -12),
     (130, -13), (126, -14), (122, -17), (118, -20), (114, -22)],
    # New Zealand
    [(167, -45), (170, -42), (174, -41), (178, -38), (176, -35),
     (174, -37), (170, -40), (167, -45)],
    # Japan
    [(130, 31), (133, 34), (137, 35), (140, 37), (141, 40), (143, 43),
     (145, 44), (142, 42), (140, 38), (138, 35), (135, 33), (131, 32)],
]


def project(lon, lat, box):
    """Equirectangular projection into the map box (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = box
    px = x0 + (lon + 170.0) / 360.0 * (x1 - x0)
    py = y0 + (70.0 - lat) / 125.0 * (y1 - y0)
    return px, py


def draw_map(draw, box, pins):
    """Draw the stylised world map with numbered pins and tags."""
    draw.rectangle(box, fill=OCEAN, outline=RULE, width=1)
    for poly in CONTINENTS:
        pts = [project(lon, lat, box) for lon, lat in poly]
        draw.polygon(pts, fill=LAND, outline=LAND_EDGE)
    # Indonesia island dots (rough, as small ellipses)
    for lon, lat in [(95, 2), (100, -1), (105, -4), (110, -7), (115, -8),
                     (120, -9), (125, -5), (130, -3), (135, -4)]:
        px, py = project(lon, lat, box)
        draw.ellipse([px - 2, py - 1, px + 3, py + 2], fill=LAND,
                     outline=LAND_EDGE)
    fnt_num = sans_b(9)
    fnt_tag = sans_b(9)
    # label placement overrides for crowded pins (by story number):
    # Antalya's tag goes above its pin so it cannot run into Bahrain's;
    # Benghazi's tag goes left so it cannot run into Bahrain's;
    # Wellington's tag goes up-left, Canberra's down-right.
    LABEL_FIX = {1: (10, -20), 5: (-58, 2), 24: (-70, -22), 38: (6, 14)}
    for pin in pins:
        px, py = project(pin["lon"], pin["lat"], box)
        draw.ellipse([px - 8, py - 8, px + 8, py + 8], fill=PIN,
                     outline=(255, 255, 255), width=1)
        num = str(pin["n"])
        tw = draw.textlength(num, font=fnt_num)
        draw.text((px - tw / 2, py - 5), num, font=fnt_num,
                  fill=(255, 255, 255))
        tag = pin["tag"]
        ox, oy = LABEL_FIX.get(pin["n"], (pin.get("ox", 8),
                                          pin.get("oy", 8)))
        tx = px + ox
        ty = py + oy
        draw.text((tx, ty), tag, font=fnt_tag, fill=INK)


# ---------------------------------------------------------------- page build

def build():
    with open(DATA, encoding="utf-8") as fh:
        d = json.load(fh)

    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    # outer frame
    draw.rectangle([3, 3, W - 4, H - 4], outline=INK, width=5)

    L, R = 18, W - 18          # content left / right
    CW = R - L                 # content width

    # ---- masthead
    y = 16
    draw.text((L, y), d["masthead"], font=serif_b(15), fill=RED)
    right = "EST. 2025  ·  ONE PAGE, ONE DAY"
    draw.text((R - text_w(draw, right, sans(10)), y + 3), right,
              font=sans(10), fill=GRAY)
    draw.line([L, 36, R, 36], fill=INK, width=2)

    # ---- date hero
    y = 42
    hero = d["date"]
    draw.text(((W - text_w(draw, hero, serif_b(50))) / 2, y), hero,
              font=serif_b(50), fill=INK)
    # ---- counts line
    y = 96
    counts = d["counts"]
    draw.text(((W - text_w(draw, counts, sans_b(12))) / 2, y), counts,
              font=sans_b(12), fill=RED)
    draw.line([L, 114, R, 114], fill=INK, width=1)

    # ---- data strip
    y = 118
    draw.rectangle([L, y, R, y + 26], fill=INK)
    strip = "  ◆  ".join(d["strip"])
    draw.text(((W - text_w(draw, strip, sans_b(13))) / 2, y + 6), strip,
              font=sans_b(13), fill=(255, 255, 255))

    # ---- three leads
    col_w = (CW - 24) // 3
    top = 152
    leads_end = top
    for i, lead in enumerate(d["leads"]):
        x = L + i * (col_w + 12)
        yy = top
        draw.text((x, yy), lead["kicker"], font=sans_b(11), fill=RED)
        yy += 16
        ART[lead["art"]](draw, x, yy, col_w, 116)
        yy += 120
        # headline: shrink until it fits in 2 lines, never 3
        hfnt, hlines = fit_lines(draw, lead["headline"], [19, 18, 17],
                                 col_w, 2)
        lh = int(hfnt.size * 1.1)
        for line in hlines:
            draw.text((x, yy), line, font=hfnt, fill=INK)
            yy += lh
        yy += 2
        # summary: at most 2 lines
        slines = wrap(draw, lead["summary"], sans(11), col_w)[:2]
        for line in slines:
            draw.text((x, yy), line, font=sans(11), fill=INK)
            yy += 13
        yy += 2
        draw.text((x, yy), lead["figures"], font=sans(10), fill=GRAY)
        yy += 15
        badge(draw, x, yy, lead["label"])
        src = lead["source"]
        draw.text((x + col_w - text_w(draw, src, sans(10)), yy + 1), src,
                  font=sans(10), fill=GRAY)
        leads_end = max(leads_end, yy + 14)

    # ---- THE DAY IN TEN (items 4-13)
    y = leads_end + 8
    draw.text((L, y), "THE DAY IN TEN", font=sans_b(12), fill=RED)
    draw.line([L, y + 16, R, y + 16], fill=INK, width=1)
    y += 22
    mid = d["mid"]
    col_w2 = (CW - 24) // 2
    row_h = 48
    for i, item in enumerate(mid):
        col = i % 2
        row = i // 2
        x = L + col * (col_w2 + 24)
        yy = y + row * row_h
        num = str(4 + i)
        draw.text((x, yy), num, font=serif_b(15), fill=RED)
        tx = x + 24
        for line in wrap(draw, item["h"], sans_b(12), col_w2 - 24):
            draw.text((tx, yy + 1), line, font=sans_b(12), fill=INK)
            yy += 14
        # summary sits under the headline block, aligned to text column
        sy = y + row * row_h + 15
        for line in wrap(draw, item["s"], sans(10), col_w2 - 24):
            draw.text((tx, sy), line, font=sans(10), fill=GRAY)
            sy += 12
        by = y + row * row_h + 36
        badge(draw, tx, by, item["label"])
        src = item["src"]
        draw.text((x + col_w2 - text_w(draw, src, sans(9)), by + 1), src,
                  font=sans(9), fill=GRAY)
    y += 5 * row_h + 6

    # ---- THE FULL LIST (items 14-38)
    draw.text((L, y), "THE FULL LIST  —  EVERY STORY, NUMBERED",
              font=sans_b(12), fill=RED)
    draw.line([L, y + 16, R, y + 16], fill=INK, width=1)
    y += 22
    items = d["list"]
    rows = 13
    row_h2 = 14
    for i, item in enumerate(items):
        col = i // rows
        row = i % rows
        x = L + col * (col_w2 + 24)
        yy = y + row * row_h2
        num = str(14 + i)
        draw.text((x, yy), num, font=serif_b(11), fill=RED)
        tx = x + 24
        # headline, truncated to leave room for badge + source
        src = item["src"]
        src_w = text_w(draw, src, sans(9))
        bw = 52
        avail = col_w2 - 24 - bw - src_w - 16
        hlines = wrap(draw, item["h"], sans(11), avail)
        head = hlines[0]
        draw.text((tx, yy), head, font=sans(11), fill=INK)
        hw = text_w(draw, head, sans(11))
        badge(draw, tx + hw + 6, yy, item["label"])
        draw.text((x + col_w2 - src_w, yy + 1), src, font=sans(9),
                  fill=GRAY)
    y += rows * row_h2 + 8

    # ---- bottom: map + date check + timeline
    draw.text((L, y), "WHERE IT HAPPENED", font=sans_b(12), fill=RED)
    map_x0, map_y0 = L, y + 18
    map_x1, map_y1 = L + 540, y + 128
    draw_map(draw, (map_x0, map_y0, map_x1, map_y1), d["pins"])

    rx = L + 552
    rw = R - rx
    ry = y
    draw.text((rx, ry), "DATE CHECK  —  WHAT WE LEFT OUT",
              font=sans_b(12), fill=RED)
    ry += 20
    for line in d["datecheck"]:
        draw.text((rx, ry), "×", font=sans_b(11), fill=RED)
        for ln in wrap(draw, line, sans(10), rw - 14):
            draw.text((rx + 14, ry), ln, font=sans(10), fill=INK)
            ry += 11
        ry += 1
    ry += 3
    draw.text((rx, ry), "THE DAY, HOUR BY HOUR (UTC)",
              font=sans_b(12), fill=RED)
    ry += 17
    for t, ev in d["timeline"]:
        draw.text((rx, ry), t, font=sans_b(10), fill=RED)
        tw = text_w(draw, t, sans_b(10))
        draw.text((rx + tw + 8, ry), ev, font=sans(10), fill=INK)
        ry += 11

    # ---- footer
    fy = H - 18
    draw.text((L, fy), d["sources"], font=sans(8), fill=GRAY)

    img.save(OUT, format="PNG")
    return OUT


if __name__ == "__main__":
    path = build()
    print("wrote", path)
