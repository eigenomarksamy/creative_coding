import cairo, math, random

WIDTH, HEIGHT = 800, 800
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

# white background
ctx.set_source_rgb(1, 1, 1)
ctx.paint()

def lsd_wave(y_offset, color):
    ctx.set_line_width(1.2)
    ctx.set_source_rgba(*color, 0.4)
    ctx.move_to(0, y_offset)

    # draw an organic sinusoidal path with random modulation
    for x in range(0, WIDTH, 5):
        amp = 30 + 10 * math.sin(x * 0.02 + random.random())
        freq = 0.015
        y = y_offset + math.sin(x * freq) * amp + random.uniform(-3, 3)
        ctx.line_to(x, y)
    ctx.stroke()

# palette of soft psychedelic tones
colors = [
    (0.8, 0.2, 0.9),
    (0.3, 0.8, 0.9),
    (0.9, 0.7, 0.2),
    (0.5, 0.3, 0.9),
]

# draw many slightly offset waves for texture
for i in range(100):
    y = random.uniform(0, HEIGHT)
    color = random.choice(colors)
    lsd_wave(y, color)

surface.write_to_png("cc_pycairo/gen/lsd_linescape.png")
print("Saved: lsd_linescape.png")
