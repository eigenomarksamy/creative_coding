import math
import random
import cairo

WIDTH, HEIGHT = 1600, 2000
CX, CY = WIDTH // 2, HEIGHT // 3  # sun center

surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

random.seed(7)

# -------------------------
# Background: sky gradient
# -------------------------
sky_grad = cairo.LinearGradient(0, 0, 0, HEIGHT)
sky_grad.add_color_stop_rgb(0.0, 0.04, 0.05, 0.12)  # deep night blue
sky_grad.add_color_stop_rgb(0.5, 0.05, 0.09, 0.18)  # muted indigo
sky_grad.add_color_stop_rgb(1.0, 0.04, 0.06, 0.10)  # near-black at bottom
ctx.set_source(sky_grad)
ctx.rectangle(0, 0, WIDTH, HEIGHT)
ctx.fill()

# Subtle sky grain
for _ in range(12000):
    x = random.uniform(0, WIDTH)
    y = random.uniform(0, HEIGHT)
    shade = random.uniform(0.03, 0.12)
    alpha = random.uniform(0.03, 0.09)
    r = random.uniform(0.4, 1.0)
    ctx.set_source_rgba(shade, shade, shade, alpha)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.fill()

# -------------------------
# Harbor water band
# -------------------------
WATER_TOP = int(HEIGHT * 0.62)
WATER_BOTTOM = HEIGHT

water_grad = cairo.LinearGradient(0, WATER_TOP, 0, WATER_BOTTOM)
water_grad.add_color_stop_rgb(0.0, 0.03, 0.04, 0.09)
water_grad.add_color_stop_rgb(1.0, 0.01, 0.01, 0.03)
ctx.set_source(water_grad)
ctx.rectangle(0, WATER_TOP, WIDTH, WATER_BOTTOM - WATER_TOP)
ctx.fill()

# Water shimmer lines
NUM_WATER_LINES = 260
for _ in range(NUM_WATER_LINES):
    y = random.uniform(WATER_TOP, WATER_BOTTOM)
    x_start = -100
    x_end = WIDTH + 100

    ctx.set_line_width(random.uniform(0.6, 1.8))
    alpha = random.uniform(0.06, 0.22)
    # cool gold reflection
    ctx.set_source_rgba(0.90, 0.78, 0.55, alpha)

    ctx.move_to(x_start, y)
    segments = 80
    for i in range(segments + 1):
        t = i / segments
        x = x_start + (x_end - x_start) * t
        wobble = math.sin(t * 15 + y * 0.015 + random.random()) * random.uniform(2.0, 7.0)
        ctx.line_to(x, y + wobble)
    ctx.stroke()

# Small bright water highlights (like light on small waves)
for _ in range(2000):
    x = random.uniform(0, WIDTH)
    y = random.uniform(WATER_TOP, WATER_BOTTOM)
    if random.random() < 0.6:
        continue
    size = random.uniform(0.4, 1.6)
    alpha = random.uniform(0.10, 0.35)
    ctx.set_source_rgba(0.95, 0.85, 0.70, alpha)
    ctx.arc(x, y, size, 0, 2 * math.pi)
    ctx.fill()


# -------------------------
# Sun core + halo
# -------------------------
R_CORE = 180

# Glow behind sun
sun_glow = cairo.RadialGradient(CX, CY, 40, CX, CY, 420)
sun_glow.add_color_stop_rgba(0.0, 1.0, 0.88, 0.60, 0.8)
sun_glow.add_color_stop_rgba(0.4, 0.95, 0.65, 0.30, 0.35)
sun_glow.add_color_stop_rgba(1.0, 0.05, 0.03, 0.05, 0.0)
ctx.set_source(sun_glow)
ctx.rectangle(0, 0, WIDTH, HEIGHT)
ctx.fill()

# Sun disc
ctx.set_source_rgb(0.98, 0.84, 0.55)
ctx.arc(CX, CY, R_CORE, 0, 2 * math.pi)
ctx.fill()

# Grain inside sun (like thick, glowing texture)
for _ in range(11000):
    angle = random.uniform(0, 2 * math.pi)
    radius = R_CORE * math.sqrt(random.random())
    x = CX + math.cos(angle) * radius
    y = CY + math.sin(angle) * radius

    base_r = 0.97
    base_g = 0.80
    base_b = 0.52
    jitter = random.uniform(-0.05, 0.03)
    r = base_r + jitter
    g = base_g + jitter * 0.9
    b = base_b + jitter * 0.5

    alpha = random.uniform(0.22, 0.55)
    dot_r = random.uniform(0.7, 2.0)

    ctx.set_source_rgba(r, g, b, alpha)
    ctx.arc(x, y, dot_r, 0, 2 * math.pi)
    ctx.fill()

# Slight vertical light gradient on sun
grad = cairo.LinearGradient(CX, CY - R_CORE, CX, CY + R_CORE)
grad.add_color_stop_rgba(0.0, 1.0, 0.95, 0.82, 0.35)
grad.add_color_stop_rgba(0.5, 0.98, 0.86, 0.70, 0.08)
grad.add_color_stop_rgba(1.0, 0.90, 0.70, 0.45, 0.28)
ctx.set_source(grad)
ctx.arc(CX, CY, R_CORE, 0, 2 * math.pi)
ctx.fill()

# -------------------------
# Honey-like downward streams
# -------------------------

# -------------------------
# Liquid + Painterly Honey Streams
# -------------------------

NUM_STREAMS = 120

for _ in range(NUM_STREAMS):

    # starting point inside bottom half of sun
    angle = random.uniform(math.pi * 0.28, math.pi * 0.72)
    start_r = random.uniform(R_CORE * 0.55, R_CORE * 0.95)

    x0 = CX + math.cos(angle) * start_r
    y0 = CY + math.sin(angle) * start_r

    # ending point on water
    end_x = CX + random.uniform(-250, 250)
    end_y = random.uniform(WATER_TOP * 0.90, WATER_TOP * 1.08)

    # number of curve segments (longer = more painterly)
    segments = random.randint(3, 5)

    # thickness = viscous
    base_thick = random.uniform(6.0, 15.0)

    # rich honey color base
    r_h = 0.98
    g_h = 0.84
    b_h = 0.52

    # begin path
    x_prev, y_prev = x0, y0

    for s in range(segments):
        t0 = s / segments
        t1 = (s + 1) / segments

        # current + next point along fall
        ys = y0 + (end_y - y0) * t0
        ye = y0 + (end_y - y0) * t1

        # introduce slight sideways drift
        side_push = random.uniform(-40, 40)
        xs = x0 + (end_x - x0) * t0 + math.sin(t0 * 3 + random.random()) * side_push
        xe = x0 + (end_x - x0) * t1 + math.sin(t1 * 3 + random.random()) * side_push

        # bulging (viscosity)
        bulge = math.sin(t0 * math.pi) * random.uniform(20, 60)

        # control points (painterly S-curve)
        cx1 = (x_prev + xs) / 2 + random.uniform(-bulge, bulge)
        cy1 = (y_prev + ys) / 2 + random.uniform(-20, 20)

        cx2 = (xs + xe) / 2 + random.uniform(-bulge, bulge)
        cy2 = (ys + ye) / 2 + random.uniform(-20, 20)

        # thickness tapering toward bottom
        thickness = base_thick * (1 - t0 * 0.85)
        alpha = 0.30 + 0.50 * (1 - t0)

        # main honey body (full stroke)
        ctx.set_line_width(thickness)
        ctx.set_source_rgba(r_h, g_h, b_h, alpha)

        ctx.move_to(x_prev, y_prev)
        ctx.curve_to(cx1, cy1, cx2, cy2, xe, ye)
        ctx.stroke()

        # painterly inner highlight (thinner + brighter)
        ctx.set_line_width(thickness * 0.35)
        ctx.set_source_rgba(1.0, 0.92, 0.75, alpha * 0.9)

        ctx.move_to(x_prev, y_prev)
        ctx.curve_to(
            cx1 + random.uniform(-10, 10),
            cy1 + random.uniform(-10, 10),
            cx2 + random.uniform(-10, 10),
            cy2 + random.uniform(-10, 10),
            xe + random.uniform(-6, 6),
            ye + random.uniform(-6, 6)
        )
        ctx.stroke()

        # subtle edge darkening (gives the stroke weight)
        ctx.set_line_width(thickness * 0.2)
        ctx.set_source_rgba(0.70, 0.45, 0.30, alpha * 0.5)

        ctx.move_to(x_prev, y_prev)
        ctx.curve_to(cx1, cy1, cx2, cy2, xe, ye)
        ctx.stroke()

        x_prev, y_prev = xe, ye


# NUM_STREAMS = 160
# STREAM_START_R_MIN = R_CORE * 0.4
# STREAM_START_R_MAX = R_CORE * 0.95
# STREAM_END_Y_MIN = WATER_TOP * 0.9
# STREAM_END_Y_MAX = WATER_TOP * 1.08

# for _ in range(NUM_STREAMS):
#     # choose angle only in lower half of sun
#     angle = random.uniform(math.pi * 0.25, math.pi * 0.75)
#     start_r = random.uniform(STREAM_START_R_MIN, STREAM_START_R_MAX)

#     x0 = CX + math.cos(angle) * start_r
#     y0 = CY + math.sin(angle) * start_r

#     # end point near water, roughly under the sun, with some drift
#     end_x = CX + random.uniform(-220, 220)
#     end_y = random.uniform(STREAM_END_Y_MIN, STREAM_END_Y_MAX)

#     mid_y = (y0 + end_y) / 2
#     mid_x = (x0 + end_x) / 2

#     # bend horizontally to suggest viscous flow
#     side = random.choice([-1, 1])
#     bend_strength = random.uniform(40, 160)
#     ctrl1_x = mid_x + side * bend_strength * random.uniform(0.2, 0.9)
#     ctrl1_y = mid_y - random.uniform(40, 120)
#     ctrl2_x = mid_x + side * bend_strength * random.uniform(0.0, 0.8)
#     ctrl2_y = mid_y + random.uniform(20, 140)

#     # thickness & alpha
#     t_weight = random.uniform(0.4, 1.0)
#     line_w = 2.0 + 4.5 * t_weight
#     alpha = 0.22 + 0.35 * t_weight

#     ctx.set_line_width(line_w)
#     ctx.set_source_rgba(0.98, 0.84, 0.55, alpha)

#     ctx.move_to(x0, y0)
#     ctx.curve_to(ctrl1_x, ctrl1_y, ctrl2_x, ctrl2_y, end_x, end_y)
#     ctx.stroke()

#     # inner brighter streak
#     ctx.set_line_width(line_w * 0.45)
#     ctx.set_source_rgba(1.0, 0.93, 0.75, alpha * 0.8)
#     ctx.move_to(x0, y0)
#     ctx.curve_to(
#         ctrl1_x + random.uniform(-15, 15),
#         ctrl1_y + random.uniform(-15, 15),
#         ctrl2_x + random.uniform(-15, 15),
#         ctrl2_y + random.uniform(-15, 15),
#         end_x + random.uniform(-10, 10),
#         end_y + random.uniform(-10, 10),
#     )
#     ctx.stroke()

# Light pooling on the water under the streams
pool_grad = cairo.RadialGradient(CX, WATER_TOP, 40, CX, WATER_TOP + 120, 420)
pool_grad.add_color_stop_rgba(0.0, 0.95, 0.82, 0.65, 0.45)
pool_grad.add_color_stop_rgba(1.0, 0.1, 0.05, 0.03, 0.0)
ctx.set_source(pool_grad)
ctx.rectangle(0, WATER_TOP - 80, WIDTH, 400)
ctx.fill()

# -------------------------
# Lady of the harbor – silhouette
# -------------------------
def draw_lady(ctx):
    # Base position near right
    base_x = WIDTH * 0.72
    base_y = WATER_TOP - 40

    # Pedestal
    ctx.set_source_rgb(0.02, 0.02, 0.03)
    ctx.rectangle(base_x - 60, base_y, 120, 180)
    ctx.fill()

    # Statue silhouette
    ctx.save()
    ctx.translate(base_x, base_y)

    # Dress / body shape
    ctx.set_source_rgb(0.02, 0.02, 0.03)
    ctx.move_to(0, -260)           # neck/shoulder start
    ctx.curve_to(-60, -260, -90, -180, -75, -80)
    ctx.curve_to(-65, 0, -45, 70, -25, 140)
    ctx.line_to(25, 140)
    ctx.curve_to(45, 70, 65, 0, 75, -80)
    ctx.curve_to(90, -180, 60, -260, 0, -260)
    ctx.close_path()
    ctx.fill()

    # Head
    ctx.arc(0, -300, 40, 0, 2 * math.pi)
    ctx.fill()

    ctx.restore()

    # Rim light on statue (gold edge)
    ctx.save()
    ctx.translate(base_x, base_y)
    ctx.set_line_width(3.0)
    ctx.set_source_rgba(0.98, 0.86, 0.60, 0.8)

    # outline head
    ctx.arc(0, -300, 40, -0.2, math.pi * 0.1)
    ctx.stroke()

    # right shoulder / arm highlight
    ctx.move_to(40, -250)
    ctx.curve_to(70, -210, 80, -150, 70, -90)
    ctx.stroke()

    # right side of dress
    ctx.move_to(80, -80)
    ctx.curve_to(90, 0, 75, 80, 40, 140)
    ctx.stroke()

    # slight highlight on left side
    ctx.set_line_width(2.0)
    ctx.set_source_rgba(0.90, 0.78, 0.60, 0.5)
    ctx.move_to(-45, -250)
    ctx.curve_to(-70, -200, -65, -120, -55, -50)
    ctx.stroke()

    ctx.restore()

draw_lady(ctx)

# Soft glow around the lady
lady_glow = cairo.RadialGradient(WIDTH * 0.72, WATER_TOP - 160, 40,
                                 WIDTH * 0.72, WATER_TOP - 160, 420)
lady_glow.add_color_stop_rgba(0.0, 0.95, 0.80, 0.65, 0.35)
lady_glow.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.0)
ctx.set_source(lady_glow)
ctx.rectangle(0, 0, WIDTH, HEIGHT)
ctx.fill()

# -------------------------
# Floating dust / light particles
# -------------------------
for _ in range(2600):
    x = random.uniform(0, WIDTH)
    y = random.uniform(HEIGHT * 0.15, HEIGHT * 0.95)

    # less dense inside the sun (already busy)
    if (x - CX) ** 2 + (y - CY) ** 2 < (R_CORE * 1.0) ** 2:
        if random.random() < 0.7:
            continue

    size = random.uniform(0.4, 1.3)
    alpha = random.uniform(0.04, 0.16)
    r = 0.95 + random.uniform(-0.03, 0.02)
    g = 0.85 + random.uniform(-0.04, 0.03)
    b = 0.70 + random.uniform(-0.04, 0.03)

    ctx.set_source_rgba(r, g, b, alpha)
    ctx.arc(x, y, size, 0, 2 * math.pi)
    ctx.fill()

# Slight overall vignette for focus
vignette = cairo.RadialGradient(WIDTH / 2, HEIGHT * 0.55, HEIGHT * 0.3,
                                WIDTH / 2, HEIGHT / 2, HEIGHT * 0.95)
vignette.add_color_stop_rgba(0.0, 0, 0, 0, 0.0)
vignette.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.7)
ctx.set_source(vignette)
ctx.rectangle(0, 0, WIDTH, HEIGHT)
ctx.fill()

# Save
surface.write_to_png("cc_pycairo/gen/sun_pouring_harbor.png")
print("Saved sun_pouring_harbor.png")
