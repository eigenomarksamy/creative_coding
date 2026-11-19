import math
import random
import cairo
from seven_levels_kit import background, glow, luminous, mix, polyline, vignette

# information.3 encoding: the Hamming(7,4) code. the word "encoding" is split
# into 4-bit symbols, and each becomes a 7-bit codeword: data bits at
# positions 3, 5, 6 and 7, parity bits at 1, 2 and 4, where the parity bit
# at position c makes even the positions whose binary form contains c. one
# received bit is flipped. the checks it breaks spell its position in binary
# (the syndrome), and the three circles below show the same codeword as the
# code's Venn diagram, with the two failing circles meeting at the bad bit.

WIDTH, HEIGHT = 1600, 2000
SEED = 403
random.seed(SEED)

surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

VIOLET = (0.60, 0.36, 1.00)
LILAC = (0.82, 0.72, 1.00)
DEEP_VIOLET = (0.26, 0.10, 0.52)
WHITE = (0.97, 0.95, 1.00)

# -------------------------
# The code
# -------------------------
MESSAGE = b"encoding"
CHECKS = (1, 2, 4)
DATA_POSITIONS = (3, 5, 6, 7)


def encode(nibble):
    """Bits at positions 1..7 (index 0 is position 1)."""
    word = [0] * 8
    for k, position in enumerate(DATA_POSITIONS):
        word[position] = (nibble >> (3 - k)) & 1
    for c in CHECKS:
        word[c] = sum(word[p] for p in range(1, 8) if p & c and p != c) % 2
    return word[1:]


def syndrome(word):
    return sum(c for c in CHECKS if sum(word[p - 1] for p in range(1, 8) if p & c) % 2)


nibbles = [n for byte in MESSAGE for n in (byte >> 4, byte & 15)]
sent = [encode(n) for n in nibbles]
assert all(syndrome(w) == 0 for w in sent)

received = [list(w) for w in sent]
bad_column = random.randrange(4, 12)
bad_position = random.choice((3, 5, 6))     # each breaks exactly two checks
received[bad_column][bad_position - 1] ^= 1
assert syndrome(received[bad_column]) == bad_position
failing = [c for c in CHECKS if bad_position & c]

# -------------------------
# Layout
# -------------------------
COLS = len(nibbles)
GRID_X0, GRID_X1 = 300, 1440
PITCH = (GRID_X1 - GRID_X0) / COLS
CELL = 44
ROW = 66
GRID_Y0 = 600                       # centre of position 1
SOURCE_Y0 = 230                     # centre of a nibble's first bit
SOURCE_ROW = 30
SOURCE_CELL = 18
RAIL_X = (165, 200, 235)            # the parity-check matrix, one rail per check


def column_x(i):
    # a byte's two nibbles sit closer together than the bytes do
    return GRID_X0 + PITCH * (i + 0.5) + (6 if i % 2 == 0 else -6)


def row_y(position):
    return GRID_Y0 + (position - 1) * ROW


def square(x, y, size):
    h = size / 2
    return [(x - h, y - h), (x + h, y - h), (x + h, y + h), (x - h, y + h), (x - h, y - h)]


def circle(x, y, r, steps=120):
    return [(x + r * math.cos(2 * math.pi * s / steps), y + r * math.sin(2 * math.pi * s / steps)) for s in range(steps + 1)]


def bit(x, y, size, on, color, strength=1.0):
    if on:
        glow(ctx, x, y, size * 1.3, color, 0.30 * strength)
        ctx.set_source_rgba(*color, 0.55 * strength)
        ctx.rectangle(x - size / 2, y - size / 2, size, size)
        ctx.fill()
        polyline(ctx, [square(x, y, size)], mix(color, WHITE, 0.5), 0.8 * strength, 1.2)
    else:
        polyline(ctx, [square(x, y, size)], color, 0.40 * strength, 1.2)


background(ctx, WIDTH, HEIGHT, VIOLET, cy=HEIGHT * 0.45)
ctx.set_operator(cairo.OPERATOR_ADD)
glow(ctx, (GRID_X0 + GRID_X1) / 2, row_y(4), 760, DEEP_VIOLET, 0.30)

# -------------------------
# Symbols: each 4-bit nibble of the message, a byte to each pair of columns
# -------------------------
for i, n in enumerate(nibbles):
    x = column_x(i)
    for k in range(4):
        bit(x, SOURCE_Y0 + k * SOURCE_ROW, SOURCE_CELL, (n >> (3 - k)) & 1, LILAC, 0.8)

# routes: data bit k of the nibble drops to codeword position DATA_POSITIONS[k]
for i in range(COLS):
    x = column_x(i)
    routes = []
    for k, position in enumerate(DATA_POSITIONS):
        lane = x + (k - 1.5) * 7
        y_from = SOURCE_Y0 + k * SOURCE_ROW
        routes.append([(x + SOURCE_CELL / 2, y_from), (lane + 14, y_from), (lane + 14, row_y(position) - CELL / 2 - 4)])
    polyline(ctx, routes, VIOLET, 0.16, 1.0)

# -------------------------
# Codewords: parity rows faintly banded, then every bit
# -------------------------
for c in CHECKS:
    y = row_y(c)
    ctx.set_source_rgba(*DEEP_VIOLET, 0.22)
    ctx.rectangle(GRID_X0 - 10, y - ROW / 2 + 6, GRID_X1 - GRID_X0 + 20, ROW - 12)
    ctx.fill()

for i, word in enumerate(received):
    for position in range(1, 8):
        is_parity = position in CHECKS
        bad = i == bad_column and position == bad_position
        color = LILAC if is_parity else VIOLET
        bit(column_x(i), row_y(position), CELL, word[position - 1], color, 0.75 if is_parity else 1.0)
        if bad:
            glow(ctx, column_x(i), row_y(position), 150, VIOLET, 0.6)
            glow(ctx, column_x(i), row_y(position), 10, WHITE, 1.0)
            luminous(ctx, [circle(column_x(i), row_y(position), CELL * 0.85)], WHITE, 0.8, 1.2)

# the parity-check matrix: rail c touches every position whose binary form has c
for c, x in zip(CHECKS, RAIL_X):
    covered = [p for p in range(1, 8) if p & c]
    luminous(ctx, [[(x, row_y(covered[0])), (x, row_y(covered[-1]))]], mix(DEEP_VIOLET, VIOLET, 0.5), 0.8, 1.2)
    for p in covered:
        glow(ctx, x, row_y(p), 12, LILAC, 0.5)
        glow(ctx, x, row_y(p), 3.5, WHITE, 0.9)

# the same three checks run through the damaged codeword: two break
bx = column_x(bad_column)
for k, c in enumerate(CHECKS):
    x = bx + CELL / 2 + 10 + k * 8
    covered = [p for p in range(1, 8) if p & c]
    broken = c in failing
    path = [(x, row_y(covered[0])), (x, row_y(covered[-1]))]
    if broken:
        luminous(ctx, [path], VIOLET, 0.9, 1.4)
    else:
        polyline(ctx, [path], DEEP_VIOLET, 0.6, 1.0)
    for p in covered:
        glow(ctx, x, row_y(p), 3.0 if not broken else 4.0, WHITE if broken else LILAC, 0.8)

# -------------------------
# Syndrome: one cell per check under the damaged column, read as binary
# -------------------------
SYN_Y0 = row_y(7) + ROW + 40
for k, c in enumerate(CHECKS):
    bit(bx, SYN_Y0 + k * 34, 24, c in failing, WHITE if c in failing else LILAC)

# -------------------------
# The Venn diagram of the damaged codeword
# -------------------------
VENN_CX, VENN_CY = 800, 1560
R = 215
SPREAD = 130
centres = {
    1: (VENN_CX - SPREAD * math.cos(math.pi / 6), VENN_CY - SPREAD * 0.5),
    2: (VENN_CX + SPREAD * math.cos(math.pi / 6), VENN_CY - SPREAD * 0.5),
    4: (VENN_CX, VENN_CY + SPREAD),
}


def inside(c, x, y):
    cx, cy = centres[c]
    return (x - cx) ** 2 + (y - cy) ** 2 <= R * R


# each region's centre of mass, by sampling: region p holds position p
sums = {p: [0.0, 0.0, 0] for p in range(1, 8)}
for gy in range(int(VENN_CY - 2 * R), int(VENN_CY + 2 * R), 4):
    for gx in range(int(VENN_CX - 2 * R), int(VENN_CX + 2 * R), 4):
        p = sum(c for c in CHECKS if inside(c, gx, gy))
        if p:
            sums[p][0] += gx
            sums[p][1] += gy
            sums[p][2] += 1
spot = {p: (sx / n, sy / n) for p, (sx, sy, n) in sums.items()}

glow(ctx, VENN_CX, VENN_CY, 520, DEEP_VIOLET, 0.30)
for c in CHECKS:
    cx, cy = centres[c]
    ring = circle(cx, cy, R, 360)
    if c in failing:
        glow(ctx, cx, cy, R * 1.15, VIOLET, 0.10)
        luminous(ctx, [ring], VIOLET, 0.9, 2.0)
    else:
        luminous(ctx, [ring], DEEP_VIOLET, 0.7, 1.4)

word = received[bad_column]
for p in range(1, 8):
    x, y = spot[p]
    bit(x, y, 40, word[p - 1], LILAC if p in CHECKS else VIOLET)
bad_x, bad_y = spot[bad_position]
glow(ctx, bad_x, bad_y, 140, VIOLET, 0.55)
glow(ctx, bad_x, bad_y, 12, WHITE, 1.0)
luminous(ctx, [circle(bad_x, bad_y, 38)], WHITE, 0.8, 1.2)

# -------------------------
# The correction path: from the bad bit, through its syndrome, to its region
# -------------------------
turn_y = SYN_Y0 + 2 * 34 + 60
path = [(bx, row_y(bad_position) + CELL / 2 + 6), (bx, SYN_Y0 - 18)]
luminous(ctx, [path], VIOLET, 0.7, 1.4)
path = [(bx, SYN_Y0 + 2 * 34 + 18), (bx, turn_y), (bad_x, turn_y), (bad_x, bad_y - 44)]
luminous(ctx, [path], VIOLET, 0.7, 1.4)

vignette(ctx, WIDTH, HEIGHT, cy=HEIGHT * 0.45)

surface.write_to_png("cc_pycairo/gen/seven_levels/information_03_violet_bitgrid.png")
print("Saved information_03_violet_bitgrid.png")
