import math
import random
import cairo
import noise

PALETTE_255 = [(234, 210, 160), (131, 161, 205), (99, 107, 47), (255, 111, 0)]

def rgb01(rgb255):
    r, g, b = rgb255
    return (r / 255.0, g / 255.0, b / 255.0)

PALETTE = [rgb01(c) for c in PALETTE_255]

WIDTH, HEIGHT = 3638, 2551
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

bg = cairo.LinearGradient(0, 0, WIDTH, 0)
bg.add_color_stop_rgb(0.0, 1.0, 1.0, 1.0)
bg.add_color_stop_rgb(1.0, 0.0, 0.0, 0.0)
ctx.set_source(bg)
ctx.paint()

def make_noise_tile(tile_w=512, tile_h=512, alpha=0.10, contrast=0.5, seed=123):
    rnd = random.Random(seed)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, tile_w, tile_h)
    data = surf.get_data()  # BGRA
    stride = surf.get_stride()

    for y in range(tile_h):
        row = y * stride
        for x in range(tile_w):
            n = rnd.random()
            n = 0.5 + (n - 0.5) * contrast  # pull toward mid grey
            g = int(max(0, min(255, n * 255)))
            a = int(max(0, min(255, alpha * 255)))

            i = row + x * 4
            data[i + 0] = g
            data[i + 1] = g
            data[i + 2] = g
            data[i + 3] = a

    surf.mark_dirty()
    return surf


def add_textured_gradient_overlay(ctx, WIDTH, HEIGHT, seed=123,
                                 paper_strength=0.10, grain_strength=0.04):
    # same gradient as background
    grad = cairo.LinearGradient(0, 0, WIDTH, 0)
    grad.add_color_stop_rgb(0.0, 1.0, 1.0, 1.0)
    grad.add_color_stop_rgb(1.0, 0.0, 0.0, 0.0)

    # PAPER (large, subtle)
    paper_tile = make_noise_tile(
        tile_w=768, tile_h=768,
        alpha=paper_strength, contrast=0.25,
        seed=seed
    )
    paper_pat = cairo.SurfacePattern(paper_tile)
    paper_pat.set_extend(cairo.EXTEND_REPEAT)

    ctx.save()
    ctx.set_operator(cairo.OPERATOR_SOFT_LIGHT)
    ctx.set_source(grad)

    m = cairo.Matrix()
    m.scale(0.35, 0.35)  # bigger features; increase to 0.5 for smaller features
    paper_pat.set_matrix(m)

    ctx.mask(paper_pat)
    ctx.restore()

    # GRAIN (fine, very subtle)
    grain_tile = make_noise_tile(
        tile_w=512, tile_h=512,
        alpha=grain_strength, contrast=0.60,
        seed=seed + 999
    )
    grain_pat = cairo.SurfacePattern(grain_tile)
    grain_pat.set_extend(cairo.EXTEND_REPEAT)

    ctx.save()
    ctx.set_operator(cairo.OPERATOR_SOFT_LIGHT)
    ctx.set_source(grad)
    ctx.mask(grain_pat)
    ctx.restore()

def make_balanced_color_bag(n_items, palette):
    k = len(palette)
    q, r = divmod(n_items, k)
    bag = []
    for c in palette:
        bag.extend([c] * q)
    bag.extend(palette[:r])
    random.shuffle(bag)
    return bag

def draw_gradient_blob(x, y, size, color):
    pat = cairo.RadialGradient(x, y, size * 0.1, x, y, size)
    r, g, b = color
    pat.add_color_stop_rgba(0, r, g, b, 0.8)
    pat.add_color_stop_rgba(1, r, g, b, 0.0)
    ctx.set_source(pat)
    ctx.arc(x, y, size, 0, 2 * math.pi)
    ctx.fill()

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
    curve_colors = make_balanced_color_bag(n_lines, PALETTE)

    for i in range(n_lines):
        x, y = random.uniform(0, WIDTH), random.uniform(0, HEIGHT)
        draw_brush_curve(x, y, color=curve_colors[i], segments=4)

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

draw_flow_field_lines(seed=42, n_lines=400)

add_textured_gradient_overlay(ctx, WIDTH, HEIGHT, seed=999,
                             paper_strength=0.10, grain_strength=0.04)

surface.write_to_png("cc_pycairo/gen/bezier_brush_12.png")
print("Saved bezier_brush_12.png")
