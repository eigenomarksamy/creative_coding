import cairo
import math
import random
import colorsys

WIDTH, HEIGHT = 800, 800

def generate_palette(hue=None, n=5, harmony="analogous"):
    """
    Generate a palette around a base hue using simple harmony rules.
    harmony options: analogous, complementary, triadic
    """
    if hue is None:
        hue = random.random()  # base hue [0,1]
    
    palette = []
    if harmony == "analogous":
        offsets = [-0.08, -0.04, 0, 0.04, 0.08]
    elif harmony == "complementary":
        offsets = [0, 0.5, 0.48, 0.52, 0.02]
    elif harmony == "triadic":
        offsets = [0, 1/3, 2/3, 0.05, 0.67]
    else:
        offsets = [0] * n
    
    for i in range(n):
        h = (hue + offsets[i % len(offsets)]) % 1.0
        s = random.uniform(0.6, 0.9)   # saturation
        v = random.uniform(0.7, 0.95)  # brightness
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        palette.append((r, g, b))
    return palette

def draw_curve(ctx, palette):
    # pick stroke color
    color = random.choice(palette)
    ctx.set_source_rgba(*color, random.uniform(0.4, 0.8))
    
    # brush-like thickness
    ctx.set_line_width(random.uniform(6, 20))
    ctx.set_line_cap(cairo.LineCap.ROUND)
    
    # random start and end
    x1, y1 = random.uniform(0, WIDTH), random.uniform(0, HEIGHT)
    x2, y2 = random.uniform(0, WIDTH), random.uniform(0, HEIGHT)
    cx1, cy1 = random.uniform(0, WIDTH), random.uniform(0, HEIGHT)
    cx2, cy2 = random.uniform(0, WIDTH), random.uniform(0, HEIGHT)
    
    ctx.move_to(x1, y1)
    ctx.curve_to(cx1, cy1, cx2, cy2, x2, y2)
    ctx.stroke()

def main():
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
    ctx = cairo.Context(surface)
    
    # background
    ctx.rectangle(0, 0, WIDTH, HEIGHT)
    ctx.set_source_rgb(0.95, 0.95, 0.95)
    ctx.fill()
    
    # generate a harmonic palette
    palette = generate_palette(harmony=random.choice(["analogous", "complementary", "triadic"]))
    
    # draw many layered strokes
    for _ in range(80):
        draw_curve(ctx, palette)
    
    surface.write_to_png("cc_pycairo/gen/hsl_curves.png")
    print("Saved hsl_curves.png")

if __name__ == "__main__":
    main()
