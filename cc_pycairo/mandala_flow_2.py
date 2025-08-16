import cairo
import math
import random

# Image size
WIDTH, HEIGHT = 800, 800

# Number of symmetry slices (like a kaleidoscope)
NUM_SYMMETRY = 12

# Number of strokes
NUM_STROKES = 300

# Flow field parameters
FLOW_SCALE = 0.002
FLOW_STRENGTH = 2.0

# Color palette generator (harmonic scheme)
def harmonic_palette(n):
    base_hue = random.random()
    colors = []
    for i in range(n):
        hue = (base_hue + (i * 0.15)) % 1.0
        sat = 0.6 + 0.3 * random.random()
        val = 0.7 + 0.3 * random.random()
        colors.append(hsv_to_rgb(hue, sat, val))
    return colors

# HSV → RGB converter
def hsv_to_rgb(h, s, v):
    i = int(h*6)
    f = h*6 - i
    p = v * (1-s)
    q = v * (1-f*s)
    t = v * (1-(1-f)*s)
    i %= 6
    if i == 0: r, g, b = v, t, p
    elif i == 1: r, g, b = q, v, p
    elif i == 2: r, g, b = p, v, t
    elif i == 3: r, g, b = p, q, v
    elif i == 4: r, g, b = t, p, v
    else: r, g, b = v, p, q
    return (r, g, b)

# Simple flow field function
def flow_field(x, y):
    angle = math.sin(x * FLOW_SCALE) + math.cos(y * FLOW_SCALE)
    return angle * FLOW_STRENGTH

# --- Drawing ---
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)
ctx.set_source_rgb(1, 1, 1)  # white background
ctx.paint()

# Move origin to center
ctx.translate(WIDTH/2, HEIGHT/2)

palette = harmonic_palette(NUM_STROKES)

for i in range(NUM_STROKES):
    # Random start point
    x, y = random.uniform(-WIDTH/2, WIDTH/2), random.uniform(-HEIGHT/2, HEIGHT/2)
    color = random.choice(palette)
    
    ctx.set_source_rgba(color[0], color[1], color[2], 0.7)
    ctx.set_line_width(random.uniform(1.5, 3.5))
    
    # Create path for stroke
    ctx.new_path()
    ctx.move_to(x, y)
    for step in range(50):
        angle = flow_field(x, y)
        x += math.cos(angle) * 4
        y += math.sin(angle) * 4
        ctx.line_to(x, y)
    
    # Repeat this stroke in all symmetry slices
    for s in range(NUM_SYMMETRY):
        ctx.save()
        ctx.rotate((2*math.pi/NUM_SYMMETRY) * s)
        ctx.stroke_preserve()
        ctx.restore()

surface.write_to_png("cc_pycairo/gen/mandala_flow_2.png")
print("Saved mandala_flow_2.png")
