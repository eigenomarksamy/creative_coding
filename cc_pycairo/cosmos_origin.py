import math
import random
import cairo
import noise

# -------------------------
# Canvas setup
# -------------------------
WIDTH, HEIGHT = 2400, 1350
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

random.seed(1)

# Earth is a huge sphere whose limb crosses the lower part of the frame
EARTH_R = 2600
EARTH_CX, EARTH_CY = WIDTH * 0.46, HEIGHT * 0.80 + EARTH_R
SUN_ANGLE = -math.pi / 2 - 0.30   # where the sun sits just under the limb

# Milky Way band runs from the lower left horizon to the top right
BAND_P0 = (-100, HEIGHT * 0.66)
BAND_P1 = (WIDTH + 100, HEIGHT * -0.02)
BAND_SIGMA = 120


def blackbody(kelvin):
    """Approximate RGB of a black body at the given temperature."""
    t = kelvin / 100.0
    if t <= 66:
        r = 1.0
        g = (99.4708025861 * math.log(t) - 161.1195681661) / 255
    else:
        r = 329.698727446 * (t - 60) ** -0.1332047592 / 255
        g = 288.1221695283 * (t - 60) ** -0.0755148492 / 255
    if t >= 66:
        b = 1.0
    elif t <= 19:
        b = 0.0
    else:
        b = (138.5177312231 * math.log(t - 10) - 305.0447927307) / 255
    return tuple(max(0.0, min(1.0, c)) for c in (r, g, b))


def glow(x, y, radius, color, alpha):
    r, g, b = color
    pat = cairo.RadialGradient(x, y, 0, x, y, radius)
    pat.add_color_stop_rgba(0.0, r, g, b, alpha)
    pat.add_color_stop_rgba(0.2, r, g, b, alpha * 0.35)
    pat.add_color_stop_rgba(1.0, r, g, b, 0.0)
    ctx.set_source(pat)
    ctx.arc(x, y, radius, 0, 2 * math.pi)
    ctx.fill()


def above_horizon(x, y, margin=0):
    return math.hypot(x - EARTH_CX, y - EARTH_CY) > EARTH_R + margin


# -------------------------
# Background: deep blue night
# -------------------------
sky = cairo.LinearGradient(0, 0, 0, HEIGHT)
sky.add_color_stop_rgb(0.0, 0.005, 0.010, 0.035)
sky.add_color_stop_rgb(0.6, 0.012, 0.030, 0.090)
sky.add_color_stop_rgb(1.0, 0.030, 0.070, 0.180)
ctx.set_source(sky)
ctx.paint()

ctx.set_operator(cairo.OPERATOR_ADD)

# -------------------------
# Nebula: fractal Perlin noise (fBm) as density
# -------------------------
for _ in range(140000):
    x = random.uniform(0, WIDTH)
    y = random.uniform(0, HEIGHT)
    n = noise.pnoise2(x * 0.0010, y * 0.0010, octaves=5, persistence=0.55, base=7)
    density = max(0.0, n + 0.15) ** 2 * 5.0
    if random.random() > density:
        continue

    hue_shift = noise.pnoise2(x * 0.0006, y * 0.0006, base=19)
    r = 0.04 + max(0.0, hue_shift) * 0.30
    g = 0.10 + random.uniform(0, 0.08)
    b = 0.45 + random.uniform(0, 0.20)
    ctx.set_source_rgba(r, g, b, random.uniform(0.015, 0.040))
    ctx.arc(x, y, random.uniform(4, 14), 0, 2 * math.pi)
    ctx.fill()

# -------------------------
# Milky Way: gaussian profile across the band, dust lanes from noise
# -------------------------
(bx0, by0), (bx1, by1) = BAND_P0, BAND_P1
band_len = math.hypot(bx1 - bx0, by1 - by0)
band_ux, band_uy = (bx1 - bx0) / band_len, (by1 - by0) / band_len


def band_point(t, d):
    """Point at fraction t along the band, offset d across it."""
    wobble = math.sin(t * 7.0) * 35 + math.sin(t * 2.3 + 1.0) * 50
    d -= wobble
    return bx0 + band_ux * band_len * t - band_uy * d, by0 + band_uy * band_len * t + band_ux * d


for _ in range(260000):
    t = random.random()
    d = random.gauss(0, BAND_SIGMA)
    x, y = band_point(t, d)
    core = math.exp(-((t - 0.30) ** 2) / 0.015)
    clump = 0.55 + noise.pnoise2(x * 0.004, y * 0.004, octaves=3, base=2) * 1.2
    if random.random() > (0.45 + 0.55 * core) * clump:
        continue

    if random.random() < 0.5:
        # diffuse glow, warmer near the core
        col = (0.28 + 0.45 * core, 0.40 + 0.28 * core, 0.90 - 0.30 * core)
        ctx.set_source_rgba(*col, random.uniform(0.012, 0.035))
        ctx.arc(x, y, random.uniform(2, 8), 0, 2 * math.pi)
    else:
        # unresolved stars
        col = blackbody(random.uniform(4500, 13000))
        ctx.set_source_rgba(*col, random.uniform(0.15, 0.6))
        ctx.arc(x, y, random.uniform(0.3, 0.9), 0, 2 * math.pi)
    ctx.fill()

# Dust lanes absorb light along the band ridge
ctx.set_operator(cairo.OPERATOR_OVER)
for _ in range(50000):
    t = random.random()
    d = random.gauss(0, BAND_SIGMA * 0.45)
    x, y = band_point(t, d)
    ridge = 1.0 - abs(noise.pnoise2(x * 0.0025, y * 0.0025, octaves=4, base=11)) * 5.0
    if ridge < 0.5 or random.random() > ridge - 0.3:
        continue
    ctx.set_source_rgba(0.004, 0.008, 0.025, random.uniform(0.04, 0.12))
    ctx.arc(x, y, random.uniform(3, 9), 0, 2 * math.pi)
    ctx.fill()
ctx.set_operator(cairo.OPERATOR_ADD)

# -------------------------
# Field stars: power law brightness, black body colour
# -------------------------
bright_stars = []
for _ in range(11000):
    x = random.uniform(0, WIDTH)
    y = random.uniform(0, HEIGHT)
    if not above_horizon(x, y, 4):
        continue

    brightness = min(5.0, 0.04 * random.paretovariate(1.6))
    kelvin = 3200 + 12000 * random.random() ** 1.3
    col = blackbody(kelvin)

    size = 0.35 + 0.8 * min(1.0, brightness)
    ctx.set_source_rgba(*col, min(1.0, 0.25 + brightness * 0.8))
    ctx.arc(x, y, size, 0, 2 * math.pi)
    ctx.fill()

    if brightness > 0.35:
        glow(x, y, 5 + brightness * 9, col, min(0.45, brightness * 0.3))
    if brightness > 1.5:
        bright_stars.append((x, y, brightness, col))

# Diffraction spikes on the brightest stars
for x, y, brightness, col in bright_stars:
    length = 18 + brightness * 14
    for ang in (0, math.pi / 2):
        for sign in (-1, 1):
            ex = x + math.cos(ang) * length * sign
            ey = y + math.sin(ang) * length * sign
            spike = cairo.LinearGradient(x, y, ex, ey)
            spike.add_color_stop_rgba(0.0, *col, 0.55)
            spike.add_color_stop_rgba(1.0, *col, 0.0)
            ctx.set_source(spike)
            ctx.set_line_width(1.1)
            ctx.move_to(x, y)
            ctx.line_to(ex, ey)
            ctx.stroke()


# -------------------------
# Spiral galaxies: logarithmic spiral arms r = a * e^(b * theta)
# -------------------------
def draw_galaxy(gx, gy, radius, arms, pitch_deg, inclination, position_angle, count):
    b = math.tan(math.radians(pitch_deg))
    theta_max = 3.2 * math.pi
    a = radius / math.exp(b * theta_max)
    squash = math.cos(inclination)
    cos_pa, sin_pa = math.cos(position_angle), math.sin(position_angle)

    def project(px, py):
        py *= squash
        return gx + px * cos_pa - py * sin_pa, gy + px * sin_pa + py * cos_pa

    # Soft disk light underneath the stars
    ctx.save()
    ctx.translate(gx, gy)
    ctx.rotate(position_angle)
    ctx.scale(1.0, squash)
    disk = cairo.RadialGradient(0, 0, 0, 0, 0, radius * 1.1)
    disk.add_color_stop_rgba(0.0, 0.95, 0.85, 0.70, 0.55)
    disk.add_color_stop_rgba(0.12, 0.65, 0.65, 0.85, 0.22)
    disk.add_color_stop_rgba(0.5, 0.25, 0.35, 0.80, 0.07)
    disk.add_color_stop_rgba(1.0, 0.10, 0.15, 0.50, 0.0)
    ctx.set_source(disk)
    ctx.arc(0, 0, radius * 1.1, 0, 2 * math.pi)
    ctx.fill()
    ctx.restore()

    for _ in range(count):
        roll = random.random()
        if roll < 0.55:
            # arm star, scattered around the spiral
            arm = random.randrange(arms)
            theta = random.uniform(0.0, theta_max)
            r = a * math.exp(b * theta)
            if random.random() > math.exp(-r / (radius * 0.55)):
                continue
            spread = random.gauss(0, 0.10 + 0.22 * r / radius)
            phi = theta + arm * 2 * math.pi / arms + spread
            r *= 1 + random.gauss(0, 0.08)
            young = math.exp(-abs(spread) * 8)
            col = blackbody(5500 + 9000 * young)
            alpha = 0.08 + 0.25 * young
            size = random.uniform(0.4, 1.3)
        elif roll < 0.85:
            # exponential disk between the arms
            r = random.expovariate(1.0 / (radius * 0.30))
            if r > radius * 1.1:
                continue
            phi = random.uniform(0, 2 * math.pi)
            col = blackbody(random.uniform(4500, 7500))
            alpha = 0.09
            size = random.uniform(0.4, 1.0)
        else:
            # old, warm bulge
            r = abs(random.gauss(0, radius * 0.09))
            phi = random.uniform(0, 2 * math.pi)
            col = blackbody(random.uniform(3500, 5200))
            alpha = 0.18
            size = random.uniform(0.5, 1.4)

        x, y = project(r * math.cos(phi), r * math.sin(phi))
        ctx.set_source_rgba(*col, alpha)
        ctx.arc(x, y, size, 0, 2 * math.pi)
        ctx.fill()

    # Dust lanes trail on the inner edge of each arm
    ctx.set_operator(cairo.OPERATOR_OVER)
    for _ in range(int(count / 8)):
        arm = random.randrange(arms)
        theta = random.uniform(0.8, theta_max)
        r = a * math.exp(b * theta) * (1 + random.gauss(0, 0.03))
        phi = theta + arm * 2 * math.pi / arms - 0.22 + random.gauss(0, 0.05)
        x, y = project(r * math.cos(phi), r * math.sin(phi))
        ctx.set_source_rgba(0.01, 0.012, 0.03, 0.10)
        ctx.arc(x, y, random.uniform(0.8, 2.0), 0, 2 * math.pi)
        ctx.fill()
    ctx.set_operator(cairo.OPERATOR_ADD)

    # Star forming knots along the arms
    for _ in range(int(count / 180)):
        arm = random.randrange(arms)
        theta = random.uniform(0.6, theta_max)
        r = a * math.exp(b * theta)
        phi = theta + arm * 2 * math.pi / arms + random.gauss(0, 0.04)
        x, y = project(r * math.cos(phi), r * math.sin(phi))
        glow(x, y, random.uniform(3, 7), (0.55, 0.70, 1.0), 0.35)

    glow(gx, gy, radius * 0.16, (1.0, 0.92, 0.78), 0.8)


draw_galaxy(WIDTH * 0.25, HEIGHT * 0.27, 330, 2, 14, math.radians(52), math.radians(-28), 60000)
draw_galaxy(WIDTH * 0.83, HEIGHT * 0.44, 150, 3, 18, math.radians(64), math.radians(35), 18000)
draw_galaxy(WIDTH * 0.60, HEIGHT * 0.07, 70, 2, 20, math.radians(20), math.radians(80), 6000)

# Deep field: distant galaxies as tiny tilted ellipses
for _ in range(45):
    x = random.uniform(0, WIDTH)
    y = random.uniform(0, HEIGHT * 0.7)
    if not above_horizon(x, y, 40):
        continue
    size = random.uniform(3, 9)
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(random.uniform(0, math.pi))
    ctx.scale(1.0, random.uniform(0.25, 0.9))
    col = blackbody(random.uniform(3800, 9000))
    pat = cairo.RadialGradient(0, 0, 0, 0, 0, size)
    pat.add_color_stop_rgba(0.0, *col, 0.55)
    pat.add_color_stop_rgba(1.0, *col, 0.0)
    ctx.set_source(pat)
    ctx.arc(0, 0, size, 0, 2 * math.pi)
    ctx.fill()
    ctx.restore()

# -------------------------
# Earth: dark night side
# -------------------------
ctx.set_operator(cairo.OPERATOR_OVER)
body = cairo.RadialGradient(EARTH_CX, EARTH_CY, EARTH_R * 0.9, EARTH_CX, EARTH_CY, EARTH_R)
body.add_color_stop_rgb(0.0, 0.004, 0.006, 0.014)
body.add_color_stop_rgb(1.0, 0.012, 0.022, 0.050)
ctx.set_source(body)
ctx.arc(EARTH_CX, EARTH_CY, EARTH_R, 0, 2 * math.pi)
ctx.fill()

ctx.set_operator(cairo.OPERATOR_ADD)


def surface_coords(x, y):
    """
    Orthographic sphere: rho/R = sin(angle from view axis), so the distance
    along the surface from the limb is R * acos(rho / R). Features compress
    towards the limb the way they do on a real globe.
    """
    dx, dy = x - EARTH_CX, y - EARTH_CY
    rho = math.hypot(dx, dy)
    u = EARTH_R * math.acos(min(1.0, rho / EARTH_R))
    v = EARTH_R * math.atan2(dy, dx)
    mu = math.sqrt(max(0.0, 1 - (rho / EARTH_R) ** 2))
    return u, v, mu, math.atan2(dy, dx)


# Clouds faintly lit by airglow, and the thin sunlit crescent near the sun
for _ in range(90000):
    x = random.uniform(0, WIDTH)
    y = random.uniform(HEIGHT * 0.68, HEIGHT)
    if above_horizon(x, y):
        continue
    u, v, mu, ang = surface_coords(x, y)
    cloud = noise.pnoise2(u * 0.004, v * 0.0025, octaves=5, base=23)
    sunlit = math.exp(-u / 70) * math.exp(-((ang - SUN_ANGLE) ** 2) / 0.01)
    level = max(0.0, cloud + 0.15) * (0.6 + 4.0 * sunlit)
    if random.random() > level:
        continue
    ctx.set_source_rgba(0.30 + sunlit * 0.5, 0.45 + sunlit * 0.4, 0.85, 0.035 + 0.15 * sunlit)
    ctx.arc(x, y, random.uniform(2.0, 5.0), 0, 2 * math.pi)
    ctx.fill()

# City lights: clustered noise on the surface, dimmed towards the limb
for _ in range(200000):
    x = random.uniform(0, WIDTH)
    y = random.uniform(HEIGHT * 0.78, HEIGHT)
    if above_horizon(x, y, -3):
        continue
    u, v, mu, ang = surface_coords(x, y)
    land = noise.pnoise2(u * 0.0015, v * 0.0012, octaves=3, base=31)
    towns = noise.pnoise2(u * 0.02, v * 0.012, octaves=2, base=37)
    if land < 0.0 or towns < 0.16:
        continue
    alpha = min(0.8, 0.15 + towns * 1.2) * (0.15 + 0.85 * mu)
    ctx.set_source_rgba(1.0, 0.76, 0.42, alpha)
    ctx.arc(x, y, random.uniform(0.5, 1.3), 0, 2 * math.pi)
    ctx.fill()
    if towns > 0.30 and random.random() < 0.15:
        glow(x, y, 7, (1.0, 0.70, 0.35), 0.12 * mu)

# -------------------------
# Atmosphere: exponential density above the limb, Rayleigh blue
# -------------------------
SCALE_HEIGHT = 14
SEGMENTS = 300
limb_span = math.asin(min(1.0, (WIDTH * 0.62) / EARTH_R))
ang_start = -math.pi / 2 - limb_span
ang_end = -math.pi / 2 + limb_span

for i in range(130):
    h = i * 0.9
    density = math.exp(-h / SCALE_HEIGHT)
    blue = min(1.0, h / 35)
    base = (0.62 - 0.55 * blue, 0.85 - 0.62 * blue, 1.0 - 0.20 * blue)
    ctx.set_line_width(1.4)
    for s in range(SEGMENTS):
        a0 = ang_start + (ang_end - ang_start) * s / SEGMENTS
        a1 = ang_start + (ang_end - ang_start) * (s + 1) / SEGMENTS
        sun = math.exp(-((a0 - SUN_ANGLE) ** 2) / 0.003)
        # forward scattering: brighter limb the closer it is to the sun
        forward = 0.45 + 1.4 * math.exp(-((a0 - SUN_ANGLE) ** 2) / 0.05)
        warm = sun * math.exp(-h / 8)
        col = (
            base[0] + (1.0 - base[0]) * warm,
            base[1] + (0.72 - base[1]) * warm,
            base[2] + (0.42 - base[2]) * warm,
        )
        ctx.set_source_rgba(*col, density * forward * 0.16)
        ctx.arc(EARTH_CX, EARTH_CY, EARTH_R + h, a0, a1)
        ctx.stroke()

# Thin airglow layer floating just above the limb
ctx.set_line_width(2.0)
ctx.set_source_rgba(0.45, 0.75, 1.0, 0.22)
ctx.arc(EARTH_CX, EARTH_CY, EARTH_R + 9, ang_start, ang_end)
ctx.stroke()

# Sunrise point
sun_x = EARTH_CX + math.cos(SUN_ANGLE) * (EARTH_R + 2)
sun_y = EARTH_CY + math.sin(SUN_ANGLE) * (EARTH_R + 2)
glow(sun_x, sun_y, 340, (0.35, 0.55, 1.0), 0.30)
glow(sun_x, sun_y, 90, (1.0, 0.88, 0.70), 0.75)
glow(sun_x, sun_y, 20, (1.0, 1.0, 1.0), 1.0)

# Short flare hugging the limb on both sides of the sun
for side in (-1, 1):
    for k in range(40):
        a0 = SUN_ANGLE + side * k * 0.004
        a1 = SUN_ANGLE + side * (k + 1) * 0.004
        ctx.set_line_width(3.0)
        ctx.set_source_rgba(0.90, 0.95, 1.0, 0.45 * math.exp(-k / 10))
        ctx.arc(EARTH_CX, EARTH_CY, EARTH_R + 3, min(a0, a1), max(a0, a1))
        ctx.stroke()

# -------------------------
# Human silhouette: forward kinematics on a simple skeleton
# -------------------------
FIG_H = 165
HEAD_TILT = 1.05   # radians the head is tipped back to look up
foot_x = WIDTH * 0.585
foot_ang = math.atan2(-math.sqrt(EARTH_R ** 2 - (foot_x - EARTH_CX) ** 2), foot_x - EARTH_CX)
foot_y = EARTH_CY + math.sin(foot_ang) * EARTH_R
normal_x, normal_y = math.cos(foot_ang), math.sin(foot_ang)
tilt = math.atan2(normal_x, -normal_y)


def chain(start, segments):
    """Walk a chain of (length, angle) bones; angle 0 points straight up."""
    points = [start]
    x, y = start
    total = 0.0
    for length, ang in segments:
        total += ang
        x += math.sin(total) * length * FIG_H
        y -= math.cos(total) * length * FIG_H
        points.append((x, y))
    return points


def bone(points, widths):
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for (p, q), w in zip(zip(points, points[1:]), widths):
        ctx.set_line_width(w * FIG_H)
        ctx.move_to(*p)
        ctx.line_to(*q)
        ctx.stroke()


def draw_figure():
    # Legs from the ground up: ankle, knee, hip. Facing left (negative x).
    back_leg = chain((0.040 * FIG_H, -0.02 * FIG_H), [(0.25, 0.00), (0.24, -0.04)])
    front_leg = chain((-0.060 * FIG_H, -0.02 * FIG_H), [(0.25, 0.10), (0.24, 0.06)])
    hip = ((back_leg[-1][0] + front_leg[-1][0]) / 2, (back_leg[-1][1] + front_leg[-1][1]) / 2)

    # Spine leans back slightly; the neck follows the head back
    spine = chain(hip, [(0.15, 0.03), (0.14, 0.08), (0.06, -0.25)])
    neck_top = spine[-1]

    shoulder = spine[2]
    back_arm = chain((shoulder[0] + 0.01 * FIG_H, shoulder[1]), [(0.17, math.pi - 0.08), (0.15, 0.10)])
    front_arm = chain((shoulder[0] - 0.01 * FIG_H, shoulder[1]), [(0.17, math.pi + 0.10), (0.15, -0.12)])

    bone(back_leg, [0.075, 0.090])
    bone(back_arm, [0.050, 0.042])
    bone(spine, [0.150, 0.160, 0.060])
    bone(front_leg, [0.075, 0.090])
    bone(front_arm, [0.052, 0.044])

    # Feet point the way the figure faces
    for ankle in (back_leg[0], front_leg[0]):
        ctx.set_line_width(0.045 * FIG_H)
        ctx.move_to(ankle[0] + 0.015 * FIG_H, ankle[1] + 0.005 * FIG_H)
        ctx.line_to(ankle[0] - 0.075 * FIG_H, ankle[1] + 0.010 * FIG_H)
        ctx.stroke()

    # Head in profile, facing left, pivoting back about the neck joint
    ctx.save()
    ctx.translate(*neck_top)
    ctx.rotate(HEAD_TILT)
    ctx.scale(0.16 * FIG_H, 0.16 * FIG_H)
    ctx.translate(-0.12, -0.22)
    ctx.new_path()
    for i in range(41):
        a = math.radians(-165 + 225 * i / 40)   # brow, over the crown, to the nape
        ctx.line_to(0.06 + math.cos(a) * 0.44, -0.08 + math.sin(a) * 0.46)
    for px, py in [(0.26, 0.42), (0.04, 0.46), (-0.28, 0.50), (-0.38, 0.36),
                   (-0.36, 0.28), (-0.44, 0.18), (-0.60, 0.08), (-0.40, -0.06),
                   (-0.42, -0.16)]:
        ctx.line_to(px, py)
    ctx.close_path()
    ctx.restore()
    ctx.fill()


# Soft backlight from the atmosphere behind the figure
glow(foot_x, foot_y - FIG_H * 0.4, FIG_H * 1.8, (0.45, 0.65, 1.0), 0.22)

ctx.set_operator(cairo.OPERATOR_OVER)
ctx.save()
ctx.translate(foot_x, foot_y + 2)
ctx.rotate(tilt)

# Rim light: the same body drawn slightly fatter in pale blue
ctx.save()
ctx.translate(0.8, 0.6)
ctx.set_source_rgba(0.55, 0.75, 1.0, 0.55)
draw_figure()
ctx.restore()

ctx.set_source_rgb(0.006, 0.008, 0.016)
draw_figure()
ctx.restore()

# -------------------------
# Vignette
# -------------------------
vignette = cairo.RadialGradient(WIDTH / 2, HEIGHT * 0.55, HEIGHT * 0.35, WIDTH / 2, HEIGHT / 2, WIDTH * 0.75)
vignette.add_color_stop_rgba(0.0, 0, 0, 0, 0.0)
vignette.add_color_stop_rgba(1.0, 0, 0, 0.01, 0.55)
ctx.set_source(vignette)
ctx.rectangle(0, 0, WIDTH, HEIGHT)
ctx.fill()

surface.write_to_png("cc_pycairo/gen/cosmos/cosmos_origin.png")
print("Saved cosmos_origin.png")
