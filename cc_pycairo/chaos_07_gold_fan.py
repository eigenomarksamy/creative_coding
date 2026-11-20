import math
import random
import cairo
import numpy as np
from seven_levels_kit import background, blur, glow, mix, polyline, raster, rk4, vignette

# chaos.7 uncertainty: an ensemble forecast of the Lorenz system, the same
# system as chaos.3. 240 runs start in a cloud a thousandth wide around one
# present state, and each is integrated with fixed-step RK4. drawn as a plume
# of x against time, rising from the present at the bottom: the brightness of
# a point is the log of how many runs pass through it, so the plume is one
# bright trunk while the runs agree, and a fan of faint futures once they
# part. a faint rule marks each time the ensemble's spread first grows
# tenfold, and a dashed one the forecast horizon, where the spread reaches
# the attractor's own size.

WIDTH, HEIGHT = 1600, 2000
SEED = 507
random.seed(SEED)
rng = np.random.default_rng(SEED)

surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

GOLD = (0.86, 0.68, 0.30)
PALE_GOLD = (0.96, 0.88, 0.64)
DEEP_GOLD = (0.42, 0.29, 0.08)
WHITE_HOT = (1.00, 0.97, 0.88)

# -------------------------
# The model: dx/dt = s (y - x), dy/dt = x (r - z) - y, dz/dt = x y - b z,
# the whole ensemble at once, one row per run
# -------------------------
SIGMA, RHO, BETA = 10.0, 28.0, 8.0 / 3.0
DT = 0.004
SETTLE = 12.5          # time spent reaching the attractor before the forecast starts
DURATION = 12.0        # time shown
MEMBERS = 240
SPREAD = 1e-3          # the present state's uncertainty, per coordinate
HORIZON = 8.0          # spread at which the forecast says no more than the attractor does


def lorenz(s):
    x, y, z = s[:, 0], s[:, 1], s[:, 2]
    return np.stack([SIGMA * (y - x), x * (RHO - z) - y, x * y - BETA * z], axis=1)


present = np.array([[1.0, 1.0, 1.0]])
for _ in range(int(SETTLE / DT)):
    present = rk4(lorenz, present, DT)

ensemble = present + rng.normal(0.0, SPREAD, (MEMBERS, 3))
ensemble[0] = present[0]   # the control run starts exactly at the present state

STEPS = int(DURATION / DT)
xs = np.empty((STEPS + 1, MEMBERS))
spread = np.empty(STEPS + 1)
for i in range(STEPS + 1):
    xs[i] = ensemble[:, 0]
    spread[i] = math.sqrt(float(((ensemble - ensemble.mean(axis=0)) ** 2).sum(axis=1).mean()))
    if i < STEPS:
        ensemble = rk4(lorenz, ensemble, DT)

# the first time the spread grows past each power of ten of its start
decades = []
k = 1
for i, s in enumerate(spread):
    while s >= spread[0] * 10.0 ** k:
        decades.append(i)
        k += 1
horizon = next(i for i, s in enumerate(spread) if s >= HORIZON)

# -------------------------
# The view: time rises from the present at the bottom, x runs across
# -------------------------
Y_NOW, Y_END = 1790, 230
X_LO, X_HI = 180, 1420
X_SPAN = 21.0


def screen_x(x):
    return X_LO + (X_HI - X_LO) * (x + X_SPAN) / (2 * X_SPAN)


def screen_y(i):
    return Y_NOW - (Y_NOW - Y_END) * i / STEPS


def screen(i, x):
    return screen_x(x), screen_y(i)


# -------------------------
# The density: each run's path, sampled every half pixel along its length,
# is spread over the four nearest pixels, so a pixel's total is close to the
# number of runs through it. a light blur gives the line its width and a
# wide one its halo, and both are shown on a log scale, so one lone run is
# faint and all 240 together are full strength
# -------------------------
density = np.zeros((HEIGHT, WIDTH))
ys = screen_y(np.arange(STEPS + 1))
for m in range(MEMBERS):
    px = screen_x(xs[:, m])
    seg = np.hypot(np.diff(px), np.diff(ys))
    n = np.maximum(1, np.ceil(seg / 0.5)).astype(int)
    start = np.repeat(np.arange(STEPS), n)
    frac = (np.arange(n.sum()) - np.repeat(np.cumsum(n) - n, n)) / np.repeat(n, n)
    sx = px[start] + (px[start + 1] - px[start]) * frac
    sy = ys[start] + (ys[start + 1] - ys[start]) * frac
    w = np.repeat(seg / n, n)
    ix, iy = np.floor(sx).astype(int), np.floor(sy).astype(int)
    fx, fy = sx - ix, sy - iy
    for dx, dy, wt in ((0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)), (0, 1, (1 - fx) * fy), (1, 1, fx * fy)):
        density += np.bincount((iy + dy) * WIDTH + ix + dx, weights=w * wt, minlength=WIDTH * HEIGHT).reshape(HEIGHT, WIDTH)


# a line one pixel wide carries about one unit per pixel; the blur keeps the total
core = blur(density, 0.7) * 1.3
halo = blur(density, 7.0) * 1.3
scale = math.log1p(MEMBERS)
lit_core = np.log1p(core) / scale
lit_halo = np.log1p(halo) / scale

light = np.zeros((HEIGHT, WIDTH, 3))
for c in range(3):
    # gold where few runs pass, warming to pale gold where nearly all of them do
    hue = GOLD[c] + (PALE_GOLD[c] - GOLD[c]) * lit_core ** 3
    light[..., c] = 0.95 * lit_core * hue + 0.22 * lit_halo * GOLD[c]

# -------------------------
# The drawing
# -------------------------
cx, cy = (X_LO + X_HI) / 2, 1100
background(ctx, WIDTH, HEIGHT, GOLD, cx=cx, cy=cy)
ctx.set_operator(cairo.OPERATOR_ADD)
glow(ctx, cx, Y_END + 300, 820, DEEP_GOLD, 0.22)

# the rules: one per tenfold growth of the spread, and the horizon
for i in decades:
    y = screen_y(i)
    polyline(ctx, [[(X_LO - 20, y), (X_HI + 20, y)]], DEEP_GOLD, 0.55, 1.0)
ctx.set_dash([12, 9])
polyline(ctx, [[(X_LO - 20, screen_y(horizon)), (X_HI + 20, screen_y(horizon))]], PALE_GOLD, 0.40, 1.2)
ctx.set_dash([])

raster(ctx, light)

# the control run, a little brighter, so one future can be followed
control = [screen(i, xs[i, 0]) for i in range(0, STEPS + 1, 2)]
polyline(ctx, [control], PALE_GOLD, 0.30, 1.0)

# the present, and where each run has got to at the end
glow(ctx, *screen(0, xs[0, 0]), 110, GOLD, 0.55)
glow(ctx, *screen(0, xs[0, 0]), 10, WHITE_HOT, 1.0)
for m in range(MEMBERS):
    x, y = screen(STEPS, xs[STEPS, m])
    glow(ctx, x, y, 12, GOLD, 0.22)
    glow(ctx, x, y, 2.5, mix(GOLD, WHITE_HOT, 0.5), 0.6)

vignette(ctx, WIDTH, HEIGHT, cx=cx, cy=cy)

surface.write_to_png("cc_pycairo/gen/seven_levels/chaos_07_gold_fan.png")
print("Saved chaos_07_gold_fan.png")
print("decades at t =", [round(i * DT, 2) for i in decades], "horizon at t =", round(horizon * DT, 2))
