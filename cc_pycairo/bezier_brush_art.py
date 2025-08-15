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
    (0.01, 0.39, 0.39),
    (0.39, 0.07, 0.42),
    (0.17, 0.77, 0.06),
    (0.49, 0.05, 0.65),
    (0.05, 0.54, 0.56),
]

# Background
ctx.set_source_rgb(0.04, 0.04, 0.04)
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

def draw_brush_curve(x, y, segments=4):
    """Draws a single Bézier curve with bold, layered brushstroke effect."""
    r, g, b = random.choice(PALETTE)

    # Base stroke thickness
    base_thickness = random.uniform(8, 20)

    # Draw multiple passes for texture
    for pass_index in range(3):
        ctx.set_line_width(base_thickness - pass_index * 2)
        ctx.set_source_rgba(r, g, b, 0.4 - pass_index * 0.1)

        ctx.move_to(x, y)
        x_curr, y_curr = x, y

        for _ in range(segments):
            angle = noise.pnoise2(x_curr * 0.001, y_curr * 0.001, octaves=3) * math.pi * 4
            length = random.uniform(50, 150)

            x2 = x_curr + math.cos(angle) * length
            y2 = y_curr + math.sin(angle) * length

            # Slight offset per pass for texture
            offset_angle = random.uniform(-0.05, 0.05)
            cx1 = x_curr + math.cos(angle + 0.5 + offset_angle) * length / 2
            cy1 = y_curr + math.sin(angle + 0.5 + offset_angle) * length / 2
            cx2 = x_curr + math.cos(angle - 0.5 - offset_angle) * length / 2
            cy2 = y_curr + math.sin(angle - 0.5 - offset_angle) * length / 2

            ctx.curve_to(cx1, cy1, cx2, cy2, x2, y2)
            x_curr, y_curr = x2, y2

        ctx.stroke()

def draw_flow_field_lines(seed):
    """Draws many flowing brush curves."""
    random.seed(seed)
    for _ in range(400):  # fewer but thicker curves
        x, y = random.uniform(0, WIDTH), random.uniform(0, HEIGHT)
        draw_brush_curve(x, y, segments=4)

# --- Layer 1: Soft blobs for depth ---
for _ in range(150):
    size = random.uniform(250, 450)
    draw_gradient_blob(
        random.uniform(0, WIDTH),
        random.uniform(0, HEIGHT),
        size,
        random.choice(PALETTE)
    )

# --- Layer 2: Flowing Bézier brush curves ---
draw_flow_field_lines(seed=42)

# Save image
surface.write_to_png("cc_pycairo/gen/bezier_brush_art.png")
print("Saved bezier_brush_art.png")
