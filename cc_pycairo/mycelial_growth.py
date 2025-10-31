import cairo, math, random, noise

WIDTH, HEIGHT = 2000, 2000
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

ctx.set_source_rgb(1, 1, 1)
ctx.paint()

NUM_ROOTS = 1200
BRANCH_PROB = 0.08
STEPS = 150
STEP_SIZE = 6
NOISE_SCALE = 0.0015

PALETTE = [
    (0.7, 0.6, 0.3),
    (0.4, 0.6, 0.3),
    (0.6, 0.5, 0.2),
    (0.8, 0.7, 0.5),
    (0.5, 0.4, 0.2),
]

def field_angle(x, y):
    return noise.pnoise2(x * NOISE_SCALE, y * NOISE_SCALE, octaves=3) * math.pi * 4

def grow_branch(x, y, color, depth=0):
    if depth > 2:  # limit recursive branches
        return

    r, g, b = color
    ctx.set_source_rgba(r, g, b, random.uniform(0.05, 0.15))
    ctx.set_line_width(random.uniform(0.5, 2.5))
    ctx.move_to(x, y)

    for _ in range(STEPS):
        angle = field_angle(x, y) + random.uniform(-0.2, 0.2)
        length = STEP_SIZE * random.uniform(0.7, 1.3)
        x += math.cos(angle) * length
        y += math.sin(angle) * length
        ctx.line_to(x, y)

        if random.random() < BRANCH_PROB:
            grow_branch(x, y, random.choice(PALETTE), depth + 1)

    ctx.stroke()

for _ in range(NUM_ROOTS):
    x, y = random.uniform(0, WIDTH), random.uniform(0, HEIGHT)
    grow_branch(x, y, random.choice(PALETTE))

surface.write_to_png("cc_pycairo/gen/mycelial_growth.png")
print("Saved mycelial_growth.png")
