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

random.seed(5)

AMBER = (1.00, 0.68, 0.20)
GOLD_WHITE = (1.00, 0.93, 0.78)
DEEP_AMBER = (0.62, 0.30, 0.05)
EMBER = (0.92, 0.42, 0.10)

# Each force owns a diagonal; its anchor sits this far from the centre
REACH = 430


def glow(x, y, radius, color, alpha):
    r, g, b = color
    pat = cairo.RadialGradient(x, y, 0, x, y, radius)
    pat.add_color_stop_rgba(0.0, r, g, b, alpha)
    pat.add_color_stop_rgba(0.25, r, g, b, alpha * 0.3)
    pat.add_color_stop_rgba(1.0, r, g, b, 0.0)
    ctx.set_source(pat)
    ctx.arc(x, y, radius, 0, 2 * math.pi)
    ctx.fill()


def polyline(points, color, alpha, width):
    ctx.set_line_width(width)
    ctx.set_source_rgba(*color, alpha)
    ctx.move_to(*points[0])
    for p in points[1:]:
        ctx.line_to(*p)
    ctx.stroke()


def luminous(points, color, alpha, width):
    polyline(points, color, alpha * 0.08, width * 6)
    polyline(points, color, alpha * 0.25, width * 2.5)
    polyline(points, color, alpha, width)


# -------------------------
# Background: warm darkness, a faint burst from the centre
# -------------------------
bg = cairo.RadialGradient(CX, CY, 0, CX, CY, WIDTH * 0.75)
bg.add_color_stop_rgb(0.0, 0.090, 0.050, 0.018)
bg.add_color_stop_rgb(0.5, 0.040, 0.024, 0.010)
bg.add_color_stop_rgb(1.0, 0.016, 0.010, 0.005)
ctx.set_source(bg)
ctx.paint()

for _ in range(12000):
    x = random.uniform(0, WIDTH)
    y = random.uniform(0, HEIGHT)
    ctx.set_source_rgba(0.9, 0.7, 0.45, random.uniform(0.02, 0.06))
    ctx.arc(x, y, random.uniform(0.4, 1.1), 0, 2 * math.pi)
    ctx.fill()

ctx.set_operator(cairo.OPERATOR_ADD)

for _ in range(360):
    a = random.uniform(0, 2 * math.pi)
    r0 = random.uniform(20, 60)
    r1 = r0 + random.expovariate(1 / 240)
    ctx.set_line_width(random.uniform(0.5, 1.2))
    ctx.set_source_rgba(*AMBER, random.uniform(0.02, 0.06))
    ctx.move_to(CX + math.cos(a) * r0, CY + math.sin(a) * r0)
    ctx.line_to(CX + math.cos(a) * r1, CY + math.sin(a) * r1)
    ctx.stroke()

# -------------------------
# Gravity (upper left): test particles leave the centre and fall into orbit.
# a = -GM r / |r|^3 * (1 + beta / r^2); the small correction makes orbits precess.
# -------------------------
MASS_X, MASS_Y = CX - REACH * 0.72, CY - REACH * 0.72
UNIT = math.hypot(CX - MASS_X, CY - MASS_Y)   # GM = 1, distances in units of UNIT
BETA = 0.004


def orbit(speed, tilt, revolutions):
    # start at the centre, moving across the line to the mass
    x, y = (CX - MASS_X) / UNIT, (CY - MASS_Y) / UNIT
    r0 = math.hypot(x, y)
    vx, vy = -y / r0 * speed, x / r0 * speed
    vx, vy = (vx * math.cos(tilt) - vy * math.sin(tilt), vx * math.sin(tilt) + vy * math.cos(tilt))

    def accel(px, py):
        r2 = px * px + py * py + 1e-4
        r = math.sqrt(r2)
        k = -(1 + BETA / r2) / (r2 * r)
        return k * px, k * py

    points = [(MASS_X + x * UNIT, MASS_Y + y * UNIT)]
    ax, ay = accel(x, y)
    angle, last = 0.0, math.atan2(y, x)
    for _ in range(60000):
        r = math.hypot(x, y)
        dt = 0.004 * r ** 1.5
        # velocity Verlet
        vx += ax * dt / 2
        vy += ay * dt / 2
        x += vx * dt
        y += vy * dt
        ax, ay = accel(x, y)
        vx += ax * dt / 2
        vy += ay * dt / 2
        points.append((MASS_X + x * UNIT, MASS_Y + y * UNIT))

        now = math.atan2(y, x)
        angle += (now - last + math.pi) % (2 * math.pi) - math.pi
        last = now
        if abs(angle) > revolutions * 2 * math.pi or r > 3.0:
            break
    return points


for i in range(16):
    speed = 0.30 + 0.55 * i / 15
    tilt = random.uniform(-0.35, 0.35)
    path = orbit(speed, tilt, random.uniform(1.2, 2.6))
    luminous(path, AMBER, 0.22 + 0.25 * (i % 3 == 0), 1.0)
    if i % 4 == 1:
        px, py = path[int(len(path) * random.uniform(0.3, 0.9))]
        glow(px, py, 22, AMBER, 0.6)
        glow(px, py, 5, GOLD_WHITE, 1.0)

# A few fly past fast enough to escape: hyperbolic slingshots
for speed, tilt in ((1.45, 0.25), (1.6, -0.15), (1.8, 0.45)):
    luminous(orbit(speed, tilt, 1.0), EMBER, 0.20, 0.9)

glow(MASS_X, MASS_Y, 260, EMBER, 0.30)
glow(MASS_X, MASS_Y, 70, AMBER, 0.8)
glow(MASS_X, MASS_Y, 22, GOLD_WHITE, 1.0)

# -------------------------
# Electromagnetism (upper right): field lines of +q at the centre and -q,
# traced with RK4 through E = sum q (r - r_i) / |r - r_i|^3
# -------------------------
CHARGES = [(CX, CY, 1.0), (CX + REACH * 0.72, CY - REACH * 0.72, -1.0)]
NEG_X, NEG_Y = CHARGES[1][0], CHARGES[1][1]


def e_field(x, y):
    ex = ey = 0.0
    for qx, qy, q in CHARGES:
        dx, dy = x - qx, y - qy
        r3 = (dx * dx + dy * dy) ** 1.5 + 1e-6
        ex += q * dx / r3
        ey += q * dy / r3
    return ex, ey


def direction(x, y):
    ex, ey = e_field(x, y)
    n = math.hypot(ex, ey) or 1.0
    return ex / n, ey / n


axis = math.atan2(NEG_Y - CY, NEG_X - CX)
for k in range(23):
    start = axis + (k / 22 - 0.5) * 2 * 1.25
    x, y = CX + math.cos(start) * 24, CY + math.sin(start) * 24
    path = [(x, y)]
    h = 4.0
    for _ in range(1400):
        k1 = direction(x, y)
        k2 = direction(x + k1[0] * h / 2, y + k1[1] * h / 2)
        k3 = direction(x + k2[0] * h / 2, y + k2[1] * h / 2)
        k4 = direction(x + k3[0] * h, y + k3[1] * h)
        x += h * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]) / 6
        y += h * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]) / 6
        path.append((x, y))
        if math.hypot(x - NEG_X, y - NEG_Y) < 20 or not (-50 < x < WIDTH + 50 and -50 < y < HEIGHT + 50):
            break
    centre_line = 1 - abs(k / 22 - 0.5) * 2
    luminous(path, AMBER, 0.20 + 0.35 * centre_line, 1.0)

# Equipotentials of +q/-q are Apollonian circles, |P - C| = k |P - E|
d = math.hypot(NEG_X - CX, NEG_Y - CY)
ux, uy = (NEG_X - CX) / d, (NEG_Y - CY) / d
for k in (1.35, 1.7, 2.2, 3.0, 4.2, 6.5):
    centre = k * k * d / (k * k - 1)
    radius = k * d / (k * k - 1)
    ex, ey = CX + ux * centre, CY + uy * centre
    for seg in range(90):
        if seg % 2:
            continue
        a0 = seg / 90 * 2 * math.pi
        ctx.set_line_width(1.0)
        ctx.set_source_rgba(*DEEP_AMBER, 0.55)
        ctx.arc(ex, ey, radius, a0, a0 + 2 * math.pi / 90)
        ctx.stroke()

glow(NEG_X, NEG_Y, 120, EMBER, 0.45)
glow(NEG_X, NEG_Y, 18, GOLD_WHITE, 0.9)
ctx.set_line_width(2.0)
ctx.set_source_rgba(*GOLD_WHITE, 0.8)
ctx.move_to(NEG_X - 8, NEG_Y)
ctx.line_to(NEG_X + 8, NEG_Y)
ctx.stroke()


# -------------------------
# Weak force (lower right): decays in a bubble chamber. Charged tracks bend
# under the Lorentz force, dv/dt = (q B / m) v x z, and lose energy.
# -------------------------
def bubbles(points, alpha, size=1.3, spacing=3.2):
    """Draw a track as a chain of bubbles, like a chamber photograph."""
    travelled = 0.0
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        travelled += math.hypot(x1 - x0, y1 - y0)
        if travelled < spacing:
            continue
        travelled = 0.0
        ctx.set_source_rgba(*GOLD_WHITE, alpha * random.uniform(0.6, 1.0))
        ctx.arc(x1 + random.gauss(0, 0.5), y1 + random.gauss(0, 0.5), size * random.uniform(0.7, 1.2), 0, 2 * math.pi)
        ctx.fill()


def track(x, y, heading, speed, omega, loss, steps):
    """omega = qB/m sets the curl; loss bleeds energy so it spirals in."""
    vx, vy = math.cos(heading) * speed, math.sin(heading) * speed
    points = [(x, y)]
    for _ in range(steps):
        c, s = math.cos(omega), math.sin(omega)
        vx, vy = vx * c - vy * s, vx * s + vy * c
        vx *= 1 - loss
        vy *= 1 - loss
        x += vx
        y += vy
        points.append((x, y))
        if math.hypot(vx, vy) < 0.15:
            break
    return points


def delta_rays(points, count):
    """Knock-on electrons: tiny tight spirals shed along a track."""
    for _ in range(count):
        x, y = random.choice(points[5:-5])
        ray = track(x, y, random.uniform(0, 2 * math.pi), random.uniform(1.2, 2.2),
                    random.choice((-1, 1)) * random.uniform(0.10, 0.18), 0.012, 400)
        bubbles(ray, 0.45, 0.8, 2.2)


def dashed(x0, y0, x1, y1, alpha):
    """Neutral particles leave no bubbles: shown dashed."""
    n = int(math.hypot(x1 - x0, y1 - y0) / 10)
    ctx.set_line_width(1.0)
    ctx.set_source_rgba(*AMBER, alpha)
    for i in range(0, n, 2):
        ctx.move_to(x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n)
        ctx.line_to(x0 + (x1 - x0) * (i + 1) / n, y0 + (y1 - y0) * (i + 1) / n)
    ctx.stroke()


# Beta decay: a neutral from the centre decays at V1 into a proton and a W,
# the W at once into an electron and an antineutrino
V1 = (CX + 210, CY + 250)
V2 = (V1[0] + 70, V1[1] + 22)
dashed(CX + 20, CY + 24, V1[0], V1[1], 0.5)

proton = track(V1[0], V1[1], 1.35, 3.2, 0.0016, 0.0004, 260)
bubbles(proton, 0.85, 1.6, 3.0)
delta_rays(proton, 4)

# W boson: a short-lived wiggle between the two vertices
w_pts = []
for i in range(81):
    t = i / 80
    nx, ny = -(V2[1] - V1[1]), V2[0] - V1[0]
    norm = math.hypot(nx, ny)
    wob = math.sin(t * math.pi * 9) * 6
    w_pts.append((V1[0] + (V2[0] - V1[0]) * t + nx / norm * wob, V1[1] + (V2[1] - V1[1]) * t + ny / norm * wob))
luminous(w_pts, EMBER, 0.8, 1.2)

electron = track(V2[0], V2[1], 0.2, 3.0, -0.035, 0.0035, 2200)
bubbles(electron, 0.9, 1.3, 2.6)
dashed(V2[0], V2[1], V2[0] + 520, V2[1] + 210, 0.35)

# More decays further out: V0 pairs that curl in opposite directions
for _ in range(7):
    a = random.uniform(0.25, 1.30)
    dist = random.uniform(330, 700)
    vx, vy = CX + math.cos(a) * dist, CY + math.sin(a) * dist
    dashed(CX + math.cos(a) * 30, CY + math.sin(a) * 30, vx, vy, 0.18)
    opening = random.uniform(0.15, 0.45)
    speed = random.uniform(2.0, 3.5)
    for sign in (-1, 1):
        t = track(vx, vy, a + sign * opening, speed, sign * random.uniform(0.006, 0.02),
                  random.uniform(0.001, 0.004), 1600)
        bubbles(t, 0.7)
        if random.random() < 0.5:
            delta_rays(t, 2)
    glow(vx, vy, 12, AMBER, 0.6)

for vx, vy in (V1, V2):
    glow(vx, vy, 30, AMBER, 0.7)
    glow(vx, vy, 6, GOLD_WHITE, 1.0)

# -------------------------
# Strong force (lower left): the colour flux tube does not spread like the
# field lines above; it stays a narrow tube, then snaps into quark pairs.
# -------------------------
NUC_X, NUC_Y = CX - REACH * 0.80, CY + REACH * 0.80
TUBE_R = 26
BREAKS = [0.30, 0.52, 0.72]
GAP = 0.035

tx, ty = NUC_X - CX, NUC_Y - CY
tube_len = math.hypot(tx, ty)
ux, uy = tx / tube_len, ty / tube_len
nx, ny = -uy, ux


def tube_point(s, offset):
    return CX + tx * s + nx * offset, CY + ty * s + ny * offset


pieces = []
start = 0.04
for b in BREAKS + [0.86]:
    pieces.append((start, b - GAP))
    start = b + GAP

for s0, s1 in pieces:
    for line in range(30):
        phase = line / 30 * 2 * math.pi
        pts = []
        steps = 90
        for i in range(steps + 1):
            s = s0 + (s1 - s0) * i / steps
            twist = phase + s * 30
            pts.append(tube_point(s, TUBE_R * math.cos(twist)))
        front = 0.5 + 0.5 * math.sin(phase)
        polyline(pts, AMBER, 0.14 + 0.36 * front, 1.0)
    # pinched glow along the piece
    a = tube_point(s0, 0)
    b = tube_point(s1, 0)
    luminous([a, b], EMBER, 0.30, 10)

# Each break leaves a quark and an antiquark facing each other
for b in BREAKS:
    for side in (-1, 1):
        qx, qy = tube_point(b + side * (GAP + 0.004), 0)
        glow(qx, qy, 34, AMBER, 0.8)
        glow(qx, qy, 7, GOLD_WHITE, 1.0)


def fibonacci_sphere(n):
    pts = []
    for i in range(n):
        z = 1 - 2 * (i + 0.5) / n
        r = math.sqrt(1 - z * z)
        a = i * math.pi * (3 - math.sqrt(5))
        pts.append((r * math.cos(a), r * math.sin(a), z))
    return pts


# Nucleus: two Fibonacci shells of nucleons, drawn back to front
nucleons = [(x * 1.0, y * 1.0, z * 1.0, i) for i, (x, y, z) in enumerate(fibonacci_sphere(20))]
nucleons += [(x * 0.45, y * 0.45, z * 0.45, 20 + i) for i, (x, y, z) in enumerate(fibonacci_sphere(6))]
NUC_R = 104
ctx.set_operator(cairo.OPERATOR_OVER)
glow(NUC_X, NUC_Y, 300, EMBER, 0.25)
for x, y, z, i in sorted(nucleons, key=lambda p: p[2]):
    px, py = NUC_X + x * NUC_R, NUC_Y + y * NUC_R
    radius = 34 * (0.85 + 0.15 * (z + 1) / 2)
    proton_like = i % 2 == 0
    base = AMBER if proton_like else DEEP_AMBER
    shade = cairo.RadialGradient(px - radius * 0.35, py - radius * 0.35, radius * 0.1, px, py, radius)
    shade.add_color_stop_rgb(0.0, *GOLD_WHITE)
    shade.add_color_stop_rgb(0.45, *base)
    shade.add_color_stop_rgb(1.0, base[0] * 0.25, base[1] * 0.2, base[2] * 0.2)
    ctx.set_source(shade)
    ctx.arc(px, py, radius, 0, 2 * math.pi)
    ctx.fill()

    # three quarks bound by curly gluon lines in the front nucleons
    if z > 0.55:
        quarks = [(px + math.cos(a) * radius * 0.45, py + math.sin(a) * radius * 0.45)
                  for a in (i, i + 2.09, i + 4.19)]
        for (x0, y0), (x1, y1) in zip(quarks, quarks[1:] + quarks[:1]):
            pts = []
            seg = math.hypot(x1 - x0, y1 - y0)
            for k in range(41):
                t = k / 40
                loop = t * 6 * 2 * math.pi
                # a gluon propagator is a cycloid: forward motion plus a small circle
                gx = x0 + (x1 - x0) * t + (math.cos(loop) - 1) * 2.2 * (x1 - x0) / seg
                gy = y0 + (y1 - y0) * t + math.sin(loop) * 2.2
                pts.append((gx, gy))
            polyline(pts, GOLD_WHITE, 0.55, 0.7)
        for qx, qy in quarks:
            ctx.set_source_rgba(1.0, 0.98, 0.9, 0.95)
            ctx.arc(qx, qy, 2.6, 0, 2 * math.pi)
            ctx.fill()
ctx.set_operator(cairo.OPERATOR_ADD)

# Electron orbits around the nucleus: atomic structure held by the EM force
for k, (rx, ry, rot) in enumerate([(205, 70, 0.5), (250, 92, -0.7), (300, 120, 1.6)]):
    pts = []
    for i in range(241):
        a = i / 240 * 2 * math.pi
        ex, ey = math.cos(a) * rx, math.sin(a) * ry
        pts.append((NUC_X + ex * math.cos(rot) - ey * math.sin(rot),
                    NUC_Y + ex * math.sin(rot) + ey * math.cos(rot)))
    luminous(pts, AMBER, 0.28, 0.8)
    ex, ey = pts[(k * 70 + 30) % 240]
    glow(ex, ey, 16, AMBER, 0.7)
    glow(ex, ey, 4, GOLD_WHITE, 1.0)

# -------------------------
# The central point all four emerge from
# -------------------------
glow(CX, CY, 420, AMBER, 0.25)
glow(CX, CY, 120, AMBER, 0.6)
glow(CX, CY, 34, GOLD_WHITE, 1.0)
for k in range(8):
    a = math.pi / 4 + k * math.pi / 4
    length = 170 if k % 2 == 0 else 90
    ctx.save()
    ctx.translate(CX, CY)
    ctx.rotate(a)
    ctx.scale(1.0, 0.035)
    flare = cairo.RadialGradient(0, 0, 0, 0, 0, length)
    flare.add_color_stop_rgba(0.0, *GOLD_WHITE, 0.45)
    flare.add_color_stop_rgba(1.0, *AMBER, 0.0)
    ctx.set_source(flare)
    ctx.arc(0, 0, length, 0, 2 * math.pi)
    ctx.fill()
    ctx.restore()

# -------------------------
# Vignette
# -------------------------
ctx.set_operator(cairo.OPERATOR_OVER)
vignette = cairo.RadialGradient(CX, CY, HEIGHT * 0.32, CX, CY, WIDTH * 0.75)
vignette.add_color_stop_rgba(0.0, 0, 0, 0, 0.0)
vignette.add_color_stop_rgba(1.0, 0.01, 0.005, 0.0, 0.6)
ctx.set_source(vignette)
ctx.rectangle(0, 0, WIDTH, HEIGHT)
ctx.fill()

surface.write_to_png("cc_pycairo/gen/cosmos/cosmos_forces.png")
print("Saved cosmos_forces.png")
