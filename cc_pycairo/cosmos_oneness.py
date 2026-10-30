import math
import random
import cairo

# -------------------------
# Canvas setup
# -------------------------
WIDTH, HEIGHT = 1800, 1800
CX, CY = WIDTH / 2, HEIGHT / 2
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

random.seed(7)

GOLD = (1.00, 0.76, 0.28)
PALE_GOLD = (1.00, 0.93, 0.72)
AMBER = (0.80, 0.45, 0.08)
BRONZE = (0.45, 0.25, 0.06)

R_SPHERE = 230
AXIS_TILT = 0.30      # polarity axis leans in the picture plane
AXIS_NOD = 0.22       # and towards the viewer
CAMERA = R_SPHERE * 7


def glow(x, y, radius, color, alpha):
    r, g, b = color
    pat = cairo.RadialGradient(x, y, 0, x, y, radius)
    pat.add_color_stop_rgba(0.0, r, g, b, alpha)
    pat.add_color_stop_rgba(0.25, r, g, b, alpha * 0.3)
    pat.add_color_stop_rgba(1.0, r, g, b, 0.0)
    ctx.set_source(pat)
    ctx.arc(x, y, radius, 0, 2 * math.pi)
    ctx.fill()


def mix(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def to_view(p):
    """Axis frame (y along the polarity axis) to view frame (z towards the viewer)."""
    x, y, z = p
    y, z = y * math.cos(AXIS_NOD) - z * math.sin(AXIS_NOD), y * math.sin(AXIS_NOD) + z * math.cos(AXIS_NOD)
    x, y = x * math.cos(AXIS_TILT) - y * math.sin(AXIS_TILT), x * math.sin(AXIS_TILT) + y * math.cos(AXIS_TILT)
    return x, y, z


def project(p):
    x, y, z = p
    s = CAMERA / (CAMERA - z)
    return CX + x * s, CY - y * s, z


def hidden(p):
    """Behind the sphere, as seen from the front."""
    x, y, z = p
    return z < 0 and x * x + y * y < R_SPHERE * R_SPHERE


def luminous_path(points, color, alpha, width):
    for w, a in ((width * 6, 0.07), (width * 2.4, 0.22), (width, 1.0)):
        ctx.set_line_width(w)
        ctx.set_source_rgba(*color, alpha * a)
        ctx.move_to(*points[0])
        for p in points[1:]:
            ctx.line_to(*p)
        ctx.stroke()


def draw_3d_curve(points3d, color, alpha, width):
    """Split a 3D curve where it passes behind the sphere; dim the far side."""
    run, run_back = [], None
    for p in points3d:
        back = hidden(p)
        if run and back != run_back:
            if len(run) > 1:
                luminous_path(run, color, alpha * (0.18 if run_back else 1.0), width)
            run = run[-1:]
        sx, sy, z = project(p)
        run.append((sx, sy))
        run_back = back
    if len(run) > 1:
        luminous_path(run, color, alpha * (0.18 if run_back else 1.0), width)


# -------------------------
# Background: warm dark, lit from the centre
# -------------------------
bg = cairo.RadialGradient(CX, CY, 0, CX, CY, WIDTH * 0.72)
bg.add_color_stop_rgb(0.0, 0.110, 0.070, 0.020)
bg.add_color_stop_rgb(0.45, 0.040, 0.025, 0.008)
bg.add_color_stop_rgb(1.0, 0.010, 0.006, 0.002)
ctx.set_source(bg)
ctx.paint()

for _ in range(12000):
    x = random.uniform(0, WIDTH)
    y = random.uniform(0, HEIGHT)
    ctx.set_source_rgba(0.95, 0.8, 0.5, random.uniform(0.02, 0.06))
    ctx.arc(x, y, random.uniform(0.4, 1.1), 0, 2 * math.pi)
    ctx.fill()

ctx.set_operator(cairo.OPERATOR_ADD)

# -------------------------
# Vibration: spherical wavefronts, amplitude falling as 1/r,
# brightness carried in packets, each front rippled with n-fold symmetry
# -------------------------
for k in range(46):
    r = R_SPHERE * 1.25 + k * 15
    packet = 0.5 + 0.5 * math.cos(k * 2 * math.pi / 9)
    alpha = 0.45 * packet ** 2 * (R_SPHERE * 1.25 / r) + 0.03
    folds = (6, 8, 12)[k % 3]
    wobble = 2.5 + k * 0.12
    phase = k * 0.4
    ctx.new_path()
    for i in range(721):
        a = i / 720 * 2 * math.pi
        rr = r + wobble * math.sin(folds * a + phase)
        ctx.line_to(CX + math.cos(a) * rr, CY + math.sin(a) * rr)
    ctx.set_line_width(1.0 + packet)
    ctx.set_source_rgba(*GOLD, alpha)
    ctx.stroke()

# Radiance: fine rays, intensity falling with distance
for _ in range(700):
    a = random.uniform(0, 2 * math.pi)
    r0 = R_SPHERE * random.uniform(1.02, 1.1)
    r1 = r0 + random.expovariate(1 / (R_SPHERE * 1.1))
    ray = cairo.LinearGradient(CX + math.cos(a) * r0, CY + math.sin(a) * r0,
                               CX + math.cos(a) * r1, CY + math.sin(a) * r1)
    ray.add_color_stop_rgba(0.0, *PALE_GOLD, random.uniform(0.05, 0.16))
    ray.add_color_stop_rgba(1.0, *GOLD, 0.0)
    ctx.set_source(ray)
    ctx.set_line_width(random.uniform(0.6, 1.6))
    ctx.move_to(CX + math.cos(a) * r0, CY + math.sin(a) * r0)
    ctx.line_to(CX + math.cos(a) * r1, CY + math.sin(a) * r1)
    ctx.stroke()

glow(CX, CY, R_SPHERE * 3.2, AMBER, 0.30)
glow(CX, CY, R_SPHERE * 1.6, GOLD, 0.35)

# -------------------------
# Polarity: dipole field lines, r = L sin^2(theta), swept around the axis
# -------------------------
for L in (1.4, 1.9, 2.6, 3.6):
    for j in range(8):
        phi = j / 8 * 2 * math.pi + 0.2
        pts = []
        for i in range(401):
            theta = i / 400 * math.pi
            r = L * R_SPHERE * math.sin(theta) ** 2
            if r < R_SPHERE:
                continue
            p = (r * math.sin(theta) * math.cos(phi), r * math.cos(theta), r * math.sin(theta) * math.sin(phi))
            pts.append(to_view(p))
        if len(pts) > 2:
            outer = (L - 1.4) / (3.6 - 1.4)
            draw_3d_curve(pts, mix(PALE_GOLD, GOLD, outer), 0.60 - 0.25 * outer, 1.1)

# Polar jets along the axis
for sign, col in ((1, PALE_GOLD), (-1, AMBER)):
    for _ in range(900):
        h = R_SPHERE * (1.0 + random.expovariate(1 / 1.3))
        spread = (h - R_SPHERE) * random.gauss(0, 0.05)
        p = to_view((spread, sign * h, random.gauss(0, 1) * spread * 0.3))
        sx, sy, _ = project(p)
        if hidden(p):
            continue
        ctx.set_source_rgba(*col, random.uniform(0.15, 0.45) * math.exp(-(h - R_SPHERE) / (R_SPHERE * 2.5)))
        ctx.arc(sx, sy, random.uniform(0.6, 1.6), 0, 2 * math.pi)
        ctx.fill()


# -------------------------
# The sphere: a Fibonacci lattice whose radius vibrates with a
# spherical harmonic, Y_6^4 ~ P_6^4(cos theta) cos(4 phi)
# -------------------------
def legendre(l, m, x):
    pmm = 1.0
    somx2 = math.sqrt(max(0.0, 1 - x * x))
    for i in range(1, m + 1):
        pmm *= -(2 * i - 1) * somx2
    if l == m:
        return pmm
    pmmp1 = x * (2 * m + 1) * pmm
    if l == m + 1:
        return pmmp1
    for ll in range(m + 2, l + 1):
        pmm, pmmp1 = pmmp1, ((2 * ll - 1) * x * pmmp1 - (ll + m - 1) * pmm) / (ll - m)
    return pmmp1


L_SH, M_SH = 6, 4
N_POINTS = 7000
lattice = []
for i in range(N_POINTS):
    cos_t = 1 - 2 * (i + 0.5) / N_POINTS
    theta = math.acos(cos_t)
    phi = i * math.pi * (3 - math.sqrt(5))
    lattice.append((theta, phi, legendre(L_SH, M_SH, cos_t) * math.cos(M_SH * phi)))
y_max = max(abs(v) for _, _, v in lattice)

body = cairo.RadialGradient(CX - R_SPHERE * 0.3, CY - R_SPHERE * 0.35, R_SPHERE * 0.1, CX, CY, R_SPHERE * 1.05)
body.add_color_stop_rgba(0.0, *GOLD, 0.30)
body.add_color_stop_rgba(0.6, *AMBER, 0.16)
body.add_color_stop_rgba(1.0, *BRONZE, 0.08)
ctx.set_source(body)
ctx.arc(CX, CY, R_SPHERE * 1.05, 0, 2 * math.pi)
ctx.fill()

for theta, phi, value in lattice:
    v = value / y_max
    r = R_SPHERE * (1 + 0.09 * v)
    p = to_view((r * math.sin(theta) * math.cos(phi), r * math.cos(theta), r * math.sin(theta) * math.sin(phi)))
    if p[2] < 0:
        continue
    sx, sy, _ = project(p)
    facing = p[2] / r                       # 1 at the centre, 0 at the limb
    rim = (1 - facing) ** 3
    crest = (0.5 + 0.5 * v) ** 2
    col = mix(AMBER, PALE_GOLD, crest)
    ctx.set_source_rgba(*col, 0.06 + 0.75 * crest * (0.3 + 0.7 * facing) + 0.35 * rim)
    ctx.arc(sx, sy, 0.8 + 1.4 * facing * (0.4 + 0.6 * crest), 0, 2 * math.pi)
    ctx.fill()

# Limb light
for w, a in ((14, 0.06), (5, 0.18), (1.6, 0.6)):
    ctx.set_line_width(w)
    ctx.set_source_rgba(*PALE_GOLD, a)
    ctx.arc(CX, CY, R_SPHERE * 1.01, 0, 2 * math.pi)
    ctx.stroke()

# -------------------------
# Unity: a (2, 45) torus knot, a coiled halo around the sphere
# -------------------------
P_KNOT, Q_KNOT = 2, 45
R_MAJOR, R_MINOR = R_SPHERE * 1.42, R_SPHERE * 0.11
KNOT_TILT = 0.55      # the torus faces the viewer, tipped back a little
knot = []
for i in range(4001):
    t = i / 4000 * 2 * math.pi
    ring = R_MAJOR + R_MINOR * math.cos(Q_KNOT * t)
    x, y, z = ring * math.cos(P_KNOT * t), ring * math.sin(P_KNOT * t), R_MINOR * math.sin(Q_KNOT * t)
    y, z = y * math.cos(KNOT_TILT) - z * math.sin(KNOT_TILT), y * math.sin(KNOT_TILT) + z * math.cos(KNOT_TILT)
    knot.append((x, y, z))
draw_3d_curve(knot, GOLD, 0.45, 1.0)

# Poles: one pale, one deep
for sign, col in ((1, PALE_GOLD), (-1, AMBER)):
    p = to_view((0, sign * R_SPHERE * 1.07, 0))
    sx, sy, _ = project(p)
    alpha = 0.25 if hidden(p) else 1.0
    glow(sx, sy, 90, col, 0.5 * alpha)
    glow(sx, sy, 16, PALE_GOLD, 0.9 * alpha)

glow(CX, CY, R_SPHERE * 0.5, PALE_GOLD, 0.25)

# Gold dust drifting outward
for _ in range(5000):
    a = random.uniform(0, 2 * math.pi)
    r = R_SPHERE * (1.1 + random.expovariate(0.7))
    x, y = CX + math.cos(a) * r, CY + math.sin(a) * r
    ctx.set_source_rgba(*PALE_GOLD, random.uniform(0.08, 0.4))
    ctx.arc(x, y, random.uniform(0.4, 1.4), 0, 2 * math.pi)
    ctx.fill()

# -------------------------
# Vignette
# -------------------------
ctx.set_operator(cairo.OPERATOR_OVER)
vignette = cairo.RadialGradient(CX, CY, HEIGHT * 0.32, CX, CY, WIDTH * 0.75)
vignette.add_color_stop_rgba(0.0, 0, 0, 0, 0.0)
vignette.add_color_stop_rgba(1.0, 0.01, 0.005, 0.0, 0.65)
ctx.set_source(vignette)
ctx.rectangle(0, 0, WIDTH, HEIGHT)
ctx.fill()

surface.write_to_png("cc_pycairo/gen/cosmos/cosmos_oneness.png")
print("Saved cosmos_oneness.png")
