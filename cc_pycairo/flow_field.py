import cairo
import math
import random

WIDTH, HEIGHT = 800, 800

surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

ctx.set_source_rgb(1, 1, 1)
ctx.paint()

# Parameters
num_particles = 300
steps = 120
step_size = 3

def harmonic_palette(t):
    r = 0.5 + 0.5 * math.sin(t)
    g = 0.5 + 0.5 * math.sin(t + 2*math.pi/3)
    b = 0.5 + 0.5 * math.sin(t + 4*math.pi/3)
    return (r, g, b)

def flow_field(x, y):
    """Defines a smooth flow using sine/cosine fields"""
    scale = 0.005
    angle = math.sin(x * scale) + math.cos(y * scale)
    return angle

# Draw particles following flow field
for i in range(num_particles):
    x = random.uniform(0, WIDTH)
    y = random.uniform(0, HEIGHT)

    t = random.random() * 6.28
    r, g, b = harmonic_palette(t)
    ctx.set_source_rgba(r, g, b, 0.6)
    ctx.set_line_width(1.5)

    ctx.move_to(x, y)
    for _ in range(steps):
        angle = flow_field(x, y)
        x += math.cos(angle) * step_size
        y += math.sin(angle) * step_size
        ctx.line_to(x, y)
    ctx.stroke()

surface.write_to_png("cc_pycairo/gen/flow_field.png")
print("Saved flow_field.png")
