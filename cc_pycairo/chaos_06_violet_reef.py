import math
import random
import cairo
import numpy as np
from seven_levels_kit import background, contour, glow, luminous, mix, polyline, vignette

# chaos.6 complexity: the Gray-Scott reaction-diffusion model, solved on a
# grid with numpy. two fields, U and V, react (U + 2V -> 3V) and diffuse at
# different rates, and a few seeded drops of V grow into a branching reef.
# drawn as a faint grayscale density of V, its threshold contours, and the
# cells that crossed the threshold most recently, where the reef still grows.

WIDTH, HEIGHT = 1600, 2000
SEED = 506
random.seed(SEED)
rng = np.random.default_rng(SEED)

surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

VIOLET = (0.62, 0.34, 1.00)
LILAC = (0.84, 0.74, 1.00)
DEEP_VIOLET = (0.28, 0.10, 0.55)
WHITE = (0.97, 0.95, 1.00)

# -------------------------
# The model: dU/dt = Du lap U - U V^2 + F (1 - U)
#            dV/dt = Dv lap V + U V^2 - (F + k) V
# with F and k in the coral regime, a 9-point Laplacian with closed edges,
# and dt = 1. drops of V land at seeded places and times, so the reef is a
# colony of clusters of different ages
# -------------------------
CELL = 4
COLS, ROWS = WIDTH // CELL, HEIGHT // CELL
DU, DV = 0.70, 0.35    # half and half: the ratio sets the pattern, the size sets its scale
FEED, KILL = 0.0545, 0.062
STEPS = 6400
RECENT = 300          # growth in the last this many steps counts as the front
THRESHOLD = 0.25
DROPS = 12
SPACING = 70          # cells between drops, at least

drops = []
while len(drops) < DROPS:
    i = int(rng.integers(COLS * 0.16, COLS * 0.84))
    j = int(rng.integers(ROWS * 0.14, ROWS * 0.86))
    if all(math.hypot(i - a, j - b) >= SPACING for a, b, _ in drops):
        drops.append((i, j, int(STEPS * 0.78 * len(drops) / DROPS)))

u = np.ones((ROWS, COLS), dtype=np.float32)
v = np.zeros((ROWS, COLS), dtype=np.float32)


def laplacian(z):
    # weights 0.2 at the sides and 0.05 at the corners: stable at dt = 1
    p = np.pad(z, 1, mode="edge")
    sides = p[:-2, 1:-1] + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:]
    corners = p[:-2, :-2] + p[:-2, 2:] + p[2:, :-2] + p[2:, 2:]
    return 0.2 * sides + 0.05 * corners - z


for step in range(STEPS):
    for i, j, start in drops:
        if step == start:
            # an irregular drop, so no cluster inherits the grid's symmetry
            r = int(rng.integers(4, 8))
            yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
            ragged = r * (0.7 + 0.3 * rng.random(yy.shape))
            inside = (xx * xx + yy * yy) <= ragged * ragged
            # Pearson's drop: U = 1/2 and V = 1/4, with a little noise
            u[j - r:j + r + 1, i - r:i + r + 1][inside] = 0.5
            noise = rng.uniform(-0.05, 0.05, int(inside.sum())).astype(np.float32)
            v[j - r:j + r + 1, i - r:i + r + 1][inside] = 0.25 + noise
    if step == STEPS - RECENT:
        earlier = v.copy()
    uvv = u * v * v
    u += DU * laplacian(u) - uvv + FEED * (1 - u)
    v += DV * laplacian(v) + uvv - (FEED + KILL) * v

# -------------------------
# Background, then V as a restrained grayscale density
# -------------------------
background(ctx, WIDTH, HEIGHT, VIOLET)
ctx.set_operator(cairo.OPERATOR_ADD)
glow(ctx, WIDTH / 2, HEIGHT / 2, 900, DEEP_VIOLET, 0.35)

level = np.clip(v / max(float(v.max()), 1e-9), 0, 1)
gray = (level * 255).astype(np.uint8)
pixels = np.empty((ROWS, COLS, 4), dtype=np.uint8)
pixels[..., 0] = pixels[..., 1] = pixels[..., 2] = gray
pixels[..., 3] = 255
density = cairo.ImageSurface.create_for_data(memoryview(np.ascontiguousarray(pixels)), cairo.FORMAT_ARGB32, COLS, ROWS)
ctx.save()
ctx.scale(CELL, CELL)
pattern = cairo.SurfacePattern(density)
pattern.set_filter(cairo.FILTER_BILINEAR)
ctx.set_source(pattern)
ctx.paint_with_alpha(0.16)
ctx.restore()

# -------------------------
# Threshold contours of V: the reef's edges, outer, main and inner
# -------------------------
half = CELL / 2
# the other field: where the reef has drawn U down, a halo just beyond V's edge
polyline(ctx, contour(u, 0.80, CELL, half, half), LILAC, 0.22, 1.0)
luminous(ctx, contour(v, 0.12, CELL, half, half), DEEP_VIOLET, 0.55, 1.0)
luminous(ctx, contour(v, THRESHOLD, CELL, half, half), VIOLET, 0.80, 1.5)
polyline(ctx, contour(v, 0.38, CELL, half, half), LILAC, 0.45, 0.9)

# -------------------------
# The front: cells that crossed the threshold in the last RECENT steps
# -------------------------
grown = np.argwhere((v > THRESHOLD) & (earlier <= THRESHOLD))
picks = grown[rng.permutation(len(grown))[:min(len(grown), 260)]]
for j, i in sorted(picks.tolist()):
    x, y = i * CELL + half, j * CELL + half
    glow(ctx, x, y, 26, VIOLET, 0.35)
    glow(ctx, x, y, 4, WHITE, 0.8)

vignette(ctx, WIDTH, HEIGHT)

surface.write_to_png("cc_pycairo/gen/seven_levels/chaos_06_violet_reef.png")
print("Saved chaos_06_violet_reef.png")
