import cairo, math, random

WIDTH, HEIGHT = 800, 600

surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

# Background gradient
grad = cairo.LinearGradient(0, 0, 0, HEIGHT)
grad.add_color_stop_rgb(0, 0.05, 0.05, 0.1)
grad.add_color_stop_rgb(1, 0.15, 0.05, 0.2)
ctx.rectangle(0, 0, WIDTH, HEIGHT)
ctx.set_source(grad)
ctx.fill()

# Function: draw figure silhouette
def draw_figure(x_offset, flip=False):
    ctx.save()
    ctx.translate(x_offset, HEIGHT * 0.5)
    if flip:
        ctx.scale(-1, 1)
    ctx.set_line_width(2.0)
    ctx.set_source_rgba(1, 0.9, 0.9, 0.4)

    # Simplified face/torso line
    ctx.move_to(0, -100)
    ctx.curve_to(30, -90, 50, -50, 40, 0)
    ctx.curve_to(35, 50, 20, 100, 0, 150)
    ctx.stroke()
    ctx.restore()

# Draw both figures
draw_figure(WIDTH * 0.35, flip=False)
draw_figure(WIDTH * 0.65, flip=True)

# Function: draw echo (the space between)
def draw_echo():
    for i in range(400):
        t = i / 400
        x = WIDTH * 0.5 + random.uniform(-50, 50)
        y = HEIGHT * 0.3 + random.uniform(0, HEIGHT * 0.4)
        alpha = random.uniform(0.02, 0.08)
        width = random.uniform(0.5, 2.0)
        ctx.set_source_rgba(1, 0.8, 0.9, alpha)
        ctx.set_line_width(width)
        ctx.move_to(x, y)
        for j in range(4):
            x += random.uniform(-20, 20)
            y += random.uniform(-20, 20)
            ctx.line_to(x, y)
        ctx.stroke()

draw_echo()

# Save output
surface.write_to_png("cc_pycairo/gen/echo_of_an_embrace.png")
print("Saved: echo_of_an_embrace.png")
