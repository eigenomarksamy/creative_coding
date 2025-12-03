import math
import random
import cairo

# -------------------------
# Canvas setup
# -------------------------
WIDTH, HEIGHT = 1500, 1500
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

random.seed(11)

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
    # Direction vector
    dx = math.cos(angle)
    dy = math.sin(angle)

    # Slight curve factor for organic feel
    curve_strength = random.uniform(-0.35, 0.35)

    # Top point
    tip_x = x + dx * length + (-dy) * curve_strength * 30
    tip_y = y + dy * length + (dx) * curve_strength * 30

    # Left and right base edges (make a wedge)
    left_angle = angle + math.pi / 2 + random.uniform(-0.12, 0.12)
    right_angle = angle - math.pi / 2 + random.uniform(-0.12, 0.12)

    left_x = x + math.cos(left_angle) * base_thick
    left_y = y + math.sin(left_angle) * base_thick
    right_x = x + math.cos(right_angle) * base_thick
    right_y = y + math.sin(right_angle) * base_thick

    # Slight mid-edge perturbation for a more splintery outline
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

    # Gradient along splinter direction
    grad = cairo.LinearGradient(x, y, tip_x, tip_y)
    # dark base, hot tip
    grad.add_color_stop_rgba(0.0, 0.35, 0.06, 0.03, 0.95)   # deep ember
    grad.add_color_stop_rgba(0.4, 0.78, 0.28, 0.08, 0.95)   # orange-red
    grad.add_color_stop_rgba(1.0, 1.0, 0.90, 0.40, 0.90)    # bright tip
    ctx.set_source(grad)
    ctx.fill_preserve()

    # Edge stroke – darker, gives definition
    ctx.set_line_width(1.4)
    ctx.set_source_rgba(0.20, 0.03, 0.02, 0.8)
    ctx.stroke()

    # ---- Inner highlight stroke ----
    # small curve from base to tip
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
# Layout of splinters
# -------------------------

# Main cluster origin – imagine an invisible "impact" or source
origin_x = WIDTH * 0.35
origin_y = HEIGHT * 0.68

NUM_MAIN_SPLINTERS = 100
for i in range(NUM_MAIN_SPLINTERS):
    # Angle mostly radiating upward-right, some spread
    base_angle = random.uniform(-0.3, 1.2)  # radians from horizontal
    length = random.uniform(140, 360)
    base_thick = random.uniform(10, 26)

    # Small scatter around origin
    ox = origin_x + random.uniform(-40, 40)
    oy = origin_y + random.uniform(-30, 40)

    draw_fire_splinter(ctx, ox, oy, length, base_thick, base_angle)

# Secondary cluster, smaller, slightly above / right
origin_x2 = WIDTH * 0.62
origin_y2 = HEIGHT * 0.55
NUM_SECONDARY = 25
for i in range(NUM_SECONDARY):
    base_angle = random.uniform(-0.5, 1.4)
    length = random.uniform(90, 230)
    base_thick = random.uniform(7, 18)

    ox = origin_x2 + random.uniform(-35, 35)
    oy = origin_y2 + random.uniform(-25, 30)

    draw_fire_splinter(ctx, ox, oy, length, base_thick, base_angle)

# A few stray splinters scattered
for _ in range(35):
    x = random.uniform(WIDTH * 0.1, WIDTH * 0.9)
    y = random.uniform(HEIGHT * 0.35, HEIGHT * 0.9)
    length = random.uniform(70, 180)
    base_thick = random.uniform(6, 14)
    angle = random.uniform(-0.6, 1.6)
    draw_fire_splinter(ctx, x, y, length, base_thick, angle)

# -------------------------
# Ember / ash particles
# -------------------------
for _ in range(5000):
    x = random.uniform(0, WIDTH)
    y = random.uniform(HEIGHT * 0.25, HEIGHT * 0.98)

    size = random.uniform(0.4, 1.4)
    if random.random() < 0.6:
        # grey ash
        shade = random.uniform(0.75, 0.93)
        alpha = random.uniform(0.04, 0.12)
        ctx.set_source_rgba(shade, shade, shade, alpha)
    else:
        # tiny warm ember
        alpha = random.uniform(0.08, 0.25)
        ctx.set_source_rgba(
            0.98,
            random.uniform(0.55, 0.78),
            random.uniform(0.18, 0.35),
            alpha,
        )

    ctx.arc(x, y, size, 0, 2 * math.pi)
    ctx.fill()

# -------------------------
# Faint motion streaks (as if splinters dragged through air)
# -------------------------
NUM_STREAKS = 200
for _ in range(NUM_STREAKS):
    # choose direction to align roughly with main splinter direction
    base_angle = random.uniform(-0.2, 1.1)
    length = random.uniform(80, 220)

    x = random.uniform(WIDTH * 0.22, WIDTH * 0.80)
    y = random.uniform(HEIGHT * 0.40, HEIGHT * 0.85)

    dx = math.cos(base_angle)
    dy = math.sin(base_angle)

    x2 = x + dx * length
    y2 = y + dy * length

    ctx.set_line_width(random.uniform(0.4, 1.4))
    alpha = random.uniform(0.04, 0.11)
    shade = random.uniform(0.70, 0.88)
    ctx.set_source_rgba(shade, shade, shade, alpha)

    ctx.move_to(x, y)
    ctx.line_to(x2, y2)
    ctx.stroke()

# -------------------------
# Vignette for focus
# -------------------------
vignette = cairo.RadialGradient(
    WIDTH / 2, HEIGHT * 0.6, HEIGHT * 0.25,
    WIDTH / 2, HEIGHT / 2, HEIGHT * 0.95
)
vignette.add_color_stop_rgba(0.0, 0, 0, 0, 0.0)
vignette.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.55)
ctx.set_source(vignette)
ctx.rectangle(0, 0, WIDTH, HEIGHT)
ctx.fill()

surface.write_to_png("cc_pycairo/gen/fire_splinters_grey.png")
print("Saved fire_splinters_grey.png")
