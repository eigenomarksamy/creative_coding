import math
import random
import cairo
import noise

PALETTE_255 = [(234, 210, 160), (131, 161, 205), (99, 107, 47), (255, 111, 0)]

def rgb01(rgb255):
    r, g, b = rgb255
    return (r / 255.0, g / 255.0, b / 255.0)

PALETTE = [rgb01(c) for c in PALETTE_255]

# --------------------------
# Canvas setup
# --------------------------
WIDTH, HEIGHT = 2560, 1600
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

bg = cairo.LinearGradient(0, 0, WIDTH, 0)
bg.add_color_stop_rgb(0.0, 1.0, 1.0, 1.0)  # white
bg.add_color_stop_rgb(1.0, 0.0, 0.0, 0.0)  # black
ctx.set_source(bg)
ctx.paint()

# --------------------------
# Helpers: balanced color bags
# --------------------------
def make_balanced_color_bag(n_items, palette):
    """
    Returns a shuffled list of length n_items with palette colors distributed
    as evenly as possible.
    """
    k = len(palette)
    q, r = divmod(n_items, k)
    bag = []
    for c in palette:
        bag.extend([c] * q)
    # distribute remainder
    bag.extend(palette[:r])
    random.shuffle(bag)
    return bag

# --------------------------
# Blob function
# --------------------------
def draw_gradient_blob(x, y, size, color):
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
def draw_brush_curve(x, y, color, segments=4):
    r, g, b = color
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

def draw_flow_field_lines(seed, n_lines=400):
    random.seed(seed)

    # balanced bag for curves
    curve_colors = make_balanced_color_bag(n_lines, PALETTE)

    for i in range(n_lines):
        x, y = random.uniform(0, WIDTH), random.uniform(0, HEIGHT)
        draw_brush_curve(x, y, color=curve_colors[i], segments=4)

# --------------------------
# Layer 1: Soft blobs (balanced)
# --------------------------
N_BLOBS = 144
blob_colors = make_balanced_color_bag(N_BLOBS, PALETTE)

for i in range(N_BLOBS):
    size = random.uniform(250, 450)
    draw_gradient_blob(
        random.uniform(0, WIDTH),
        random.uniform(0, HEIGHT),
        size,
        blob_colors[i]
    )

# --------------------------
# Layer 2: Brush curves (balanced)
# --------------------------
draw_flow_field_lines(seed=42, n_lines=400)

# --------------------------
# Save image
# --------------------------
surface.write_to_png("cc_pycairo/gen/bezier_brush_12.png")
print("Saved bezier_brush_12.png")
