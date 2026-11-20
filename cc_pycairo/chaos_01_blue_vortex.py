import math
import random
import cairo
import numpy as np
from seven_levels_kit import axes, background, glow, mix, polyline, rk4, vignette

# chaos.1 order: a damped Duffing oscillator, a stiff spring with friction,
# dx/dt = v, dv/dt = -x - x^3 - c v. it has one fixed point, at rest in the
# middle, and it is stable: friction drains the energy of every start, so
# all of them spiral into it. drawn in the phase plane, the same frame as
# chaos.2, over the vector field itself: 150 seeded starting points, each
# integrated with fixed-step RK4 for the same short time.

WIDTH, HEIGHT = 1600, 2000
SEED = 501
random.seed(SEED)
rng = np.random.default_rng(SEED)

surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

BLUE = (0.20, 0.40, 1.00)
PALE_BLUE = (0.62, 0.75, 1.00)
DEEP_BLUE = (0.05, 0.11, 0.42)
WHITE_HOT = (0.90, 0.94, 1.00)

# -------------------------
# The model, every start at once
# -------------------------
DAMPING = 0.25
DT = 0.01
DURATION = 18.0
STARTS = 150
ENERGY = 4.5           # starts are scattered over the states with at most this energy


def duffing(s):
    x, v = s[:, 0], s[:, 1]
    return np.stack([v, -x - x ** 3 - DAMPING * v], axis=1)


def energy(x, v):
    return v * v / 2 + x * x / 2 + x ** 4 / 4


# uniform over the box, keeping the states below the energy line, so no
# path ever leaves the frame: friction only ever lowers the energy
starts = []
while len(starts) < STARTS:
    x, v = rng.uniform(-2.0, 2.0), rng.uniform(-3.0, 3.0)
    if energy(x, v) <= ENERGY:
        starts.append((x, v))
state = np.array(starts)

STEPS = int(DURATION / DT)
paths = np.empty((STEPS + 1, STARTS, 2))
for i in range(STEPS + 1):
    paths[i] = state
    if i < STEPS:
        state = rk4(duffing, state, DT)

# -------------------------
# The view: x across, v up, one scale for both
# -------------------------
CX, CY = 800, 1010
SCALE = 262


def screen(q):
    x, v = q
    return CX + x * SCALE, CY - v * SCALE


background(ctx, WIDTH, HEIGHT, BLUE, cx=CX, cy=CY)
ctx.set_operator(cairo.OPERATOR_ADD)
glow(ctx, CX, CY, 760, DEEP_BLUE, 0.35)

axes(ctx, screen, (-2.3, 2.3), (-3.0, 3.0), 0.5, DEEP_BLUE, 0.9)

# -------------------------
# The vector field: a short stroke along the flow at each point of a grid,
# brighter where the flow is faster
# -------------------------
GRID = 0.25
strokes = {}
for gx in np.arange(-2.25, 2.26, GRID):
    for gv in np.arange(-3.0, 3.01, GRID):
        dx, dv = duffing(np.array([[gx, gv]]))[0]
        speed = math.hypot(dx, dv)
        if speed < 1e-9:
            continue
        half = 0.32 * GRID
        a = (gx - dx / speed * half, gv - dv / speed * half)
        b = (gx + dx / speed * half, gv + dv / speed * half)
        level = min(3, int(math.log1p(speed)))
        strokes.setdefault(level, []).append([screen(a), screen(b)])
for level, group in sorted(strokes.items()):
    polyline(ctx, group, mix(DEEP_BLUE, BLUE, 0.4 + 0.2 * level), 0.30 + 0.08 * level, 1.0)

# -------------------------
# The paths: each fades in from its start and brightens as it closes in,
# then thins out near the middle, where all of them meet
# -------------------------
CHUNK = 50
for k in range(0, STEPS, CHUNK):
    end = min(STEPS, k + CHUNK)
    t = k / STEPS
    group = [[screen(q) for q in paths[k:end + 1:2, m]] for m in range(STARTS)]
    r = np.hypot(paths[k, :, 0], paths[k, :, 1])
    near = float(np.median(r))
    fade = min(1.0, near / 0.35)
    color = mix(BLUE, PALE_BLUE, t)
    polyline(ctx, group, color, (0.10 + 0.35 * min(1.0, t * 3)) * fade, 1.1 + 0.4 * t)

# the scattered starts
for x, v in starts:
    px, py = screen((x, v))
    glow(ctx, px, py, 14, BLUE, 0.40)
    glow(ctx, px, py, 3.0, PALE_BLUE, 0.85)

# the fixed point: where everything ends, at rest
glow(ctx, CX, CY, 180, BLUE, 0.55)
glow(ctx, CX, CY, 60, PALE_BLUE, 0.45)
glow(ctx, CX, CY, 9, WHITE_HOT, 1.0)

vignette(ctx, WIDTH, HEIGHT, cx=CX, cy=CY)

surface.write_to_png("cc_pycairo/gen/seven_levels/chaos_01_blue_vortex.png")
print("Saved chaos_01_blue_vortex.png")
