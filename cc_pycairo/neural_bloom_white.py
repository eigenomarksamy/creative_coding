import cairo, math, random, noise

# --- Canvas setup ---
WIDTH, HEIGHT = 2000, 2000
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

# white background
ctx.set_source_rgb(1, 1, 1)
ctx.paint()

# --- Parameters ---
NUM_LINES = 2500
STEPS = 150
STEP_SIZE = 6
NOISE_SCALE = 0.002
LINE_WIDTH = 1.0

PALETTE = [
    (0.6, 0.4, 0.9),
    (0.4, 0.7, 0.9),
    (0.9, 0.5, 0.4),
    (0.9, 0.7, 0.3),
    (0.5, 0.9, 0.6),
]

def flow_field_angle(x, y):
    """Generate a smooth angle based on Perlin noise."""
    return noise.pnoise2(x * NOISE_SCALE, y * NOISE_SCALE, octaves=3) * math.pi * 4

def draw_filament(x, y, color):
    """Draw a single flowing filament with subtle noise-guided curvature."""
    ctx.move_to(x, y)
    r, g, b = color
    ctx.set_source_rgba(r, g, b, random.uniform(0.15, 0.35))
    ctx.set_line_width(LINE_WIDTH + random.uniform(0.0, 0.7))

    for _ in range(STEPS):
        angle = flow_field_angle(x, y)
        x += math.cos(angle) * STEP_SIZE
        y += math.sin(angle) * STEP_SIZE
        ctx.line_to(x, y)

        # add subtle local distortion for textural depth
        x += math.sin(y * 0.01) * 0.5
        y += math.cos(x * 0.01) * 0.5

        # fade opacity slightly as the line grows
        ctx.set_source_rgba(r, g, b, max(0.05, 0.35 - _ / STEPS * 0.3))

    ctx.stroke()

# --- Draw field ---
for _ in range(NUM_LINES):
    x, y = random.uniform(0, WIDTH), random.uniform(0, HEIGHT)
    color = random.choice(PALETTE)
    draw_filament(x, y, color)

surface.write_to_png("cc_pycairo/gen/neural_bloom_white.png")
print("Saved: neural_bloom_white.png")
