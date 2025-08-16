import cairo
import math
import random

# Image size
WIDTH, HEIGHT = 800, 800

# Create cairo surface
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

# Background
ctx.rectangle(0, 0, WIDTH, HEIGHT)
ctx.set_source_rgb(0.05, 0.05, 0.08)  # dark bg
ctx.fill()

# Dynamic palette (harmonic with base hue)
def generate_palette():
    base_hue = random.random()
    return [
        (base_hue, 0.6, 0.8),
        ((base_hue + 0.2) % 1.0, 0.7, 0.9),
        ((base_hue + 0.4) % 1.0, 0.5, 0.7),
    ]

def hsv_to_rgb(h, s, v):
    i = int(h * 6)
    f = h * 6 - i
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    i %= 6
    if i == 0: return (v, t, p)
    if i == 1: return (q, v, p)
    if i == 2: return (p, v, t)
    if i == 3: return (p, q, v)
    if i == 4: return (t, p, v)
    if i == 5: return (v, p, q)

palette = [hsv_to_rgb(*c) for c in generate_palette()]

# Function to draw one curve + its symmetries
def draw_symmetric_curve():
    x1, y1 = random.randint(100, 300), random.randint(100, 300)
    x2, y2 = random.randint(500, 700), random.randint(100, 300)
    x3, y3 = random.randint(100, 300), random.randint(500, 700)
    x4, y4 = random.randint(500, 700), random.randint(500, 700)

    color = random.choice(palette)
    ctx.set_source_rgb(*color)
    ctx.set_line_width(random.uniform(2.5, 5.0))

    # All symmetry variants
    points = [
        (x1, y1, x2, y2, x3, y3, x4, y4),
        (WIDTH-x1, y1, WIDTH-x2, y2, WIDTH-x3, y3, WIDTH-x4, y4),  # mirror X
        (x1, HEIGHT-y1, x2, HEIGHT-y2, x3, HEIGHT-y3, x4, HEIGHT-y4),  # mirror Y
        (WIDTH-x1, HEIGHT-y1, WIDTH-x2, HEIGHT-y2, WIDTH-x3, HEIGHT-y3, WIDTH-x4, HEIGHT-y4),  # both
    ]

    for (a,b,c,d,e,f,g,h) in points:
        ctx.move_to(a, b)
        ctx.curve_to(c, d, e, f, g, h)
        ctx.stroke()

# Draw many symmetric curves
for _ in range(30):
    draw_symmetric_curve()

# Save image
surface.write_to_png("cc_pycairo/gen/symmetric_art.png")
print("Saved symmetric_art.png")
