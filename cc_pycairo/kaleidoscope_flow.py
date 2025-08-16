import cairo
import math
import random

WIDTH, HEIGHT = 800, 800

# Number of symmetry slices (like a kaleidoscope)
SYMMETRY = 8
CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2

# Flow field parameters
SCALE = 0.005
ANGLE_VARIATION = 2 * math.pi

def flow_angle(x, y, t=0):
    """Flow field: determines angle at position (x, y)."""
    return math.sin(x * SCALE + t) + math.cos(y * SCALE - t)

# Create surface
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

# Background
ctx.set_source_rgb(0.05, 0.05, 0.08)
ctx.paint()

# Generate strokes
num_strokes = 300
for _ in range(num_strokes):
    # Random start point near center
    x, y = CENTER_X + random.uniform(-200, 200), CENTER_Y + random.uniform(-200, 200)

    # Choose color (harmonic palette)
    r = 0.5 + 0.5 * math.sin(random.random() * math.pi * 2)
    g = 0.5 + 0.5 * math.sin(random.random() * math.pi * 2 + 2)
    b = 0.5 + 0.5 * math.sin(random.random() * math.pi * 2 + 4)

    ctx.set_source_rgba(r, g, b, 0.6)
    ctx.set_line_width(random.uniform(1.5, 3.5))

    # Each stroke follows flow field
    ctx.new_path()
    for step in range(80):
        angle = flow_angle(x, y)
        dx, dy = math.cos(angle), math.sin(angle)

        # Draw symmetrical copies
        for s in range(SYMMETRY):
            theta = 2 * math.pi * s / SYMMETRY
            rx = math.cos(theta) * (x - CENTER_X) - math.sin(theta) * (y - CENTER_Y) + CENTER_X
            ry = math.sin(theta) * (x - CENTER_X) + math.cos(theta) * (y - CENTER_Y) + CENTER_Y

            if step == 0:
                ctx.move_to(rx, ry)
            else:
                ctx.line_to(rx, ry)

        x += dx * 5
        y += dy * 5

    ctx.stroke()

# Save output
surface.write_to_png("cc_pycairo/gen/kaleidoscope_flow.png")
print("Saved kaleidoscope_flow.png")
