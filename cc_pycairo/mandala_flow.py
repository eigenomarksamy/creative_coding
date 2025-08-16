import cairo
import math
import random

# Image size
WIDTH, HEIGHT = 800, 800

# Parameters
NUM_STROKES = 1500
STROKE_LENGTH = 30
PALETTE = [(239/255, 71/255, 111/255),
           (255/255, 209/255, 102/255),
           (6/255, 214/255, 160/255),
           (17/255, 138/255, 178/255),
           (7/255, 59/255, 76/255)]

# Symmetry (number of mirrored slices)
SYMMETRY = 8  

# Flow field function
def flow_field(x, y):
    angle = math.sin(x * 0.005) + math.cos(y * 0.005)
    return angle * math.pi

# Draw function
def draw(ctx):
    ctx.set_line_width(1.8)
    for _ in range(NUM_STROKES):
        # Random starting position
        x, y = random.uniform(0, WIDTH/2), random.uniform(0, HEIGHT/2)
        color = random.choice(PALETTE)
        ctx.set_source_rgba(*color, 0.7)

        # Draw in multiple symmetric slices
        for s in range(SYMMETRY):
            angle_offset = (2 * math.pi / SYMMETRY) * s
            for i in range(STROKE_LENGTH):
                angle = flow_field(x, y) + angle_offset
                nx = x + math.cos(angle) * 2
                ny = y + math.sin(angle) * 2

                # Translate + mirror
                ctx.move_to(WIDTH/2 + x, HEIGHT/2 + y)
                ctx.line_to(WIDTH/2 + nx, HEIGHT/2 + ny)

                # Rotate around center
                rx = math.cos(angle_offset) * (nx) - math.sin(angle_offset) * (ny)
                ry = math.sin(angle_offset) * (nx) + math.cos(angle_offset) * (ny)
                ctx.move_to(WIDTH/2 + rx, HEIGHT/2 + ry)
                ctx.line_to(WIDTH/2 + x, HEIGHT/2 + y)

                x, y = nx, ny
            ctx.stroke()

# Main
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

# Background
ctx.set_source_rgb(1, 1, 1)
ctx.paint()

# Draw pattern
draw(ctx)

# Save
surface.write_to_png("cc_pycairo/gen/mandala_flow.png")
print("Saved mandala_flow.png")
