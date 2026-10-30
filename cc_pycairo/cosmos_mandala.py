import math
import random
import cairo

# -------------------------
# Canvas setup
# -------------------------
WIDTH, HEIGHT = 2000, 2000
CX, CY = WIDTH / 2, HEIGHT / 2
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

random.seed(6)

MAGENTA = (1.00, 0.22, 0.72)
ROSE = (1.00, 0.62, 0.88)
PLUM = (0.45, 0.08, 0.40)
PEARL = (1.00, 0.92, 0.98)

SYMMETRY = 12
R_ORBITAL = 250          # quantum core
R_INNER = 330            # sand begins
R_PLATE = 760            # edge of the vibrating plate


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


def polar_path(radius_fn, steps=720):
    ctx.new_path()
    for i in range(steps + 1):
        a = i / steps * 2 * math.pi
        r = radius_fn(a)
        ctx.line_to(CX + math.cos(a) * r, CY + math.sin(a) * r)


# -------------------------
# Bessel functions from their integral, J_n(x) = 1/pi * int_0^pi cos(n t - x sin t) dt,
# tabulated once, then looked up
# -------------------------
X_MAX = 32.0
TABLE_N = 3200


def bessel_table(n):
    table = []
    samples = 400
    for i in range(TABLE_N + 1):
        x = X_MAX * i / TABLE_N
        total = 0.0
        for k in range(samples):
            t = (k + 0.5) / samples * math.pi
            total += math.cos(n * t - x * math.sin(t))
        table.append(total / samples)
    return table


def bessel(table, x):
    f = x / X_MAX * TABLE_N
    i = min(int(f), TABLE_N - 1)
    return table[i] + (table[i + 1] - table[i]) * (f - i)


def zeros(table):
    out = []
    for i in range(1, TABLE_N):
        if table[i] == 0 or (table[i] > 0) != (table[i + 1] > 0):
            out.append(X_MAX * (i + table[i] / (table[i] - table[i + 1])) / TABLE_N)
    return out


# Modes (n, m, weight) of a clamped circular drum: J_n(j_nm r / R) cos(n theta),
# where j_nm is the m-th zero of J_n, so the rim never moves
MODES = [(6, 5, 1.0), (18, 3, 0.9), (12, 2, 0.6), (0, 8, 0.3)]
TABLES = {n: bessel_table(n) for n, _, _ in MODES}
MODES = [(n, zeros(TABLES[n])[m - 1], w) for n, m, w in MODES]


def membrane(r, a):
    rho = r / R_PLATE
    return sum(w * bessel(TABLES[n], k * rho) * math.cos(n * a) for n, k, w in MODES)


# -------------------------
# Hydrogen orbital |psi_9,6,6|^2 in the equatorial plane:
# R_nl ~ rho^l e^(-rho/2) L_(n-l-1)^(2l+1)(rho), rho = 2r/n, angular part cos(6 phi)
# -------------------------
N_Q, L_Q, M_Q = 9, 6, 6


def laguerre(k, alpha, x):
    if k == 0:
        return 1.0
    prev, cur = 1.0, 1.0 + alpha - x
    for j in range(1, k):
        prev, cur = cur, ((2 * j + 1 + alpha - x) * cur - (j + alpha) * prev) / (j + 1)
    return cur


def radial(r):
    rho = 2 * r / N_Q
    return rho ** L_Q * math.exp(-rho / 2) * laguerre(N_Q - L_Q - 1, 2 * L_Q + 1, rho)


# Fit the orbital's extent (in Bohr radii) to the core radius
radii = [i * 0.25 for i in range(1, 1200)]
weights = [radial(r) ** 2 * r for r in radii]
total, running, extent = sum(weights), 0.0, radii[-1]
for r, w in zip(radii, weights):
    running += w
    if running > 0.995 * total:
        extent = r
        break
BOHR = R_ORBITAL / extent
peak = max(radial(r) ** 2 for r in radii)

# -------------------------
# Background: deep plum
# -------------------------
bg = cairo.RadialGradient(CX, CY, 0, CX, CY, WIDTH * 0.72)
bg.add_color_stop_rgb(0.0, 0.110, 0.020, 0.090)
bg.add_color_stop_rgb(0.55, 0.050, 0.008, 0.042)
bg.add_color_stop_rgb(1.0, 0.016, 0.003, 0.014)
ctx.set_source(bg)
ctx.paint()

for _ in range(10000):
    x = random.uniform(0, WIDTH)
    y = random.uniform(0, HEIGHT)
    ctx.set_source_rgba(0.9, 0.6, 0.85, random.uniform(0.02, 0.06))
    ctx.arc(x, y, random.uniform(0.4, 1.1), 0, 2 * math.pi)
    ctx.fill()

ctx.set_operator(cairo.OPERATOR_ADD)
glow(CX, CY, R_PLATE * 1.25, PLUM, 0.35)

# -------------------------
# Rays: waveforms travelling outward between the petals
# -------------------------
for k in range(SYMMETRY * 4):
    a0 = k / (SYMMETRY * 4) * 2 * math.pi
    major = k % 4 == 0
    pts = []
    for i in range(301):
        r = R_PLATE + 140 + i * 2.2
        envelope = math.sin(i / 300 * math.pi)
        offset = math.sin(r * 0.06) * (10 if major else 5) * envelope / r
        a = a0 + offset
        pts.append((CX + math.cos(a) * r, CY + math.sin(a) * r))
    ctx.set_line_width(1.6 if major else 0.8)
    ctx.set_source_rgba(*ROSE, 0.30 if major else 0.14)
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.stroke()

# Stardust beyond the plate, thinning outward
for _ in range(9000):
    a = random.uniform(0, 2 * math.pi)
    r = R_PLATE * (1.0 + random.expovariate(3.0))
    x, y = CX + math.cos(a) * r, CY + math.sin(a) * r
    ctx.set_source_rgba(*ROSE, random.uniform(0.08, 0.35))
    ctx.arc(x, y, random.uniform(0.5, 1.4), 0, 2 * math.pi)
    ctx.fill()

# -------------------------
# Lotus: layered petals, r = R1 + (R2 - R1) (1 - |sin(6 theta)|)^p,
# pointed where sin(6 theta) = 0
# -------------------------
for layer, (r1, r2, power, shift, alpha) in enumerate([
    (R_PLATE + 10, R_PLATE + 185, 1.6, 0.0, 0.55),
    (R_PLATE + 10, R_PLATE + 140, 1.5, math.pi / 12, 0.42),
    (R_PLATE + 10, R_PLATE + 90, 1.3, 0.0, 0.30),
]):
    def petal(a, r1=r1, r2=r2, power=power, shift=shift):
        return r1 + (r2 - r1) * (1 - abs(math.sin(6 * (a + shift)))) ** power

    for w, a in ((7.0, 0.07), (2.4, 0.22), (1.0, 1.0)):
        polar_path(petal, 1440)
        ctx.set_line_width(w)
        ctx.set_source_rgba(*MAGENTA, alpha * a)
        ctx.stroke()

# Plate rim
for w, a in ((9.0, 0.08), (3.0, 0.25), (1.2, 0.9)):
    ctx.set_line_width(w)
    ctx.set_source_rgba(*ROSE, a)
    ctx.arc(CX, CY, R_PLATE, 0, 2 * math.pi)
    ctx.stroke()

# -------------------------
# Chladni sand: particles settle where the membrane does not move
# -------------------------
SIGMA = 0.015
accepted = 0
while accepted < 130000:
    r = R_PLATE * math.sqrt(random.uniform((R_INNER / R_PLATE) ** 2, 1.0))
    a = random.uniform(0, 2 * math.pi)
    u = membrane(r, a)
    if random.random() > math.exp(-(u / SIGMA) ** 2):
        continue
    accepted += 1
    x, y = CX + math.cos(a) * r, CY + math.sin(a) * r
    edge = (r - R_INNER) / (R_PLATE - R_INNER)
    col = mix(PEARL, MAGENTA, edge * 0.8)
    ctx.set_source_rgba(*col, random.uniform(0.12, 0.35))
    ctx.arc(x, y, random.uniform(0.6, 1.4), 0, 2 * math.pi)
    ctx.fill()

# Faint glow where the plate swings hardest (antinodes)
for _ in range(18000):
    r = R_PLATE * math.sqrt(random.uniform((R_INNER / R_PLATE) ** 2, 1.0))
    a = random.uniform(0, 2 * math.pi)
    u = abs(membrane(r, a))
    if u < 0.25 or random.random() > u:
        continue
    x, y = CX + math.cos(a) * r, CY + math.sin(a) * r
    ctx.set_source_rgba(*PLUM, 0.05)
    ctx.arc(x, y, random.uniform(3, 7), 0, 2 * math.pi)
    ctx.fill()

# -------------------------
# Standing-wave rings between the sand and the core:
# r = R + A sin(k theta) cos(t), drawn at several moments
# -------------------------
for base, k, amp in ((R_ORBITAL + 28, 24, 9), (R_INNER - 22, 36, 6)):
    for snap in range(9):
        t = snap / 8 * math.pi
        polar_path(lambda a: base + amp * math.sin(k * a) * math.cos(t), 1440)
        ctx.set_line_width(1.0)
        ctx.set_source_rgba(*ROSE, 0.10 if 0 < snap < 8 else 0.45)
        ctx.stroke()

# Bead rings: particles with dihedral symmetry, sized by cos(6 theta)
for radius, count in ((R_INNER - 2, 96), (R_PLATE - 30, 144), (R_PLATE + 192, 48)):
    for j in range(count):
        a = j / count * 2 * math.pi
        size = 1.6 + 1.4 * abs(math.cos(6 * a))
        x, y = CX + math.cos(a) * radius, CY + math.sin(a) * radius
        glow(x, y, size * 5, MAGENTA, 0.30)
        ctx.set_source_rgba(*PEARL, 0.9)
        ctx.arc(x, y, size * 0.6, 0, 2 * math.pi)
        ctx.fill()

# -------------------------
# Quantum core: rejection-sampled electron density
# -------------------------
glow(CX, CY, R_ORBITAL * 1.2, MAGENTA, 0.18)
accepted = 0
while accepted < 70000:
    r = R_ORBITAL * math.sqrt(random.random())
    a = random.uniform(0, 2 * math.pi)
    density = radial(r / BOHR) ** 2 * math.cos(M_Q * a) ** 2 / peak
    # accept on a softened density so the faint outer lobes still show
    if random.random() > density ** 0.6:
        continue
    accepted += 1
    x, y = CX + math.cos(a) * r, CY + math.sin(a) * r
    col = mix(MAGENTA, PEARL, min(1.0, density * 1.3))
    ctx.set_source_rgba(*col, 0.16 + 0.2 * density)
    ctx.arc(x, y, random.uniform(0.5, 1.2), 0, 2 * math.pi)
    ctx.fill()

# The nucleus: a single bright point
glow(CX, CY, 46, MAGENTA, 0.6)
glow(CX, CY, 10, PEARL, 1.0)

# -------------------------
# Vignette
# -------------------------
ctx.set_operator(cairo.OPERATOR_OVER)
vignette = cairo.RadialGradient(CX, CY, HEIGHT * 0.38, CX, CY, WIDTH * 0.72)
vignette.add_color_stop_rgba(0.0, 0, 0, 0, 0.0)
vignette.add_color_stop_rgba(1.0, 0.01, 0.0, 0.01, 0.6)
ctx.set_source(vignette)
ctx.rectangle(0, 0, WIDTH, HEIGHT)
ctx.fill()

surface.write_to_png("cc_pycairo/gen/cosmos/cosmos_mandala.png")
print("Saved cosmos_mandala.png")
