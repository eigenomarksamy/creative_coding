import cairo, math, random, noise

WIDTH, HEIGHT = 2000, 2000
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

# White background
ctx.set_source_rgb(1, 1, 1)
ctx.paint()

# --- Tuned Parameters ---
NUM_LINES = 2000
STEPS = 250
STEP_SIZE = 8
NOISE_SCALE = 0.0012  # smaller = smoother, larger = more chaotic

PALETTE = [
    (0.25, 0.2, 0.8),
    (0.2, 0.6, 0.9),
    (0.9, 0.4, 0.5),
    (0.4, 0.8, 0.7),
    (0.7, 0.5, 0.9),
]

def field_angle(x, y):
    """Vector field based on 3D Perlin noise."""
    return noise.pnoise3(x * NOISE_SCALE, y * NOISE_SCALE, 0.5, octaves=3) * math.pi * 4

def draw_neural_path(x, y, color):
    r, g, b = color
    base_opacity = random.uniform(0.25, 0.4)
    base_width = random.uniform(0.6, 2.5)
    ctx.set_line_width(base_width)
    ctx.set_source_rgba(r, g, b, base_opacity)
    ctx.move_to(x, y)

    for step in range(STEPS):
        angle = field_angle(x, y)
        x += math.cos(angle) * STEP_SIZE
        y += math.sin(angle) * STEP_SIZE
        ctx.line_to(x, y)

        # slight recursive drift (memory)
        angle2 = field_angle(x * 0.3, y * 0.3)
        x += math.cos(angle2) * 0.5
        y += math.sin(angle2) * 0.5

        # fade color slightly
        if step % 20 == 0:
            ctx.stroke_preserve()
            ctx.set_source_rgba(r, g, b, max(0.05, base_opacity - step / STEPS * 0.3))

    ctx.stroke()

# --- Draw the network ---
for _ in range(NUM_LINES):
    x, y = random.uniform(0, WIDTH), random.uniform(0, HEIGHT)
    draw_neural_path(x, y, random.choice(PALETTE))

surface.write_to_png("cc_pycairo/gen/neural_intelligence_blooming.png")
print("Saved neural_intelligence_blooming.png")
