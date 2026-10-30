import math
import random
import cairo

# -------------------------
# Canvas setup
# -------------------------
WIDTH, HEIGHT = 2000, 1400
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

random.seed(2)

TURQUOISE = (0.25, 0.95, 0.85)
DEEP_TEAL = (0.05, 0.50, 0.52)
FOAM = (0.85, 1.00, 0.97)


def glow(x, y, radius, color, alpha):
    r, g, b = color
    pat = cairo.RadialGradient(x, y, 0, x, y, radius)
    pat.add_color_stop_rgba(0.0, r, g, b, alpha)
    pat.add_color_stop_rgba(0.25, r, g, b, alpha * 0.3)
    pat.add_color_stop_rgba(1.0, r, g, b, 0.0)
    ctx.set_source(pat)
    ctx.arc(x, y, radius, 0, 2 * math.pi)
    ctx.fill()


# -------------------------
# Background: deep teal night
# -------------------------
bg = cairo.LinearGradient(0, 0, 0, HEIGHT)
bg.add_color_stop_rgb(0.0, 0.006, 0.030, 0.036)
bg.add_color_stop_rgb(0.5, 0.010, 0.050, 0.058)
bg.add_color_stop_rgb(1.0, 0.004, 0.022, 0.028)
ctx.set_source(bg)
ctx.paint()

for _ in range(9000):
    x = random.uniform(0, WIDTH)
    y = random.uniform(0, HEIGHT)
    ctx.set_source_rgba(0.4, 0.8, 0.8, random.uniform(0.02, 0.06))
    ctx.arc(x, y, random.uniform(0.4, 1.0), 0, 2 * math.pi)
    ctx.fill()

ctx.set_operator(cairo.OPERATOR_ADD)

# -------------------------
# Concentric waves: two coherent point sources, u = sum cos(k * r_i).
# Crests are circles; where they cancel, the nodal lines are hyperbolas.
# -------------------------
SOURCES = [(WIDTH * 0.34, HEIGHT * 0.50), (WIDTH * 0.58, HEIGHT * 0.36)]
WAVELENGTH = 46
WAVE_K = 2 * math.pi / WAVELENGTH
FADE = 650
CELL = 4


def wave_field(x, y):
    return sum(math.cos(WAVE_K * math.hypot(x - sx, y - sy)) for sx, sy in SOURCES)


def fade(x, y):
    d = min(math.hypot(x - sx, y - sy) for sx, sy in SOURCES)
    return math.exp(-d / FADE)


# Crest rings of each source
for sx, sy in SOURCES:
    for n in range(1, 40):
        r = n * WAVELENGTH
        ctx.set_line_width(1.4)
        ctx.set_source_rgba(*TURQUOISE, 0.20 * math.exp(-r / FADE))
        ctx.arc(sx, sy, r, 0, 2 * math.pi)
        ctx.stroke()

cols = WIDTH // CELL + 1
rows = HEIGHT // CELL + 1
field = [[wave_field(i * CELL, j * CELL) for i in range(cols)] for j in range(rows)]


def contour(level, color, alpha, width):
    """
    Marching squares: one segment per cell where the level is crossed.
    Segments are bucketed by distance so the lines fade like the rings.
    """
    buckets = [[] for _ in range(8)]

    def lerp(a, b, va, vb):
        t = (level - va) / (vb - va)
        return a + (b - a) * t

    for j in range(rows - 1):
        y0, y1 = j * CELL, (j + 1) * CELL
        row0, row1 = field[j], field[j + 1]
        for i in range(cols - 1):
            a, b, c, d = row0[i], row0[i + 1], row1[i + 1], row1[i]
            x0, x1 = i * CELL, (i + 1) * CELL
            points = []
            if (a > level) != (b > level):
                points.append((lerp(x0, x1, a, b), y0))
            if (b > level) != (c > level):
                points.append((x1, lerp(y0, y1, b, c)))
            if (c > level) != (d > level):
                points.append((lerp(x1, x0, c, d), y1))
            if (d > level) != (a > level):
                points.append((x0, lerp(y1, y0, d, a)))
            if len(points) < 2:
                continue
            bucket = min(7, int(fade(x0, y0) * 8))
            for k in range(0, len(points) - 1, 2):
                buckets[bucket].append((points[k], points[k + 1]))

    ctx.set_line_width(width)
    for bucket, segments in enumerate(buckets):
        ctx.set_source_rgba(*color, alpha * (bucket + 0.5) / 8)
        for p, q in segments:
            ctx.move_to(*p)
            ctx.line_to(*q)
        ctx.stroke()


contour(1.75, FOAM, 0.40, 1.0)     # antinodes: both crests together
contour(-1.75, DEEP_TEAL, 0.35, 1.0)

# Nodal lines: hyperbolas where the path difference is half a wavelength
(s1x, s1y), (s2x, s2y) = SOURCES
mid_x, mid_y = (s1x + s2x) / 2, (s1y + s2y) / 2
half_gap = math.hypot(s2x - s1x, s2y - s1y) / 2
axis_x, axis_y = (s2x - s1x) / (2 * half_gap), (s2y - s1y) / (2 * half_gap)
for m in range(-12, 12):
    delta = (m + 0.5) * WAVELENGTH      # r1 - r2
    a = abs(delta) / 2
    if a >= half_gap:
        continue
    b = math.sqrt(half_gap ** 2 - a ** 2)
    side = 1 if delta > 0 else -1
    for branch in (-1, 1):
        ctx.new_path()
        for s in range(121):
            u = s / 120 * 3.0
            along = side * a * math.cosh(u)
            across = branch * b * math.sinh(u)
            ctx.line_to(mid_x + axis_x * along - axis_y * across,
                        mid_y + axis_y * along + axis_x * across)
        ctx.set_line_width(1.0)
        ctx.set_source_rgba(*DEEP_TEAL, 0.35)
        ctx.stroke()

# Sources
for sx, sy in SOURCES:
    glow(sx, sy, 40, TURQUOISE, 0.25)
    glow(sx, sy, 6, FOAM, 0.7)

# -------------------------
# Pendulum wave: periods T / (N0 + n), so lengths L ~ T_n ^ 2.
# Seen from slightly above, the depth swing reads as vertical motion.
# -------------------------
N_PEND = 34
N0 = 38
CYCLE = 60.0                       # seconds until they all realign
THETA0 = 0.32
RAIL_Y = 110
RAIL_X0, RAIL_X1 = WIDTH * 0.10, WIDTH * 0.90
L_MAX = 520
SNAP_T = CYCLE * 0.137             # the moment captured


def pendulum(n, t):
    """Screen position of bob n at time t, plus its pivot."""
    x = RAIL_X0 + (RAIL_X1 - RAIL_X0) * n / (N_PEND - 1)
    length = L_MAX * (N0 / (N0 + n)) ** 2
    theta = THETA0 * math.cos(2 * math.pi * (N0 + n) * t / CYCLE)
    y = RAIL_Y + length * math.cos(theta)
    z = length * math.sin(theta)
    return (x + 0.10 * z, y - 0.55 * z), (x, RAIL_Y)


# Rail
ctx.set_line_width(2.0)
ctx.set_source_rgba(*TURQUOISE, 0.35)
ctx.move_to(RAIL_X0 - 40, RAIL_Y)
ctx.line_to(RAIL_X1 + 40, RAIL_Y)
ctx.stroke()

# Each bob's full swing, faint, like a long exposure
for n in range(N_PEND):
    ctx.set_line_width(1.0)
    ctx.set_source_rgba(*DEEP_TEAL, 0.25)
    for s in range(61):
        t = s / 60 * CYCLE / (N0 + n)
        (bx, by), _ = pendulum(n, t)
        if s == 0:
            ctx.move_to(bx, by)
        else:
            ctx.line_to(bx, by)
    ctx.stroke()

# Ghosts of the wave a moment earlier: the chain of bobs travels
for g in range(14, 0, -1):
    t = SNAP_T - g * 0.012
    ctx.set_line_width(1.2)
    ctx.set_source_rgba(*TURQUOISE, 0.10 * (1 - g / 15))
    for n in range(N_PEND):
        (bx, by), _ = pendulum(n, t)
        if n == 0:
            ctx.move_to(bx, by)
        else:
            ctx.line_to(bx, by)
    ctx.stroke()

# Motion trails, then strings and glowing bobs at the snapshot
for n in range(N_PEND):
    for s in range(40):
        t = SNAP_T - s * 0.004
        (bx, by), _ = pendulum(n, t)
        ctx.set_source_rgba(*TURQUOISE, 0.12 * (1 - s / 40))
        ctx.arc(bx, by, 3.0, 0, 2 * math.pi)
        ctx.fill()

    (bx, by), (px, py) = pendulum(n, SNAP_T)
    ctx.set_line_width(0.8)
    ctx.set_source_rgba(*FOAM, 0.30)
    ctx.move_to(px, py)
    ctx.line_to(bx, by)
    ctx.stroke()

    glow(bx, by, 34, TURQUOISE, 0.45)
    glow(bx, by, 9, FOAM, 0.9)
    ctx.set_source_rgba(*FOAM, 0.6)
    ctx.arc(px, py, 2.2, 0, 2 * math.pi)
    ctx.fill()

# -------------------------
# Fireflies: Kuramoto oscillators, d(theta_i)/dt = w_i + K r sin(psi - theta_i)
# Time runs left to right; each dot is a flash. Coupling K ramps up, so
# scattered flashes lock into columns.
# -------------------------
N_FLIES = 72
T_TOTAL = 30.0
DT = 0.004
OMEGA0 = 2 * math.pi
SIGMA = 0.10 * OMEGA0
K_CRIT = 2 * SIGMA * math.sqrt(2 * math.pi) / math.pi   # 2 / (pi g(0)) for a gaussian
FIELD_X0, FIELD_X1 = WIDTH * 0.05, WIDTH * 0.95
FIELD_Y0, FIELD_Y1 = HEIGHT * 0.60, HEIGHT * 0.96

omegas = sorted(random.gauss(OMEGA0, SIGMA) for _ in range(N_FLIES))
phases = [random.uniform(0, 2 * math.pi) for _ in range(N_FLIES)]
row_y = [FIELD_Y0 + (FIELD_Y1 - FIELD_Y0) * (i + 0.5) / N_FLIES for i in range(N_FLIES)]

flashes = []
order = []
t = 0.0
while t < T_TOTAL:
    k = K_CRIT * 2.6 * min(1.0, max(0.0, (t - 3.0) / 22.0))
    re = sum(math.cos(p) for p in phases) / N_FLIES
    im = sum(math.sin(p) for p in phases) / N_FLIES
    r, psi = math.hypot(re, im), math.atan2(im, re)
    order.append((t, r, psi))

    for i in range(N_FLIES):
        p = phases[i] + (omegas[i] + k * r * math.sin(psi - phases[i])) * DT
        if p >= 2 * math.pi:
            p -= 2 * math.pi
            flashes.append((t, i))
        phases[i] = p
    t += DT


def time_to_x(t):
    return FIELD_X0 + (FIELD_X1 - FIELD_X0) * t / T_TOTAL


# The swarm rides gently on the waves above
for t, i in flashes:
    x = time_to_x(t) + random.gauss(0, 1.5)
    y = row_y[i] + math.sin(x * 0.012 + i * 0.7) * 6 + wave_field(x, row_y[i]) * 2
    sync = min(1.0, t / T_TOTAL * 1.4)
    col = (
        DEEP_TEAL[0] + (TURQUOISE[0] - DEEP_TEAL[0]) * sync,
        DEEP_TEAL[1] + (TURQUOISE[1] - DEEP_TEAL[1]) * sync,
        DEEP_TEAL[2] + (TURQUOISE[2] - DEEP_TEAL[2]) * sync,
    )
    glow(x, y, 14 + 8 * sync, col, 0.30 + 0.25 * sync)
    ctx.set_source_rgba(*FOAM, 0.55 + 0.4 * sync)
    ctx.arc(x, y, 1.6 + 0.8 * sync, 0, 2 * math.pi)
    ctx.fill()

# Collective rhythm: the mean field r cos(psi) grows out of the noise
WAVE_Y = HEIGHT * 0.555
for width, alpha in ((7.0, 0.06), (3.0, 0.14), (1.2, 0.55)):
    ctx.set_line_width(width)
    ctx.set_source_rgba(*TURQUOISE, alpha)
    for s, (t, r, psi) in enumerate(order[::4]):
        x = time_to_x(t)
        y = WAVE_Y - 46 * r * math.cos(psi)
        if s == 0:
            ctx.move_to(x, y)
        else:
            ctx.line_to(x, y)
    ctx.stroke()

# -------------------------
# Vignette
# -------------------------
ctx.set_operator(cairo.OPERATOR_OVER)
vignette = cairo.RadialGradient(WIDTH / 2, HEIGHT / 2, HEIGHT * 0.35, WIDTH / 2, HEIGHT / 2, WIDTH * 0.72)
vignette.add_color_stop_rgba(0.0, 0, 0, 0, 0.0)
vignette.add_color_stop_rgba(1.0, 0, 0.01, 0.01, 0.6)
ctx.set_source(vignette)
ctx.rectangle(0, 0, WIDTH, HEIGHT)
ctx.fill()

surface.write_to_png("cc_pycairo/gen/cosmos/cosmos_resonance.png")
print("Saved cosmos_resonance.png")
