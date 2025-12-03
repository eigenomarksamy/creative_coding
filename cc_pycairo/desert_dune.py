import math
import random
import cairo

# -------------------------
# Canvas setup
# -------------------------
WIDTH, HEIGHT = 1500, 1500
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

random.seed(8)

# -------------------------
# Background: grey sky
# -------------------------
sky_grad = cairo.LinearGradient(0, 0, 0, HEIGHT)
sky_grad.add_color_stop_rgb(0.0, 0.82, 0.82, 0.84)  # light grey top
sky_grad.add_color_stop_rgb(0.5, 0.76, 0.76, 0.78)
sky_grad.add_color_stop_rgb(1.0, 0.68, 0.68, 0.70)  # darker towards horizon
ctx.set_source(sky_grad)
ctx.rectangle(0, 0, WIDTH, HEIGHT)
ctx.fill()

# Subtle texture (paper-like)
for _ in range(9000):
    x = random.uniform(0, WIDTH)
    y = random.uniform(0, HEIGHT)
    shade = random.uniform(0.7, 0.9)
    alpha = random.uniform(0.03, 0.09)
    r = random.uniform(0.4, 1.0)
    ctx.set_source_rgba(shade, shade, shade, alpha)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.fill()

# -------------------------
# Dune shapes (curvilinear, layered)
# -------------------------
def draw_dune(y_base, height, offset=0, darkness=0.0):
    """
    Draws a single dune as a soft, curvy band across the canvas.
    y_base: baseline of the dune (from top)
    height: how tall the dune crest is
    offset: horizontal phase shift for variation
    darkness: 0..1 – how dark the dune is
    """
    # gradient per dune (slightly darker at bottom)
    dune_grad = cairo.LinearGradient(0, y_base - height, 0, y_base + 80)
    base = 0.60 - darkness * 0.18
    dune_grad.add_color_stop_rgb(0.0, base + 0.06, base + 0.06, base + 0.07)
    dune_grad.add_color_stop_rgb(1.0, base - 0.05, base - 0.05, base - 0.04)

    ctx.set_source(dune_grad)

    ctx.new_path()
    ctx.move_to(-100, HEIGHT)  # start off-canvas left bottom

    # control points for the dune crest (smooth, wavy)
    num_points = 8
    for i in range(num_points + 1):
        t = i / num_points
        x = -100 + (WIDTH + 200) * t + offset
        # sinusoidal crest with random variation
        crest = math.sin((t + offset * 0.0003) * math.pi * 1.2) * height
        crest += random.uniform(-height * 0.15, height * 0.15)
        y = y_base - crest
        ctx.line_to(x, y)

    # close shape downwards
    ctx.line_to(WIDTH + 200, HEIGHT + 50)
    ctx.line_to(-100, HEIGHT + 50)
    ctx.close_path()
    ctx.fill()

# Draw layered dunes: back to front
draw_dune(y_base=HEIGHT * 0.78, height=70, offset=40,  darkness=0.1)
draw_dune(y_base=HEIGHT * 0.72, height=110, offset=-60, darkness=0.2)
draw_dune(y_base=HEIGHT * 0.66, height=150, offset=120, darkness=0.32)
draw_dune(y_base=HEIGHT * 0.60, height=190, offset=-150, darkness=0.45)

# -------------------------
# Flow function (pseudo-field for wind lines)
# -------------------------
def flow_angle(x, y):
    """
    Pseudo flow field: gently bends lines as if wind is crossing dunes.
    Uses a mix of sin/cos to avoid extra dependencies.
    """
    xs = x * 0.0015
    ys = y * 0.0012
    v = (
        math.sin(xs * 2.1 + ys * 0.7) * 0.7 +
        math.cos(xs * 0.9 - ys * 1.3) * 0.5 +
        math.sin(ys * 1.9) * 0.4
    )
    # Slight upward drift, mostly horizontal undulation
    return v * 0.8  # in radians, small deviation around horizontal

# -------------------------
# Wind / motion lines
# -------------------------
NUM_STREAMS = 900

for _ in range(NUM_STREAMS):
    # start somewhere low-ish, as if wind hugging the dunes
    x = random.uniform(-100, WIDTH + 100)
    y = random.uniform(HEIGHT * 0.50, HEIGHT * 0.90)

    steps = random.randint(40, 85)
    base_width = random.uniform(0.7, 2.4)

    # Motion line color: cool grey, slightly translucent
    base_grey = random.uniform(0.82, 0.95)
    r_c = base_grey * random.uniform(0.95, 1.02)
    g_c = base_grey * random.uniform(0.96, 1.04)
    b_c = base_grey * random.uniform(1.02, 1.10)

    ctx.move_to(x, y)

    for i in range(steps):
        t = i / steps
        angle = flow_angle(x, y) + random.uniform(-0.18, 0.18)
        speed = 6.0 + 3.0 * (1 - t)  # a bit stronger at the start

        # predominantly left→right or right→left depending on seed
        direction = random.choice([-1, 1]) if i == 0 else direction

        x += math.cos(angle) * speed * direction
        y += math.sin(angle) * speed * 0.4  # vertical drift is gentler

        ctx.line_to(x, y)

        # fade out towards the ends
        alpha = (0.35 * (1 - abs(t - 0.3)))  # stronger mid-curve
        alpha *= random.uniform(0.6, 1.0)
        alpha = max(0.0, min(0.32, alpha))

        ctx.set_source_rgba(r_c, g_c, b_c, alpha)
        ctx.set_line_width(base_width * (0.6 + 0.5 * (1 - t)))

        # draw in segments
        if i % 10 == 0:
            ctx.stroke_preserve()

    ctx.stroke()

# -------------------------
# Small drifting sand particles
# -------------------------
for _ in range(2600):
    x = random.uniform(0, WIDTH)
    y = random.uniform(HEIGHT * 0.50, HEIGHT * 0.94)

    size = random.uniform(0.4, 1.3)
    alpha = random.uniform(0.04, 0.14)

    # slightly lighter than background
    shade = random.uniform(0.85, 0.96)
    ctx.set_source_rgba(shade, shade, shade, alpha)
    ctx.arc(x, y, size, 0, 2 * math.pi)
    ctx.fill()

# -------------------------
# Soft vignette to keep focus in the center
# -------------------------
vignette = cairo.RadialGradient(
    WIDTH / 2, HEIGHT * 0.7, HEIGHT * 0.2,
    WIDTH / 2, HEIGHT / 2, HEIGHT * 0.9
)
vignette.add_color_stop_rgba(0.0, 0, 0, 0, 0.0)
vignette.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.55)
ctx.set_source(vignette)
ctx.rectangle(0, 0, WIDTH, HEIGHT)
ctx.fill()

surface.write_to_png("cc_pycairo/gen/desert_dune.png")
print("Saved desert_dune.png")
