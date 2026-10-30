import cmath
import math
import random
import cairo

# -------------------------
# Canvas setup
# -------------------------
WIDTH, HEIGHT = 2400, 1500
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

random.seed(4)

INDIGO = (0.36, 0.38, 1.00)
DEEP_INDIGO = (0.16, 0.14, 0.55)
PERIWINKLE = (0.66, 0.72, 1.00)
VIOLET = (0.58, 0.36, 1.00)
WHITE = (0.94, 0.95, 1.00)


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


# -------------------------
# Camera: a pinhole floating between two sheets, pitched slightly down
# -------------------------
CAM_Y, CAM_Z = 1.0, -3.0
PITCH = 0.10
FOCAL = 1100
SCREEN_CX, SCREEN_CY = WIDTH / 2, HEIGHT * 0.50


def project(x, y, z):
    """World point to screen, plus the camera depth for fading."""
    dy, dz = y - CAM_Y, z - CAM_Z
    zc = -dy * math.sin(PITCH) + dz * math.cos(PITCH)
    yc = dy * math.cos(PITCH) + dz * math.sin(PITCH)
    return SCREEN_CX + FOCAL * x / zc, SCREEN_CY - FOCAL * yc / zc, zc


HORIZON_Y = SCREEN_CY - FOCAL * math.tan(PITCH)

# -------------------------
# Curvature: wells of a softened Newtonian potential, -m / sqrt(r^2 + e^2),
# and ripples spreading from an orbiting binary
# -------------------------
MASSES = [(-1.7, 3.2, 1.3), (2.6, 6.5, 0.9), (-4.5, 10.0, 0.8), (0.6, 14.0, 0.7)]
BINARY = (1.6, 1.6)
SOFTEN = 0.25
SHEET_GAP = 2.3


def warp(x, z):
    y = 0.0
    for mx, mz, m in MASSES:
        y -= 0.42 * m / math.sqrt((x - mx) ** 2 + (z - mz) ** 2 + SOFTEN ** 2)
    bx, bz = BINARY
    r = math.hypot(x - bx, z - bz)
    spiral = math.atan2(z - bz, x - bx) * 2
    y -= 0.06 / math.sqrt(r * r + 0.10)
    y += 0.05 * math.sin(7.0 * r - spiral) * math.exp(-r / 3.5) * min(1.0, r * 2)
    return y


def upper_warp(x, z):
    """The second sheet overhead, pulled up where the first is pulled down."""
    y = SHEET_GAP
    for mx, mz, m in MASSES:
        y += 0.30 * m / math.sqrt((x - mx) ** 2 + (z - mz) ** 2 + 0.8)
    return y + 0.06 * math.sin(x * 1.1 + z * 0.6)


# -------------------------
# Background: deep indigo, brightest at the horizon
# -------------------------
bg = cairo.LinearGradient(0, 0, 0, HEIGHT)
bg.add_color_stop_rgb(0.0, 0.012, 0.010, 0.050)
bg.add_color_stop_rgb(HORIZON_Y / HEIGHT, 0.060, 0.050, 0.200)
bg.add_color_stop_rgb(1.0, 0.012, 0.010, 0.050)
ctx.set_source(bg)
ctx.paint()

ctx.set_operator(cairo.OPERATOR_ADD)

haze = cairo.RadialGradient(SCREEN_CX, HORIZON_Y, 0, SCREEN_CX, HORIZON_Y, WIDTH * 0.45)
haze.add_color_stop_rgba(0.0, *INDIGO, 0.22)
haze.add_color_stop_rgba(1.0, *INDIGO, 0.0)
ctx.set_source(haze)
ctx.paint()


# -------------------------
# Spacetime sheets as wireframe meshes
# -------------------------
def mesh_line(points, color, base_alpha, rest_y):
    """
    Stroke a polyline of world points segment by segment so each piece
    fades with distance and brightens the further it is pulled from rest.
    """
    projected = [(project(x, y, z), y) for x, y, z in points]
    for ((x0, y0, d0), w0), ((x1, y1, d1), _) in zip(projected, projected[1:]):
        if d0 < 0.6 or d1 < 0.6:
            continue
        if max(x0, x1) < -50 or min(x0, x1) > WIDTH + 50:
            continue
        fade = math.exp(-max(0.0, d0 - 3.0) / 8.0)
        bend = min(1.0, abs(w0 - rest_y) / 0.9)
        col = mix(color, WHITE, bend)
        alpha = base_alpha * fade * (0.55 + 1.0 * bend)
        width = max(0.6, min(2.2, 3.0 / d0))
        for w, a in ((width * 4, 0.10), (width, 1.0)):
            ctx.set_line_width(w)
            ctx.set_source_rgba(*col, alpha * a)
            ctx.move_to(x0, y0)
            ctx.line_to(x1, y1)
            ctx.stroke()


def draw_sheet(height_fn, color, alpha, spacing, rest_y):
    x_min, x_max, z_min, z_max = -11.0, 11.0, -2.0, 26.0
    step = 0.08
    for k in range(int((x_max - x_min) / spacing) + 1):
        x = x_min + k * spacing
        zs = [z_min + i * step for i in range(int((z_max - z_min) / step))]
        mesh_line([(x, height_fn(x, z), z) for z in zs], color, alpha, rest_y)
    for k in range(int((z_max - z_min) / spacing) + 1):
        z = z_min + k * spacing
        xs = [x_min + i * step for i in range(int((x_max - x_min) / step))]
        mesh_line([(x, height_fn(x, z), z) for x in xs], color, alpha, rest_y)


draw_sheet(upper_warp, VIOLET, 0.34, 0.40, SHEET_GAP)
draw_sheet(warp, INDIGO, 0.36, 0.25, 0.0)

# Masses glowing at the bottom of their wells
for mx, mz, m in MASSES:
    sx, sy, d = project(mx, warp(mx, mz), mz)
    size = 160 * m / d
    glow(sx, sy, size * 6, INDIGO, 0.30)
    glow(sx, sy, size * 1.5, PERIWINKLE, 0.7)
    glow(sx, sy, size * 0.5, WHITE, 1.0)

for side in (-1, 1):
    bx, bz = BINARY[0] + side * 0.10, BINARY[1]
    sx, sy, d = project(bx, warp(bx, bz), bz)
    glow(sx, sy, 160 / d, PERIWINKLE, 0.6)
    glow(sx, sy, 36 / d, WHITE, 1.0)


# -------------------------
# Strings: open strings end on the two sheets and vibrate in
# standing-wave modes, sum a_n sin(n pi s) cos(n t + phase_n)
# -------------------------
def draw_string(points3d, color, alpha, width=1.0):
    pts = [project(*p) for p in points3d]
    if min(d for _, _, d in pts) < 0.6:
        return
    for w, a in ((width * 7, 0.05), (width * 2.5, 0.16), (width, 0.7)):
        ctx.set_line_width(w)
        ctx.set_source_rgba(*color, alpha * a)
        ctx.move_to(pts[0][0], pts[0][1])
        for x, y, _ in pts[1:]:
            ctx.line_to(x, y)
        ctx.stroke()


# Two colonnades receding either side of the vanishing point, like a loom
strings = []
for _ in range(20):
    z0 = random.uniform(0.0, 16.0)
    x0 = random.choice((-1, 1)) * random.uniform(1.6, 4.8)
    strings.append((x0, z0))
strings.sort(key=lambda s: -s[1])   # far strings first

for x0, z0 in strings:
    x1, z1 = x0 + random.uniform(-0.6, 0.6), z0 + random.uniform(-0.6, 0.6)
    p0 = (x0, warp(x0, z0), z0)
    p1 = (x1, upper_warp(x1, z1), z1)
    modes = [(n, random.uniform(0.04, 0.20) / n, random.uniform(0, 2 * math.pi)) for n in range(1, 5)]
    near = max(0.0, 1.0 - z0 / 18.0)

    for snap in range(7):
        t = snap / 7 * math.pi
        pts = []
        for i in range(81):
            s = i / 80
            amp = sum(a * math.sin(n * math.pi * s) * math.cos(n * t + ph) for n, a, ph in modes)
            pts.append((
                p0[0] + (p1[0] - p0[0]) * s + amp,
                p0[1] + (p1[1] - p0[1]) * s,
                p0[2] + (p1[2] - p0[2]) * s + amp * 0.3,
            ))
        if snap == 0:
            draw_string(pts, WHITE, 0.35 + 0.45 * near, 1.2)
        else:
            draw_string(pts, PERIWINKLE, 0.12 + 0.18 * near)

    for p in (p0, p1):
        sx, sy, d = project(*p)
        if d > 0.6:
            glow(sx, sy, 90 / d, WHITE, 0.5)

# Closed strings drift free between the sheets: loops with a small Fourier wobble
for _ in range(12):
    cz = random.uniform(2.0, 12.0)
    cx = random.choice((-1, 1)) * random.uniform(1.0, 4.0)
    cy = random.uniform(0.5, 1.8)
    radius = random.uniform(0.12, 0.30)
    modes = [(n, random.uniform(0.02, 0.07), random.uniform(0, 2 * math.pi)) for n in range(2, 5)]
    tilt = random.uniform(0, math.pi)
    for snap in range(4):
        t = snap / 4 * math.pi
        pts = []
        for i in range(121):
            a = i / 120 * 2 * math.pi
            r = radius * (1 + sum(m * math.cos(n * a + ph + n * t) for n, m, ph in modes))
            u, v = r * math.cos(a), r * math.sin(a)
            pts.append((cx + u * math.cos(tilt), cy + v, cz + u * math.sin(tilt)))
        draw_string(pts, PERIWINKLE if snap == 0 else VIOLET, 0.6 if snap == 0 else 0.22)


# -------------------------
# Hidden dimensions at the vanishing point: a Calabi-Yau cross section,
# z1^5 + z2^5 = 1 with z1 = e^(2 pi i k1 / 5) cos(u)^(2/5),
#                       z2 = e^(2 pi i k2 / 5) sin(u)^(2/5)
# -------------------------
N_CY = 5
CY_X, CY_Y, CY_SIZE = SCREEN_CX, HORIZON_Y, 125
CY_ALPHA = math.pi / 4
CY_ROT = (0.55, 0.35)


def calabi_yau(k1, k2, a, b):
    u = complex(a, b)
    z1 = cmath.exp(2j * math.pi * k1 / N_CY) * cmath.cos(u) ** (2 / N_CY)
    z2 = cmath.exp(2j * math.pi * k2 / N_CY) * cmath.sin(u) ** (2 / N_CY)
    x, y = z1.real, z2.real
    z = math.cos(CY_ALPHA) * z1.imag + math.sin(CY_ALPHA) * z2.imag
    # turn it in 3D, then flatten with a little perspective
    rx, ry = CY_ROT
    y, z = y * math.cos(rx) - z * math.sin(rx), y * math.sin(rx) + z * math.cos(rx)
    x, z = x * math.cos(ry) + z * math.sin(ry), -x * math.sin(ry) + z * math.cos(ry)
    depth = 4.0 / (4.0 + z)
    return CY_X + x * CY_SIZE * depth, CY_Y - y * CY_SIZE * depth


glow(CY_X, CY_Y, CY_SIZE * 2.6, INDIGO, 0.35)
for k1 in range(N_CY):
    for k2 in range(N_CY):
        tone = (k1 * N_CY + k2) / (N_CY * N_CY)
        col = mix(PERIWINKLE, VIOLET, tone)
        for fixed_a in (True, False):
            for i in range(11):
                ctx.new_path()
                for j in range(25):
                    if fixed_a:
                        a, b = (math.pi / 2) * i / 10, -0.9 + 1.8 * j / 24
                    else:
                        a, b = (math.pi / 2) * j / 24, -0.9 + 1.8 * i / 10
                    ctx.line_to(*calabi_yau(k1, k2, a, b))
                ctx.set_line_width(0.8)
                ctx.set_source_rgba(*col, 0.22)
                ctx.stroke()

glow(CY_X, CY_Y, 40, WHITE, 0.45)

# -------------------------
# Vignette
# -------------------------
ctx.set_operator(cairo.OPERATOR_OVER)
vignette = cairo.RadialGradient(SCREEN_CX, HORIZON_Y, HEIGHT * 0.30, SCREEN_CX, HORIZON_Y, WIDTH * 0.72)
vignette.add_color_stop_rgba(0.0, 0, 0, 0, 0.0)
vignette.add_color_stop_rgba(1.0, 0.0, 0.0, 0.02, 0.65)
ctx.set_source(vignette)
ctx.rectangle(0, 0, WIDTH, HEIGHT)
ctx.fill()

surface.write_to_png("cc_pycairo/gen/cosmos/cosmos_spacetime.png")
print("Saved cosmos_spacetime.png")
