import math
import random
import cairo

# -------------------------
# Canvas setup
# -------------------------
WIDTH, HEIGHT = 1800, 1100
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

random.seed(23)

# -------------------------
# Background: layered greys
# -------------------------
bg_grad = cairo.LinearGradient(0, 0, 0, HEIGHT)
bg_grad.add_color_stop_rgb(0.0, 0.84, 0.84, 0.86)   # top
bg_grad.add_color_stop_rgb(0.5, 0.78, 0.78, 0.81)
bg_grad.add_color_stop_rgb(1.0, 0.70, 0.71, 0.75)   # bottom
ctx.set_source(bg_grad)
ctx.rectangle(0, 0, WIDTH, HEIGHT)
ctx.fill()

# Paper-like noise
for _ in range(10000):
    x = random.uniform(0, WIDTH)
    y = random.uniform(0, HEIGHT)
    shade = random.uniform(0.74, 0.92)
    alpha = random.uniform(0.02, 0.08)
    r = random.uniform(0.4, 1.0)
    ctx.set_source_rgba(shade, shade, shade, alpha)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.fill()

# -------------------------
# Soft "water band" under the conservatory
# -------------------------
WATER_Y = int(HEIGHT * 0.65)

water_grad = cairo.LinearGradient(0, WATER_Y - 120, 0, HEIGHT)
water_grad.add_color_stop_rgba(0.0, 0.65, 0.70, 0.74, 0.0)
water_grad.add_color_stop_rgba(0.3, 0.64, 0.69, 0.74, 0.20)
water_grad.add_color_stop_rgba(1.0, 0.58, 0.63, 0.70, 0.45)
ctx.set_source(water_grad)
ctx.rectangle(0, WATER_Y - 150, WIDTH, HEIGHT - (WATER_Y - 150))
ctx.fill()

# subtle horizontal shimmer lines on water
NUM_WATER_LINES = 180
for _ in range(NUM_WATER_LINES):
    y = random.uniform(WATER_Y - 40, HEIGHT)
    x_start = -100
    x_end = WIDTH + 100

    ctx.set_line_width(random.uniform(0.6, 1.6))
    alpha = random.uniform(0.04, 0.16)
    ctx.set_source_rgba(0.86, 0.90, 0.93, alpha)  # cool light

    ctx.move_to(x_start, y)
    segments = 80
    for i in range(segments + 1):
        t = i / segments
        x = x_start + (x_end - x_start) * t
        wobble = math.sin(t * 14 + y * 0.015 + random.random()) * random.uniform(1.5, 5.0)
        ctx.line_to(x, y + wobble)
    ctx.stroke()

# soft ripples under the future conservatory position
cx = WIDTH * 0.5
for i in range(8):
    radius_x = 80 + i * 26
    radius_y = 18 + i * 6
    alpha = max(0.0, 0.18 - i * 0.018)

    ctx.save()
    ctx.translate(cx, WATER_Y + 10)
    ctx.scale(radius_x, radius_y)
    ctx.set_line_width(1.0 / max(radius_x, radius_y))
    ctx.set_source_rgba(0.88, 0.92, 0.95, alpha)
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()
    ctx.stroke()

# -------------------------
# Floating shadow (under conservatory)
# -------------------------
shadow = cairo.RadialGradient(cx, WATER_Y - 60, 10, cx, WATER_Y + 40, 260)
shadow.add_color_stop_rgba(0.0, 0.10, 0.12, 0.18, 0.40)
shadow.add_color_stop_rgba(1.0, 0.10, 0.12, 0.18, 0.0)
ctx.set_source(shadow)
ctx.rectangle(0, WATER_Y - 200, WIDTH, 400)
ctx.fill()

# -------------------------
# Floating conservatory – abstract glass structure
# -------------------------
def draw_conservatory(ctx, center_x, center_y, scale=1.0):
    width = 520 * scale
    height = 320 * scale
    dome_height = 180 * scale
    base_y = center_y + height * 0.1

    left = center_x - width / 2
    right = center_x + width / 2
    top = base_y - height

    # Outer shell path: arch + base
    ctx.new_path()
    ctx.move_to(left, base_y)

    # left arch side
    ctx.curve_to(
        left, base_y - dome_height * 0.3,
        center_x - width * 0.4, top - dome_height * 0.2,
        center_x, top - dome_height * 0.1
    )
    # right arch side
    ctx.curve_to(
        center_x + width * 0.4, top - dome_height * 0.2,
        right, base_y - dome_height * 0.3,
        right, base_y
    )
    # close base
    ctx.line_to(left, base_y)
    ctx.close_path()

    # Glass fill
    glass_grad = cairo.LinearGradient(center_x, top - dome_height * 0.3, center_x, base_y + 40)
    glass_grad.add_color_stop_rgba(0.0, 0.92, 0.95, 0.98, 0.35)
    glass_grad.add_color_stop_rgba(0.5, 0.85, 0.90, 0.95, 0.23)
    glass_grad.add_color_stop_rgba(1.0, 0.80, 0.86, 0.92, 0.18)
    ctx.set_source(glass_grad)
    ctx.fill_preserve()

    # shell outline
    ctx.set_line_width(2.4 * scale)
    ctx.set_source_rgba(0.52, 0.58, 0.63, 0.9)
    ctx.stroke()

    # Internal vertical ribs
    num_cols = 7
    for i in range(num_cols + 1):
        t = i / num_cols
        x = left + (right - left) * t

        # approximate dome curve for rib end
        rib_top_y = top + math.sin(t * math.pi) * (dome_height * 0.3)

        ctx.set_line_width(1.3 * scale)
        ctx.set_source_rgba(0.70, 0.78, 0.84, 0.6)
        ctx.move_to(x, base_y)
        ctx.line_to(x, rib_top_y)
        ctx.stroke()

    # Horizontal bands
    band_levels = [0.25, 0.5, 0.72]
    for lvl in band_levels:
        y = base_y - height * lvl
        ctx.set_line_width(1.1 * scale)
        ctx.set_source_rgba(0.72, 0.80, 0.86, 0.55)
        ctx.move_to(left + 8 * scale, y)
        ctx.line_to(right - 8 * scale, y)
        ctx.stroke()

    # Slight interior haze
    haze = cairo.RadialGradient(center_x, base_y - height * 0.6, 20 * scale,
                                center_x, base_y - height * 0.2, 260 * scale)
    haze.add_color_stop_rgba(0.0, 0.96, 0.98, 1.0, 0.20)
    haze.add_color_stop_rgba(1.0, 0.90, 0.94, 0.98, 0.0)
    ctx.set_source(haze)
    ctx.rectangle(left - 20 * scale, top - dome_height * 0.5,
                  width + 40 * scale, height + dome_height)
    ctx.fill()

    # Light “contents” – abstract plants / structures as vertical strokes
    num_insides = 22
    for _ in range(num_insides):
        px = random.uniform(left + width * 0.1, right - width * 0.1)
        py_base = base_y - random.uniform(40 * scale, 120 * scale)
        height_inner = random.uniform(40 * scale, 160 * scale)

        ctx.set_line_width(random.uniform(1.0, 2.4) * scale)
        ctx.set_source_rgba(0.68, 0.83, 0.80, random.uniform(0.28, 0.55))
        ctx.move_to(px, py_base)
        ctx.line_to(px, py_base - height_inner)
        ctx.stroke()

        # little horizontal "leaf" hints
        if random.random() < 0.55:
            ctx.set_line_width(random.uniform(0.8, 1.6) * scale)
            ctx.set_source_rgba(0.76, 0.87, 0.84, random.uniform(0.18, 0.4))
            ctx.move_to(px - 10 * scale, py_base - height_inner * random.uniform(0.2, 0.8))
            ctx.line_to(px + 10 * scale, py_base - height_inner * random.uniform(0.2, 0.8))
            ctx.stroke()

    # Soft highlight on right edge
    ctx.set_line_width(3.0 * scale)
    ctx.set_source_rgba(0.97, 0.99, 1.0, 0.7)
    ctx.move_to(right, base_y)
    ctx.curve_to(
        right + 18 * scale, base_y - height * 0.4,
        center_x + width * 0.36, top - dome_height * 0.15,
        center_x + width * 0.18, top - dome_height * 0.05
    )
    ctx.stroke()

# Draw the conservatory
CONS_Y = HEIGHT * 0.48
draw_conservatory(ctx, cx, CONS_Y, scale=1.0)

# -------------------------
# Flow field for motion (air/water around)
# -------------------------
def flow_angle(x, y):
    xs = x * 0.0014
    ys = y * 0.0010
    v = (
        math.sin(xs * 2.3 + ys * 0.7) * 0.7 +
        math.cos(xs * 0.9 - ys * 1.4) * 0.5 +
        math.sin(ys * 1.8) * 0.4
    )
    return v * 0.8  # radians, small deviation

# -------------------------
# Curvilinear motion lines
# -------------------------
NUM_STREAMS = 520

for _ in range(NUM_STREAMS):
    # Start around and slightly below the conservatory
    x = random.uniform(WIDTH * 0.15, WIDTH * 0.85)
    y = random.uniform(HEIGHT * 0.40, HEIGHT * 0.85)

    steps = random.randint(35, 80)
    base_width = random.uniform(0.6, 1.8)

    base_grey = random.uniform(0.84, 0.96)
    r_c = base_grey * random.uniform(0.96, 1.02)
    g_c = base_grey * random.uniform(0.97, 1.05)
    b_c = base_grey * random.uniform(1.00, 1.10)

    # Some lines slightly tinted blue/green for water/air feel
    if random.random() < 0.35:
        b_c += 0.04
        g_c += 0.02

    ctx.move_to(x, y)
    direction = random.choice([-1, 1])

    for i in range(steps):
        t = i / steps
        angle = flow_angle(x, y) + random.uniform(-0.18, 0.18)
        speed = 5.0 + 3.0 * (1 - t)

        x += math.cos(angle) * speed * direction
        y += math.sin(angle) * speed * 0.5  # gentle vertical

        ctx.line_to(x, y)

        alpha = (0.32 * (1 - abs(t - 0.3)))  # stronger mid-curve
        alpha *= random.uniform(0.6, 1.0)
        alpha = max(0.0, min(0.28, alpha))

        # slightly stronger near water band
        if y > WATER_Y - 50:
            alpha *= 1.2

        ctx.set_source_rgba(r_c, g_c, b_c, alpha)
        ctx.set_line_width(base_width * (0.7 + 0.4 * (1 - t)))

        if i % 10 == 0:
            ctx.stroke_preserve()
    ctx.stroke()

# -------------------------
# Floating droplets / glass dust
# -------------------------
for _ in range(2300):
    x = random.uniform(0, WIDTH)
    y = random.uniform(HEIGHT * 0.18, HEIGHT * 0.95)

    # avoid overloading inside conservatory center
    if (abs(x - cx) < 260) and (CONS_Y - 260 < y < CONS_Y + 120):
        if random.random() < 0.6:
            continue

    size = random.uniform(0.4, 1.4)
    alpha = random.uniform(0.04, 0.16)
    r = 0.92 + random.uniform(-0.03, 0.03)
    g = 0.95 + random.uniform(-0.03, 0.03)
    b = 0.98 + random.uniform(-0.02, 0.02)

    ctx.set_source_rgba(r, g, b, alpha)
    ctx.arc(x, y, size, 0, 2 * math.pi)
    ctx.fill()

# -------------------------
# Soft vignette
# -------------------------
vignette = cairo.RadialGradient(
    WIDTH / 2, HEIGHT * 0.60, HEIGHT * 0.18,
    WIDTH / 2, HEIGHT / 2, HEIGHT * 0.95
)
vignette.add_color_stop_rgba(0.0, 0, 0, 0, 0.0)
vignette.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.45)
ctx.set_source(vignette)
ctx.rectangle(0, 0, WIDTH, HEIGHT)
ctx.fill()

surface.write_to_png("cc_pycairo/gen/floating_conservatory.png")
print("Saved floating_conservatory.png")
