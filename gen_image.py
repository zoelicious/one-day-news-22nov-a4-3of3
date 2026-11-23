#!/usr/bin/env python3
"""Render entry.png for news-image-20261122, Agent 4 — TIMELINE EDITION.

One-page newspaper: masthead, giant date headline, 6-number stat strip,
region bar, 13 numbered stories hung left/right of a central UTC timeline
spine (each panel carries a small clock face), THE DAY IN UTC strip, dotted
world map with numbered pins on land, ALSO list 14-38, red-framed DATE CHECK.
Drawn from scratch with PIL; no external assets.
"""
import math
import textwrap
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
CREAM = (247, 240, 222)
PAPER = (252, 247, 233)
INK = (26, 32, 44)
NAVY = (31, 58, 95)
NAVY_D = (18, 34, 60)
RED = (178, 34, 34)
RED_D = (140, 22, 22)
TEAL = (23, 120, 110)
GOLD = (201, 148, 42)
GREY = (90, 92, 96)
LINE = (120, 110, 88)
DOT = (138, 122, 90)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS_I = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"


def F(path, size):
    return ImageFont.truetype(path, size)


img = Image.new("RGB", (W, H), CREAM)
d = ImageDraw.Draw(img, "RGBA")


def wrap(draw, text, font, width):
    """Greedy wrap that never exceeds `width` pixels."""
    lines = []
    for para in text.split("\n"):
        words, cur = para.split(), ""
        for w in words:
            t = (cur + " " + w).strip()
            if draw.textlength(t, font=font) <= width:
                cur = t
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
    return lines


def text_block(x, y, text, font, fill, width, leading, max_lines=None):
    lines = wrap(d, text, font, width)
    if max_lines:
        lines = lines[:max_lines]
    for ln in lines:
        d.text((x, y), ln, font=font, fill=fill)
        y += leading
    return y


def clock(cx, cy, r, hour=None, minute=0, bg=(255, 255, 255), ring=NAVY):
    """Small clock face; hands only when the time is known."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=bg, outline=ring, width=2)
    d.ellipse([cx - 1, cy - 1, cx + 1, cy + 1], fill=ring)
    if hour is not None:
        ha = math.radians((hour % 12) * 30 - 90)
        ma = math.radians(minute * 6 - 90)
        d.line([cx, cy, cx + r * 0.5 * math.cos(ha), cy + r * 0.5 * math.sin(ha)],
               fill=ring, width=2)
        d.line([cx, cy, cx + r * 0.8 * math.cos(ma), cy + r * 0.8 * math.sin(ma)],
               fill=RED, width=2)


def tag_chip(x, y, label, fill):
    f = F(SANS_B, 10)
    w = d.textlength(label, font=f) + 10
    d.rounded_rectangle([x, y, x + w, y + 15], radius=3, fill=fill)
    d.text((x + 5, y + 2), label, font=f, fill=(255, 255, 255))
    return w


def num_badge(cx, cy, n, r=12):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED, outline=(255, 255, 255), width=2)
    f = F(SANS_B, 14)
    t = str(n)
    d.text((cx - d.textlength(t, font=f) / 2, cy - 8), t, font=f, fill=(255, 255, 255))


# ---------------------------------------------------------------- helpers: scenes
def skyline(x, y, w, h, base, tops, win=(255, 214, 120)):
    """Flat night skyline; tops = list of (rel_x, rel_w, rel_h)."""
    for rx, rw, rh in tops:
        bx, bw = x + rx * w, rw * w
        d.rectangle([bx, y + h - rh * h, bx + bw, y + h], fill=base)
        for wy in range(3):
            for wx in range(max(1, int(bw // 14))):
                if (wx + wy) % 2 == 0:
                    d.rectangle([bx + 3 + wx * 12, y + h - rh * h + 5 + wy * 9,
                                 bx + 7 + wx * 12, y + h - rh * h + 10 + wy * 9],
                                fill=win)


def drones(x, y, w, h, n=6):
    for i in range(n):
        cx = x + 12 + (w - 24) * (i + 0.5) / n
        cy = y + 8 + (i % 3) * (h // 3)
        d.ellipse([cx - 3, cy - 2, cx + 3, cy + 2], fill=(230, 230, 230))
        d.line([cx - 9, cy - 4, cx + 9, cy - 4], fill=(230, 230, 230), width=1)
        d.line([cx - 9, cy + 4, cx + 9, cy + 4], fill=(230, 230, 230), width=1)
        d.ellipse([cx - 1, cy + 5, cx + 1, cy + 7], fill=(255, 120, 60))


def flames(x, y, w, h, n=4):
    for i in range(n):
        cx = x + w * (i + 0.5) / n
        fh = h * (0.55 + 0.35 * ((i * 37) % 10) / 10)
        d.polygon([(cx - w / (n * 2.4), y + h), (cx, y + h - fh),
                   (cx + w / (n * 2.4), y + h)], fill=(232, 110, 30))
        d.polygon([(cx - w / (n * 4), y + h), (cx, y + h - fh * 0.55),
                   (cx + w / (n * 4), y + h)], fill=(255, 196, 66))


def smoke(x, y, w, n=3):
    """Smoke puffs hanging just below y (the flame top), never above it."""
    for i in range(n):
        cx = x + w * (i + 0.5) / n
        cy = y + 8 + (i % 2) * 6
        d.ellipse([cx - 9, cy - 7, cx + 9, cy + 7], fill=(120, 120, 125, 190))
        d.ellipse([cx - 5, cy - 12, cx + 5, cy - 2], fill=(140, 140, 145, 170))


def stars(x, y, w, h, n=14, seed=7):
    for i in range(n):
        sx = x + ((i * 53 + seed) % max(1, w - 6)) + 3
        sy = y + ((i * 29 + seed * 3) % max(1, h - 6)) + 3
        r = 1 if i % 3 else 2
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(255, 255, 255))

# ---------------------------------------------------------------- panel scenes
def scene_ukraine(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY_D)
    stars(x, y, w, h)
    d.ellipse([x + w - 34, y + 6, x + w - 14, y + 26], fill=(240, 230, 190))
    drones(x, y + 2, w, h // 2)
    flames(x + w * 0.55, y + h - 22, w * 0.4, 22, 3)
    skyline(x, y + 26, w, h - 26, (10, 18, 36),
            [(0.02, 0.10, 0.55), (0.14, 0.08, 0.75), (0.24, 0.12, 0.5),
             (0.38, 0.07, 0.85), (0.47, 0.11, 0.6), (0.60, 0.09, 0.8),
             (0.71, 0.12, 0.55), (0.85, 0.10, 0.7)])
    d.polygon([(x + 30, y + h), (x + 60, y + 12), (x + 66, y + 12), (x + 44, y + h)],
              fill=(255, 220, 130, 60))


def scene_cop31(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(18, 90, 82))
    d.rectangle([x, y, x + w, y + max(6, h * 0.18)], fill=(12, 66, 60))
    # wall clock showing 03:00
    clock(x + w - 24, y + h * 0.32, 11, hour=3, minute=0)
    # long negotiation table
    ty = y + h * 0.66
    d.polygon([(x + 8, y + h - 4), (x + w - 8, y + h - 4),
               (x + w - 30, ty), (x + 30, ty)], fill=(120, 72, 32))
    d.rectangle([x + 12, ty - 6, x + w - 12, ty], fill=(150, 96, 44))
    # delegates around the table
    for i in range(7):
        px = x + 16 + i * ((w - 32) / 7)
        hy = y + h * 0.34
        d.ellipse([px, hy, px + 12, hy + 12], fill=(235, 200, 160))
        d.rectangle([px - 1, hy + 12, px + 13, ty - 4],
                    fill=[(178, 34, 34), (31, 58, 95), (23, 120, 110), (201, 148, 42),
                          (90, 60, 120), (31, 58, 95), (178, 34, 34)][i])
    # papers on the table
    for i in range(4):
        px = x + 24 + i * ((w - 60) / 4)
        d.rectangle([px, ty - 5, px + 16, ty - 1], fill=(255, 255, 255))
    # flags
    for i, c in enumerate([(178, 34, 34), (31, 58, 95), (23, 120, 110)]):
        fx = x + 10 + i * 18
        d.line([fx, y + 4, fx, y + h * 0.30], fill=(220, 220, 220), width=2)
        d.rectangle([fx, y + 4, fx + 14, y + 12], fill=c)


def scene_bahrain(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(24, 20, 34))
    stars(x, y, w, h // 2)
    d.ellipse([x + w - 30, y + 6, x + w - 12, y + 24], fill=(240, 230, 190))
    # radar dish on a mast
    bx = x + w * 0.42
    d.rectangle([bx - 3, y + h * 0.45, bx + 3, y + h], fill=(90, 90, 96))
    d.pieslice([bx - 42, y + 6, bx + 42, y + h * 0.5], 200, 340, fill=(200, 205, 215))
    d.line([bx, y + h * 0.28, bx + 46, y + 4], fill=(220, 220, 220), width=2)
    d.ellipse([bx - 5, y + h * 0.24, bx + 5, y + h * 0.24 + 10], fill=(220, 220, 220))
    flames(x + w * 0.62, y + h * 0.45, w * 0.34, h * 0.55, 3)
    smoke(x + w * 0.62, y + h * 0.45, w * 0.34, 2)
    # low buildings
    d.rectangle([x, y + h - 14, x + w * 0.3, y + h], fill=(12, 12, 20))
    d.rectangle([x + w * 0.72, y + h - 10, x + w, y + h], fill=(12, 12, 20))


def scene_sparta(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(28, 52, 84))
    stars(x, y, w, h // 2)
    d.rectangle([x, y + h * 0.62, x + w, y + h], fill=(16, 38, 66))
    for i in range(5):
        wx = x + 8 + i * (w // 5)
        d.arc([wx, y + h * 0.66, wx + 26, y + h * 0.78], 0, 180, fill=(120, 180, 220), width=2)
    # cargo ship
    d.rectangle([x + w * 0.12, y + h * 0.42, x + w * 0.88, y + h * 0.62], fill=(120, 30, 28))
    d.rectangle([x + w * 0.70, y + h * 0.28, x + w * 0.82, y + h * 0.42], fill=(200, 200, 205))
    d.rectangle([x + w * 0.16, y + h * 0.46, x + w * 0.30, y + h * 0.52], fill=(240, 200, 90))
    flames(x + w * 0.30, y + h * 0.10, w * 0.42, h * 0.34, 3)
    smoke(x + w * 0.30, y + h * 0.10, w * 0.42, 3)
    # lifeboat
    d.polygon([(x + w * 0.05, y + h * 0.72), (x + w * 0.16, y + h * 0.72),
               (x + w * 0.14, y + h * 0.80), (x + w * 0.07, y + h * 0.80)],
              fill=(232, 160, 40))


def scene_hk(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(31, 58, 95))
    skyline(x, y + 8, w, h - 8, (16, 34, 62),
            [(0.02, 0.12, 0.7), (0.16, 0.09, 0.9), (0.27, 0.13, 0.6),
             (0.42, 0.08, 1.0), (0.52, 0.11, 0.7), (0.65, 0.09, 0.85),
             (0.76, 0.12, 0.6), (0.90, 0.08, 0.75)])
    # ballot box + ballot
    bx, by = x + w * 0.36, y + h - 34
    d.rectangle([bx, by, bx + 34, by + 22], fill=(178, 34, 34))
    d.rectangle([bx - 3, by - 4, bx + 37, by], fill=(140, 22, 22))
    d.polygon([(bx + 8, by - 18), (bx + 18, by - 30), (bx + 26, by - 18)],
              fill=(255, 255, 255))
    d.text((bx + 12, by + 5), "✓", font=F(SANS_B, 14), fill=(255, 255, 255))


def scene_hormuz(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(23, 90, 100))
    d.rectangle([x, y + h * 0.6, x + w, y + h], fill=(14, 60, 80))
    for i in range(4):
        wx = x + 6 + i * (w // 4)
        d.arc([wx, y + h * 0.64, wx + 24, y + h * 0.76], 0, 180, fill=(140, 200, 220), width=2)
    d.rectangle([x + w * 0.10, y + h * 0.34, x + w * 0.62, y + h * 0.58], fill=(150, 50, 36))
    d.rectangle([x + w * 0.62, y + h * 0.22, x + w * 0.72, y + h * 0.58], fill=(220, 220, 225))
    flames(x + w * 0.68, y + h * 0.30, w * 0.26, h * 0.26, 2)
    smoke(x + w * 0.68, y + h * 0.30, w * 0.26, 2)


def scene_cricket(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(28, 110, 60))
    d.ellipse([x + w - 40, y + 3, x + w - 8, y + h - 1], fill=(255, 255, 255))
    d.text((x + w - 37, y + h * 0.22), "720", font=F(SANS_B, 11), fill=(28, 110, 60))
    d.text((x + w - 34, y + h * 0.55), "/9", font=F(SANS_B, 9), fill=(28, 110, 60))
    # stumps
    for i in range(3):
        sx = x + 14 + i * 7
        d.rectangle([sx, y + h - 26, sx + 3, y + h - 8], fill=(240, 220, 140))
    d.rectangle([x + 14, y + h - 29, x + 34, y + h - 26], fill=(240, 220, 140))
    # bat + ball
    d.line([x + w * 0.55, y + h - 10, x + w * 0.72, y + h * 0.45],
           fill=(220, 180, 110), width=5)
    d.ellipse([x + w * 0.74, y + h * 0.30, x + w * 0.74 + 10, y + h * 0.30 + 10],
              fill=(178, 34, 34))
    d.rectangle([x + 8, y + h - 8, x + w - 8, y + h], fill=(20, 80, 44))


def scene_f1(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(20, 20, 28))
    # checkered flag
    for r in range(3):
        for c in range(5):
            if (r + c) % 2 == 0:
                d.rectangle([x + 8 + c * 8, y + 6 + r * 8, x + 16 + c * 8, y + 14 + r * 8],
                            fill=(255, 255, 255))
            else:
                d.rectangle([x + 8 + c * 8, y + 6 + r * 8, x + 16 + c * 8, y + 14 + r * 8],
                            fill=(20, 20, 28))
    d.line([x + 8, y + 6, x + 8, y + h - 12], fill=(200, 200, 200), width=2)
    # race car silhouette
    cx, cy = x + w * 0.45, y + h - 22
    d.polygon([(cx, cy), (cx + 8, cy - 12), (cx + 44, cy - 12), (cx + 58, cy - 4),
               (cx + 58, cy), (cx, cy)], fill=(178, 34, 34))
    d.ellipse([cx + 10, cy - 2, cx + 22, cy + 8], fill=(15, 15, 15))
    d.ellipse([cx + 40, cy - 2, cx + 52, cy + 8], fill=(15, 15, 15))
    d.rectangle([cx + 56, cy - 16, cx + 62, cy - 2], fill=(178, 34, 34))
    d.text((x + w - 30, y + h - 18), "P1", font=F(SANS_B, 14), fill=(255, 196, 66))


def scene_gaza(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(196, 164, 120))
    # aid truck
    d.rectangle([x + 10, y + h * 0.42, x + w * 0.62, y + h * 0.85],
                fill=(240, 240, 235))
    d.rectangle([x + w * 0.62, y + h * 0.50, x + w * 0.82, y + h * 0.85],
                fill=(178, 34, 34))
    d.ellipse([x + 20, y + h * 0.82, x + 30, y + h * 0.97], fill=(30, 30, 30))
    d.ellipse([x + w * 0.68, y + h * 0.82, x + w * 0.68 + 10, y + h * 0.97],
              fill=(30, 30, 30))
    d.text((x + 16, y + h * 0.52), "AID", font=F(SANS_B, 10), fill=(178, 34, 34))
    # broken wall + smoke
    d.rectangle([x + w * 0.85, y + h * 0.30, x + w, y + h * 0.85],
                fill=(120, 100, 80))
    smoke(x + w * 0.8, y + h * 0.30, w * 0.18, 1)


def scene_basra(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(60, 60, 70))
    # cooling towers
    for i, tx in enumerate([0.12, 0.42, 0.70]):
        bx = x + w * tx
        d.polygon([(bx, y + h - 2), (bx + 8, y + h * 0.30), (bx + 30, y + h * 0.30),
                   (bx + 38, y + h - 2)], fill=(150, 150, 155))
        d.ellipse([bx + 8, y + h * 0.30 - 4, bx + 30, y + h * 0.30 + 2],
                  fill=(170, 170, 175))
    flames(x + w * 0.42, y + h * 0.55, w * 0.3, h * 0.45, 2)
    smoke(x + w * 0.42, y + h * 0.55, w * 0.3, 2)


def scene_bayelsa(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(20, 70, 110))
    d.rectangle([x, y + h * 0.55, x + w, y + h], fill=(14, 48, 84))
    for i in range(4):
        wx = x + 6 + i * (w // 4)
        d.arc([wx, y + h * 0.58, wx + 24, y + h * 0.70], 0, 180, fill=(140, 200, 230), width=2)
    # capsized hull (upside down)
    d.pieslice([x + w * 0.2, y + h * 0.30, x + w * 0.8, y + h * 0.75], 180, 360,
               fill=(120, 70, 30))
    d.rectangle([x + w * 0.42, y + h * 0.30, x + w * 0.58, y + h * 0.36], fill=(90, 50, 22))


def scene_cikande(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(96, 52, 40))
    d.rectangle([x + w * 0.68, y + 2, x + w * 0.78, y + h * 0.4],
                fill=(120, 120, 125))
    d.rectangle([x + 6, y + h * 0.55, x + w - 6, y + h - 2], fill=(70, 38, 30))
    flames(x + 8, y + h * 0.30, w - 16, h * 0.45, 3)
    smoke(x + 8, y + h * 0.35, w - 16, 2)
    d.text((x + 10, y + h - 11), "CANDY", font=F(SANS_B, 8),
           fill=(240, 200, 120))


def scene_bepi(x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(8, 10, 26))
    stars(x, y, w, h)
    # Mercury
    mr = max(6, min(16, int(h * 0.42)))
    mx, my = x + w * 0.30, y + h * 0.55
    d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(176, 148, 120))
    for cx, cy, cr in [(mx - 7, my - 5, 3), (mx + 6, my + 4, 4), (mx + 2, my - 9, 2)]:
        d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(140, 112, 88))
    # spacecraft
    sx, sy = x + w * 0.66, y + h * 0.30
    d.rectangle([sx - 4, sy - 4, sx + 4, sy + 4], fill=(220, 220, 225))
    d.rectangle([sx - 16, sy - 2, sx - 4, sy + 2], fill=(60, 90, 180))
    d.rectangle([sx + 4, sy - 2, sx + 16, sy + 2], fill=(60, 90, 180))
    d.line([sx, sy, mx + 12, my - 8], fill=(255, 196, 66), width=1)

SCENES = {1: scene_cop31, 2: scene_ukraine, 3: scene_bahrain, 4: scene_sparta,
          5: scene_hk, 6: scene_hormuz, 7: scene_cricket, 8: scene_f1,
          9: scene_gaza, 10: scene_basra, 11: scene_bayelsa,
          12: scene_cikande, 13: scene_bepi}

# ---------------------------------------------------------------- panel data
# (num, clock hour/minute or None, time label, tag, tag colour, source,
#  title, body)
PANELS = [
 (1, (3, 0), "03:00 GMT", "CONFIRMED", NAVY, "REUTERS · AP",
  "COP31 nears deal as approval session opens",
  "Final text tabled early Sunday in Antalya. Objections close 03:00 GMT; "
  "approval 06:00 GMT. No fossil fuels; power 35% by 2035; $120bn target "
  "dropped."),
 (2, (0, 0), "00:00", "CONFIRMED", NAVY, "AP · KYIV INDEPENDENT",
  "186 drones in one night over Ukraine",
  "Russia launched 186 drones overnight; 161 shot down or jammed, 18 sites "
  "hit. Kryvyi Rih: 2 killed, 60 hurt."),
 (3, None, "OVERNIGHT", "CLAIM", RED, "AL JAZEERA · REUTERS",
  "Iran claims strikes on US bases in Bahrain",
  "Tehran claims 2 Patriot radars hit at al-Riffa and Awali, one site "
  "ablaze, no casualties. Bahrain says most were intercepted; fire at a "
  "civilian site."),
 (4, None, "SUNDAY", "CONFIRMED", NAVY, "REUTERS",
  "Russian ship Sparta II still burning",
  "Cargo ship ablaze in the Gulf of Finland; 16 crew evacuated. Fire still "
  "raging Sunday; Finland leads the rescue."),
 (5, (13, 0), "13:00", "OFFICIAL", TEAL, "SCMP",
  "Hong Kong votes for 723 seats",
  "856 candidates chase 723 seats. Turnout 89.81% at 13:00."),
 (6, None, "SUNDAY", "REPORTED", TEAL, "UKMTO",
  "Two tankers hit leaving Hormuz",
  "Two tankers struck leaving the Strait. Torkel still burning at anchor."),
 (7, None, "SUNDAY", "CONFIRMED", NAVY, "REUTERS",
  "Pant 128 as India declare 720/9",
  "Pant 128, Rahul 136; India declare 720/9, lead 352. New Zealand 105/2."),
 (8, (4, 0), "04:00 GMT", "CONFIRMED", NAVY, "REUTERS · F1",
  "Verstappen wins the Las Vegas GP",
  "Verstappen wins by 0.639 from Norris; Norris 2nd, Piastri 3rd."),
 (9, None, "SUNDAY", "REPORTED", RED, "AL JAZEERA · AP",
  "Four killed as Gaza ceasefire frays",
  "Four dead; an aid van hit."),
 (10, None, "SUNDAY", "CONFIRMED", NAVY, "REUTERS",
  "Power-plant fire kills four in Basra",
  "Blaze kills 4, hurts 35."),
 (11, None, "SUNDAY", "CONFIRMED", NAVY, "AP · DW",
  "Boat carrying mourners capsizes, 24 dead",
  "Boat capsizes; 24 dead."),
 (12, None, "SUNDAY", "REPORTED", TEAL, "WIRES",
  "Candy-factory fire in Cikande",
  "Factory fire kills 3; 36 missing."),
 (13, None, "SUNDAY", "OFFICIAL", TEAL, "ESA · AP",
  "BepiColombo enters orbit around Mercury",
  "ESA craft in Mercury orbit."),
]

TAG_FILL = {"CONFIRMED": NAVY, "CLAIM": RED, "REPORTED": TEAL,
            "OFFICIAL": (90, 60, 120), "PENDING": (150, 110, 20)}


def panel(x, y, w, h, p, hero=False, compact=False):
    num, clk, tlabel, tag, _tc, src, title, body = p
    d.rectangle([x, y, x + w, y + h], fill=PAPER, outline=INK, width=1)
    ill_h = 56 if hero else (24 if compact else 36)
    SCENES[num](x + 1, y + 1, w - 2, ill_h)
    num_badge(x + 16, y + 16, num)
    if compact:
        # tag chip + clock live inside the thin illustration band
        if clk:
            clock(x + w - 14, y + 13, 9, hour=clk[0], minute=clk[1])
        else:
            clock(x + w - 14, y + 13, 9)
        tf = F(SANS_B, 8)
        tw = d.textlength(tag, font=tf) + 8
        cx1 = x + w - 14 - 11 - tw
        d.rounded_rectangle([cx1, y + 5, cx1 + tw, y + 17], radius=3,
                            fill=TAG_FILL[tag])
        d.text((cx1 + 4, y + 6), tag, font=tf, fill=(255, 255, 255))
        ty = y + ill_h + 4
        tsize, bsize = 11, 9
        tlead, blead = 14, 12
        title_lines = wrap(d, title, F(SERIF_B, tsize), w - 12)
        for ln in title_lines[:2]:
            d.text((x + 6, ty), ln, font=F(SERIF_B, tsize), fill=INK)
            ty += tlead
        # one body line, then the source in tiny red type at the foot
        avail = y + h - 4 - 10 - ty
        max_body = max(1, avail // blead)
        text_block(x + 6, ty, body, F(SANS, bsize), (50, 50, 52), w - 12,
                   blead, max_lines=max_body)
        d.text((x + 6, y + h - 11), src, font=F(SANS_B, 7), fill=RED_D)
        return
    # clock face + time label at the top-right of the illustration
    if clk:
        clock(x + w - 26, y + 18, 11, hour=clk[0], minute=clk[1])
    else:
        clock(x + w - 26, y + 18, 11)
    tf = F(SANS_B, 9)
    tw = d.textlength(tlabel, font=tf)
    d.rectangle([x + w - 26 - tw - 14, y + 34, x + w - 12, y + 46],
                fill=(255, 255, 255))
    d.text((x + w - 26 - tw - 9, y + 36), tlabel, font=tf, fill=NAVY)
    ty = y + ill_h + 5
    # tag chip + source
    tw_chip = tag_chip(x + 6, ty, tag, TAG_FILL[tag])
    sf = F(SANS_B, 8)
    d.text((x + 6 + tw_chip + 5, ty + 3), src, font=sf, fill=RED_D)
    ty += 19
    tsize = 14 if hero else (11 if h <= 110 else 12)
    bsize = 11 if hero else (9 if h <= 110 else 10)
    tlead = tsize + 3
    blead = bsize + 3
    title_lines = wrap(d, title, F(SERIF_B, tsize), w - 12)
    for ln in title_lines[:2]:
        d.text((x + 6, ty), ln, font=F(SERIF_B, tsize), fill=INK)
        ty += tlead
    avail = y + h - 4 - ty
    max_body = max(1, avail // blead)
    text_block(x + 6, ty, body, F(SANS, bsize), (50, 50, 52), w - 12, blead,
               max_lines=max_body)


# ---------------------------------------------------------------- header
d.rectangle([0, 0, W, 40], fill=RED_D)
d.text((10, 8), "THE WORLD IN ONE DAY", font=F(SERIF_B, 24), fill=(255, 255, 255))
d.text((W - 10 - d.textlength("SUNDAY EDITION  •  22 NOV 2026", font=F(SANS_B, 12)),
        13), "SUNDAY EDITION  •  22 NOV 2026", font=F(SANS_B, 12),
       fill=(255, 220, 200))

d.text((8, 44), "Sunday 22 November 2026", font=F(SERIF_B, 42), fill=INK)
d.text((8, 92), "COP31 nears a deal in Antalya  •  186 drones over Ukraine  •  "
                 "Iran claims US bases hit in Bahrain",
       font=F(SERIF_I, 15), fill=RED)

# stat strip: 186 / 03:00 / 06:00 / 89.81% / 720/9 / 50 pts
STATS = [("186", "drones launched, Ukraine"),
         ("03:00", "GMT — COP31 objections close"),
         ("06:00", "GMT — COP31 approval session"),
         ("89.81%", "Hong Kong turnout, 13:00"),
         ("720/9", "India declare, cricket"),
         ("50 PTS", "Wembanyama, Spurs record")]
sx, sw, gap = 8, 160, 4
for i, (big, small) in enumerate(STATS):
    bx = sx + i * (sw + gap)
    d.rectangle([bx, 116, bx + sw, 150], fill=PAPER, outline=RED, width=1)
    d.text((bx + sw / 2 - d.textlength(big, font=F(SERIF_B, 20)) / 2, 119),
           big, font=F(SERIF_B, 20), fill=RED)
    d.text((bx + sw / 2 - d.textlength(small, font=F(SANS, 8)) / 2, 140),
           small, font=F(SANS, 8), fill=GREY)

# region bar — 38 stories in total
d.rectangle([8, 156, 1016, 168], fill=NAVY)
segs = [("Europe", 9, NAVY), ("Middle East", 8, RED), ("Asia", 7, TEAL),
        ("Americas", 7, GOLD), ("Africa", 3, (90, 60, 120)),
        ("Oceania", 3, (150, 110, 20)), ("Global", 1, GREY)]
bx = 8
for name, n, c in segs:
    wseg = 1008 * n / 38
    d.rectangle([bx, 156, bx + wseg, 168], fill=c)
    bx += wseg
d.text((8, 171), "Europe 9  •  Middle East 8  •  Asia 7  •  Americas 7  •  "
                 "Africa 3  •  Oceania 3  •  Global 1  •  TOTAL 38",
       font=F(SANS_B, 10), fill=INK)

# ---------------------------------------------------------------- story zone + spine
def point_in_poly(px, py, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > py) != (yj > py):
            xint = xi + (py - yi) * (xj - xi) / (yj - yi)
            if px < xint:
                inside = not inside
        j = i
    return inside


LAND = [
 [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 80),
  (-80, 73), (-75, 72), (-65, 60), (-55, 52), (-60, 47), (-70, 42),
  (-75, 35), (-80, 32), (-81, 26), (-90, 21), (-97, 16), (-92, 15),
  (-86, 12), (-83, 9), (-79, 8), (-92, 14), (-105, 20), (-110, 23),
  (-114, 29), (-120, 34), (-125, 40), (-124, 48), (-130, 55), (-150, 60),
  (-165, 60)],
 [(-58, 64), (-45, 60), (-40, 64), (-30, 68), (-22, 70), (-30, 76),
  (-55, 76), (-60, 74)],
 [(-79, 9), (-72, 12), (-62, 10), (-52, 5), (-50, 0), (-44, -3),
  (-35, -8), (-40, -20), (-48, -28), (-58, -38), (-65, -45), (-70, -54),
  (-73, -50), (-73, -37), (-70, -20), (-77, -12), (-80, -5), (-81, 0)],
 [(-17, 15), (-17, 21), (-10, 31), (-5, 35), (10, 37), (11, 34), (20, 32),
  (32, 31), (35, 28), (34, 27), (39, 21), (43, 12), (51, 11), (51, 2),
  (48, -2), (40, -10), (40, -19), (36, -26), (32, -29), (28, -33),
  (20, -35), (17, -32), (15, -27), (12, -18), (13, -10), (9, 4), (-8, 4),
  (-13, 8), (-17, 12)],
 [(-10, 36), (-9, 43), (-2, 48), (-5, 50), (0, 51), (5, 53), (8, 57),
  (10, 59), (5, 60), (12, 56), (18, 56), (21, 55), (24, 58), (21, 60),
  (25, 60), (30, 60), (30, 65), (35, 68), (45, 68), (55, 69), (70, 72),
  (80, 73), (100, 76), (110, 74), (130, 72), (150, 70), (170, 66),
  (178, 65), (178, 62), (170, 60), (162, 56), (158, 52), (142, 50),
  (140, 45), (135, 43), (130, 42), (127, 40), (122, 38), (120, 32),
  (122, 28), (118, 25), (110, 20), (108, 18), (105, 10), (103, 8),
  (100, 6), (98, 10), (95, 15), (92, 21), (89, 22), (86, 20), (82, 17),
  (80, 13), (77, 8), (75, 12), (72, 20), (68, 23), (66, 25), (61, 25),
  (58, 26), (56, 27), (52, 28), (50, 30), (48, 30), (44, 29), (40, 31),
  (36, 36), (33, 36), (30, 36), (27, 37), (23, 36), (19, 40), (15, 44),
  (12, 44), (8, 44), (3, 43), (0, 40), (-2, 37), (-6, 36), (-9, 38)],
 [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51)],
 [(130, 31), (132, 33), (135, 34), (138, 35), (140, 37), (141, 40),
  (142, 42), (144, 44), (141, 45), (140, 42), (137, 37), (133, 35),
  (130, 33)],
 [(95, 5), (98, 3), (100, 0), (103, -2), (106, -6), (110, -7), (114, -8),
  (118, -9), (120, -10), (119, -5), (117, 0), (113, 2), (110, 1),
  (106, 2), (104, 1), (101, 4)],
 [(131, -1), (136, -2), (141, -3), (146, -6), (150, -9), (147, -9),
  (143, -8), (138, -8), (134, -4)],
 [(113, -22), (114, -30), (115, -35), (120, -34), (129, -32), (132, -32),
  (135, -35), (138, -35), (140, -38), (145, -38), (150, -37), (153, -32),
  (153, -27), (150, -23), (146, -19), (142, -11), (142, -15), (136, -12),
  (132, -12), (130, -13), (126, -14), (122, -17), (118, -20)],
 [(167, -45), (170, -42), (173, -40), (175, -38), (177, -38), (174, -41),
  (172, -43), (168, -46)],
]

# spine first (visible in the gutter between the two columns and on the
# seam between the middle panels), then panels over it
d.line([512, 188, 512, 566], fill=RED, width=4)
d.line([512, 188, 512, 566], fill=(255, 255, 255), width=1)

panel(8, 188, 490, 142, PANELS[1], hero=True)    # 2 Ukraine, 00:00
panel(526, 188, 490, 142, PANELS[0], hero=True)  # 1 COP31, 03:00/06:00
panel(8, 336, 490, 116, PANELS[2])              # 3 Bahrain
panel(526, 336, 490, 116, PANELS[3])            # 4 Sparta II
_cw = 247
for i, p in enumerate([PANELS[4], PANELS[5], PANELS[6], PANELS[7]]):
    panel(8 + i * (_cw + 6), 458, _cw, 108, p)
_dw = 196
for i, p in enumerate([PANELS[8], PANELS[9], PANELS[10], PANELS[11], PANELS[12]]):
    panel(8 + i * (_dw + 6), 572, _dw, 84, p, compact=True)

# spine time nodes (pills sitting on the spine, chronological top to bottom)
for ny, label in [(205, "00:00"), (265, "03:00"), (478, "04:00"),
                  (512, "06:00"), (546, "13:00")]:
    nf = F(SANS_B, 9)
    nw = d.textlength(label, font=nf) + 10
    d.rounded_rectangle([512 - nw / 2, ny - 8, 512 + nw / 2, ny + 8],
                        radius=8, fill=(255, 255, 255), outline=RED, width=2)
    d.text((512 - d.textlength(label, font=nf) / 2, ny - 6), label,
           font=nf, fill=RED_D)

# ---------------------------------------------------------------- UTC strip
d.rectangle([8, 662, 1016, 684], fill=NAVY)
_utc = ("THE DAY IN UTC  •  00:00 drones over Ukraine  •  03:00 COP31 "
        "objections close  •  04:00 Verstappen wins Las Vegas  •  06:00 "
        "COP31 approval  •  13:00 HK turnout 89.81%  •  16:30 Liverpool v "
        "Man Utd  •  17:00 ATP final")
_uf = 9
while d.textlength(_utc, font=F(SANS_B, _uf)) > 1000 and _uf > 7:
    _uf -= 1
d.text((14, 668), _utc, font=F(SANS_B, _uf), fill=(255, 255, 255))

# ---------------------------------------------------------------- map + ALSO
d.text((8, 690), "WHERE IT HAPPENED — 13 STORIES, PINNED",
       font=F(SANS_B, 11), fill=INK)
d.text((506, 690), "ALSO ON SUNDAY 22 NOVEMBER — 25 MORE STORIES (14–38)",
       font=F(SANS_B, 11), fill=INK)
d.rectangle([8, 704, 498, 872], fill=(238, 230, 208), outline=INK, width=1)
MX0, MY0, MW, MH = 8, 704, 490, 168
def project(lat, lon):
    return (MX0 + (lon + 170) / 360 * MW, MY0 + (75 - lat) / 131 * MH)

for gy in range(MY0 + 4, MY0 + MH - 2, 6):
    for gx in range(MX0 + 4, MX0 + MW - 2, 6):
        lon = (gx - MX0) / MW * 360 - 170
        lat = 75 - (gy - MY0) / MH * 131
        if any(point_in_poly(lon, lat, poly) for poly in LAND):
            d.ellipse([gx - 1, gy - 1, gx + 1, gy + 1], fill=DOT)

# (num, lat, lon, dx, dy) — dx/dy are manual nudges so Europe/Middle East
# pins never overlap and never fall in the sea
PINS = [(1, 36.9, 30.7, 14, 12), (2, 50.45, 30.52, -6, -12),
        (3, 26.23, 50.59, 4, 14), (4, 60.0, 24.8, -18, -10),
        (5, 22.3, 114.17, 0, 0), (6, 26.2, 56.35, 20, -4),
        (7, 21.0, 78.0, 0, 0), (8, 36.17, -115.14, 0, 0),
        (9, 31.5, 34.47, -20, 2), (10, 30.5, 47.8, 14, -8),
        (11, 4.9, 6.3, 0, 0), (12, -6.2, 106.35, 0, 0),
        (13, 49.87, 8.65, -12, 0)]
for num, lat, lon, dx, dy in PINS:
    px, py = project(lat, lon)
    px, py = px + dx, py + dy
    d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED,
              outline=(255, 255, 255), width=2)
    nf = F(SANS_B, 9)
    t = str(num)
    d.text((px - d.textlength(t, font=nf) / 2, py - 6), t, font=nf,
           fill=(255, 255, 255))

ALSO = [
 "14. Sudan El-Fasher — 5,000 still missing [MSF]",
 "15. Wembanyama 50 pts, 19 reb — Spurs record [AP]",
 "16. Nvidia — SEC probe, shares -14% [Straits Times]",
 "17. Bolsonaro in ICU, stable [Al Jazeera]",
 "18. Estonia closes Russia border 1 Dec [Reuters]",
 "19. S. Korea finance chief quits [Guardian]",
 "20. China bans US phones as “malicious” [S. Times]",
 "21. Japan–India first live-fire drill [Reuters]",
 "22. Nepal PM in Delhi, first visit [IANS]",
 "23. Marles rejects US AUKUS report [ABC]",
 "24. EU–Indonesia deal, 98.5% tariffs cut [Reuters]",
 "25. Belgium ATC strike, Mon flights off [AFP]",
 "26. France seeks UN action on Myanmar [UN]",
 "27. Chinese bomber turns back near Manila [Reports]",
 "28. Liverpool v Man Utd 16:30 GMT [BBC]",
 "29. Zverev v Alcaraz, ATP final 17:00 [ATP]",
 "30. Saudi coalition downs 3 Houthi missiles [Wires]",
 "31. Australia chase 188, beat England T20 [ABC]",
 "32. Kyiv Oblast — drone hits 5-storey block [K. Ind.]",
 "33. Iran power rationing, 2-hr blackouts [RFE/RL]",
 "34. FBI probes hack of crime database [Wires]",
 "35. Pope Leo lunch for 1,300 poor guests [Vatican]",
 "36. Court: Myanmar committed Rohingya genocide [Guardian]",
 "37. Eisenkot invites Likud to coalition talks [S. Times]",
 "38. Four nations press Israel on Gaza aid [Wires]",
]
af = F(SANS, 9)
for i, item in enumerate(ALSO):
    col = i // 13
    row = i % 13
    ax = 506 + col * 258
    ay = 706 + row * 13
    # shrink only if a line would overflow its column
    f = af
    if d.textlength(item, font=f) > 254:
        f = F(SANS, 8)
    d.text((ax, ay), item, font=f, fill=INK)

# ---------------------------------------------------------------- DATE CHECK
d.rectangle([8, 880, 1016, 968], fill=(255, 244, 238), outline=RED, width=2)
d.text((14, 885), "DATE CHECK — NOT 22 NOVEMBER, SO NOT IN THIS GRID",
       font=F(SANS_B, 10), fill=RED_D)
dc = ("Every story here happened, or was first reported, on Sunday "
      "22 November 2026 in at least one time zone. Tonight's barrage was "
      "186 drones — not Friday's 400. Left out as earlier news: Peru quake "
      "(Fri 20 Nov) · El Chapo Isidro captured (Fri) · missiles landing in "
      "Poland (19 Nov) · Kerch Bridge strikes (earlier this week) · "
      "Shenzhen summit (19 Nov) · Voyager 1 (18 Nov) · GTA VI launch "
      "(19 Nov) · Anthropic IPO (19 Nov). Not yet happened when drawn: "
      "final COP31 approval (06:00 GMT session) · ATP final (17:00 GMT) · "
      "Liverpool v Man Utd (16:30 GMT).")
text_block(14, 902, dc, F(SANS, 10), INK, 992, 13)

d.text((8, 976),
       "Sources: Reuters • AP • AFP • BBC • SCMP • Al Jazeera • UKMTO • ESA • "
       "F1 • ATP  —  HOW WE CHECKED: each story dated to 22 Nov; earlier "
       "news is in DATE CHECK.  •  Agent 4 — TIMELINE EDITION",
       font=F(SANS, 9), fill=GREY)

img.save("entry.png", optimize=True)
print("saved entry.png", img.size)
