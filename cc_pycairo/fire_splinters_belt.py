import math
import random
import cairo

# -------------------------
# Canvas setup
# -------------------------
WIDTH, HEIGHT = 1500, 1500
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

random.seed(19)

# -------------------------
# Background: grey field
# -------------------------
bg_grad = cairo.LinearGradient(0, 0, 0, HEIGHT)
bg_grad.add_color_stop_rgb(0.0, 0.82, 0.83, 0.86)  # top
bg_grad.add_color_stop_rgb(0.5, 0.76, 0.78, 0.81)
bg_grad.add_color_stop_rgb(1.0, 0.68, 0.70, 0.74)  # bottom
ctx.set_source(bg_grad)
ctx.rectangle(0, 0, WIDTH, HEIGHT)
ctx.fill()

# Subtle paper texture
for _ in range(9000):
    x = random.uniform(0, WIDTH)
    y = random.uniform(0, HEIGHT)
    shade = random.uniform(0.72, 0.9)
    alpha = random.uniform(0.03, 0.08)
    r = random.uniform(0.4, 1.0)
    ctx.set_source_rgba(shade, shade, shade, alpha)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.fill()

# -------------------------
# Warm glow for the fire band
# -------------------------
fire_glow = cairo.RadialGradient(
    WIDTH * 0.5, HEIGHT * 0.6, HEIGHT * 0.1,
    WIDTH * 0.5, HEIGHT * 0.6, HEIGHT * 0.8
)
fire_glow.add_color_stop_rgba(0.0, 0.9, 0.55, 0.35, 0.55)
fire_glow.add_color_stop_rgba(0.5, 0.6, 0.30, 0.20, 0.35)
fire_glow.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.0)
ctx.set_source(fire_glow)
ctx.rectangle(0, 0, WIDTH, HEIGHT)
ctx.fill()

# -------------------------
# Fire splinter function
# -------------------------
def draw_fire_splinter(ctx, x, y, length, base_thick, angle):
    """
    Draw a single fire splinter: a sharp, slightly irregular shard
    with layered color (shadow, body, highlight).
    (x, y): base of splinter
    length: how far it extends
    base_thick: base width at the root
    angle: general direction (radians)
    """
    dx = math.cos(angle)
    dy = math.sin(angle)

    curve_strength = random.uniform(-0.35, 0.35)

    tip_x = x + dx * length + (-dy) * curve_strength * 30
    tip_y = y + dy * length + (dx) * curve_strength * 30

    left_angle = angle + math.pi / 2 + random.uniform(-0.12, 0.12)
    right_angle = angle - math.pi / 2 + random.uniform(-0.12, 0.12)

    left_x = x + math.cos(left_angle) * base_thick
    left_y = y + math.sin(left_angle) * base_thick
    right_x = x + math.cos(right_angle) * base_thick
    right_y = y + math.sin(right_angle) * base_thick

    mid_t = random.uniform(0.35, 0.75)
    mid_x = x + dx * (length * mid_t) + random.uniform(-10, 10)
    mid_y = y + dy * (length * mid_t) + random.uniform(-10, 10)

    # ---- Main body path (filled shape) ----
    ctx.new_path()
    ctx.move_to(left_x, left_y)
    ctx.line_to(mid_x + (-dy) * base_thick * 0.25,
                mid_y + (dx) * base_thick * 0.25)
    ctx.line_to(tip_x, tip_y)
    ctx.line_to(mid_x + (dy) * base_thick * 0.15,
                mid_y - (dx) * base_thick * 0.15)
    ctx.line_to(right_x, right_y)
    ctx.close_path()

    grad = cairo.LinearGradient(x, y, tip_x, tip_y)
    grad.add_color_stop_rgba(0.0, 0.35, 0.06, 0.03, 0.95)   # deep ember
    grad.add_color_stop_rgba(0.4, 0.78, 0.28, 0.08, 0.95)   # orange-red
    grad.add_color_stop_rgba(1.0, 1.0, 0.90, 0.40, 0.90)    # bright tip
    ctx.set_source(grad)
    ctx.fill_preserve()

    ctx.set_line_width(1.4)
    ctx.set_source_rgba(0.20, 0.03, 0.02, 0.8)
    ctx.stroke()

    # ---- Inner highlight stroke ----
    ctx.set_line_width(base_thick * 0.28)
    ctx.set_source_rgba(1.0, 0.93, 0.65, 0.85)
    ctx.move_to(x, y)
    ctrl_x = (x + tip_x) / 2 + (-dy) * 18
    ctrl_y = (y + tip_y) / 2 + (dx) * 18
    ctx.curve_to(ctrl_x, ctrl_y,
                 ctrl_x + random.uniform(-10, 10),
                 ctrl_y + random.uniform(-10, 10),
                 tip_x, tip_y)
    ctx.stroke()

    # Tiny bright core stroke
    ctx.set_line_width(base_thick * 0.12)
    ctx.set_source_rgba(1.0, 0.98, 0.85, 0.9)
    ctx.move_to(x, y)
    ctx.curve_to(
        (x + tip_x) / 2 + random.uniform(-8, 8),
        (y + tip_y) / 2 + random.uniform(-8, 8),
        tip_x + random.uniform(-4, 4),
        tip_y + random.uniform(-4, 4),
        tip_x,
        tip_y
    )
    ctx.stroke()

# -------------------------
# Fire band: multiple connected origins along an arc
# -------------------------

def fire_band_origins(num_points):
    """
    Generate origin points along a broad arc / band where fire is concentrated.
    """
    origins = []
    center_x = WIDTH * 0.45
    center_y = HEIGHT * 0.65
    radius_x = WIDTH * 0.35
    radius_y = HEIGHT * 0.18

    for i in range(num_points):
        t = i / max(1, num_points - 1)
        # parametric ellipse-ish band
        angle = math.pi * (0.15 + 0.7 * t)
        x = center_x + math.cos(angle) * radius_x + random.uniform(-40, 40)
        y = center_y + math.sin(angle) * radius_y + random.uniform(-30, 30)
        origins.append((x, y))
    return origins

origins = fire_band_origins(14)

# main dense splinters from these origins
for (ox, oy) in origins:
    num_from_origin = random.randint(18, 32)
    for _ in range(num_from_origin):
        base_angle = random.uniform(-0.4, 1.4)
        length = random.uniform(130, 360)
        base_thick = random.uniform(10, 26)
        draw_fire_splinter(ctx, ox, oy, length, base_thick, base_angle)

# add extra dense core near center of band
core_x, core_y = WIDTH * 0.46, HEIGHT * 0.62
for _ in range(28):
    base_angle = random.uniform(-0.2, 1.2)
    length = random.uniform(150, 320)
    base_thick = random.uniform(12, 28)
    x = core_x + random.uniform(-50, 50)
    y = core_y + random.uniform(-40, 40)
    draw_fire_splinter(ctx, x, y, length, base_thick, base_angle)

# some stray splinters near edges of band to soften boundary
for _ in range(24):
    x = random.uniform(WIDTH * 0.1, WIDTH * 0.9)
    y = random.uniform(HEIGHT * 0.35, HEIGHT * 0.9)
    length = random.uniform(90, 220)
    base_thick = random.uniform(7, 18)
    angle = random.uniform(-0.6, 1.6)
    draw_fire_splinter(ctx, x, y, length, base_thick, angle)

# -------------------------
# Connective "fire filaments"
# -------------------------
NUM_FILAMENTS = 140
for _ in range(NUM_FILAMENTS):
    # choose two random origins or near them
    (x1, y1) = random.choice(origins)
    (x2, y2) = random.choice(origins)

    x1 += random.uniform(-30, 30)
    y1 += random.uniform(-20, 20)
    x2 += random.uniform(-30, 30)
    y2 += random.uniform(-20, 20)

    mid_x = (x1 + x2) / 2 + random.uniform(-30, 30)
    mid_y = (y1 + y2) / 2 + random.uniform(-30, 30)

    ctx.set_line_width(random.uniform(1.0, 3.0))
    ctx.set_source_rgba(0.95, 0.75, 0.45, random.uniform(0.12, 0.35))

    ctx.move_to(x1, y1)
    ctx.curve_to(
        mid_x + random.uniform(-20, 20),
        mid_y + random.uniform(-20, 20),
        mid_x + random.uniform(-20, 20),
        mid_y + random.uniform(-20, 20),
        x2,
        y2
    )
    ctx.stroke()

# -------------------------
# Ember / ash particles
# -------------------------
for _ in range(3200):
    x = random.uniform(0, WIDTH)
    y = random.uniform(HEIGHT * 0.25, HEIGHT * 0.98)

    # bias more particles near the fire band vertically
    band_center_y = HEIGHT * 0.6
    dy = abs(y - band_center_y) / HEIGHT
    weight = max(0.2, 1.0 - dy * 2.0)

    size = random.uniform(0.4, 1.6)
    if random.random() < 0.55:
        # grey ash
        shade = random.uniform(0.75, 0.93)
        alpha = random.uniform(0.03, 0.12) * weight
        ctx.set_source_rgba(shade, shade, shade, alpha)
    else:
        # warm ember
        alpha = random.uniform(0.08, 0.30) * weight
        ctx.set_source_rgba(
            0.98,
            random.uniform(0.55, 0.78),
            random.uniform(0.18, 0.35),
            alpha,
        )

    ctx.arc(x, y, size, 0, 2 * math.pi)
    ctx.fill()

# -------------------------
# Vignette for focus
# -------------------------
vignette = cairo.RadialGradient(
    WIDTH / 2, HEIGHT * 0.6, HEIGHT * 0.15,
    WIDTH / 2, HEIGHT / 2, HEIGHT * 0.95
)
vignette.add_color_stop_rgba(0.0, 0, 0, 0, 0.0)
vignette.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.45)
ctx.set_source(vignette)
ctx.rectangle(0, 0, WIDTH, HEIGHT)
ctx.fill()

surface.write_to_png("cc_pycairo/gen/fire_splinters_belt.png")
print("Saved fire_splinters_belt.png")
