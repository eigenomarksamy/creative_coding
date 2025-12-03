import math
import random
import cairo

# -------------------------
# Canvas setup
# -------------------------
WIDTH, HEIGHT = 1800, 1100
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

random.seed(31)

# -------------------------
# Background: stormy grey sky
# -------------------------
sky_grad = cairo.LinearGradient(0, 0, 0, HEIGHT)
sky_grad.add_color_stop_rgb(0.0, 0.30, 0.32, 0.36)   # darker top
sky_grad.add_color_stop_rgb(0.4, 0.50, 0.53, 0.58)   # mid
sky_grad.add_color_stop_rgb(1.0, 0.62, 0.65, 0.70)   # lighter near bottom
ctx.set_source(sky_grad)
ctx.rectangle(0, 0, WIDTH, HEIGHT)
ctx.fill()

# Subtle sky texture
for _ in range(11000):
    x = random.uniform(0, WIDTH)
    y = random.uniform(0, HEIGHT)
    shade = random.uniform(0.65, 0.90)
    alpha = random.uniform(0.02, 0.06)
    r = random.uniform(0.4, 1.0)
    ctx.set_source_rgba(shade, shade, shade, alpha)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.fill()

# -------------------------
# Water band
# -------------------------
HORIZON_Y = int(HEIGHT * 0.58)

water_grad = cairo.LinearGradient(0, HORIZON_Y, 0, HEIGHT)
water_grad.add_color_stop_rgba(0.0, 0.30, 0.34, 0.40, 0.95)
water_grad.add_color_stop_rgba(0.5, 0.26, 0.29, 0.35, 0.98)
water_grad.add_color_stop_rgba(1.0, 0.18, 0.20, 0.26, 1.00)
ctx.set_source(water_grad)
ctx.rectangle(0, HORIZON_Y, WIDTH, HEIGHT - HORIZON_Y)
ctx.fill()

# Choppy waves – chaotic horizontal strokes
NUM_WAVE_LINES = 260
for _ in range(NUM_WAVE_LINES):
    y = random.uniform(HORIZON_Y - 20, HEIGHT + 40)
    x_start = -120
    x_end = WIDTH + 120

    ctx.set_line_width(random.uniform(0.7, 2.3))
    alpha = random.uniform(0.05, 0.22)
    ctx.set_source_rgba(0.86, 0.90, 0.94, alpha)

    ctx.move_to(x_start, y)
    segments = 70
    amp = random.uniform(3.0, 10.0)
    freq = random.uniform(10.0, 22.0)

    for i in range(segments + 1):
        t = i / segments
        x = x_start + (x_end - x_start) * t
        wobble = (
            math.sin(t * freq + y * 0.02 + random.random()) * amp +
            math.sin(t * freq * 0.5 + random.random()) * (amp * 0.4)
        )
        ctx.line_to(x, y + wobble)
    ctx.stroke()

# Foam / spray near “top” of water
for _ in range(2600):
    x = random.uniform(0, WIDTH)
    y = random.uniform(HORIZON_Y - 30, HORIZON_Y + 160)

    size = random.uniform(0.5, 1.7)
    alpha = random.uniform(0.05, 0.28)
    ctx.set_source_rgba(0.92, 0.96, 0.98, alpha)
    ctx.arc(x, y, size, 0, 2 * math.pi)
    ctx.fill()

# -------------------------
# Abstract pier – pillars + deck
# -------------------------
def draw_pier(ctx):
    pier_y = HORIZON_Y - 10       # deck height
    perspective_tilt = -0.06      # slight tilt

    num_pillars = 11
    pier_start_x = WIDTH * 0.12
    pier_end_x = WIDTH * 0.88
    span = pier_end_x - pier_start_x

    pillars = []
    for i in range(num_pillars):
        t = i / max(1, num_pillars - 1)
        x = pier_start_x + span * t
        x += (t - 0.5) * 40       # subtle bow
        # slight vertical perspective slope
        y_base = pier_y + (t - 0.5) * 40 * math.tan(perspective_tilt)

        height = random.uniform(160, 260)
        thickness = random.uniform(14, 26)

        # dark pillar body
        ctx.set_source_rgba(0.10, 0.12, 0.16, 0.96)
        ctx.rectangle(x - thickness / 2, y_base, thickness, height)
        ctx.fill()

        # wet highlight edge toward “storm light” (left/top)
        ctx.set_line_width(3.0)
        ctx.set_source_rgba(0.72, 0.78, 0.84, 0.55)
        ctx.move_to(x - thickness / 2, y_base + 4)
        ctx.line_to(x - thickness / 2, y_base + height * random.uniform(0.35, 0.9))
        ctx.stroke()

        # small irregular top edge, like planks / erosion
        ctx.set_line_width(2.0)
        ctx.set_source_rgba(0.22, 0.26, 0.32, 0.9)
        ctx.move_to(x - thickness / 2, y_base)
        ctx.line_to(x + thickness / 2, y_base + random.uniform(-4, 4))
        ctx.stroke()

        pillars.append((x, y_base, height, thickness))

    # Deck – abstracted as two bands
    ctx.set_line_width(10.0)
    ctx.set_source_rgba(0.18, 0.20, 0.26, 0.95)
    ctx.move_to(pier_start_x - 20, pier_y - 6)
    ctx.line_to(pier_end_x + 20, pier_y - 2)
    ctx.stroke()

    ctx.set_line_width(4.0)
    ctx.set_source_rgba(0.38, 0.42, 0.48, 0.8)
    ctx.move_to(pier_start_x - 18, pier_y - 14)
    ctx.line_to(pier_end_x + 18, pier_y - 10)
    ctx.stroke()

    return pillars

pillars = draw_pier(ctx)

# Reflections of pillars in water (broken, stormy)
for (x, y_base, height, thickness) in pillars:
    top_y = y_base
    reflect_height = height * random.uniform(0.4, 0.9)
    segments = 14

    ctx.set_line_width(thickness * random.uniform(0.4, 0.7))
    ctx.set_source_rgba(0.10, 0.12, 0.16, 0.55)

    ctx.move_to(x + random.uniform(-3, 3), HORIZON_Y + 4)
    for i in range(segments + 1):
        t = i / segments
        y = HORIZON_Y + t * reflect_height
        jitter_x = math.sin(t * 12 + x * 0.01) * random.uniform(-6, 6)
        ctx.line_to(x + jitter_x, y)
    ctx.stroke()

# Extra spray around pillar bases
for (x, y_base, height, thickness) in pillars:
    base_y = HORIZON_Y + random.uniform(-6, 10)
    for _ in range(70):
        ang = random.uniform(-math.pi * 0.35, math.pi * 0.35)
        dist = random.uniform(0, 40)
        px = x + math.cos(ang) * dist
        py = base_y + math.sin(ang) * dist * 0.5

        size = random.uniform(0.5, 1.8)
        alpha = random.uniform(0.08, 0.35)
        ctx.set_source_rgba(0.92, 0.96, 0.99, alpha)
        ctx.arc(px, py, size, 0, 2 * math.pi)
        ctx.fill()

# -------------------------
# Storm motion – diagonal rain / wind streaks
# -------------------------
NUM_RAIN = 420
rain_angle = -math.pi / 3.0  # ~ -60 degrees

for _ in range(NUM_RAIN):
    # start mostly in upper 2/3
    x = random.uniform(-200, WIDTH + 200)
    y = random.uniform(-100, HORIZON_Y + 80)

    length = random.uniform(60, 220)
    thickness = random.uniform(0.6, 1.8)

    dx = math.cos(rain_angle)
    dy = math.sin(rain_angle)

    x2 = x + dx * length
    y2 = y + dy * length

    # slightly flickering intensity
    alpha = random.uniform(0.05, 0.18)
    shade = random.uniform(0.84, 0.97)

    ctx.set_line_width(thickness)
    ctx.set_source_rgba(shade, shade, shade, alpha)
    ctx.move_to(x, y)
    ctx.line_to(x2, y2)
    ctx.stroke()

# -------------------------
# Curved gusts: abstract wind arcs near pier
# -------------------------
NUM_GUSTS = 80
for _ in range(NUM_GUSTS):
    # center gusts near the pier region
    gx = random.uniform(WIDTH * 0.10, WIDTH * 0.90)
    gy = random.uniform(HORIZON_Y - 120, HORIZON_Y + 40)

    radius = random.uniform(120, 320)
    span = random.uniform(0.4, 1.1) * math.pi
    base_angle = random.uniform(-0.1, 0.4)

    ctx.set_line_width(random.uniform(1.0, 2.8))
    alpha = random.uniform(0.05, 0.18)
    shade = random.uniform(0.86, 0.96)
    ctx.set_source_rgba(shade, shade, shade, alpha)

    ctx.new_path()
    steps = 40
    for i in range(steps + 1):
        t = i / steps
        ang = base_angle + (t - 0.5) * span
        wobble = random.uniform(-6, 6)
        x = gx + math.cos(ang) * (radius + wobble)
        y = gy + math.sin(ang) * (radius * 0.35 + wobble * 0.5)
        if i == 0:
            ctx.move_to(x, y)
        else:
            ctx.line_to(x, y)
    ctx.stroke()

# -------------------------
# Ash / rain mist particles
# -------------------------
for _ in range(2800):
    x = random.uniform(0, WIDTH)
    y = random.uniform(0, HEIGHT)

    size = random.uniform(0.4, 1.5)
    alpha = random.uniform(0.03, 0.14)

    shade = random.uniform(0.80, 0.96)
    ctx.set_source_rgba(shade, shade, shade, alpha)
    ctx.arc(x, y, size, 0, 2 * math.pi)
    ctx.fill()

# -------------------------
# Vignette for focus
# -------------------------
vignette = cairo.RadialGradient(
    WIDTH / 2, HORIZON_Y + 80, HEIGHT * 0.22,
    WIDTH / 2, HEIGHT / 2, HEIGHT * 0.95
)
vignette.add_color_stop_rgba(0.0, 0, 0, 0, 0.0)
vignette.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.50)
ctx.set_source(vignette)
ctx.rectangle(0, 0, WIDTH, HEIGHT)
ctx.fill()

surface.write_to_png("cc_pycairo/gen/stormy_pier_abstract.png")
print("Saved stormy_pier_abstract.png")
