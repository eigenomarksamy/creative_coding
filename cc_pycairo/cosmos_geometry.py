import math
import random
import cairo
import noise

# -------------------------
# Canvas setup
# -------------------------
WIDTH, HEIGHT = 1800, 1800
CX, CY = WIDTH * 0.46, HEIGHT * 0.54
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

random.seed(3)

VIOLET = (0.62, 0.38, 1.00)
LAVENDER = (0.82, 0.70, 1.00)
DEEP_VIOLET = (0.30, 0.12, 0.55)
WHITE = (0.96, 0.94, 1.00)

PHI = (1 + math.sqrt(5)) / 2
GOLDEN_ANGLE = math.pi * (3 - math.sqrt(5))


def glow(x, y, radius, color, alpha):
    r, g, b = color
    pat = cairo.RadialGradient(x, y, 0, x, y, radius)
    pat.add_color_stop_rgba(0.0, r, g, b, alpha)
    pat.add_color_stop_rgba(0.25, r, g, b, alpha * 0.3)
    pat.add_color_stop_rgba(1.0, r, g, b, 0.0)
    ctx.set_source(pat)
    ctx.arc(x, y, radius, 0, 2 * math.pi)
    ctx.fill()


def dissolve(x, y):
    """
    0 where geometry is intact, 1 where it has become stardust.
    A diagonal front towards the upper right, roughened by Perlin noise.
    """
    t = ((x - WIDTH / 2) - (y - HEIGHT / 2)) / (WIDTH * 0.72)
    t += 0.22 * noise.pnoise2(x * 0.0025, y * 0.0025, octaves=3, base=5)
    s = (t + 0.05) / 0.55
    s = max(0.0, min(1.0, s))
    return s * s * (3 - 2 * s)


def drift(x, y, s):
    """Where a dissolved point ends up: carried up and right along a noise flow."""
    ang = -math.pi / 4 + 1.8 * noise.pnoise2(x * 0.003, y * 0.003, octaves=2, base=9)
    dist = s * s * random.uniform(40, 260)
    return x + math.cos(ang) * dist, y + math.sin(ang) * dist


# -------------------------
# Background: violet depth
# -------------------------
bg = cairo.RadialGradient(CX, CY, 0, CX, CY, WIDTH * 0.8)
bg.add_color_stop_rgb(0.0, 0.075, 0.025, 0.130)
bg.add_color_stop_rgb(0.6, 0.030, 0.010, 0.060)
bg.add_color_stop_rgb(1.0, 0.012, 0.004, 0.025)
ctx.set_source(bg)
ctx.paint()

for _ in range(10000):
    x = random.uniform(0, WIDTH)
    y = random.uniform(0, HEIGHT)
    ctx.set_source_rgba(0.7, 0.6, 0.9, random.uniform(0.02, 0.05))
    ctx.arc(x, y, random.uniform(0.4, 1.0), 0, 2 * math.pi)
    ctx.fill()

ctx.set_operator(cairo.OPERATOR_ADD)

# -------------------------
# Cartesian grid: crisp lines that break into dashes, then into nodes
# -------------------------
GRID = 60
for horizontal in (True, False):
    for k in range(-1, WIDTH // GRID + 2):
        c = k * GRID
        for step in range(0, WIDTH, 6):
            if horizontal:
                x0, y0, x1, y1 = step, c, step + 6, c
            else:
                x0, y0, x1, y1 = c, step, c, step + 6
            s = dissolve(x0, y0)
            if random.random() < s * 1.4:
                continue
            ctx.set_source_rgba(*DEEP_VIOLET, 0.30 * (1 - s))
            ctx.set_line_width(1.0)
            ctx.move_to(x0, y0)
            ctx.line_to(x1, y1)
            ctx.stroke()

# The lattice survives as points of light where the lines have gone
for i in range(WIDTH // GRID + 1):
    for j in range(HEIGHT // GRID + 1):
        x, y = i * GRID, j * GRID
        s = dissolve(x, y)
        if s < 0.3:
            continue
        x, y = drift(x, y, s * 0.4)
        glow(x, y, 6 + 6 * s, LAVENDER, 0.25 * s)
        ctx.set_source_rgba(*WHITE, 0.5 * s)
        ctx.arc(x, y, 1.1, 0, 2 * math.pi)
        ctx.fill()

# -------------------------
# Polar grid around the solids
# -------------------------
for ring in range(1, 14):
    r = ring * 58
    for seg in range(int(r * 0.6)):
        a0 = seg / (r * 0.6) * 2 * math.pi
        a1 = (seg + 0.7) / (r * 0.6) * 2 * math.pi
        x, y = CX + math.cos(a0) * r, CY + math.sin(a0) * r
        s = dissolve(x, y)
        if random.random() < s * 1.3:
            continue
        ctx.set_source_rgba(*VIOLET, 0.12 * (1 - s))
        ctx.set_line_width(1.0)
        ctx.arc(CX, CY, r, a0, a1)
        ctx.stroke()

for spoke in range(24):
    a = spoke * math.pi / 12
    for step in range(0, 760, 8):
        x0, y0 = CX + math.cos(a) * step, CY + math.sin(a) * step
        s = dissolve(x0, y0)
        if random.random() < s * 1.3:
            continue
        ctx.set_source_rgba(*VIOLET, 0.08 * (1 - s))
        ctx.set_line_width(1.0)
        ctx.move_to(x0, y0)
        ctx.line_to(CX + math.cos(a) * (step + 6), CY + math.sin(a) * (step + 6))
        ctx.stroke()

# -------------------------
# Phyllotaxis: golden angle spiral, r = c * sqrt(n)
# -------------------------
SPIRAL_X, SPIRAL_Y = WIDTH * 0.77, HEIGHT * 0.22
for n in range(1, 1400):
    r = 7.2 * math.sqrt(n)
    a = n * GOLDEN_ANGLE
    x = SPIRAL_X + math.cos(a) * r
    y = SPIRAL_Y + math.sin(a) * r * 0.82
    edge = n / 1400
    size = 0.6 + 1.8 * (1 - edge)
    ctx.set_source_rgba(*WHITE, 0.25 + 0.5 * (1 - edge))
    ctx.arc(x, y, size, 0, 2 * math.pi)
    ctx.fill()
    if n % 7 == 0:
        glow(x, y, 8 + 10 * (1 - edge), VIOLET, 0.20)
glow(SPIRAL_X, SPIRAL_Y, 160, VIOLET, 0.25)
glow(SPIRAL_X, SPIRAL_Y, 30, WHITE, 0.6)


# -------------------------
# Platonic solids, rotated in 3D and seen in perspective
# -------------------------
def edges_of(vertices):
    """Edges are the vertex pairs at the minimum distance."""
    pairs = []
    best = min(
        math.dist(p, q) for i, p in enumerate(vertices) for q in vertices[i + 1:]
    )
    for i, p in enumerate(vertices):
        for j in range(i + 1, len(vertices)):
            if abs(math.dist(p, vertices[j]) - best) < 1e-6:
                pairs.append((i, j))
    return pairs


def signs(*values):
    """Every combination of signs of the non-zero values."""
    out = [()]
    for v in values:
        out = [o + (s * v,) for o in out for s in ((1, -1) if v else (1,))]
    return out


# Oriented as duals: both have midradius phi and their edges cross at
# right angles, and the cube sits on eight of the dodecahedron's corners.
CUBE = signs(1, 1, 1)
TETRA = [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)]
DODECA = CUBE + signs(0, PHI, 1 / PHI) + signs(1 / PHI, 0, PHI) + signs(PHI, 1 / PHI, 0)
ICOSA = signs(0, 1, PHI) + signs(1, PHI, 0) + signs(PHI, 0, 1)


def rotate(p, ax, ay, az):
    x, y, z = p
    y, z = y * math.cos(ax) - z * math.sin(ax), y * math.sin(ax) + z * math.cos(ax)
    x, z = x * math.cos(ay) + z * math.sin(ay), -x * math.sin(ay) + z * math.cos(ay)
    x, y = x * math.cos(az) - y * math.sin(az), x * math.sin(az) + y * math.cos(az)
    return x, y, z


def project(p, cx, cy, scale, rot):
    x, y, z = rotate(p, *rot)
    depth = 5.0 / (5.0 + z)
    return cx + x * scale * depth, cy + y * scale * depth, z


def draw_solid(vertices, cx, cy, scale, rot, color, width, can_dissolve=True):
    pts = [project(v, cx, cy, scale, rot) for v in vertices]
    for i, j in edges_of(vertices):
        (x0, y0, z0), (x1, y1, z1) = pts[i], pts[j]
        samples = 140
        run = []
        for k in range(samples + 1):
            t = k / samples
            x, y, z = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, z0 + (z1 - z0) * t
            front = 0.45 + 0.55 * (1 - (z + 2) / 4)
            s = dissolve(x, y) if can_dissolve else 0.0
            if s < 0.04:
                run.append((x, y, front))
                continue

            # stardust: points shed from the edge and carried away
            if run:
                stroke_run(run, color, width)
                run = []
            if random.random() > 1 - s * 0.6:
                continue
            dx, dy = drift(x, y, s)
            ctx.set_source_rgba(*WHITE, 0.55 * front * (1 - 0.6 * s))
            ctx.arc(dx, dy, 0.6 + 1.0 * random.random(), 0, 2 * math.pi)
            ctx.fill()
            if random.random() < 0.06 * s:
                glow(dx, dy, random.uniform(6, 16), color, 0.35)
        if run:
            stroke_run(run, color, width)

    for x, y, z in pts:
        if can_dissolve and dissolve(x, y) > 0.3:
            continue
        glow(x, y, 16, color, 0.45)
        ctx.set_source_rgba(*WHITE, 0.9)
        ctx.arc(x, y, 2.0, 0, 2 * math.pi)
        ctx.fill()


def stroke_run(run, color, width):
    front = sum(f for _, _, f in run) / len(run)
    for w, a in ((width * 5, 0.06), (width * 2, 0.20), (width, 0.75)):
        ctx.set_line_width(w)
        ctx.set_source_rgba(*color, a * front)
        ctx.move_to(run[0][0], run[0][1])
        for x, y, _ in run[1:]:
            ctx.line_to(x, y)
        ctx.stroke()


ROT = (0.42, 0.62, 0.18)
SCALE = 300

# Circumscribed sphere: three great circles as projected ellipses
for tilt in range(3):
    ctx.new_path()
    for k in range(361):
        a = k / 360 * 2 * math.pi
        p = (math.cos(a) * PHI * 1.12, math.sin(a) * PHI * 1.12, 0)
        p = rotate(p, tilt * math.pi / 3, tilt * 0.9, 0)
        x, y, _ = project(p, CX, CY, SCALE, ROT)
        ctx.line_to(x, y)
    ctx.set_line_width(1.0)
    ctx.set_source_rgba(*DEEP_VIOLET, 0.6)
    ctx.stroke()

# Kepler's nesting: the dodecahedron holds a cube, with the dual
# icosahedron threaded faintly through it
draw_solid(ICOSA, CX, CY, SCALE, ROT, DEEP_VIOLET, 0.8)
draw_solid(DODECA, CX, CY, SCALE, ROT, VIOLET, 2.0)
draw_solid(CUBE, CX, CY, SCALE, ROT, LAVENDER, 0.9)

glow(CX, CY, 260, VIOLET, 0.18)
glow(CX, CY, 40, WHITE, 0.5)

# -------------------------
# Bubble universes, each with its own small solid
# -------------------------
for bx, by, br, solid in [
    (WIDTH * 0.90, HEIGHT * 0.50, 70, signs(1, 0, 0) + signs(0, 1, 0) + signs(0, 0, 1)),
    (WIDTH * 0.58, HEIGHT * 0.10, 52, TETRA),
    (WIDTH * 0.92, HEIGHT * 0.08, 40, CUBE),
    (WIDTH * 0.68, HEIGHT * 0.42, 34, ICOSA),
]:
    ctx.set_line_width(1.0)
    ctx.set_source_rgba(*LAVENDER, 0.35)
    ctx.arc(bx, by, br, 0, 2 * math.pi)
    ctx.stroke()
    glow(bx, by, br * 1.2, DEEP_VIOLET, 0.25)
    size = br * 0.55 / max(math.sqrt(sum(c * c for c in solid[0])), 1)
    rot = (random.uniform(0, 3), random.uniform(0, 3), random.uniform(0, 3))
    draw_solid(solid, bx, by, size, rot, LAVENDER, 0.9, can_dissolve=False)

# -------------------------
# Equations: whole where geometry holds, letters scattering where it dissolves
# -------------------------
EQUATIONS = [
    "e^{iπ} + 1 = 0", "∇ · E = ρ / ε_{0}", "iħ ∂ψ/∂t = Ĥψ", "G_{μν} + Λg_{μν} = 8πG T_{μν}",
    "ζ(s) = Σ n^{−s}", "φ = (1 + √5) / 2", "V − E + F = 2", "∇ × B = μ_{0} J",
    "S = k ln W", "E = mc^{2}", "∫ e^{−x²} dx = √π", "Δx Δp ≥ ħ / 2",
    "SU(3) × SU(2) × U(1)", "ds^{2} = −c^{2}dt^{2} + dx^{2}", "∂_{μ} F^{μν} = J^{ν}",
    "χ = 2 − 2g", "e^{iθ} = cos θ + i sin θ", "F = G m_{1}m_{2} / r^{2}", "∇^{2}Φ = 4πGρ",
    "|ψ⟩ = α|0⟩ + β|1⟩", "a^{2} + b^{2} = c^{2}", "θ = 137.507°", "F_{n} = F_{n−1} + F_{n−2}",
    "R_{μν} = 0", "h^{1,1} = 1", "Ω_{Λ} + Ω_{m} = 1", "λ = h / p", "e = Σ 1 / n!",
]


def layout(text, size):
    """Glyph positions for an equation; ^{..} and _{..} become small raised or lowered text."""
    glyphs = []
    pen = 0.0
    i = 0
    while i < len(text):
        ch = text[i]
        if ch in "^_" and text[i + 1:i + 2] == "{":
            close = text.index("}", i)
            small = size * 0.62
            dy = -0.42 * size if ch == "^" else 0.24 * size
            ctx.set_font_size(small)
            for c in text[i + 2:close]:
                glyphs.append((c, pen, dy, small))
                pen += ctx.text_extents(c).x_advance
            i = close + 1
            continue
        ctx.set_font_size(size)
        glyphs.append((ch, pen, 0.0, size))
        pen += ctx.text_extents(ch).x_advance
        i += 1
    return glyphs, pen


ctx.select_font_face("DejaVu Serif", cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_NORMAL)
boxes = []
for text in random.sample(EQUATIONS, len(EQUATIONS)):
    size = random.uniform(16, 30)
    glyphs, text_w = layout(text, size)
    for _ in range(400):
        x = random.uniform(30, WIDTH - text_w - 30)
        y = random.uniform(50, HEIGHT - 30)
        box = (x - 12, y - size * 1.4, x + text_w + 12, y + size * 0.6)
        clear_of_solid = math.hypot(x + text_w / 2 - CX, y - CY) > SCALE * 1.8
        clear_of_text = all(
            box[2] < b[0] or box[0] > b[2] or box[3] < b[1] or box[1] > b[3] for b in boxes
        )
        if clear_of_solid and clear_of_text:
            break
    else:
        continue
    boxes.append(box)

    alpha = random.uniform(0.22, 0.45)
    s = dissolve(x, y)
    for i, (ch, px, dy, gsize) in enumerate(glyphs):
        gx, gy = x + px, y + dy
        if s > 0.08:
            # letters carried away, each a little further than the last
            gx, gy = drift(gx, gy, min(1.0, s * (0.6 + i / len(glyphs))))
        ctx.set_font_size(gsize)
        ctx.set_source_rgba(*LAVENDER, alpha * (1 - 0.7 * s))
        ctx.move_to(gx, gy)
        ctx.show_text(ch)

# -------------------------
# Vignette
# -------------------------
ctx.set_operator(cairo.OPERATOR_OVER)
vignette = cairo.RadialGradient(CX, CY, HEIGHT * 0.3, WIDTH / 2, HEIGHT / 2, WIDTH * 0.78)
vignette.add_color_stop_rgba(0.0, 0, 0, 0, 0.0)
vignette.add_color_stop_rgba(1.0, 0.01, 0, 0.02, 0.6)
ctx.set_source(vignette)
ctx.rectangle(0, 0, WIDTH, HEIGHT)
ctx.fill()

surface.write_to_png("cc_pycairo/gen/cosmos/cosmos_geometry.png")
print("Saved cosmos_geometry.png")
