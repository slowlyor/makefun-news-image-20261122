#!/usr/bin/env python3
"""Draw one poster image summing up the world news of Sunday 22 November 2026.

Standard library only, no network, deterministic: two runs write
byte-identical PNG bytes to $MAKEFUN_OUTPUT_DIR/entry.png.
"""
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 cells, '#' = on, '.' = off.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ':': ("00000", "01100", "00000", "00000", "00000", "01100", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '+': ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    '=': ("00000", "00000", "01110", "00000", "01110", "00000", "00000"),
    '?': ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    ';': ("00000", "01100", "00000", "00000", "01100", "00100", "01000"),
    '*': ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
}


def text_width(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(cv, x, y, s, color, scale=2):
    """Draw upper-case text; unknown chars render as blank."""
    s = s.upper()
    cx = x
    for ch in s:
        glyph = FONT.get(ch, FONT[' '])
        for r in range(7):
            row = glyph[r]
            for c in range(5):
                if row[c] == '1':
                    cv.rect(cx + c * scale, y + r * scale, scale, scale, color)
        cx += 6 * scale
    return cx


def wrap(text, max_chars):
    """Greedy word wrap into lines of at most max_chars characters."""
    lines, cur = [], ""
    for word in text.split(" "):
        if cur and len(cur) + 1 + len(word) > max_chars:
            lines.append(cur)
            cur = word
        else:
            cur = (cur + " " + word).strip()
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        while True:
            for a in range(thick):
                for b in range(thick):
                    self.set(x + a - thick // 2, y + b - thick // 2, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, color, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill:
                    if d2 <= r * r:
                        self.set(xx, yy, color)
                else:
                    if abs(d2 - r * r) <= r * 2:
                        self.set(xx, yy, color)

    def triangle(self, p1, p2, p3, color):
        (x1, y1), (x2, y2), (x3, y3) = p1, p2, p3
        minx, maxx = min(x1, x2, x3), max(x1, x2, x3)
        miny, maxy = min(y1, y2, y3), max(y1, y2, y3)
        d = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
        if d == 0:
            return
        for yy in range(miny, maxy + 1):
            for xx in range(minx, maxx + 1):
                a = ((y2 - y3) * (xx - x3) + (x3 - x2) * (yy - y3)) / d
                b = ((y3 - y1) * (xx - x3) + (x1 - x3) * (yy - y3)) / d
                c = 1 - a - b
                if a >= 0 and b >= 0 and c >= 0:
                    self.set(xx, yy, color)


# ---------------------------------------------------------------- palette
BG = (13, 27, 46)
HEADER = (19, 42, 71)
PANEL = (22, 40, 63)
PANEL_LINE = (42, 74, 107)
PIC_BG = (13, 27, 46)
WHITE = (245, 247, 250)
SUB = (185, 201, 220)
GOLD = (242, 183, 5)
RED = (229, 72, 77)
ORANGE = (247, 107, 21)
TEAL = (43, 179, 163)
GREEN = (70, 167, 88)
AMBER = (245, 165, 36)
BLUE = (62, 155, 255)
GREY = (150, 163, 180)


# ---------------------------------------------------------------- pictograms
def pic_explosion(cv, x, y, s):
    """Burst over the Gulf: starburst + flame."""
    cx, cy = x + s // 2, y + s // 2
    for k in range(12):
        import math
        ang = k * math.pi / 6
        r1 = s // 6
        r2 = s // 2
        cv.line(cx + int(r1 * math.cos(ang)), cy + int(r1 * math.sin(ang)),
                cx + int(r2 * math.cos(ang)), cy + int(r2 * math.sin(ang)),
                GOLD, 5)
    cv.circle(cx, cy, s // 5, ORANGE)
    cv.circle(cx, cy, s // 8, GOLD)


def pic_missile(cv, x, y, s):
    """Rocket arcing down onto a city skyline."""
    cv.rect(x + 8, y + s - 22, 12, 22, GREY)
    cv.rect(x + 30, y + s - 34, 12, 34, GREY)
    cv.rect(x + 52, y + s - 16, 12, 16, GREY)
    cv.rect(x + 74, y + s - 28, 12, 28, GREY)
    cv.line(x + 20, y + 18, x + 78, y + 58, WHITE, 6)
    cv.triangle((x + 74, y + 54), (x + 86, y + 66), (x + 64, y + 68), RED)
    cv.circle(x + 16, y + 14, 7, ORANGE)
    cv.circle(x + 16, y + 14, 4, GOLD)


def pic_climate(cv, x, y, s):
    """Globe heating up: circle, land blobs, rising thermometer."""
    cx, cy = x + s // 2 - 8, y + s // 2
    cv.circle(cx, cy, s // 2 - 8, TEAL)
    cv.circle(cx - 14, cy - 12, 12, GREEN)
    cv.circle(cx + 12, cy + 8, 10, GREEN)
    cv.circle(cx + 16, cy - 16, 6, GREEN)
    # thermometer at right
    tx = x + s - 22
    cv.rect(tx, y + 18, 10, s - 44, WHITE)
    cv.circle(tx + 5, y + s - 20, 10, RED)
    cv.rect(tx + 2, y + s - 46, 6, 26, RED)


def pic_trade(cv, x, y, s):
    """Two flags shaking hands on a deal: EU blue + Indonesia red/white."""
    fx, fy = x + 8, y + 14
    cv.rect(fx, fy, 40, 26, (0, 51, 153))
    for k in range(8):
        import math
        ang = k * math.pi / 4
        cv.circle(fx + 20 + int(9 * math.cos(ang)), fy + 13 + int(9 * math.sin(ang)),
                  2, GOLD)
    fx2 = x + s - 48
    cv.rect(fx2, fy, 40, 13, (213, 0, 50))
    cv.rect(fx2, fy + 13, 40, 13, WHITE)
    cv.line(x + 28, fy + 26, x + 28, y + s - 18, GREY, 3)
    cv.line(fx2 + 20, fy + 26, fx2 + 20, y + s - 18, GREY, 3)
    cv.line(x + 22, y + s - 34, x + s - 22, y + s - 34, GOLD, 4)
    cv.line(x + 22, y + s - 34, x + 34, y + s - 22, GOLD, 4)
    cv.line(x + s - 22, y + s - 34, x + s - 34, y + s - 22, GOLD, 4)


def pic_quake(cv, x, y, s):
    """Mountain ridge with a seismic zigzag."""
    base = y + s - 20
    cv.triangle((x + 6, base), (x + 40, y + 26), (x + 74, base), GREY)
    cv.triangle((x + 34, base), (x + 62, y + 44), (x + 92, base), (110, 125, 145))
    cv.triangle((x + 34, y + 32), (x + 40, y + 26), (x + 46, y + 32), WHITE)
    pts = [(x + 6, y + 16), (x + 22, y + 16), (x + 30, y + 6), (x + 38, y + 26),
           (x + 46, y + 10), (x + 54, y + 16), (x + 70, y + 16), (x + 78, y + 6),
           (x + 86, y + 26), (x + 94, y + 12)]
    for a, b in zip(pts, pts[1:]):
        cv.line(a[0], a[1], b[0], b[1], RED, 3)


def pic_markets(cv, x, y, s):
    """Falling chart: axes, descending line, red arrow."""
    ox, oy = x + 12, y + s - 16
    cv.line(ox, y + 12, ox, oy, WHITE, 3)
    cv.line(ox, oy, x + s - 8, oy, WHITE, 3)
    pts = [(ox + 6, y + 26), (ox + 26, y + 40), (ox + 46, y + 34),
           (ox + 62, y + 58), (ox + 82, y + 74)]
    for a, b in zip(pts, pts[1:]):
        cv.line(a[0], a[1], b[0], b[1], RED, 4)
    ex, ey = pts[-1]
    cv.triangle((ex - 2, ey - 14), (ex + 10, ey - 2), (ex - 12, ey - 2), RED)


# ---------------------------------------------------------------- stories
STORIES = [
    ("GULF ON EDGE", RED, pic_explosion, "MIDDLE EAST",
     "Iran strikes US bases in Bahrain and Kuwait; tankers hit off Oman."),
    ("LVIV UNDER FIRE", ORANGE, pic_missile, "EUROPE",
     "Russian missile hits Lviv: 2 killed, 10 hurt; war spills into Poland."),
    ("CLIMATE STALLS", TEAL, pic_climate, "CLIMATE",
     "COP31 talks in Turkey in overtime as a fossil-fuel fight blocks a deal."),
    ("EU-INDONESIA DEAL", GREEN, pic_trade, "TRADE",
     "After 10 years of talks, EU and Indonesia sign a pact; 98.5% of tariffs to go."),
    ("PERU QUAKE", AMBER, pic_quake, "LATIN AMERICA",
     "Magnitude 6.9 earthquake shakes Peru's Andes; no casualties reported at first."),
    ("TECH STOCKS FALL", BLUE, pic_markets, "MARKETS",
     "Wall Street tech sell-off deepens; shares slide across Asia and Europe."),
]


def draw_panel(cv, x, y, w, h, headline, accent, pic, tag, body):
    cv.rect(x, y, w, h, PANEL)
    cv.rect(x, y, w, 2, PANEL_LINE)
    cv.rect(x, y + h - 2, w, 2, PANEL_LINE)
    cv.rect(x, y, 2, h, PANEL_LINE)
    cv.rect(x + w - 2, y, 2, h, PANEL_LINE)
    cv.rect(x, y, w, 6, accent)
    # pictogram box
    px, py, ps = x + 16, y + 26, 116
    cv.rect(px, py, ps, 150, PIC_BG)
    cv.rect(px, py, ps, 2, PANEL_LINE)
    cv.rect(px, py + 148, ps, 2, PANEL_LINE)
    cv.rect(px, py, 2, 150, PANEL_LINE)
    cv.rect(px + ps - 2, py, 2, 150, PANEL_LINE)
    pic(cv, px + 8, py + 22, 100)
    # headline + body
    tx = x + 148
    draw_text(cv, tx, y + 34, headline, WHITE, 3)
    lines = wrap(body, 26)
    ly = y + 76
    for ln in lines[:5]:
        draw_text(cv, tx, ly, ln, SUB, 2)
        ly += 20
    # tag strip at the bottom
    draw_text(cv, x + 16, y + h - 30, tag, accent, 2)


def build():
    cv = Canvas(W, H, BG)
    # header
    cv.rect(0, 0, W, 158, HEADER)
    title = "WORLD NEWS"
    draw_text(cv, (W - text_width(title, 6)) // 2, 24, title, WHITE, 6)
    date = "SUNDAY, 22 NOVEMBER 2026"
    draw_text(cv, (W - text_width(date, 3)) // 2, 92, date, GOLD, 3)
    cv.rect(0, 156, W, 4, GOLD)
    # 2 x 3 grid of stories
    gx, gy = 24, 176
    pw, ph = 484, 262
    for i, (headline, accent, pic, tag, body) in enumerate(STORIES):
        px = gx + (i % 2) * (pw + 16)
        py = gy + (i // 2) * (ph + 16)
        draw_panel(cv, px, py, pw, ph, headline, accent, pic, tag, body)
    # footer
    foot = "THE WORLD IN ONE PICTURE"
    draw_text(cv, (W - text_width(foot, 2)) // 2, 998, foot, SUB, 2)
    return cv


def write_png(cv, path):
    raw = bytearray()
    for yy in range(cv.h):
        raw.append(0)
        raw += cv.px[yy * cv.w * 3:(yy + 1) * cv.w * 3]

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    cv = build()
    write_png(cv, os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
