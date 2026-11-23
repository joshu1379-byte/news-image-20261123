#!/usr/bin/env python3
"""Sum up Monday 23 November 2026's world news in one image.

Entry for make.fun bounty news-image-20261123 (program/v1).

The program draws a one-page newspaper front page -- masthead, one lead
story, six regional story cards and an "also today" strip -- with nothing
but the Python 3.13 standard library, and writes it to
/output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png outside the grader).

It is fully deterministic: the news is fixed data in this file, the
drawing is pure arithmetic, and the PNG encoder emits identical bytes on
every run. No network, no clock, no randomness, no files read.

News covered is what had been reported by late morning of 23 November
2026 (UTC) (refreshed ~11:00 UTC; COP31 collapse and the Shenzhen
summit added); the day was still in progress when this entry was built,
so a later refresh with the full day's news is possible before the
deadline.

Layout (1024 x 1024):
  masthead  : THE WORLD IN ONE IMAGE -- MONDAY 23 NOVEMBER 2026
  lead      : Ukraine sinks the Russian corvette Merkury off Libya
  cards 2x3 : Dymer strike, Democrats' 258 House seats, Nikkei slide,
              Iran's MQ-9 claim, Indonesia's chemical ship seizure,
              Riemann Hypothesis proof claim
  also strip: penny ends, South Korea's $1T exports, COP31 collapse,
              Trump calls Putin "my friend" after Shenzhen
  footer    : sources named

Run:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import struct
import sys
import zlib

# ---------------------------------------------------------------- font --
# 5x7 pixel font, uppercase + digits + punctuation. Each glyph is 7 rows
# of 5 cells ('#' = ink). Text is rendered in capitals, newspaper style.
FONT = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    '0': (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    '-': (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    '(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    '/': ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    '&': (".###.", "#...#", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    '%': ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    '+': (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    '=': (".....", ".....", ".###.", ".....", ".###.", ".....", "....."),
    '$': ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    '*': (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    '#': (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    '_': (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    '<': ("...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."),
    '>': (".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."),
    '[': (".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."),
    ']': (".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."),
}
# Punctuation rendered as a plain hyphen (en/em dash fall back here).
FONT['\u2013'] = FONT['-']
FONT['\u2014'] = FONT['-']
FONT['\u2019'] = FONT["'"]
FONT['\u201c'] = FONT['"']
FONT['\u201d'] = FONT['"']
FONT['\u00b7'] = (".....", ".....", ".##..", ".##..", ".....", ".....", ".....")
FONT['\u2022'] = (".....", ".....", ".###.", ".###.", ".###.", ".....", ".....")
FONT['\u00d7'] = (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#")
FONT['\u00a2'] = FONT['C']

CHAR_W = 6   # 5 px glyph + 1 px gap
CHAR_H = 9   # 7 px glyph + 2 px leading


def text_width(text, scale):
    """Pixel width of `text` at `scale` (no wrapping)."""
    return len(text) * CHAR_W * scale - scale


def draw_text(cv, x, y, text, scale, color):
    """Draw upper-case text left-aligned at (x, y). Returns width used."""
    text = text.upper()
    cx = x
    for ch in text:
        glyph = FONT.get(ch)
        if glyph is None:
            cx += CHAR_W * scale
            continue
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == '#':
                    cv.fill_rect(cx + col * scale, y + row * scale,
                                 scale, scale, color)
        cx += CHAR_W * scale
    return cx - x


def draw_text_centered(cv, cx, y, text, scale, color):
    draw_text(cv, cx - text_width(text, scale) // 2, y, text, scale, color)


def wrap_text(text, scale, max_width):
    """Greedy word wrap; returns list of lines fitting max_width px."""
    words = text.upper().split(' ')
    lines, cur = [], ''
    for w in words:
        trial = (cur + ' ' + w).strip()
        if text_width(trial, scale) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_para(cv, x, y, text, scale, color, max_width, line_h=None):
    """Draw a wrapped paragraph; returns the y just below the last line."""
    lh = line_h if line_h is not None else CHAR_H * scale
    for line in wrap_text(text, scale, max_width):
        draw_text(cv, x, y, line, scale, color)
        y += lh
    return y


# -------------------------------------------------------------- canvas --
class Canvas:
    """A plain RGB raster with rectangle/circle/line/text primitives."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg * (w * h))

    def _off(self, x, y):
        return (y * self.w + x) * 3

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            o = self._off(x, y)
            self.px[o:o + 3] = color

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = color * (x1 - x0)
        for yy in range(y0, y1):
            o = self._off(x0, yy)
            self.px[o:o + len(row)] = row

    def rect(self, x, y, w, h, color, t=1):
        self.fill_rect(x, y, w, t, color)
        self.fill_rect(x, y + h - t, w, t, color)
        self.fill_rect(x, y, t, h, color)
        self.fill_rect(x + w - t, y, t, h, color)

    def line(self, x0, y0, x1, y1, color, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.fill_rect(x - t // 2, y - t // 2, t, t, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
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
                    if abs(d2 - r * r) <= r:
                        self.set(xx, yy, color)

    def triangle(self, pts, color):
        (x0, y0), (x1, y1), (x2, y2) = pts
        min_y, max_y = min(y0, y1, y2), max(y0, y1, y2)
        for yy in range(min_y, max_y + 1):
            xs = []
            for (ax, ay), (bx, by) in (((x0, y0), (x1, y1)),
                                       ((x1, y1), (x2, y2)),
                                       ((x2, y2), (x0, y0))):
                if ay == by:
                    continue
                if min(ay, by) <= yy < max(ay, by) or yy == max_y:
                    t = (yy - ay) / (by - ay)
                    xs.append(ax + t * (bx - ax))
            if len(xs) >= 2:
                self.fill_rect(int(min(xs)), yy, int(max(xs)) - int(min(xs)) + 1,
                               1, color)


# ------------------------------------------------------------ png out ---
def write_png(cv):
    """Encode the canvas as a deterministic PNG (filter 0, zlib level 9)."""
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw.extend(cv.px[y * stride:(y + 1) * stride])
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack('>I', len(data)) + tag + data
        out += struct.pack('>I', zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr)
            + chunk(b'IDAT', comp) + chunk(b'IEND', b''))


# -------------------------------------------------------------- palette --
PAPER = bytes((247, 243, 234))
INK = bytes((20, 20, 20))
WHITE = bytes((255, 255, 255))
NAVY = bytes((16, 35, 63))
NAVY2 = bytes((28, 56, 92))
GOLD = bytes((201, 162, 39))
RED = bytes((178, 34, 34))
CARD_BG = bytes((255, 255, 255))
CARD_LINE = bytes((205, 198, 184))
MUTED = bytes((90, 86, 76))
LEAD_BG = bytes((255, 248, 230))
STRIP_BG = bytes((232, 228, 218))

# --------------------------------------------------------------- icons --
# Small pictograms drawn from primitives, one per story, inside a
# coloured square. They are decoration; the words carry the facts.
# Every icon takes a square of side s and scales its drawing to it.

def _sc(s, v):
    return int(round(v * s / 64.0))


def icon_globe(cv, x, y, s, fg, bg):
    cv.fill_rect(x, y, s, s, bg)
    cx, cy, r = x + s // 2, y + s // 2, s // 2 - 4
    cv.circle(cx, cy, r, fg, fill=False)
    cv.line(cx - r, cy, cx + r, cy, fg, 2)
    cv.line(cx, cy - r, cx, cy + r, fg, 2)
    cv.circle(cx - r // 2, cy - r // 3, r // 3, fg)
    cv.circle(cx + r // 2, cy + r // 3, r // 4, fg)


def icon_flame(cv, x, y, s, fg, bg):
    cv.fill_rect(x, y, s, s, bg)
    cx, cy = x + s // 2, y + s // 2
    u = lambda v: _sc(s, v)
    cv.triangle([(cx - u(20), cy + u(20)), (cx + u(20), cy + u(20)),
                 (cx, cy - u(24))], fg)
    cv.circle(cx, cy + u(10), u(14), fg)
    cv.circle(cx, cy + u(14), u(8), bg)
    cv.circle(cx, cy + u(16), u(4), fg)


def icon_missile(cv, x, y, s, fg, bg):
    cv.fill_rect(x, y, s, s, bg)
    cx, cy = x + s // 2, y + s // 2
    u = lambda v: _sc(s, v)
    cv.line(cx - u(20), cy + u(14), cx + u(16), cy - u(14), fg, max(2, u(6)))
    cv.triangle([(cx + u(14), cy - u(16)), (cx + u(26), cy - u(20)),
                 (cx + u(20), cy - u(6))], fg)
    cv.line(cx - u(16), cy + u(8), cx - u(26), cy + u(18), fg, max(2, u(4)))
    cv.line(cx - u(12), cy + u(14), cx - u(22), cy + u(24), fg, max(2, u(4)))
    cv.circle(cx - u(24), cy + u(20), max(2, u(3)), fg)
    cv.circle(cx - u(28), cy + u(24), max(1, u(2)), fg)


def icon_ship(cv, x, y, s, fg, bg):
    cv.fill_rect(x, y, s, s, bg)
    cx, cy = x + s // 2, y + s // 2
    u = lambda v: _sc(s, v)
    cv.fill_rect(cx - u(4), cy - u(18), u(4), u(24), fg)
    cv.fill_rect(cx, cy - u(18), u(16), u(8), fg)
    cv.fill_rect(cx - u(22), cy + u(4), u(44), u(10), fg)
    cv.triangle([(cx - u(22), cy + u(14)), (cx + u(22), cy + u(14)),
                 (cx, cy + u(24))], fg)
    cv.line(cx - u(26), cy + u(28), cx + u(26), cy + u(28), fg, 2)


def icon_gavel(cv, x, y, s, fg, bg):
    cv.fill_rect(x, y, s, s, bg)
    cx, cy = x + s // 2, y + s // 2
    u = lambda v: _sc(s, v)
    cv.line(cx - u(20), cy - u(14), cx + u(16), cy - u(14), fg, max(3, u(9)))
    cv.line(cx - u(2), cy - u(10), cx - u(18), cy + u(20), fg, max(2, u(5)))
    cv.line(cx - u(24), cy + u(24), cx + u(20), cy + u(24), fg, max(2, u(4)))


def icon_ballot(cv, x, y, s, fg, bg):
    cv.fill_rect(x, y, s, s, bg)
    cx, cy = x + s // 2, y + s // 2
    u = lambda v: _sc(s, v)
    cv.rect(cx - u(20), cy - u(2), u(40), u(24), fg, max(2, u(3)))
    cv.fill_rect(cx - u(14), cy - u(8), u(28), u(4), fg)
    cv.line(cx - u(10), cy - u(16), cx - u(2), cy - u(6), fg, max(2, u(4)))
    cv.line(cx - u(2), cy - u(6), cx + u(14), cy - u(22), fg, max(2, u(4)))


def icon_factory(cv, x, y, s, fg, bg):
    cv.fill_rect(x, y, s, s, bg)
    cx, cy = x + s // 2, y + s // 2
    u = lambda v: _sc(s, v)
    cv.fill_rect(cx - u(24), cy - u(2), u(48), u(24), fg)
    cv.triangle([(cx - u(24), cy - u(2)), (cx - u(12), cy - u(14)),
                 (cx, cy - u(2))], fg)
    cv.triangle([(cx, cy - u(2)), (cx + u(12), cy - u(14)),
                 (cx + u(24), cy - u(2))], fg)
    cv.fill_rect(cx + u(14), cy - u(22), u(6), u(22), fg)
    cv.circle(cx + u(17), cy - u(26), max(2, u(4)), fg)
    cv.circle(cx + u(22), cy - u(30), max(2, u(3)), fg)


def icon_chart_down(cv, x, y, s, fg, bg):
    cv.fill_rect(x, y, s, s, bg)
    cx, cy = x + s // 2, y + s // 2
    u = lambda v: _sc(s, v)
    cv.line(cx - u(22), cy + u(18), cx - u(22), cy - u(20), fg, max(2, u(3)))
    cv.line(cx - u(22), cy + u(18), cx + u(22), cy + u(18), fg, max(2, u(3)))
    cv.line(cx - u(18), cy - u(10), cx - u(6), cy + u(2), fg, max(2, u(4)))
    cv.line(cx - u(6), cy + u(2), cx + u(6), cy - u(6), fg, max(2, u(4)))
    cv.line(cx + u(6), cy - u(6), cx + u(20), cy + u(12), fg, max(2, u(4)))
    cv.triangle([(cx + u(20), cy + u(12)), (cx + u(12), cy + u(10)),
                 (cx + u(20), cy + u(4))], fg)


def icon_warning(cv, x, y, s, fg, bg):
    cv.fill_rect(x, y, s, s, bg)
    cx, cy = x + s // 2, y + s // 2
    u = lambda v: _sc(s, v)
    cv.triangle([(cx, cy - u(20)), (cx - u(22), cy + u(16)),
                 (cx + u(22), cy + u(16))], fg)
    cv.fill_rect(cx - u(2), cy - u(10), u(4), u(14), bg)
    cv.fill_rect(cx - u(2), cy + u(8), u(4), u(4), bg)


def icon_plane(cv, x, y, s, fg, bg):
    cv.fill_rect(x, y, s, s, bg)
    cx, cy = x + s // 2, y + s // 2
    u = lambda v: _sc(s, v)
    cv.triangle([(cx - u(22), cy + u(4)), (cx + u(24), cy - u(8)),
                 (cx + u(10), cy + u(8))], fg)
    cv.line(cx - u(6), cy - u(2), cx - u(16), cy - u(16), fg, max(2, u(5)))
    cv.line(cx + u(2), cy + u(2), cx - u(6), cy + u(16), fg, max(2, u(5)))


def icon_doc(cv, x, y, s, fg, bg):
    cv.fill_rect(x, y, s, s, bg)
    cx, cy = x + s // 2, y + s // 2
    u = lambda v: _sc(s, v)
    cv.rect(cx - u(14), cy - u(20), u(28), u(40), fg, max(2, u(3)))
    cv.line(cx - u(8), cy - u(10), cx + u(8), cy - u(10), fg, max(2, u(3)))
    cv.line(cx - u(8), cy - u(2), cx + u(8), cy - u(2), fg, max(2, u(3)))
    cv.line(cx - u(8), cy + u(6), cx + u(2), cy + u(6), fg, max(2, u(3)))
    cv.circle(cx + u(10), cy + u(14), max(2, u(6)), fg)


ICONS = {
    'globe': icon_globe, 'flame': icon_flame, 'missile': icon_missile,
    'ship': icon_ship, 'gavel': icon_gavel, 'ballot': icon_ballot,
    'factory': icon_factory, 'chart': icon_chart_down,
    'warning': icon_warning, 'plane': icon_plane, 'doc': icon_doc,
}

# Region accent colours (R, G, B), keyed by the card tag.
REGION_COLORS = {
    'WAR': (142, 43, 43),
    'EUROPE': (31, 78, 121),
    'AMERICAS': (122, 90, 18),
    'MARKETS': (15, 118, 110),
    'MIDDLE EAST': (142, 43, 43),
    'ASIA': (46, 107, 52),
    'SCIENCE': (91, 45, 142),
}

# ------------------------------------------------------------- the news --
# What had been reported by late morning of Monday 23 November 2026
# (UTC) (refreshed ~11:00 UTC; COP31 and Shenzhen added), from AP /
# BBC / France 24 and wire reporting. Claims are attributed ("Iran
# claims", "claim a proof") where only one side has said so. The day
# was still in progress when this entry was built.

LEAD = {
    'tag': 'WAR - BENGHAZI, LIBYA',
    'icon': 'globe',
    'headline': 'UKRAINE SINKS RUSSIAN WARSHIP',
    'deck': ('Zelenskyy confirms a Ukrainian naval drone sank the '
             'corvette Merkury at Benghazi; Kyiv says it also hit the '
             'cargo ship MV Angara.'),
}

CARDS = [
    {
        'tag': 'EUROPE',
        'icon': 'missile',
        'headline': 'STRIKE KILLS 10 IN DYMER',
        'deck': ('A Russian strike on Dymer, north of Kyiv, kills at '
                 'least 10; a boy of 7 is pulled alive from the rubble.'),
    },
    {
        'tag': 'AMERICAS',
        'icon': 'ballot',
        'headline': 'DEMOCRATS WIN 258 HOUSE SEATS',
        'deck': ('A North Carolina recount gives Democrats their '
                 'largest House majority since 1992.'),
    },
    {
        'tag': 'MARKETS',
        'icon': 'chart',
        'headline': 'NIKKEI FALLS 5% AS AI SELLS OFF',
        'deck': ("Japan's Nikkei drops 5.06% as the AI sell-off spreads "
                 'across Asia; Hong Kong hits a 19-month low.'),
    },
    {
        'tag': 'MIDDLE EAST',
        'icon': 'plane',
        'headline': 'IRAN CLAIMS US DRONE DOWNED',
        'deck': ('Tehran claims it shot down a US MQ-9A Reaper over the '
                 'Strait of Hormuz, its 58th such claim.'),
    },
    {
        'tag': 'ASIA',
        'icon': 'ship',
        'headline': 'INDONESIA SEIZES CHEMICAL SHIP',
        'deck': ('A ship from China to Bangladesh is seized carrying '
                 '405 tonnes of sodium perchlorate, a rocket chemical.'),
    },
    {
        'tag': 'SCIENCE',
        'icon': 'doc',
        'headline': 'MATHS: RIEMANN PROOF CLAIMED',
        'deck': ('Levent Alpoge and Claude claim a proof of the Riemann '
                 'Hypothesis; the Lean community confirms it.'),
    },
]

ALSO = [
    ('MONEY', 'Trump signs the Common Cents Act, ending the penny after '
              '232 years.'),
    ('KOREA', "South Korea's annual exports top $1 trillion for the "
              'first time.'),
    ('CLIMATE', 'COP31 climate talks collapse in Antalya over fossil '
                'fuels.'),
    ('AMERICAS', "Trump calls Putin 'my friend' after a Shenzhen "
                 'summit.'),
]

# -------------------------------------------------------------- layout --
W, H = 1024, 1024
MARGIN = 28


def draw_masthead(cv):
    cv.fill_rect(0, 0, W, 100, NAVY)
    cv.fill_rect(0, 100, W, 4, GOLD)
    draw_text_centered(cv, W // 2, 10, 'THE WORLD IN ONE IMAGE', 2,
                       bytes((201, 162, 39)))
    draw_text_centered(cv, W // 2, 32, 'MONDAY 23 NOVEMBER 2026', 4, WHITE)
    draw_text_centered(cv, W // 2, 74, 'THE DAY\u2019S WORLD NEWS, IN ONE PAGE',
                       2, bytes((180, 195, 215)))


def draw_lead(cv, y):
    h = 180
    cv.fill_rect(MARGIN, y, W - 2 * MARGIN, h, LEAD_BG)
    cv.rect(MARGIN, y, W - 2 * MARGIN, h, CARD_LINE, 2)
    tag, icon = LEAD['tag'], LEAD['icon']
    color = bytes(REGION_COLORS['WAR'])
    # Tag chip.
    tw = text_width(tag, 2) + 20
    cv.fill_rect(MARGIN + 16, y + 14, tw, 30, color)
    draw_text(cv, MARGIN + 26, y + 20, tag, 2, WHITE)
    # Icon panel on the right.
    ICONS[icon](cv, W - MARGIN - 16 - 150, y + 15, 150, color, LEAD_BG)
    # Headline + deck on the left.
    tx = MARGIN + 16
    tw_max = W - 2 * MARGIN - 32 - 150 - 24
    yy = draw_para(cv, tx, y + 56, LEAD['headline'], 4, INK, tw_max,
                   line_h=40)
    draw_para(cv, tx, yy + 8, LEAD['deck'], 2, MUTED, tw_max, line_h=24)
    return y + h


def draw_cards(cv, y):
    cols, rows = 3, 2
    gap = 14
    cw = (W - 2 * MARGIN - gap * (cols - 1)) // cols
    ch = 236
    for i, card in enumerate(CARDS):
        cx = MARGIN + (i % cols) * (cw + gap)
        cy = y + (i // cols) * (ch + gap)
        color = bytes(REGION_COLORS[card['tag']])
        cv.fill_rect(cx, cy, cw, ch, CARD_BG)
        cv.rect(cx, cy, cw, ch, CARD_LINE, 2)
        # Tag chip (short region tag, never under the icon).
        tag = card['tag']
        tw = text_width(tag, 2) + 16
        cv.fill_rect(cx + 12, cy + 12, tw, 26, color)
        draw_text(cv, cx + 20, cy + 17, tag, 2, WHITE)
        # Icon, top right.
        ICONS[card['icon']](cv, cx + cw - 12 - 64, cy + 12, 64, color,
                            CARD_BG)
        # Headline (max 2 lines) then deck (max 4 lines).
        hy = draw_para(cv, cx + 12, cy + 84, card['headline'], 3, INK,
                       cw - 24, line_h=30)
        draw_para(cv, cx + 12, hy + 6, card['deck'], 2, MUTED, cw - 24,
                  line_h=21)
    return y + rows * ch + (rows - 1) * gap


def draw_also(cv, y):
    h = 168
    cv.fill_rect(MARGIN, y, W - 2 * MARGIN, h, STRIP_BG)
    cv.rect(MARGIN, y, W - 2 * MARGIN, h, CARD_LINE, 2)
    draw_text(cv, MARGIN + 16, y + 10, 'ALSO TODAY', 2, INK)
    cv.fill_rect(MARGIN + 16, y + 34, W - 2 * MARGIN - 32, 2, GOLD)
    cols = 2
    cw = (W - 2 * MARGIN - 32 - 16) // cols
    for i, (tag, text) in enumerate(ALSO):
        cx = MARGIN + 16 + (i % cols) * (cw + 16)
        cy = y + 46 + (i // cols) * 62
        draw_text(cv, cx, cy, tag + ':', 2, bytes((91, 45, 142)))
        draw_para(cv, cx, cy + 18, text, 2, INK, cw - 8, line_h=20)
    return y + h


def draw_footer(cv, y):
    draw_text_centered(
        cv, W // 2, y,
        'ONE DAY. ONE IMAGE. - REPORTED 23 NOV 2026: AP, BBC, FRANCE 24',
        2, MUTED)


def build_image():
    cv = Canvas(W, H, PAPER)
    draw_masthead(cv)
    y = draw_lead(cv, 118)
    y = draw_cards(cv, y + 14)
    y = draw_also(cv, y + 14)
    draw_footer(cv, y + 12)
    return cv


def main():
    out_dir = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    os.makedirs(out_dir, exist_ok=True)
    data = write_png(build_image())
    path = os.path.join(out_dir, 'entry.png')
    with open(path, 'wb') as f:
        f.write(data)
    sys.stderr.write('wrote %s (%d bytes)\n' % (path, len(data)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
