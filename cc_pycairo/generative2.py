import cairo
import math
import random

WIDTH, HEIGHT = 800, 800

class GenerativeCanvas:
    def __init__(self, width=WIDTH, height=HEIGHT, background=(0,0,0)):
        self.width, self.height = width, height
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        self.ctx = cairo.Context(self.surface)

        # background
        self.ctx.set_source_rgb(*background)
        self.ctx.paint()

        # move origin to center (useful for symmetry / mandalas)
        self.ctx.translate(width / 2, height / 2)

    def save(self, filename="output.png"):
        self.surface.write_to_png(filename)
        print(f"Saved {filename}")

# --- Drawing modules (engines) ---

def kaleidoscope(ctx, num_shapes=200, slices=12):
    """Draw symmetric kaleidoscope pattern"""
    for i in range(num_shapes):
        angle = random.random() * 2 * math.pi
        r = random.uniform(50, 350)
        x, y = r * math.cos(angle), r * math.sin(angle)

        # random color
        ctx.set_source_rgba(random.random(), random.random(), random.random(), 0.7)

        # repeat symmetrically
        for s in range(slices):
            theta = 2 * math.pi * s / slices
            ctx.save()
            ctx.rotate(theta)
            ctx.arc(x, y, random.uniform(5, 15), 0, 2 * math.pi)
            ctx.fill()
            ctx.restore()


def flow_field(ctx, num_lines=300, steps=100, step_size=5):
    """Particles follow a flow field based on sin/cos"""
    for i in range(num_lines):
        x, y = random.uniform(-WIDTH/2, WIDTH/2), random.uniform(-HEIGHT/2, HEIGHT/2)
        ctx.set_source_rgba(random.random(), random.random(), random.random(), 0.4)
        ctx.set_line_width(1.0)

        ctx.move_to(x, y)
        for _ in range(steps):
            angle = math.sin(y * 0.01) + math.cos(x * 0.01)
            x += math.cos(angle) * step_size
            y += math.sin(angle) * step_size
            ctx.line_to(x, y)

        ctx.stroke()


def fractal_branches(ctx, depth=6, length=120, angle=math.pi/4):
    """Recursive branching fractal (like a tree / neuron)"""
    def branch(x, y, length, depth, theta):
        if depth == 0:
            return
        ctx.move_to(x, y)
        x2 = x + math.cos(theta) * length
        y2 = y + math.sin(theta) * length
        ctx.line_to(x2, y2)
        ctx.stroke()

        # recursive calls
        branch(x2, y2, length * 0.7, depth - 1, theta + angle * random.uniform(0.6,1.4))
        branch(x2, y2, length * 0.7, depth - 1, theta - angle * random.uniform(0.6,1.4))

    ctx.set_source_rgb(0.8, 0.9, 1.0)
    ctx.set_line_width(2.0)
    branch(0, 0, length, depth, -math.pi/2)

# --- Main execution ---

if __name__ == "__main__":
    canvas = GenerativeCanvas(background=(0.05, 0.05, 0.08))

    # try any “engine” here:
    fractal_branches(canvas.ctx, depth=7, length=150)

    canvas.save("cc_pycairo/gen/generative2.png")
