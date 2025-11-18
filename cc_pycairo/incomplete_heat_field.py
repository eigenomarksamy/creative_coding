import math
import random
import cairo

# Canvas
WIDTH, HEIGHT = 1600, 1600
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

# ---------- Background: deep black with subtle grain ----------
ctx.set_source_rgb(0.02, 0.01, 0.03)
ctx.paint()

# Dark grain
for _ in range(9000):
    x = random.uniform(0, WIDTH)
    y = random.uniform(0, HEIGHT)
    shade = random.uniform(0.03, 0.09)
    alpha = random.uniform(0.04, 0.12)
    r = random.uniform(0.4, 1.2)
    ctx.set_source_rgba(shade, shade, shade, alpha)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.fill()

# ---------- Base glow near the "heat source" ----------
base_glow = cairo.LinearGradient(0, HEIGHT, 0, HEIGHT * 0.35)
base_glow.add_color_stop_rgba(0.0, 0.95, 0.55, 0.20, 0.6)   # deep orange at bottom
base_glow.add_color_stop_rgba(0.4, 0.65, 0.18, 0.10, 0.25) # red-brown
base_glow.add_color_stop_rgba(1.0, 0.05, 0.02, 0.05, 0.0)  # fades into black
ctx.set_source(base_glow)
ctx.rectangle(0, HEIGHT * 0.3, WIDTH, HEIGHT * 0.7)
ctx.fill()

# ---------- Pseudo-noise function for flow ----------
def flow_angle(x, y):
    """Angle for heat filaments: not true noise, but smooth-ish."""
    x *= 0.002
    y *= 0.002
    v = (
        math.sin(x * 2.3 + y * 0.7) +
        math.sin(x * 1.1 - y * 1.9) * 0.6 +
        math.cos(y * 3.1) * 0.4
    )
    return v * math.pi * 0.8  # limited bend, mostly upward

# ---------- Rising heat filaments ----------
NUM_FILAMENTS = 1400
STEPS_MIN, STEPS_MAX = 80, 150

for _ in range(NUM_FILAMENTS):
    # start somewhere along a band near the bottom
    x = random.uniform(WIDTH * 0.15, WIDTH * 0.85)
    y = random.uniform(HEIGHT * 0.65, HEIGHT * 0.98)

    steps = random.randint(STEPS_MIN, STEPS_MAX)
    base_width = random.uniform(0.6, 2.2)

    # color: from deep red to muted orange
    cr = random.uniform(0.8, 1.0)
    cg = random.uniform(0.25, 0.55)
    cb = random.uniform(0.1, 0.25)

    ctx.move_to(x, y)

    for i in range(steps):
        t = i / steps
        ang = flow_angle(x, y) + random.uniform(-0.25, 0.25)
        step_len = random.uniform(4.0, 7.5) * (1.0 - t * 0.3)

        x += math.sin(ang) * step_len * 0.6   # sideways wobble
        y -= step_len                         # mostly upward

        ctx.line_to(x, y)

        # fade opacity and line width as it rises
        alpha = (0.32 * (1 - t)) * random.uniform(0.7, 1.0)
        ctx.set_source_rgba(cr, cg, cb, alpha)
        ctx.set_line_width(base_width * (1 - t * 0.8))

        # every few steps, commit the stroke and keep going
        if i % 12 == 0:
            ctx.stroke_preserve()

    ctx.stroke()

# ---------- Ember particles near the base ----------
for _ in range(2200):
    # cluster mostly in lower half
    x = random.uniform(WIDTH * 0.1, WIDTH * 0.9)
    y = random.uniform(HEIGHT * 0.55, HEIGHT * 0.98)

    size = random.uniform(0.6, 2.2)
    # brighter towards the very bottom
    t = (HEIGHT - y) / (HEIGHT * 0.45 + 1e-6)
    t = max(0.0, min(1.0, t))

    r = 0.9 + 0.1 * random.random()
    g = 0.55 + 0.4 * t
    b = 0.2 + 0.2 * t
    alpha = random.uniform(0.15, 0.5) * (0.3 + 0.7 * t)

    ctx.set_source_rgba(r, g, b, alpha)
    ctx.arc(x, y, size, 0, 2 * math.pi)
    ctx.fill()

# ---------- Heat shimmer: horizontal distortions ----------
NUM_SHIMMER_LINES = 260
for _ in range(NUM_SHIMMER_LINES):
    y = random.uniform(HEIGHT * 0.35, HEIGHT * 0.8)
    x_start = -100
    x_end = WIDTH + 100

    # subtle wave
    ctx.set_line_width(random.uniform(0.5, 1.4))
    alpha = random.uniform(0.05, 0.16)
    ctx.set_source_rgba(0.9, 0.6, 0.4, alpha)

    ctx.move_to(x_start, y)
    segments = 80
    for i in range(segments + 1):
        t = i / segments
        x = x_start + (x_end - x_start) * t
        wobble = math.sin(t * 12 + y * 0.01) * random.uniform(3.0, 9.0)
        ctx.line_to(x, y + wobble)
    ctx.stroke()

# ---------- Slight vignetting ----------
vignette = cairo.RadialGradient(
    WIDTH / 2, HEIGHT * 0.75, HEIGHT * 0.2,
    WIDTH / 2, HEIGHT / 2, HEIGHT * 0.9
)
vignette.add_color_stop_rgba(0.0, 0, 0, 0, 0.0)
vignette.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.6)
ctx.set_source(vignette)
ctx.rectangle(0, 0, WIDTH, HEIGHT)
ctx.fill()

surface.write_to_png("cc_pycairo/gen/incomplete_heat_field.png")
print("Saved incomplete_heat_field.png")
