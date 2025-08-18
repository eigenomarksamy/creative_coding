import cairo, math, random

WIDTH, HEIGHT = 800, 800

def draw_branch(ctx, x, y, length, angle, depth, max_depth, symmetry=6):
    if depth > max_depth or length < 2:
        return
    
    # Compute branch end
    x2 = x + length * math.cos(angle)
    y2 = y + length * math.sin(angle)
    
    # Draw symmetric copies
    for i in range(symmetry):
        theta = angle + (2 * math.pi * i / symmetry)
        x_sym = WIDTH/2 + (x - WIDTH/2)*math.cos(2*math.pi*i/symmetry) - (y - HEIGHT/2)*math.sin(2*math.pi*i/symmetry)
        y_sym = HEIGHT/2 + (x - WIDTH/2)*math.sin(2*math.pi*i/symmetry) + (y - HEIGHT/2)*math.cos(2*math.pi*i/symmetry)
        x2_sym = WIDTH/2 + (x2 - WIDTH/2)*math.cos(2*math.pi*i/symmetry) - (y2 - HEIGHT/2)*math.sin(2*math.pi*i/symmetry)
        y2_sym = HEIGHT/2 + (x2 - WIDTH/2)*math.sin(2*math.pi*i/symmetry) + (y2 - HEIGHT/2)*math.cos(2*math.pi*i/symmetry)

        ctx.move_to(x_sym, y_sym)
        ctx.line_to(x2_sym, y2_sym)
        ctx.set_line_width(0.6 + 1.5 * (1 - depth/max_depth))
        ctx.stroke()
    
    # Recursive branching with slight randomness
    new_length = length * (0.65 + random.uniform(-0.1, 0.1))
    for delta in [-0.5, 0.5, random.uniform(-0.2,0.2)]:
        new_angle = angle + delta
        draw_branch(ctx, x2, y2, new_length, new_angle, depth+1, max_depth, symmetry)


def generate_mushroom_network(filename="cc_pycairo/gen/mushroom_intelligence.png"):
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
    ctx = cairo.Context(surface)

    # Background
    ctx.set_source_rgb(0.05, 0.05, 0.08)  
    ctx.paint()

    # Start branches like spores at the center
    ctx.set_source_rgb(0.8, 0.9, 0.8)  
    for _ in range(12):
        angle = random.uniform(0, 2*math.pi)
        draw_branch(ctx, WIDTH/2, HEIGHT/2, random.uniform(60,100), angle, 0, 9, symmetry=8)

    surface.write_to_png(filename)
    print(f"Saved {filename}")


generate_mushroom_network()
