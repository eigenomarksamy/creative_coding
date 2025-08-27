import cairo, math, random

WIDTH, HEIGHT = 1920, 1920

# --- palette ---
BACKGROUND = (0.05, 0.02, 0.08)  # dark purple
COLORS = [
    (0.8, 0.9, 0.8),   # fungal white
    (0.4, 0.9, 0.5),   # glowing green
    (0.6, 0.3, 0.9),   # violet
    (0.9, 0.6, 0.3),   # amber nodes
]

# --- recursive drawing ---
def draw_branch(ctx, x, y, length, angle, depth):
    if depth <= 0 or length < 5:
        return

    # endpoint
    x2 = x + math.cos(angle) * length
    y2 = y + math.sin(angle) * length

    # choose color
    color = random.choice(COLORS)
    ctx.set_source_rgba(*color, 0.7)

    # draw curved stroke (Bezier)
    ctrl1x = x + math.cos(angle + random.uniform(-0.5, 0.5)) * length * 0.5
    ctrl1y = y + math.sin(angle + random.uniform(-0.5, 0.5)) * length * 0.5
    ctrl2x = x + math.cos(angle + random.uniform(-0.5, 0.5)) * length * 0.8
    ctrl2y = y + math.sin(angle + random.uniform(-0.5, 0.5)) * length * 0.8

    ctx.move_to(x, y)
    ctx.curve_to(ctrl1x, ctrl1y, ctrl2x, ctrl2y, x2, y2)
    ctx.set_line_width(max(0.5, depth * 0.8))
    ctx.stroke()

    # node glow
    if random.random() < 0.2:
        ctx.arc(x2, y2, 3, 0, 2 * math.pi)
        ctx.set_source_rgba(*color, 0.5)
        ctx.fill()

    # recursive branching
    new_depth = depth - 1
    for _ in range(random.randint(2, 4)):
        new_angle = angle + random.uniform(-1.2, 1.2)
        new_length = length * random.uniform(0.5, 0.8)
        draw_branch(ctx, x2, y2, new_length, new_angle, new_depth)

# --- main ---
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

# background
ctx.set_source_rgb(*BACKGROUND)
ctx.paint()

# start from center (mushroom brain core)
for _ in range(15):
    start_angle = random.uniform(0, 2*math.pi)
    draw_branch(ctx, WIDTH/2, HEIGHT/2, random.uniform(HEIGHT/8, 3*HEIGHT/16), start_angle, depth=8)

# add noise texture (spores/fungal grain)
for _ in range(16000):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    ctx.rectangle(x, y, 1, 1)
    ctx.set_source_rgba(1, 1, 1, random.uniform(0.01, 0.05))
    ctx.fill()

surface.write_to_png("cc_pycairo/gen/neural_mushroom_brain.png")
print("Saved neural_mushroom_brain.png")
