import math
import random
import cairo
import noise

# Image settings
WIDTH, HEIGHT = 2500, 2500
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

# --- Fire palette (deep red → orange → yellow → white) ---
PALETTE = [
    (0.90, 0.15, 0.00),  # deep red
    (1.00, 0.35, 0.00),  # bright orange
    (1.00, 0.60, 0.05),  # warm orange-yellow
    (1.00, 0.82, 0.30),  # soft yellow
    (1.00, 0.96, 0.85),  # near-white glow
]

# Background: very dark, slightly warm
ctx.set_source_rgb(0.96, 0.96, 0.96)
ctx.paint()


def draw_gradient_blob(x, y, size, color):
    """Soft radial gradient blob, used as glowing fire base."""
    pat = cairo.RadialGradient(x, y, size * 0.1, x, y, size)
    r, g, b = color
    pat.add_color_stop_rgba(0, r, g, b, 0.95)
    pat.add_color_stop_rgba(0.4, r, g, b, 0.6)
    pat.add_color_stop_rgba(1, r, g, b, 0.0)
    ctx.set_source(pat)
    ctx.arc(x, y, size, 0, 2 * math.pi)
    ctx.fill()


def draw_fire_flow_lines(seed):
    """Draws flame-like Bézier curves biased upwards, influenced by noise."""
    random.seed(seed)

    num_curves = 650
    segments_per_curve = 7
    noise_scale = 0.0015

    for _ in range(num_curves):
        # Start mostly near the bottom half, as if flames rising from a base.
        x = random.uniform(0, WIDTH)
        y = random.uniform(HEIGHT * 0.55, HEIGHT * 0.98)

        # Slightly thicker at the base, thinner as they go up
        base_line_width = random.uniform(3.0, 7.0)
        ctx.set_line_width(base_line_width)

        r, g, b = random.choice(PALETTE)

        ctx.move_to(x, y)

        for i in range(segments_per_curve):
            n = noise.pnoise2(x * noise_scale, y * noise_scale, octaves=3)

            # Base direction: upwards (-pi/2), with small noisy deviation.
            angle = -math.pi / 2 + n * math.pi * 0.7

            # Longer strokes closer to bottom, shorter higher up.
            height_factor = y / HEIGHT  # 1 near bottom, 0 near top
            length = random.uniform(120, 260) * (0.4 + 0.6 * height_factor)

            x2 = x + math.cos(angle) * length
            y2 = y + math.sin(angle) * length

            # Control points to make the curve flicker and dance
            jitter = 0.7
            cx1 = x + math.cos(angle + jitter) * length * 0.4
            cy1 = y + math.sin(angle + jitter) * length * 0.4
            cx2 = x + math.cos(angle - jitter) * length * 0.4
            cy2 = y + math.sin(angle - jitter) * length * 0.4

            # Alpha stronger near the base, fading upwards
            alpha = 0.15 + 0.65 * (y / HEIGHT)  # y big (bottom) → more alpha

            ctx.set_source_rgba(r, g, b, alpha)
            ctx.curve_to(cx1, cy1, cx2, cy2, x2, y2)

            x, y = x2, y2

        ctx.stroke()


# --- Layer 1: Glowing fire base blobs (clustered near bottom) ---
for _ in range(80):
    size = random.uniform(300, 1000)
    draw_gradient_blob(
        random.uniform(0, WIDTH),
        random.uniform(HEIGHT * 0.55, HEIGHT * 1.05),  # concentrate low
        size,
        random.choice(PALETTE),
    )

# --- Layer 2: Flame-like Bézier curves ---
draw_fire_flow_lines(seed=1337)

# Save image
surface.write_to_png("cc_pycairo/gen/fire_flow_art.png")
print("Saved fire_flow_art.png")
