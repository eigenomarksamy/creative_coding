import math
import random
import cairo
import noise

# Image settings
WIDTH, HEIGHT = 5000, 5000
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

# --- Color palette (soft pastel + contrast) ---
PALETTE = [
    (0.92, 0.39, 0.39),
    (0.39, 0.67, 0.92),
    (0.97, 0.77, 0.36),
    (0.49, 0.85, 0.65),
    (0.75, 0.54, 0.96),
]

# Background
ctx.set_source_rgb(0.96, 0.96, 0.96)
ctx.paint()

def draw_gradient_blob(x, y, size, color):
    """Draws a soft radial gradient blob."""
    pat = cairo.RadialGradient(x, y, size * 0.1, x, y, size)
    r, g, b = color
    pat.add_color_stop_rgba(0, r, g, b, 0.8)
    pat.add_color_stop_rgba(1, r, g, b, 0.0)
    ctx.set_source(pat)
    ctx.arc(x, y, size, 0, 2 * math.pi)
    ctx.fill()

def draw_flow_field_lines(seed):
    """Draws Bézier lines influenced by noise."""
    random.seed(seed)
    for _ in range(300):  # number of curves
        x, y = random.uniform(0, WIDTH), random.uniform(0, HEIGHT)
        ctx.set_line_width(random.uniform(2, 5))
        r, g, b = random.choice(PALETTE)
        ctx.set_source_rgba(r, g, b, 0.35)

        ctx.move_to(x, y)
        for _ in range(4):  # segments per curve
            angle = noise.pnoise2(x * 0.001, y * 0.001, octaves=3) * math.pi * 4
            length = random.uniform(100, 300)
            x2 = x + math.cos(angle) * length
            y2 = y + math.sin(angle) * length
            # Bézier control points
            cx1 = x + math.cos(angle + 0.5) * length / 2
            cy1 = y + math.sin(angle + 0.5) * length / 2
            cx2 = x + math.cos(angle - 0.5) * length / 2
            cy2 = y + math.sin(angle - 0.5) * length / 2
            ctx.curve_to(cx1, cy1, cx2, cy2, x2, y2)
            x, y = x2, y2
        ctx.stroke()

# --- Layer 1: Soft blobs for depth ---
for _ in range(50):
    size = random.uniform(200, 800)
    draw_gradient_blob(
        random.uniform(0, WIDTH),
        random.uniform(0, HEIGHT),
        size,
        random.choice(PALETTE)
    )

# --- Layer 2: Flowing Bézier curves ---
draw_flow_field_lines(seed=42)

# Save image
surface.write_to_png("cc_pycairo/gen/bezier_flow_art.png")
print("Saved bezier_flow_art.png")
