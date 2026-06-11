import math
import random
import cairo
import noise

# --------------------------
# Layer-specific palettes
# --------------------------

BLOB_PALETTE = [
    (0.55, 0.02, 0.03),  # deep blood red
    (0.75, 0.04, 0.05),  # strong red
    (0.95, 0.18, 0.15),  # hot red
    (0.85, 0.55, 0.52),  # muted pale red
    (0.92, 0.82, 0.78),  # off-white blush
]

LINE_PALETTE = [
    (0.18, 0.19, 0.21),  # dark grey
    (0.38, 0.40, 0.44),  # mid grey
    (0.62, 0.65, 0.70),  # light grey
    (0.78, 0.82, 0.86),  # off-white grey
    (0.05, 0.55, 0.65),  # cyan
    (0.15, 0.75, 0.85),  # brighter cyan
]

# --------------------------
# Canvas setup
# --------------------------

WIDTH, HEIGHT = 5760, 2880

surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

# Black background
ctx.set_source_rgb(0.005, 0.005, 0.007)
ctx.paint()

# --------------------------
# Blob function
# --------------------------

def draw_gradient_blob(x, y, size, color):
    """Draw a soft red/off-white atmospheric blob."""
    pat = cairo.RadialGradient(x, y, size * 0.1, x, y, size)

    r, g, b = color

    pat.add_color_stop_rgba(0.0, r, g, b, 0.45)
    pat.add_color_stop_rgba(0.45, r, g, b, 0.18)
    pat.add_color_stop_rgba(1.0, r, g, b, 0.0)

    ctx.set_source(pat)
    ctx.arc(x, y, size, 0, 2 * math.pi)
    ctx.fill()

# --------------------------
# Brushstroke curves
# --------------------------

def choose_line_color():
    """Weighted choice: mostly greys, occasional cyan."""
    r = random.random()

    if r < 0.30:
        return LINE_PALETTE[0]  # dark grey
    elif r < 0.58:
        return LINE_PALETTE[1]  # mid grey
    elif r < 0.78:
        return LINE_PALETTE[2]  # light grey
    elif r < 0.90:
        return LINE_PALETTE[3]  # off-white grey
    elif r < 0.97:
        return LINE_PALETTE[4]  # cyan
    else:
        return LINE_PALETTE[5]  # brighter cyan


def draw_brush_curve(x, y, segments=4):
    """Draw a single Bézier curve with bold, layered brushstroke effect."""
    r, g, b = choose_line_color()

    base_thickness = random.uniform(8, 20)

    for pass_index in range(3):
        thickness = base_thickness - pass_index * 2

        if thickness <= 0:
            continue

        alpha = 0.42 - pass_index * 0.11

        ctx.set_line_width(thickness)
        ctx.set_source_rgba(r, g, b, alpha)

        ctx.move_to(x, y)

        x_curr, y_curr = x, y

        for _ in range(segments):
            angle = (
                noise.pnoise2(
                    x_curr * 0.001,
                    y_curr * 0.001,
                    octaves=3
                )
                * math.pi
                * 4
            )

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
    """Draw many flowing brush curves."""
    random.seed(seed)

    for _ in range(400):
        x = random.uniform(0, WIDTH)
        y = random.uniform(0, HEIGHT)

        draw_brush_curve(x, y, segments=4)

# --------------------------
# Layer 1: Red/off-white blobs
# --------------------------

for _ in range(150):
    size = random.uniform(250, 450)

    draw_gradient_blob(
        random.uniform(0, WIDTH),
        random.uniform(0, HEIGHT),
        size,
        random.choice(BLOB_PALETTE)
    )

# --------------------------
# Layer 2: Grey/cyan brush curves
# --------------------------

draw_flow_field_lines(seed=42)

# --------------------------
# Optional subtle cyan sparks
# --------------------------

for _ in range(600):
    x = random.uniform(0, WIDTH)
    y = random.uniform(0, HEIGHT)

    size = random.uniform(0.8, 2.2)
    alpha = random.uniform(0.05, 0.18)

    ctx.set_source_rgba(0.12, 0.75, 0.85, alpha)
    ctx.arc(x, y, size, 0, 2 * math.pi)
    ctx.fill()

# --------------------------
# Save image
# --------------------------

surface.write_to_png("cc_pycairo/gen/bezier_brush_hoogstraat.png")
print("Saved bezier_brush_hoogstraat.png")