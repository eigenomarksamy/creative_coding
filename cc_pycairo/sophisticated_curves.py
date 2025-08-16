import cairo, math, random, colorsys

WIDTH, HEIGHT = 800, 800
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

# background
ctx.set_source_rgb(0.05, 0.05, 0.07)
ctx.paint()

# choose a harmonic palette around one hue
base_hue = random.random()
palette = []
for i in range(5):
    # spread hues harmonically (complementary + analogous)
    hue = (base_hue + random.choice([0, 0.05, -0.05, 0.5])) % 1.0
    sat = random.uniform(0.6, 0.9)
    light = random.uniform(0.4, 0.7)
    r, g, b = colorsys.hls_to_rgb(hue, light, sat)
    palette.append((r, g, b))

# draw many flowing curves
for i in range(200):
    # pick color with slight transparency
    r, g, b = random.choice(palette)
    ctx.set_source_rgba(r, g, b, 0.25)

    # vary thickness dynamically
    ctx.set_line_width(random.uniform(4, 10))

    # starting point near center
    angle = random.uniform(0, 2*math.pi)
    radius = random.uniform(50, WIDTH/2 - 50)
    x0 = WIDTH/2 + math.cos(angle) * radius
    y0 = HEIGHT/2 + math.sin(angle) * radius

    # control points follow a sinusoidal flow
    flow_angle = angle + random.uniform(-0.5, 0.5)
    x1 = x0 + math.cos(flow_angle) * random.uniform(80, 200)
    y1 = y0 + math.sin(flow_angle) * random.uniform(80, 200)

    x2 = x1 + math.cos(flow_angle + 0.5) * random.uniform(80, 200)
    y2 = y1 + math.sin(flow_angle + 0.5) * random.uniform(80, 200)

    x3 = WIDTH/2 + math.cos(angle + random.uniform(-0.3, 0.3)) * (radius + random.uniform(50, 150))
    y3 = HEIGHT/2 + math.sin(angle + random.uniform(-0.3, 0.3)) * (radius + random.uniform(50, 150))

    ctx.move_to(x0, y0)
    ctx.curve_to(x1, y1, x2, y2, x3, y3)
    ctx.stroke()

surface.write_to_png("cc_pycairo/gen/sophisticated_curves.png")
print("Saved sophisticated_curves.png")
