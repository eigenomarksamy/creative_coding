import math
import random
import cairo
import numpy as np
from seven_levels_kit import axes, background, glow, luminous, mix, polyline, rk4, vignette

# chaos.2 motion: the phase portrait of a pendulum, H = p^2 / 2 - cos(theta),
# one law that moves every state along its own curve of constant energy.
# near the bottom the orbits are the ellipses of a harmonic oscillator, and
# they stretch into eyes as the swing grows, up to the separatrix, beyond
# which the pendulum goes over the top. every swing starts from its turning
# point at the same moment, and is integrated with fixed-step RK4; markers
# show where each one is at equal steps of time. the faint lines joining
# equal times are straight where the motion is harmonic, every swing taking
# the same time, and curl where the bigger swings fall behind.

WIDTH, HEIGHT = 1600, 2000
SEED = 502
random.seed(SEED)

surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

STEEL = (0.58, 0.68, 0.80)
PALE_STEEL = (0.85, 0.90, 0.96)
DEEP_STEEL = (0.20, 0.26, 0.36)
WHITE_HOT = (0.96, 0.98, 1.00)

# -------------------------
# The model: d(theta)/dt = p, dp/dt = -sin(theta), every swing at once
# -------------------------
DT = 0.002
SWINGS = 12            # librations, from a small swing to near the separatrix
A_LO, A_HI = 0.26, 2.95
PERIOD = 2 * math.pi   # a small swing's period
MARKS = 24             # markers per small-swing period
OVER = (2.15, 2.4, 2.7)   # momentum at the bottom of the orbits that go over the top


def pendulum(s):
    return np.stack([s[:, 1], -np.sin(s[:, 0])], axis=1)


amplitudes = np.linspace(A_LO, A_HI, SWINGS)
state = np.stack([amplitudes, np.zeros(SWINGS)], axis=1)
steps_per_mark = round(PERIOD / MARKS / DT)


def period_of(a):
    """A swing's period, 4 K(sin(a/2)), by the arithmetic-geometric mean."""
    x, y = 1.0, math.cos(a / 2)
    while abs(x - y) > 1e-15:
        x, y = (x + y) / 2, math.sqrt(x * y)
    return 2 * math.pi / x


# the whole orbit of each swing, and its position at every mark
longest = max(period_of(a) for a in amplitudes)
orbit_steps = int(longest / DT) + 2
path = np.empty((orbit_steps + 1, SWINGS, 2))
for i in range(orbit_steps + 1):
    path[i] = state
    if i < orbit_steps:
        state = rk4(pendulum, state, DT)
marks = path[: MARKS * steps_per_mark + 1 : steps_per_mark]   # one small period of marks
closed = [path[: int(period_of(a) / DT) + 2, k] for k, a in enumerate(amplitudes)]

# the energy is a check on the integrator: it should hold along each orbit
drift = max(float(np.ptp(o[:, 1] ** 2 / 2 - np.cos(o[:, 0]))) for o in closed)
assert drift < 1e-9, drift

# -------------------------
# The view: theta across, -pi to pi, and p up
# -------------------------
CX, CY = 800, 1010
SX = 1260 / (2 * math.pi)
SY = 1540 / 5.6


def screen(q):
    theta, p = q
    return CX + theta * SX, CY - p * SY


background(ctx, WIDTH, HEIGHT, STEEL, cx=CX, cy=CY)
ctx.set_operator(cairo.OPERATOR_ADD)
glow(ctx, CX, CY, 700, DEEP_STEEL, 0.30)

axes(ctx, screen, (-math.pi, math.pi), (-2.75, 2.75), math.pi / 2, DEEP_STEEL, 0.9)

# the separatrix, H = 1: p = 2 cos(theta / 2), the edge between swinging and going over
sep = [[screen((t, s * 2 * math.cos(t / 2))) for t in np.linspace(-math.pi, math.pi, 600)] for s in (1, -1)]
luminous(ctx, sep, PALE_STEEL, 0.55, 1.4)

# the orbits that go over the top: wavy lines above and below
for p0 in OVER:
    h = p0 * p0 / 2 - 1
    for s in (1, -1):
        line = [screen((t, s * math.sqrt(2 * (h + math.cos(t))))) for t in np.linspace(-math.pi, math.pi, 400)]
        luminous(ctx, [line], STEEL, 0.32, 1.1)

# the swings, from the small inner ellipses outwards
for k, orbit in enumerate(closed):
    t = k / (SWINGS - 1)
    luminous(ctx, [[screen(q) for q in orbit[::4]]], mix(STEEL, PALE_STEEL, 0.4 * (1 - t)), 0.40 + 0.15 * (1 - t), 1.2)

# -------------------------
# Equal times: a faint line through the markers of each moment, then the
# markers, growing brighter as time goes on
# -------------------------
for j in range(1, MARKS + 1):
    polyline(ctx, [[screen(q) for q in marks[j]]], STEEL, 0.24 + 0.16 * j / MARKS, 1.0)

for j in range(MARKS + 1):
    age = j / MARKS
    for q in marks[j]:
        x, y = screen(q)
        glow(ctx, x, y, 14, STEEL, 0.22 + 0.25 * age)
        glow(ctx, x, y, 3.2, mix(PALE_STEEL, WHITE_HOT, age), 0.55 + 0.45 * age)

# the rest point at the bottom, and the balance point at the top, theta = pi
glow(ctx, CX, CY, 70, STEEL, 0.5)
glow(ctx, CX, CY, 7, WHITE_HOT, 1.0)
for theta in (-math.pi, math.pi):
    x, y = screen((theta, 0.0))
    glow(ctx, x, y, 50, PALE_STEEL, 0.35)
    glow(ctx, x, y, 5, WHITE_HOT, 0.9)

vignette(ctx, WIDTH, HEIGHT, cx=CX, cy=CY)

surface.write_to_png("cc_pycairo/gen/seven_levels/chaos_02_steel_ellipses.png")
print("Saved chaos_02_steel_ellipses.png")
