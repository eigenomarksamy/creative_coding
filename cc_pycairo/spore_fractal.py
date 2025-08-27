import cairo
import math
import random

WIDTH, HEIGHT = 2800, 2800

def spore_burst(ctx, x, y, radius, depth, max_depth):
    if depth > max_depth or radius < 1:
        return
    
    # Base color with variation depending on depth
    hue = (depth * 40 + random.randint(-10, 10)) % 360
    r, g, b = hsv_to_rgb(hue/360, 0.8, 0.9)
    ctx.set_source_rgba(r, g, b, 0.6 / (depth + 1))
    
    # Draw central spore
    ctx.arc(x, y, radius, 0, 2 * math.pi)
    ctx.fill()
    
    # Generate children spores
    num_children = random.randint(4, 7)
    for _ in range(num_children):
        angle = random.random() * 2 * math.pi
        dist = random.uniform(radius * 1.5, radius * 3.5)
        new_x = x + math.cos(angle) * dist
        new_y = y + math.sin(angle) * dist
        new_radius = radius * random.uniform(0.4, 0.7)
        spore_burst(ctx, new_x, new_y, new_radius, depth + 1, max_depth)


def hsv_to_rgb(h, s, v):
    i = int(h * 6)
    f = h * 6 - i
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    i = i % 6
    if i == 0: r, g, b = v, t, p
    if i == 1: r, g, b = q, v, p
    if i == 2: r, g, b = p, v, t
    if i == 3: r, g, b = p, q, v
    if i == 4: r, g, b = t, p, v
    if i == 5: r, g, b = v, p, q
    return r, g, b


def draw_spore_explosions(filename="cc_pycairo/gen/spore_fractal.png"):
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
    ctx = cairo.Context(surface)

    # Background texture-like noise
    ctx.set_source_rgb(0.05, 0.05, 0.08)
    ctx.paint()

    for _ in range(15):  # multiple bursts
        x = random.randint(WIDTH//4, 3*WIDTH//4)
        y = random.randint(HEIGHT//4, 3*HEIGHT//4)
        spore_burst(ctx, x, y, radius=80, depth=0, max_depth=6)

    surface.write_to_png(filename)
    print(f"Saved {filename}")


if __name__ == "__main__":
    draw_spore_explosions()
