import cairo
import math, random

WIDTH, HEIGHT = 1800, 1800
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

# Background
ctx.set_source_rgb(0.05, 0.05, 0.08)
ctx.paint()

# ---- TATTOO LAYER ----
def draw_tattoo_lines(ctx, num=1350):
    ctx.set_line_width(random.uniform(0.2, 4.0))
    for _ in range(num):
        x1 = random.uniform(0, WIDTH)
        y1 = random.uniform(HEIGHT/2, HEIGHT)
        x2 = x1 + random.uniform(-60, 60)
        y2 = y1 + random.uniform(-60, 60)

        intensity = random.uniform(0.1, 0.4)
        ctx.set_source_rgba(1, 1, 1, intensity)  # faint white lines
        ctx.move_to(x1, y1)
        ctx.line_to(x2, y2)
        ctx.stroke()

draw_tattoo_lines(ctx)

# ---- BALLOON LAYER ----
def draw_balloon(ctx, x, y, r):
    # Balloon gradient
    grad = cairo.RadialGradient(x, y, r*0.1, x, y, r)
    # Softer gradient
    grad.add_color_stop_rgba(0, random.uniform(0.6, 0.9), 
                                random.uniform(0.6, 0.9), 
                                random.uniform(0.6, 0.9), 0.35)
    grad.add_color_stop_rgba(1, random.uniform(0.2, 0.5), 
                                random.uniform(0.2, 0.5), 
                                random.uniform(0.2, 0.5), 0.0)

    grad.add_color_stop_rgba(1, random.random(), random.random(), random.random(), 0.3)

    ctx.set_source(grad)
    ctx.arc(x, y, r, 0, 2*math.pi)
    ctx.fill()

    # String
    ctx.set_source_rgb(0.8, 0.8, 0.9)
    ctx.set_line_width(0.5)
    ctx.move_to(x, y + r)
    ctx.line_to(x, y + r + 40)
    ctx.stroke()

# Draw multiple balloons rising from tattoos
for _ in range(900):
    x = random.uniform(100, WIDTH - 100)
    y = random.uniform(100, HEIGHT/2)
    r = random.uniform(20, 60)
    draw_balloon(ctx, x, y, r)

surface.write_to_png("cc_pycairo/gen/tattoos_and_balloons.png")
print("Saved tattoos_and_balloons.png")
