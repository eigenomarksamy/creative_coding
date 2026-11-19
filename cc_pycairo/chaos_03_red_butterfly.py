import math
import random
import cairo
from seven_levels_kit import background, glow, luminous, mix, polyline, vignette

# chaos.3 instability: two runs of the Lorenz system that start a millionth
# apart, integrated with a fixed-step RK4 solver. they trace one line, then
# split. below, their separation on a log scale grows along a straight line,
# the largest Lyapunov exponent, until it reaches the attractor's size.

WIDTH, HEIGHT = 1600, 2000
SEED = 503
random.seed(SEED)

surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

RED = (1.00, 0.16, 0.22)
ROSE = (1.00, 0.62, 0.58)
DEEP_RED = (0.50, 0.04, 0.09)
WHITE_HOT = (1.00, 0.90, 0.88)

# -------------------------
# The model: dx/dt = s (y - x), dy/dt = x (r - z) - y, dz/dt = x y - b z
# -------------------------
SIGMA, RHO, BETA = 10.0, 28.0, 8.0 / 3.0
DT = 0.004
SETTLE = 10.0          # time spent reaching the attractor before the picture starts
DURATION = 21.0        # time shown
OFFSET = 1e-6          # the second run starts this far along x
LYAPUNOV = 0.9056      # the largest Lyapunov exponent of these parameters


def lorenz(p):
    x, y, z = p
    return (SIGMA * (y - x), x * (RHO - z) - y, x * y - BETA * z)


def rk4(p, h):
    k1 = lorenz(p)
    k2 = lorenz(tuple(p[i] + h / 2 * k1[i] for i in range(3)))
    k3 = lorenz(tuple(p[i] + h / 2 * k2[i] for i in range(3)))
    k4 = lorenz(tuple(p[i] + h * k3[i] for i in range(3)))
    return tuple(p[i] + h / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]) for i in range(3))


start = (1.0, 1.0, 1.0)
for _ in range(int(SETTLE / DT)):
    start = rk4(start, DT)

a, b = start, (start[0] + OFFSET, start[1], start[2])
run_a, run_b = [a], [b]
for _ in range(int(DURATION / DT)):
    a, b = rk4(a, DT), rk4(b, DT)
    run_a.append(a)
    run_b.append(b)
separation = [math.dist(p, q) for p, q in zip(run_a, run_b)]

# -------------------------
# The view: turned a little about z, so the wings separate in depth
# -------------------------
TURN = 0.42


def flat(p):
    x, y, z = p
    return x * math.cos(TURN) + y * math.sin(TURN), z


flat_a = [flat(p) for p in run_a]
flat_b = [flat(p) for p in run_b]
us = [u for u, _ in flat_a + flat_b]
vs = [v for _, v in flat_a + flat_b]
BOX_X0, BOX_X1, BOX_Y0, BOX_Y1 = 170, 1430, 200, 1430
scale = min((BOX_X1 - BOX_X0) / (max(us) - min(us)), (BOX_Y1 - BOX_Y0) / (max(vs) - min(vs)))
u_mid, v_mid = (max(us) + min(us)) / 2, (max(vs) + min(vs)) / 2
mid_x, mid_y = (BOX_X0 + BOX_X1) / 2, (BOX_Y0 + BOX_Y1) / 2


def screen(q):
    u, v = q
    return mid_x + (u - u_mid) * scale, mid_y - (v - v_mid) * scale


pts_a = [screen(q) for q in flat_a]
pts_b = [screen(q) for q in flat_b]

# the runs count as apart once they are a pixel apart on screen
split = next(i for i, d in enumerate(separation) if d * scale > 1.0)

background(ctx, WIDTH, HEIGHT, RED, cx=mid_x, cy=mid_y)
ctx.set_operator(cairo.OPERATOR_ADD)
glow(ctx, mid_x, mid_y, 760, DEEP_RED, 0.30)

# -------------------------
# Together: one quiet line, the whole shared history
# -------------------------
CHUNK = 150
for k in range(0, split, CHUNK):
    piece = pts_a[k:min(split, k + CHUNK) + 1]
    luminous(ctx, [piece], mix(DEEP_RED, RED, 0.3 + 0.5 * k / split), 0.22 + 0.20 * k / split, 1.0)

# -------------------------
# Apart: rungs join the two runs at equal times, then each run brightens
# as it goes, so their last loops, in different wings, carry the picture
# -------------------------
# only while the gap is short enough to read as a widening ladder
for i in range(split, len(pts_a), 18):
    gap = math.dist(pts_a[i], pts_b[i])
    if gap > 260:
        break
    polyline(ctx, [[pts_a[i], pts_b[i]]], ROSE, 0.10 + 0.25 * gap / 260, 0.9)

tail = len(pts_a) - split
for k in range(split, len(pts_a) - 1, CHUNK):
    end = min(len(pts_a), k + CHUNK + 1)
    ramp = ((k - split) / tail) ** 1.5
    luminous(ctx, [pts_a[k:end]], RED, 0.25 + 0.75 * ramp, 1.2 + 1.0 * ramp)
    luminous(ctx, [pts_b[k:end]], WHITE_HOT, 0.15 + 0.65 * ramp, 1.2 + 1.0 * ramp)

glow(ctx, *pts_a[0], 60, ROSE, 0.6)
glow(ctx, *pts_a[0], 9, WHITE_HOT, 1.0)
glow(ctx, *pts_a[split], 90, RED, 0.55)
glow(ctx, *pts_a[split], 12, WHITE_HOT, 1.0)
for (x, y), color in ((pts_a[-1], RED), (pts_b[-1], ROSE)):
    glow(ctx, x, y, 70, color, 0.7)
    glow(ctx, x, y, 8, WHITE_HOT, 1.0)

# -------------------------
# The separation, log scale: a straight climb at the Lyapunov rate, then a
# ceiling at the attractor's size. a decade per faint rule, no labels.
# -------------------------
PLOT_X0, PLOT_X1 = 220, 1380
PLOT_Y0, PLOT_Y1 = 1560, 1800
LOG_LO, LOG_HI = -7, 2


def plot(t, d):
    x = PLOT_X0 + (PLOT_X1 - PLOT_X0) * t / DURATION
    y = PLOT_Y1 - (PLOT_Y1 - PLOT_Y0) * (math.log10(d) - LOG_LO) / (LOG_HI - LOG_LO)
    return x, y


for decade in range(LOG_LO, LOG_HI + 1):
    y = plot(0, 10.0 ** decade)[1]
    polyline(ctx, [[(PLOT_X0, y), (PLOT_X1, y)]], DEEP_RED, 0.35 if decade in (LOG_LO, 0) else 0.18, 1.0)

curve = [plot(i * DT, max(d, 10.0 ** LOG_LO)) for i, d in enumerate(separation)]
x_split = curve[split][0]
polyline(ctx, [[(x_split, PLOT_Y0 - 20), (x_split, PLOT_Y1)]], ROSE, 0.25, 1.0)

# the exponential law, dashed: d(t) = d0 e^(lambda t)
law = []
for s in range(0, 121):
    t = DURATION * s / 120
    d = OFFSET * math.exp(LYAPUNOV * t)
    if d > 10.0 ** LOG_HI:
        break
    law.append(plot(t, d))
ctx.set_dash([10, 8])
polyline(ctx, [law], ROSE, 0.55, 1.2)
ctx.set_dash([])

luminous(ctx, [curve[::2]], RED, 0.8, 1.4)
glow(ctx, *curve[split], 40, RED, 0.6)
glow(ctx, *curve[split], 6, WHITE_HOT, 1.0)

vignette(ctx, WIDTH, HEIGHT, cx=mid_x, cy=mid_y)

surface.write_to_png("cc_pycairo/gen/seven_levels/chaos_03_red_butterfly.png")
print("Saved chaos_03_red_butterfly.png")
