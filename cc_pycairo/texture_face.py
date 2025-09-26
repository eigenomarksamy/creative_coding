import cairo, math, random, noise

WIDTH, HEIGHT = 1000, 1200
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

# --- Background ---
ctx.set_source_rgb(0.05, 0.05, 0.08)
ctx.paint()

# --- Face silhouette ---
cx, cy, r = WIDTH/2, HEIGHT/2, 400
ctx.arc(cx, cy, r, 0, 2*math.pi)
ctx.clip()  # all textures now stay inside the head shape

# --- Skin texture: stippling ---
for _ in range(25000):
    x = random.uniform(cx-r, cx+r)
    y = random.uniform(cy-r, cy+r)
    if (x-cx)**2 + (y-cy)**2 <= r**2:  # inside circle
        alpha = random.uniform(0.02, 0.06)
        size = random.uniform(0.5, 1.5)
        ctx.set_source_rgba(1, 1, 1, alpha)
        ctx.arc(x, y, size, 0, 2*math.pi)
        ctx.fill()

# --- Eye regions (darker clusters) ---
for ex in [-120, 120]:  # left & right eyes
    for _ in range(1500):
        angle = random.uniform(0, 2*math.pi)
        dist = random.uniform(0, 50)
        x = cx + ex + math.cos(angle)*dist
        y = cy - 80 + math.sin(angle)*dist
        ctx.set_source_rgba(0.9, 0.9, 1, 0.1)
        ctx.arc(x, y, random.uniform(0.5, 1.2), 0, 2*math.pi)
        ctx.fill()

# --- Mouth (flow lines) ---
mx, my = cx, cy+180
for i in range(80):
    x, y = mx-100, my + i*2
    ctx.set_line_width(0.6)
    ctx.set_source_rgba(1, 0.6, 0.6, 0.05)
    ctx.move_to(x, y)
    for _ in range(40):
        angle = noise.pnoise2(x*0.01, y*0.01)*math.pi*2
        x += math.cos(angle)*5
        y += math.sin(angle)*3
        ctx.line_to(x, y)
    ctx.stroke()

# --- Surreal spores overlay ---
for _ in range(100):
    x = random.uniform(cx-r, cx+r)
    y = random.uniform(cy-r, cy+r)
    if (x-cx)**2 + (y-cy)**2 <= r**2:
        rr = random.uniform(10, 40)
        grad = cairo.RadialGradient(x, y, rr*0.1, x, y, rr)
        grad.add_color_stop_rgba(0, 0.8, 0.8, 1, 0.05)
        grad.add_color_stop_rgba(1, 0.3, 0.6, 0.9, 0)
        ctx.set_source(grad)
        ctx.arc(x, y, rr, 0, 2*math.pi)
        ctx.fill()

surface.write_to_png("cc_pycairo/gen/textured_face.png")
print("Saved textured_face.png")
