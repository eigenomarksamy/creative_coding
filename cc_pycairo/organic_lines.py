import math
import random
import cairo
import noise  # pip install noise

# Image settings
WIDTH, HEIGHT = 4000, 4000
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

# Background
ctx.set_source_rgb(0.8, 0.8, 0.8)
ctx.paint()

# Parameters
num_lines = 200
points_per_line = 100
line_spacing = 20
noise_scale = 0.005
amplitude = 100

# Draw layered organic lines
for i in range(num_lines):
    y_offset = i * line_spacing + 200
    hue = random.random()
    r, g, b = 0.5 + 0.5 * math.sin(hue * math.pi * 2), 0.5 + 0.5 * math.sin(hue * math.pi * 4), 0.5 + 0.5 * math.cos(hue * math.pi * 2)
    ctx.set_source_rgba(r, g, b, 0.5)

    ctx.move_to(0, y_offset)
    for j in range(points_per_line):
        x = j * (WIDTH / points_per_line)
        n = noise.pnoise2(x * noise_scale, i * noise_scale, octaves=3)
        y = y_offset + n * amplitude
        ctx.line_to(x, y)
    ctx.stroke()

# Save
surface.write_to_png("cc_pycairo/gen/organic_lines.png")
print("Saved organic_lines.png")
