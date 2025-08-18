import math
import random
import cairo

# Canvas size
WIDTH, HEIGHT = 800, 800

def draw_recursive_glitch(ctx, x, y, radius, depth, max_depth, symmetry=6):
    if depth > max_depth or radius < 5:
        return

    # Random color with glitchy distortions
    r = abs(math.sin(depth * 0.7 + random.random()))
    g = abs(math.cos(depth * 1.3 + random.random()))
    b = abs(math.sin(depth * 0.9 + random.random() * 2))
    ctx.set_source_rgba(r, g, b, 0.7)

    # Line thickness changes with recursion
    ctx.set_line_width(max(1, (max_depth - depth) * 1.5))

    for i in range(symmetry):
        angle = (2 * math.pi / symmetry) * i + random.uniform(-0.05, 0.05)  # glitch jitter
        nx = x + math.cos(angle) * radius
        ny = y + math.sin(angle) * radius

        ctx.move_to(x, y)
        ctx.line_to(nx, ny)
        ctx.stroke()

        # Recursive call with smaller radius, but slight glitch offset
        draw_recursive_glitch(ctx,
                              nx + random.uniform(-10, 10),
                              ny + random.uniform(-10, 10),
                              radius * 0.6,
                              depth + 1,
                              max_depth,
                              symmetry)

# Create Cairo surface
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

# Background
ctx.set_source_rgb(0.05, 0.05, 0.08)
ctx.paint()

# Draw recursive glitch symmetry
draw_recursive_glitch(ctx, WIDTH/2, HEIGHT/2, 250, 0, 5, symmetry=8)

# Save result
surface.write_to_png("cc_pycairo/gen/recursive_glitch_symmetry.png")
print("Saved recursive_glitch_symmetry.png")
