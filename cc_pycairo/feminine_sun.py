import math
import random
import cairo

WIDTH, HEIGHT = 1600, 1600
CX, CY = WIDTH // 2, HEIGHT // 2

surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

ctx.set_source_rgb(255/255, 229/255, 180/255)
ctx.paint()

for _ in range(8000):
    x = random.uniform(0, WIDTH)
    y = random.uniform(0, HEIGHT)
    shade = 0.96 + random.uniform(-0.02, 0.015)
    ctx.set_source_rgba(shade, shade, shade, 0.06)
    r = random.uniform(0.3, 0.9)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.fill()

R_CORE = 230

for _ in range(5000):
    x = random.uniform(0, WIDTH)
    y = random.uniform(0, HEIGHT)

    if (x - CX) ** 2 + (y - CY) ** 2 < (R_CORE * 1.8) ** 2:
        continue

    grey = random.uniform(0.55, 0.72)
    alpha = random.uniform(0.025, 0.06)
    r = random.uniform(0.4, 1.4)

    ctx.set_source_rgba(grey, grey, grey, alpha)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.fill()

NUM_BG_LINES = 160

for _ in range(NUM_BG_LINES):
    x1 = random.uniform(-200, WIDTH + 200)
    y1 = random.uniform(-200, HEIGHT + 200)

    angle = random.uniform(-0.4, 0.4) + random.choice([0, math.pi])
    length = random.uniform(WIDTH * 0.4, WIDTH * 0.9)

    x2 = x1 + math.cos(angle) * length
    y2 = y1 + math.sin(angle) * length

    grey = random.uniform(0.6, 0.75)
    alpha = random.uniform(0.03, 0.08)
    width = random.uniform(1.2, 3.0)

    mx = (x1 + x2) / 2
    my = (y1 + y2) / 2
    if (mx - CX) ** 2 + (my - CY) ** 2 < (R_CORE * 1.6) ** 2:
        continue

    ctx.set_line_width(width)
    ctx.set_source_rgba(grey, grey, grey, alpha)
    ctx.move_to(x1, y1)
    ctx.line_to(x2, y2)
    ctx.stroke()

glow = cairo.RadialGradient(CX, CY, 80, CX, CY, 520)
glow.add_color_stop_rgba(0.0, 0.98, 0.92, 0.86, 0.35)
glow.add_color_stop_rgba(1.0, 0.88, 0.82, 0.78, 0.0)
ctx.set_source(glow)
ctx.rectangle(0, 0, WIDTH, HEIGHT)
ctx.fill()

ctx.set_source_rgb(0.95, 0.90, 0.84)
ctx.arc(CX, CY, R_CORE, 0, 2*math.pi)
ctx.fill()

for _ in range(9000):
    angle = random.uniform(0, 2 * math.pi)
    radius = R_CORE * math.sqrt(random.random())
    x = CX + math.cos(angle) * radius
    y = CY + math.sin(angle) * radius

    base_r = 0.90
    base_g = 0.82
    base_b = 0.75

    jitter_r = random.uniform(-0.03, 0.03)
    jitter_g = random.uniform(-0.04, 0.02)
    jitter_b = random.uniform(-0.04, 0.02)

    r = base_r + jitter_r
    g = base_g + jitter_g
    b = base_b + jitter_b

    alpha = random.uniform(0.20, 0.45)
    dot_r = random.uniform(0.6, 1.6)

    ctx.set_source_rgba(r, g, b, alpha)
    ctx.arc(x, y, dot_r, 0, 2 * math.pi)
    ctx.fill()

for _ in range(4000):
    angle = random.uniform(0, 2 * math.pi)
    radius = R_CORE * math.sqrt(random.random())
    x = CX + math.cos(angle) * radius
    y = CY + math.sin(angle) * radius

    base_r = 0.90
    base_g = 0.82
    base_b = 0.75

    jitter_r = random.uniform(-0.03, 0.03)
    jitter_g = random.uniform(-0.04, 0.02)
    jitter_b = random.uniform(-0.04, 0.02)

    r = base_r + jitter_r
    g = base_g + jitter_g
    b = base_b + jitter_b

    alpha = random.uniform(0.18, 0.40)
    dot_r = random.uniform(0.6, 1.5)

    ctx.set_source_rgba(r, g, b, alpha)
    ctx.arc(x, y, dot_r, 0, 2 * math.pi)
    ctx.fill()

ripple_radii = [0.40, 0.78]
band_width = 0.07

for _ in range(7000):
    angle = random.uniform(0, 2 * math.pi)
    ring = random.choice(ripple_radii)

    radius = R_CORE * (
        ring + random.uniform(-band_width, band_width)
    )
    if radius < 0:
        continue

    x = CX + math.cos(angle) * radius
    y = CY + math.sin(angle) * radius

    base_r = 0.86
    base_g = 0.78
    base_b = 0.70

    jitter = random.uniform(-0.03, 0.03)
    r = base_r + jitter
    g = base_g + jitter * 0.8
    b = base_b + jitter * 0.6

    alpha = random.uniform(0.40, 0.70)
    dot_r = random.uniform(1.3, 2.8)

    ctx.set_source_rgba(r, g, b, alpha)
    ctx.arc(x, y, dot_r, 0, 2 * math.pi)
    ctx.fill()

grad = cairo.LinearGradient(CX, CY - R_CORE, CX, CY + R_CORE)
grad.add_color_stop_rgba(0.0, 1.0, 0.96, 0.92, 0.30)
grad.add_color_stop_rgba(0.5, 0.97, 0.93, 0.89, 0.08)
grad.add_color_stop_rgba(1.0, 0.92, 0.85, 0.80, 0.22)

ctx.set_source(grad)
ctx.arc(CX, CY, R_CORE, 0, 2 * math.pi)
ctx.fill()

blush = cairo.RadialGradient(CX, CY, R_CORE * 0.9, CX, CY, R_CORE * 1.6)
blush.add_color_stop_rgba(0.0, 1.0, 0.9, 0.9, 0.0)
blush.add_color_stop_rgba(0.6, 0.96, 0.78, 0.78, 0.23)
blush.add_color_stop_rgba(1.0, 0.96, 0.78, 0.78, 0.0)

ctx.set_source(blush)
ctx.arc(CX, CY, R_CORE * 1.7, 0, 2 * math.pi)
ctx.fill()

ctx.set_line_width(1.2)
ctx.set_source_rgba(0.88, 0.74, 0.68, 0.55)
ctx.arc(CX, CY, R_CORE + 1.0, 0, 2 * math.pi)
ctx.stroke()

R_LACE = 260
NUM_LACE = 140

for i in range(NUM_LACE):
    t = i / NUM_LACE
    angle = t * 2*math.pi + random.uniform(-0.03, 0.03)
    arc_r = R_LACE + random.uniform(-10, 18)
    width = random.uniform(0.8, 1.8)
    length = random.uniform(0.22, 0.38)

    x = CX + math.cos(angle) * arc_r
    y = CY + math.sin(angle) * arc_r

    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(angle + math.pi/2)

    ctx.set_line_width(width)
    ctx.set_source_rgba(0.95, 0.80, 0.70, 0.45)

    ctx.arc(0, 0, 16 + random.uniform(-4, 6), -length/2, length/2)
    ctx.stroke()
    ctx.restore()

NUM_RAYS = 220
R_START = R_LACE + 10
R_END_MIN = R_LACE + 200
R_END_MAX = R_LACE + 480

BASE_RAY_COLOR = (0.78, 0.55, 0.52)

for _ in range(NUM_RAYS):
    base_angle = random.uniform(0, 2*math.pi)
    start_r = R_START + random.uniform(-8, 8)
    end_r = random.uniform(R_END_MIN, R_END_MAX)

    x1 = CX + math.cos(base_angle) * start_r
    y1 = CY + math.sin(base_angle) * start_r
    x2 = CX + math.cos(base_angle) * end_r
    y2 = CY + math.sin(base_angle) * end_r

    mid_r = (start_r + end_r) / 2

    bend = random.uniform(50, 140)
    side = random.choice([-1, 1])
    ctrl_angle = (
        base_angle +
        side * random.uniform(0.30, 0.85) +
        math.sin(base_angle * 3 + random.random() * 2) * 0.25)

    cx1r = CX + math.cos(ctrl_angle) * (mid_r - bend) + random.uniform(-20, 20)
    cy1r = CY + math.sin(ctrl_angle) * (mid_r - bend) + random.uniform(-20, 20)

    cx2r = CX + math.cos(ctrl_angle) * (mid_r + bend) + random.uniform(-20, 20)
    cy2r = CY + math.sin(ctrl_angle) * (mid_r + bend) + random.uniform(-20, 20)

    t = (end_r - R_START) / (R_END_MAX - R_START + 1e-6)

    line_w = 1.6 + (2.2 * (1 - t)) * random.uniform(0.7, 1.2)
    alpha = 0.30 + 0.35 * (1 - t)

    r_col, g_col, b_col = BASE_RAY_COLOR
    ctx.set_line_width(line_w)
    ctx.set_source_rgba(r_col, g_col, b_col, alpha)

    ctx.move_to(x1, y1)
    ctx.curve_to(cx1r, cy1r, cx2r, cy2r, x2, y2)

    ctx.save()
    ctx.set_line_width(line_w * 0.5)
    ctx.set_source_rgba(r_col, g_col, b_col, alpha * 0.4)

    for j in range(4):
        wobble = random.uniform(-15, 15)
        ctx.move_to(x1, y1)
        ctx.curve_to(cx1r + wobble, cy1r - wobble, cx2r - wobble, cy2r + wobble, x2, y2)
        ctx.stroke()

    ctx.restore()
    ctx.stroke()

for _ in range(1800):
    angle = random.uniform(0, 2 * math.pi)
    radius = random.uniform(R_END_MAX * 0.9, R_END_MAX * 1.25)
    x = CX + math.cos(angle) * radius
    y = CY + math.sin(angle) * radius

    alpha = random.uniform(0.03, 0.10)
    size = random.uniform(0.6, 1.6)

    ctx.set_source_rgba(0.96, 0.87, 0.82, alpha)
    ctx.arc(x, y, size, 0, 2 * math.pi)
    ctx.fill()

NUM_VEIL = 260
for _ in range(NUM_VEIL):
    x = CX + random.uniform(-R_CORE * 0.7, R_CORE * 0.7)
    y_start = CY + R_CORE * 0.2 + random.uniform(-15, 15)
    length = random.uniform(120, 260)

    ctx.set_line_width(random.uniform(0.5, 1.1))
    ctx.set_source_rgba(0.9, 0.82, 0.78, random.uniform(0.06, 0.14))

    ctx.move_to(x, y_start)

    y = y_start
    segments = 25
    for i in range(segments):
        y += length / segments
        x_step = math.sin((y * 0.01) + random.uniform(-0.3, 0.3)) * 2.0
        ctx.line_to(x + x_step, y)
    ctx.stroke()

surface.write_to_png("cc_pycairo/gen/feminine_sun.png")
print("Saved feminine_sun.png")
