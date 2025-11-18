import math
import random
import colorsys
import cairo
import noise

# --------------------------
# Dynamic harmonic palette
# --------------------------
def generate_palette(num_colors=5):
    """Black → charcoal → grey → blue-grey → off-white"""
    palette = []

    for i in range(num_colors):
        t = i / max(1, (num_colors - 1))

        # Smooth gradient across a "desaturated cold spectrum":
        # 0 → near-black, 0.3 → charcoal grey, 0.6 → blue-grey, 1 → off-white
        # This keeps the palette harmonic and gentle.
        grey = 0.05 + t * 0.75                 # greys 0.05 → 0.80
        blue_tint = 0.1 + t * 0.25             # subtle blue channel lift

        r = grey * (1.0 - 0.10 * t)            # slightly warmer deep greys
        g = grey * (1.0 - 0.15 * t)
        b = grey * (1.0 + blue_tint)           # blue-grey drift

        # Clamp RGB
        r, g, b = max(0, min(1, r)), max(0, min(1, g)), max(0, min(1, b))

        # Introduce tiny randomness so the palette feels organic
        jitter = 0.03
        r += random.uniform(-jitter, jitter)
        g += random.uniform(-jitter, jitter)
        b += random.uniform(-jitter, jitter)

        # Ensure still in valid range
        r, g, b = max(0, min(1, r)), max(0, min(1, g)), max(0, min(1, b))

        palette.append((r, g, b))

    return palette


# Generate once per run
PALETTE = generate_palette()

# --------------------------
# Canvas setup
# --------------------------
WIDTH, HEIGHT = 5760, 2880
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

# Background
ctx.set_source_rgb(0.04, 0.04, 0.04)
ctx.paint()

# --------------------------
# Blob function
# --------------------------
def draw_gradient_blob(x, y, size, color):
    """Draws a soft radial gradient blob."""
    pat = cairo.RadialGradient(x, y, size * 0.1, x, y, size)
    r, g, b = color
    pat.add_color_stop_rgba(0, r, g, b, 0.8)
    pat.add_color_stop_rgba(1, r, g, b, 0.0)
    ctx.set_source(pat)
    ctx.arc(x, y, size, 0, 2 * math.pi)
    ctx.fill()

# --------------------------
# Brushstroke curves
# --------------------------
def draw_brush_curve(x, y, segments=4):
    """Draws a single Bézier curve with bold, layered brushstroke effect."""
    r, g, b = random.choice(PALETTE)
    base_thickness = random.uniform(8, 20)

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
    for _ in range(400):
        x, y = random.uniform(0, WIDTH), random.uniform(0, HEIGHT)
        draw_brush_curve(x, y, segments=4)

# --------------------------
# Layer 1: Soft blobs
# --------------------------
for _ in range(150):
    size = random.uniform(250, 450)
    draw_gradient_blob(
        random.uniform(0, WIDTH),
        random.uniform(0, HEIGHT),
        size,
        random.choice(PALETTE)
    )

# --------------------------
# Layer 2: Brush curves
# --------------------------
draw_flow_field_lines(seed=42)

# --------------------------
# Save image
# --------------------------
surface.write_to_png("cc_pycairo/gen/bezier_brush_dyn_new_pal.png")
print("Saved bezier_brush_dyn_new_pal.png")
