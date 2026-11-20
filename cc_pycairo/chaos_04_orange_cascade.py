import math
import random
import cairo
import numpy as np
from seven_levels_kit import background, blur, glow, mix, polyline, raster, vignette

# chaos.4 nonlinearity: the logistic map, x -> r x (1 - x), one line of
# feedback. for each value of r, a row of the picture, 1200 seeded starting
# points are iterated, the first 800 steps are dropped, and the next 300 are
# counted into the row's bins: the brightness is the log of how often the
# map visits each x. r grows downward, so the single stream at the top
# splits in two, four, eight, and then breaks into a spray, with windows of
# order inside it. the thin column on the right is the Lyapunov exponent of
# each row, the average of log |r (1 - 2x)|: left of its centre line the
# row settles into a cycle, right of it the row is chaotic.

WIDTH, HEIGHT = 1600, 2000
SEED = 504
random.seed(SEED)
rng = np.random.default_rng(SEED)

surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

ORANGE = (1.00, 0.52, 0.10)
PALE_ORANGE = (1.00, 0.82, 0.56)
DEEP_ORANGE = (0.46, 0.15, 0.02)
WHITE_HOT = (1.00, 0.95, 0.88)

# -------------------------
# The view: x across the main panel, r down it
# -------------------------
X0, X1 = 160, 1290               # x from 0 to 1
Y0, Y1 = 200, 1820               # r from R_LO to R_HI
R_LO, R_HI = 2.9, 4.0
L0, L1 = 1330, 1440              # the Lyapunov column
L_LO, L_HI = -1.6, 0.8

ROWS, COLS = Y1 - Y0, X1 - X0

# -------------------------
# The model, every row at once
# -------------------------
STARTS = 1200
SETTLE = 800
COUNT = 300

r = R_LO + (R_HI - R_LO) * (np.arange(ROWS) + 0.5) / ROWS
x = rng.uniform(0.02, 0.98, (ROWS, STARTS))
rr = r[:, None]
for _ in range(SETTLE):
    x = rr * x * (1.0 - x)

hits = np.zeros(ROWS * COLS)
lyapunov = np.zeros(ROWS)
row_base = (np.arange(ROWS) * COLS)[:, None]
for _ in range(COUNT):
    x = rr * x * (1.0 - x)
    lyapunov += np.log(np.maximum(np.abs(rr * (1.0 - 2.0 * x)), 1e-12)).mean(axis=1)
    col = np.minimum((x * COLS).astype(int), COLS - 1)
    hits += np.bincount((row_base + col).ravel(), minlength=ROWS * COLS)
lyapunov /= COUNT
hits = hits.reshape(ROWS, COLS) / (STARTS * COUNT)   # the share of a row's visits in each bin

# a log scale: a bin a stable cycle sits on is full strength, and the thin
# spray of the chaotic rows still shows
FLOOR = 0.6 / COLS
lit = np.log1p(hits / FLOOR) / math.log1p(1.0 / FLOOR)
halo = np.log1p(blur(hits, 4.0) / FLOOR) / math.log1p(1.0 / FLOOR)

light = np.zeros((ROWS, COLS, 3))
for c in range(3):
    hue = ORANGE[c] + (PALE_ORANGE[c] - ORANGE[c]) * lit ** 4
    light[..., c] = 1.1 * lit * hue + 0.2 * halo * ORANGE[c]


def y_of(rv):
    return Y0 + (rv - R_LO) / (R_HI - R_LO) * ROWS


# -------------------------
# The drawing
# -------------------------
cx, cy = (X0 + X1) / 2, 1080
background(ctx, WIDTH, HEIGHT, ORANGE, cx=cx, cy=cy)
ctx.set_operator(cairo.OPERATOR_ADD)
glow(ctx, cx, cy + 200, 820, DEEP_ORANGE, 0.28)

# faint rules at the first doublings, the end of the cascade (Feigenbaum's
# point) and the start of the period-3 window, each a computed constant
marks = (3.0, 1 + math.sqrt(6), 3.5440903, 3.5699456, 1 + math.sqrt(8))
polyline(ctx, [[(X0 - 10, y_of(m)), (L1, y_of(m))] for m in marks], DEEP_ORANGE, 0.40, 1.0)

raster(ctx, light, X0, Y0)

# the Lyapunov column: its zero line, then the exponent row by row
def l_x(v):
    return L0 + (min(max(v, L_LO), L_HI) - L_LO) / (L_HI - L_LO) * (L1 - L0)


polyline(ctx, [[(l_x(0.0), Y0), (l_x(0.0), Y1)]], DEEP_ORANGE, 0.9, 1.0)
trace = [(l_x(v), Y0 + j + 0.5) for j, v in enumerate(lyapunov)]
polyline(ctx, [trace], mix(ORANGE, PALE_ORANGE, 0.3), 0.75, 1.0)

# where the single stream first splits
glow(ctx, X0 + (1 - 1 / 3.0) * COLS, y_of(3.0), 60, ORANGE, 0.45)
glow(ctx, X0 + (1 - 1 / 3.0) * COLS, y_of(3.0), 6, WHITE_HOT, 0.9)

vignette(ctx, WIDTH, HEIGHT, cx=cx, cy=cy)

surface.write_to_png("cc_pycairo/gen/seven_levels/chaos_04_orange_cascade.png")
print("Saved chaos_04_orange_cascade.png")
print("chaotic rows:", int((lyapunov > 0).sum()), "of", ROWS)
