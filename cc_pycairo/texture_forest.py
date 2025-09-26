import cairo, math, random, noise

WIDTH, HEIGHT = 1200, 1600  # vertical canvas
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

# --- Background fog ---
grad = cairo.LinearGradient(0, 0, 0, HEIGHT)
grad.add_color_stop_rgb(0, 0.05, 0.07, 0.09)   # dark top
grad.add_color_stop_rgb(1, 0.02, 0.03, 0.04)   # lighter bottom
ctx.set_source(grad)
ctx.rectangle(0, 0, WIDTH, HEIGHT)
ctx.fill()

# --- Texture 1: misty stippling ---
for _ in range(8000):
    x = random.uniform(0, WIDTH)
    y = random.uniform(0, HEIGHT)
    r = random.uniform(0.5, 1.2)
    alpha = random.uniform(0.01, 0.05)
    ctx.set_source_rgba(1, 1, 1, alpha)
    ctx.arc(x, y, r, 0, 2*math.pi)
    ctx.fill()

# --- Texture 2: trunks / roots ---
for i in range(200):
    x = random.uniform(100, WIDTH-100)
    y = HEIGHT
    ctx.set_source_rgba(0.3, 0.25, 0.2, 0.15)
    ctx.set_line_width(random.uniform(2, 8))
    ctx.move_to(x, y)
    steps = random.randint(60, 120)
    for _ in range(steps):
        angle = noise.pnoise2(x*0.002, y*0.002, repeatx=9999, repeaty=9999)*math.pi*2
        x += math.cos(angle)*2
        y -= 5  # upward growth
        ctx.line_to(x, y)
    ctx.stroke()

# --- Texture 3: canopy clusters ---
for _ in range(150):
    cx = random.uniform(100, WIDTH-100)
    cy = random.uniform(200, HEIGHT/2)
    r = random.uniform(50, 120)
    for _ in range(600):
        angle = random.uniform(0, 2*math.pi)
        dist = random.uniform(0, r)
        x = cx + math.cos(angle)*dist
        y = cy + math.sin(angle)*dist
        alpha = random.uniform(0.01, 0.08)
        ctx.set_source_rgba(0.2, 0.6+random.uniform(-0.1,0.2), 0.3, alpha)
        ctx.arc(x, y, random.uniform(0.8, 2.0), 0, 2*math.pi)
        ctx.fill()

# --- Texture 4: spores / mist bubbles ---
for _ in range(80):
    x = random.uniform(0, WIDTH)
    y = random.uniform(0, HEIGHT)
    r = random.uniform(20, 60)
    grad = cairo.RadialGradient(x, y, r*0.1, x, y, r)
    grad.add_color_stop_rgba(0, 0.9, 0.9, 1, 0.06)
    grad.add_color_stop_rgba(1, 0.6, 0.8, 0.9, 0.0)
    ctx.set_source(grad)
    ctx.arc(x, y, r, 0, 2*math.pi)
    ctx.fill()

surface.write_to_png("cc_pycairo/gen/textural_forest.png")
print("Saved textural_forest.png")
