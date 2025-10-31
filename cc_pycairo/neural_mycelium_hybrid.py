import math
import random
import cairo

# Canvas size
WIDTH, HEIGHT = 1800, 1800
OUTPUT = "cc_pycairo/gen/neural_mycelium_hybrid.png"

def lerp(a, b, t):
    return a + (b - a) * t

def draw_neural_mycelium(ctx, x, y, radius, depth, max_depth):
    if depth > max_depth or radius < 2:
        return

    t = depth / max_depth  # blend factor between organic and neural
    # --- Color gradient: earthy roots → luminous synapses
    r = lerp(0.8, 0.4 + 0.6 * math.sin(t * 4), t)
    g = lerp(0.9, 0.6 + 0.4 * math.sin(t * 5 + 2), t)
    b = lerp(0.7, 0.8 + 0.3 * math.sin(t * 6 + 4), t)
    alpha = lerp(0.08, 0.4, t) + random.uniform(-0.02, 0.02)
    ctx.set_source_rgba(r, g, b, alpha)

    # --- Line width: thicker organic roots → fine neural filaments
    ctx.set_line_width(lerp(2.5, 0.3, t) * random.uniform(0.8, 1.2))

    # --- Symmetry changes with depth
    symmetry = int(lerp(4, 9, t))

    for i in range(symmetry):
        angle = (2 * math.pi / symmetry) * i + random.uniform(-0.05, 0.05)
        nx = x + math.cos(angle) * radius * random.uniform(0.9, 1.1)
        ny = y + math.sin(angle) * radius * random.uniform(0.9, 1.1)

        # Main line
        ctx.move_to(x, y)
        ctx.line_to(nx, ny)
        ctx.stroke()

        # --- Textural side filaments
        if random.random() < 0.35:
            ctx.set_source_rgba(r * 1.1, g * 1.1, b * 1.1, alpha * 0.3)
            ctx.set_line_width(lerp(1.0, 0.2, t))
            ctx.move_to(nx, ny)
            ctx.line_to(nx + random.uniform(-10, 10),
                        ny + random.uniform(-10, 10))
            ctx.stroke()

        # --- Neural cross connections (at higher depths)
        if t > 0.6 and random.random() < 0.2:
            ctx.set_source_rgba(r * 1.3, g * 1.3, b * 1.5, 0.2)
            ctx.set_line_width(0.5)
            ctx.move_to(x + random.uniform(-radius * 0.4, radius * 0.4),
                        y + random.uniform(-radius * 0.4, radius * 0.4))
            ctx.line_to(nx, ny)
            ctx.stroke()

        # Recurse with smaller radius and slight drift
        draw_neural_mycelium(
            ctx,
            nx + random.uniform(-5, 5),
            ny + random.uniform(-5, 5),
            radius * (0.65 + random.uniform(-0.05, 0.05)),
            depth + 1,
            max_depth,
        )

# --- Create Cairo surface
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

# --- Background: near-white to keep contrast for both earthy + neural tones
ctx.set_source_rgb(0.97, 0.97, 0.98)
ctx.paint()

# --- Subtle paper-like noise texture
for _ in range(7000):
    x = random.random() * WIDTH
    y = random.random() * HEIGHT
    shade = 0.9 + random.uniform(-0.03, 0.03)
    ctx.set_source_rgba(shade, shade, shade, 0.03)
    ctx.arc(x, y, random.uniform(0.3, 0.8), 0, 2 * math.pi)
    ctx.fill()

# --- Draw hybrid structure
draw_neural_mycelium(ctx, WIDTH / 2, HEIGHT / 2, 260, 0, 6)

# --- Save result
surface.write_to_png(OUTPUT)
print(f"Saved {OUTPUT}")
