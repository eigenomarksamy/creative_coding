import cairo, math, random, noise

WIDTH, HEIGHT = 1000, 1000
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

# Background wash
grad = cairo.RadialGradient(WIDTH/2, HEIGHT/2, 200, WIDTH/2, HEIGHT/2, WIDTH/1.2)
grad.add_color_stop_rgb(0, 0.1, 0.1, 0.12)
grad.add_color_stop_rgb(1, 0.02, 0.02, 0.03)
ctx.set_source(grad)
ctx.rectangle(0, 0, WIDTH, HEIGHT)
ctx.fill()

# --- Texture 1: stippling
for _ in range(5000):
    x = random.uniform(0, WIDTH)
    y = random.uniform(0, HEIGHT)
    alpha = random.uniform(0.02, 0.07)
    r = random.uniform(0.5, 1.5)
    ctx.set_source_rgba(1, 1, 1, alpha)
    ctx.arc(x, y, r, 0, 2*math.pi)
    ctx.fill()

# --- Texture 2: cross-hatching
ctx.set_line_width(0.5)
for i in range(2000):
    x = random.uniform(0, WIDTH)
    y = random.uniform(0, HEIGHT)
    length = random.uniform(20, 60)
    angle = random.choice([0, math.pi/4, math.pi/2, 3*math.pi/4])
    ctx.set_source_rgba(1, 1, 1, 0.05)
    ctx.move_to(x, y)
    ctx.line_to(x + math.cos(angle)*length, y + math.sin(angle)*length)
    ctx.stroke()

# --- Texture 3: noisy flow lines
for i in range(2000):
    x = random.uniform(0, WIDTH)
    y = random.uniform(0, HEIGHT)
    ctx.set_source_rgba(0.7, 0.9, 1, 0.08)
    ctx.set_line_width(1)
    ctx.move_to(x, y)
    for _ in range(15):
        angle = noise.pnoise2(x*0.002, y*0.002)*math.pi*2
        step = 8
        x += math.cos(angle)*step
        y += math.sin(angle)*step
        ctx.line_to(x, y)
    ctx.stroke()

# --- Overlay wash
ctx.set_source_rgba(0.2, 0.1, 0.3, 0.15)
ctx.rectangle(0, 0, WIDTH, HEIGHT)
ctx.fill()

surface.write_to_png("cc_pycairo/gen/textural_garden.png")
print("Saved textural_garden.png")
