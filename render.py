#!/usr/bin/env python3
"""Render one front page: Monday 23 November 2026 world news.

Own code, written in-session for this edition. Deterministic: no clock,
no random, fixed font paths, sorted lookups only. Reads stories.json next
to this file and writes the PNG to /output/entry.png (or $ENTRY_OUT).
Coverage is as of 00:30 UTC on Monday 23 November 2026 - most stories
are Sunday 22 November events reported overnight, labelled as such.
"""
import json
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
DATA = json.loads((HERE / "stories.json").read_text(encoding="utf-8"))
OUT = Path(os.environ.get("ENTRY_OUT", "/output/entry.png"))

W = H = 1024
M = 26                       # outer margin
PAPER = (250, 246, 236)      # warm newsprint
INK = (24, 24, 28)
RED = (178, 34, 28)
BLUE = (28, 58, 112)
TEAL = (18, 96, 84)
AMBER = (196, 120, 20)
GREY = (96, 92, 86)
LINE = (200, 192, 178)

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
SERIF = FONT_DIR / "DejaVuSerif-Bold.ttf"
SERIF_R = FONT_DIR / "DejaVuSerif.ttf"
SANS = FONT_DIR / "DejaVuSans-Bold.ttf"
SANS_R = FONT_DIR / "DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(str(path), size)


F = {
    "brand": font(SANS, 11),
    "date": font(SERIF, 44),
    "counts": font(SANS, 12),
    "strip": font(SANS, 13),
    "kick": font(SANS, 10),
    "head": font(SERIF, 17),
    "mid_head": font(SERIF, 13),
    "body": font(SERIF_R, 11),
    "small": font(SANS_R, 10),
    "tiny": font(SANS_R, 9),
    "list_head": font(SERIF, 12),
    "num": font(SANS, 12),
    "chip": font(SANS, 9),
    "pin": font(SANS, 8),
}


def measure(draw, text, fnt):
    b = draw.textbbox((0, 0), text, font=fnt)
    return b[2] - b[0], b[3] - b[1]


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if measure(draw, trial, fnt)[0] <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_chip(draw, x, y, text, fg, bg):
    tw, th = measure(draw, text, F["chip"])
    pad_x, pad_y = 5, 1
    draw.rounded_rectangle(
        [x, y, x + tw + pad_x * 2, y + th + pad_y * 2 + 1],
        radius=3, fill=bg)
    draw.text((x + pad_x, y + pad_y), text, font=F["chip"], fill=fg)
    return tw + pad_x * 2


def tag_chip(draw, x, y, label):
    palette = {
        "CONFIRMED": ((255, 255, 255), (18, 96, 84)),
        "OFFICIAL": ((255, 255, 255), (28, 58, 112)),
        "REPORTED": ((24, 24, 28), (232, 226, 212)),
        "CLAIMED": ((255, 255, 255), (178, 34, 28)),
    }
    fg, bg = palette.get(label, ((255, 255, 255), GREY))
    return draw_chip(draw, x, y, label, fg, bg)


# ---- flat illustrations (own drawings, new for this edition) -------------

def art_cop31(draw, x, y, w, h):
    # Empty chairs around a broken table: the talks collapse.
    draw.rectangle([x, y, x + w, y + h], fill=(58, 96, 138))
    draw.ellipse([x + w - 52, y + 8, x + w - 8, y + 52], fill=(250, 214, 90))
    draw.rectangle([x, y + h - 26, x + w, y + h], fill=(30, 46, 74))
    # long table, cracked in the middle
    draw.rectangle([x + 20, y + h - 58, x + w - 20, y + h - 46],
                   fill=(196, 120, 20))
    draw.line([x + w // 2, y + h - 58, x + w // 2 + 8, y + h - 46],
              fill=(178, 34, 28), width=3)
    # empty chairs, tipped
    for cx in (36, 96, 156, 216):
        draw.rectangle([x + cx, y + h - 44, x + cx + 22, y + h - 26],
                       fill=(240, 236, 224))
        draw.rectangle([x + cx + 4, y + h - 62, x + cx + 8, y + h - 44],
                       fill=(240, 236, 224))
    # two flags drooping
    for fx, col in [(60, (178, 34, 28)), (180, (18, 96, 84))]:
        draw.line([x + fx, y + 12, x + fx, y + 38], fill=(240, 236, 224),
                  width=2)
        draw.polygon([(x + fx, y + 12), (x + fx + 16, y + 16),
                      (x + fx, y + 20)], fill=col)


def art_gulf(draw, x, y, w, h):
    # Tanker in the strait, smoke columns and a missile arc.
    draw.rectangle([x, y, x + w, y + h], fill=(24, 52, 96))
    draw.rectangle([x, y + h - 30, x + w, y + h], fill=(16, 34, 66))
    # tanker hull
    draw.rectangle([x + 30, y + h - 52, x + w - 30, y + h - 34],
                   fill=(178, 34, 28))
    draw.rectangle([x + w - 78, y + h - 70, x + w - 52, y + h - 52],
                   fill=(240, 236, 224))
    # smoke columns
    for sx in (70, 130, 190):
        draw.ellipse([x + sx - 8, y + 14, x + sx + 8, y + 34],
                     fill=(120, 120, 118))
        draw.ellipse([x + sx - 5, y + 6, x + sx + 5, y + 20],
                     fill=(160, 158, 152))
    # missile arc with flame
    draw.arc([x + 150, y + 4, x + 240, y + 44], start=200, end=340,
             fill=(250, 180, 60), width=3)
    draw.ellipse([x + 228, y + 30, x + 236, y + 38], fill=(250, 120, 40))
    # sea lanes
    for ly in (y + h - 22, y + h - 12):
        draw.line([x + 8, ly, x + w - 8, ly], fill=(120, 160, 200), width=1)


def art_football(draw, x, y, w, h):
    # Green pitch, goal, ball in the net: 4-0.
    draw.rectangle([x, y, x + w, y + h], fill=(30, 110, 60))
    # mowing stripes
    for i in range(5):
        if i % 2 == 0:
            draw.rectangle([x + i * (w // 5), y,
                            x + (i + 1) * (w // 5), y + h],
                           fill=(38, 126, 70))
    # pitch lines
    draw.line([x + w // 2, y, x + w // 2, y + h], fill=(240, 236, 224),
              width=2)
    draw.ellipse([x + w // 2 - 26, y + h // 2 - 26,
                  x + w // 2 + 26, y + h // 2 + 26],
                 outline=(240, 236, 224), width=2)
    # goal frame top right
    draw.rectangle([x + w - 66, y + 10, x + w - 10, y + 46],
                   outline=(255, 255, 255), width=3)
    draw.line([x + w - 66, y + 10, x + w - 10, y + 10],
              fill=(255, 255, 255), width=3)
    # ball in the net
    draw.ellipse([x + w - 52, y + 22, x + w - 28, y + 46],
                 fill=(255, 255, 255), outline=INK, width=1)
    # scoreboard
    draw.rectangle([x + 10, y + 8, x + 86, y + 30], fill=(24, 24, 28))
    draw.text((x + 16, y + 11), "LIV 4-0 MUN", font=F["chip"],
              fill=(250, 214, 90))


ARTS = {"cop31": art_cop31, "gulf": art_gulf, "football": art_football}


# ---- world map (equirectangular, own rough continent outlines) -----------

CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-80, 73), (-65, 60),
     (-55, 47), (-70, 42), (-75, 35), (-81, 26), (-90, 21), (-97, 16),
     (-105, 20), (-117, 33), (-125, 49), (-140, 60), (-168, 66)],
    # South America
    [(-80, 9), (-62, 11), (-52, 5), (-35, -8), (-40, -22), (-48, -28),
     (-58, -38), (-65, -52), (-70, -55), (-73, -37), (-70, -18),
     (-80, -4), (-80, 9)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (0, 51), (5, 58), (10, 59), (18, 56),
     (21, 55), (28, 45), (23, 40), (19, 42), (12, 44), (8, 44), (3, 42),
     (-2, 37), (-10, 36)],
    # Africa
    [(-17, 15), (-16, 28), (-10, 31), (10, 37), (20, 32), (32, 31),
     (35, 28), (43, 12), (51, 11), (48, -1), (40, -15), (35, -25),
     (28, -33), (18, -34), (12, -18), (9, 4), (-8, 5), (-17, 15)],
    # Asia
    [(30, 36), (36, 36), (44, 39), (48, 30), (57, 26), (61, 25),
     (66, 25), (72, 20), (77, 8), (80, 13), (88, 22), (92, 16),
     (98, 10), (104, 2), (108, 11), (114, 22), (121, 28), (127, 40),
     (130, 42), (135, 44), (142, 50), (158, 52), (170, 60), (180, 66),
     (180, 72), (160, 70), (140, 72), (110, 74), (80, 73), (60, 69),
     (50, 69), (40, 68), (32, 70), (30, 62), (28, 55), (30, 45),
     (28, 41), (30, 36)],
    # Australia
    [(114, -22), (114, -35), (124, -33), (130, -32), (137, -35),
     (140, -38), (150, -37), (153, -27), (146, -19), (142, -11),
     (136, -12), (132, -11), (126, -14), (122, -17), (114, -22)],
]


def project(lon, lat, x0, y0, w, h):
    px = x0 + (lon + 180.0) / 360.0 * w
    py = y0 + (80.0 - lat) / 135.0 * h
    return px, py


def draw_map(draw, x0, y0, w, h, pins):
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(214, 226, 232))
    for poly in CONTINENTS:
        pts = [project(lon, lat, x0, y0, w, h) for lon, lat in poly]
        draw.polygon(pts, fill=(232, 226, 212), outline=(150, 146, 138))
    for pin in pins:
        px, py = project(pin["lon"], pin["lat"], x0, y0, w, h)
        draw.ellipse([px - 7, py - 7, px + 7, py + 7], fill=RED)
        draw.text((px - 3, py - 6), str(pin["n"]), font=F["pin"],
                  fill=(255, 255, 255))
        ox, oy = pin.get("ox", 8), pin.get("oy", -14)
        tw, _ = measure(draw, pin["tag"], F["pin"])
        lx = min(max(px + ox, x0 + 2), x0 + w - tw - 2)
        ly = min(max(py + oy, y0 + 2), y0 + h - 12)
        draw.line([px, py, lx + tw / 2, ly + 4], fill=RED, width=1)
        draw.text((lx, ly), pin["tag"], font=F["pin"], fill=INK)


# ---- page -----------------------------------------------------------------

def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle([4, 4, W - 5, H - 5], outline=INK, width=2)
    d.rectangle([8, 8, W - 9, H - 9], outline=LINE, width=1)

    # masthead
    d.text((M, 16), DATA["masthead"], font=F["brand"], fill=RED)
    d.text((W - M - measure(d, "EST. 2025 · ONE PAGE, ONE DAY", F["brand"])[0],
            16), "EST. 2025 · ONE PAGE, ONE DAY", font=F["brand"], fill=GREY)
    d.line([M, 36, W - M, 36], fill=INK, width=2)
    dw, _ = measure(d, DATA["date"], F["date"])
    d.text(((W - dw) / 2, 40), DATA["date"], font=F["date"], fill=INK)
    cw, _ = measure(d, DATA["counts"], F["counts"])
    d.text(((W - cw) / 2, 92), DATA["counts"], font=F["counts"], fill=RED)
    d.line([M, 112, W - M, 112], fill=INK, width=1)

    # data strip
    sy = 118
    d.rectangle([M, sy, W - M, sy + 24], fill=INK)
    strip = "   ◆   ".join(DATA["strip"])
    sw, _ = measure(d, strip, F["strip"])
    d.text(((W - sw) / 2, sy + 4), strip, font=F["strip"], fill=(250, 246, 236))

    # three leads
    ly, lh = 150, 200
    col_w = (W - 2 * M - 2 * 14) // 3
    for i, lead in enumerate(DATA["leads"]):
        x = M + i * (col_w + 14)
        d.text((x, ly), lead["kicker"], font=F["kick"], fill=RED)
        ax, ay = x, ly + 16
        ARTS[lead["art"]](d, ax, ay, col_w, 78)
        hy = ay + 78 + 6
        for ln in wrap(d, lead["headline"], F["head"], col_w):
            d.text((x, hy), ln, font=F["head"], fill=INK)
            hy += 20
        for ln in wrap(d, lead["summary"], F["body"], col_w):
            d.text((x, hy), ln, font=F["body"], fill=INK)
            hy += 13
        d.text((x, ly + lh - 30), lead["figures"], font=F["small"], fill=GREY)
        tag_chip(d, x, ly + lh - 18, lead["label"])
        sw2, _ = measure(d, lead["source"], F["tiny"])
        d.text((x + col_w - sw2, ly + lh - 16), lead["source"],
               font=F["tiny"], fill=GREY)
        d.line([x, ly + lh - 4, x + col_w, ly + lh - 4], fill=LINE, width=1)

    # ten mid stories, two columns
    my = ly + lh + 8
    d.text((M, my), "THE DAY IN TEN", font=F["brand"], fill=RED)
    d.line([M, my + 15, W - M, my + 15], fill=INK, width=1)
    mid_y = my + 20
    mid_col_w = (W - 2 * M - 20) // 2
    row_h = 43
    for i, st in enumerate(DATA["mid"]):
        col = i % 2
        row = i // 2
        x = M + col * (mid_col_w + 20)
        y = mid_y + row * row_h
        d.text((x, y), f"{i + 4}.", font=F["num"], fill=RED)
        tx = x + 26
        for ln in wrap(d, st["h"], F["mid_head"], mid_col_w - 26):
            d.text((tx, y), ln, font=F["mid_head"], fill=INK)
            y += 16
        for ln in wrap(d, st["s"], F["tiny"], mid_col_w - 26):
            d.text((tx, y), ln, font=F["tiny"], fill=GREY)
            y += 12
        tag_chip(d, tx, mid_y + row * row_h + row_h - 16, st["label"])
        sw3, _ = measure(d, st["src"], F["tiny"])
        d.text((x + mid_col_w - sw3, mid_y + row * row_h + row_h - 14),
               st["src"], font=F["tiny"], fill=GREY)

    # full numbered list
    list_y = mid_y + 5 * row_h + 6
    d.text((M, list_y), "THE FULL LIST — EVERY STORY, NUMBERED", font=F["brand"],
           fill=RED)
    d.line([M, list_y + 15, W - M, list_y + 15], fill=INK, width=1)
    list_top = list_y + 20
    list_col_w = (W - 2 * M - 20) // 2
    list_row_h = 15
    for i, st in enumerate(DATA["list"]):
        n = i + 14
        col = i % 2
        row = i // 2
        x = M + col * (list_col_w + 20)
        y = list_top + row * list_row_h
        d.text((x, y), f"{n}.", font=F["num"], fill=RED)
        d.text((x + 26, y + 1), st["h"], font=F["list_head"], fill=INK)
        hw, _ = measure(d, st["h"], F["list_head"])
        sw4, _ = measure(d, st["src"], F["tiny"])
        lx = x + 26 + hw + 8
        # Only draw the badge when it fits clear of the source credit.
        cw4, _ = measure(d, st["label"], F["chip"])
        if lx + cw4 + 12 < x + list_col_w - sw4 - 6:
            tag_chip(d, lx, y, st["label"])
        d.text((x + list_col_w - sw4, y + 2), st["src"], font=F["tiny"],
               fill=GREY)

    # map + date check
    bottom_y = list_top + 13 * list_row_h + 8
    d.text((M, bottom_y), "WHERE IT HAPPENED", font=F["brand"], fill=RED)
    d.text((W // 2 + 6, bottom_y), "DATE CHECK — WHAT WE LEFT OUT",
           font=F["brand"], fill=RED)
    d.line([M, bottom_y + 15, W - M, bottom_y + 15], fill=INK, width=1)
    map_y = bottom_y + 20
    map_h = H - 32 - map_y
    map_w = W // 2 - M - 6
    draw_map(d, M, map_y, map_w, map_h, DATA["pins"])

    dx = W // 2 + 6
    dy = map_y
    for item in DATA["datecheck"]:
        d.text((dx + 8, dy), "✕", font=F["small"], fill=RED)
        for ln in wrap(d, item, F["small"], W - M - dx - 20):
            d.text((dx + 22, dy), ln, font=F["small"], fill=INK)
            dy += 12
        dy += 3
    dy += 2
    d.line([dx, dy, W - M, dy], fill=LINE, width=1)
    dy += 6
    d.text((dx, dy), "THE DAY, HOUR BY HOUR (UTC)", font=F["brand"], fill=RED)
    dy += 15
    for t, ev in DATA["timeline"]:
        d.text((dx, dy), t, font=F["chip"], fill=RED)
        d.text((dx + 96, dy), ev, font=F["small"], fill=INK)
        dy += 11

    # footer
    fy = H - 24
    d.line([M, fy - 6, W - M, fy - 6], fill=INK, width=1)
    d.text((M, fy), "Sources: " + DATA["sources"], font=F["tiny"], fill=GREY)
    tag = "MONDAY 23 NOVEMBER 2026"
    tw5, _ = measure(d, tag, F["tiny"])
    d.text((W - M - tw5, fy), tag, font=F["tiny"], fill=GREY)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, format="PNG")
    print(f"wrote {OUT} {img.size}")


if __name__ == "__main__":
    render()
