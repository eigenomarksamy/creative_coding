import cairo
import math
import random

# Image size
WIDTH, HEIGHT = 800, 800

# Color palette (harmonic gradient)
def palette(t):
    # soft gradient from warm to cool
    return (
        0.6 + 0.4 * math.sin(t * 2 * math.pi),
        0.6 + 0.4 * math.sin(t * 2 * math.pi + 2),
        0.6 + 0.4 * math.sin(t * 2 * math.pi + 4)
    )

# Function to draw one wedge and then repeat it around
def draw_mandala(ctx, num_wedges=12, num_strokes=150):
    angle_step = 2 * math.pi / num_wedges
    
    for i in range(num_strokes):
        # pick random points within one wedge
        r1 = random.uniform(50, WIDTH // 2 - 50)
        r2 = random.uniform(50, WIDTH // 2 - 50)
        a1 = random.uniform(0, angle_step)
        a2 = random.uniform(0, angle_step)

        # convert polar → cartesian
        x1, y1 = r1 * math.cos(a1), r1 * math.sin(a1)
        x2, y2 = r2 * math.cos(a2), r2 * math.sin(a2)
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2  # curve control point

        # color based on radial distance
        col = palette(r1 / (WIDTH / 2))
        ctx.set_source_rgba(*col, 0.7)
        ctx.set_line_width(random.uniform(1.5, 4.0))

        # draw same stroke rotated around circle
        for k in range(num_wedges):
            theta = k * angle_step
            cos_t, sin_t = math.cos(theta), math.sin(theta)

            def rotate(x, y):
                return x * cos_t - y * sin_t, x * sin_t + y * cos_t

            X1, Y1 = rotate(x1, y1)
            X2, Y2 = rotate(x2, y2)
            CX, CY = rotate(cx, cy)

            ctx.move_to(WIDTH/2 + X1, HEIGHT/2 + Y1)
            ctx.curve_to(WIDTH/2 + CX, HEIGHT/2 + CY,
                         WIDTH/2 + CX, HEIGHT/2 + CY,
                         WIDTH/2 + X2, HEIGHT/2 + Y2)
            ctx.stroke()

# Create surface
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)
ctx.set_source_rgb(1, 1, 1)  # background
ctx.paint()

draw_mandala(ctx, num_wedges=16, num_strokes=300)

surface.write_to_png("cc_pycairo/gen/mandala.png")
print("Saved mandala.png")
