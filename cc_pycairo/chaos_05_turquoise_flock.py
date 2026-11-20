import math
import random
import cairo
import numpy as np
from seven_levels_kit import background, glow, luminous, mix, polyline, vignette

# chaos.5 emergence: Reynolds boids. each of 120 agents sees only the others
# within a short radius, and steers by three local rules: align with their
# heading, move toward their centre, and keep clear of any that are too
# close. nothing steers the whole. from random places and headings, on a
# world whose edges wrap around, the agents gather into groups and the
# groups into one flock. drawn in three bands, top to bottom, at three
# moments: each agent as a short trail of its recent positions and a dot
# at its head. a world that wraps has no edge to draw, so each band's view
# is centred on its largest group, which keeps a flock from being cut in two.

WIDTH, HEIGHT = 1600, 2000
SEED = 505
random.seed(SEED)
rng = np.random.default_rng(SEED)

surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)

TURQUOISE = (0.18, 0.86, 0.78)
PALE_TURQUOISE = (0.70, 0.98, 0.94)
DEEP_TURQUOISE = (0.03, 0.30, 0.30)
WHITE_HOT = (0.92, 1.00, 0.98)

# -------------------------
# The model: positions and velocities, updated together every step
# -------------------------
AGENTS = 120
WORLD = np.array([24.0, 9.0])     # wraps at both edges
SIGHT = 1.4                       # an agent sees the others this close
ROOM = 0.5                        # and keeps clear of any closer than this
ALIGN, GATHER, AVOID = 1.0, 0.3, 0.15
WANDER = 0.4                      # each agent's own small random steering
V_MIN, V_MAX = 0.6, 1.0
DT = 0.1
TRAIL = 24                        # steps of trail drawn behind each agent
MOMENTS = (TRAIL, 160, 900)       # the step each band shows


def step(pos, vel):
    d = pos[None, :, :] - pos[:, None, :]      # d[i, j]: from agent i to agent j
    d -= WORLD * np.round(d / WORLD)           # the shortest way round the world
    dist = np.hypot(d[..., 0], d[..., 1])
    np.fill_diagonal(dist, np.inf)

    seen = dist < SIGHT
    count = seen.sum(axis=1, keepdims=True)
    lonely = count[:, 0] == 0
    count = np.maximum(count, 1)
    mean_vel = (seen[..., None] * vel[None, :, :]).sum(axis=1) / count
    mean_off = (seen[..., None] * d).sum(axis=1) / count
    steer = ALIGN * (mean_vel - vel) + GATHER * mean_off
    steer[lonely] = 0.0

    close = dist < ROOM
    steer -= AVOID * (close[..., None] * d / np.maximum(dist, 1e-6)[..., None] ** 2).sum(axis=1)

    steer += WANDER * rng.normal(0.0, 1.0, vel.shape)
    vel = vel + DT * steer
    speed = np.linalg.norm(vel, axis=1, keepdims=True)
    vel = vel / speed * np.clip(speed, V_MIN, V_MAX)
    return (pos + DT * vel) % WORLD, vel


heading = rng.uniform(0.0, 2 * math.pi, AGENTS)
pos = rng.uniform([0.0, 0.0], WORLD, (AGENTS, 2))
vel = 0.8 * np.stack([np.cos(heading), np.sin(heading)], axis=1)

history = [pos]
headings = [vel]
for _ in range(max(MOMENTS)):
    pos, vel = step(pos, vel)
    history.append(pos)
    headings.append(vel)


def largest_group(p):
    """The agents linked to each other by chains of sight, the biggest such group."""
    d = p[None, :, :] - p[:, None, :]
    d -= WORLD * np.round(d / WORLD)
    linked = np.hypot(d[..., 0], d[..., 1]) < SIGHT
    unseen = set(range(len(p)))
    best = []
    while unseen:
        group, todo = [], [unseen.pop()]
        while todo:
            a = todo.pop()
            group.append(a)
            for b in np.nonzero(linked[a])[0]:
                if int(b) in unseen:
                    unseen.remove(int(b))
                    todo.append(int(b))
        if len(group) > len(best):
            best = group
    return sorted(best)


def centre_of(p):
    """The mean position of agents on a world that wraps, axis by axis, as a mean of angles."""
    angle = p / WORLD * 2 * math.pi
    mean = np.arctan2(np.sin(angle).mean(axis=0), np.cos(angle).mean(axis=0))
    return (mean / (2 * math.pi) * WORLD) % WORLD


def polarization(v):
    """How aligned the headings are: 0 for random, 1 for one direction."""
    u = v / np.linalg.norm(v, axis=1, keepdims=True)
    return float(np.linalg.norm(u.mean(axis=0)))


# -------------------------
# The bands: three windows on the whole world, one above the other
# -------------------------
BAND_X0, BAND_X1 = 170, 1430
BAND_H = (BAND_X1 - BAND_X0) * WORLD[1] / WORLD[0]
GAP = (1810 - 210 - 3 * BAND_H) / 2
TOPS = [210 + k * (BAND_H + GAP) for k in range(3)]
SCALE = (BAND_X1 - BAND_X0) / WORLD[0]

background(ctx, WIDTH, HEIGHT, TURQUOISE)
ctx.set_operator(cairo.OPERATOR_ADD)
glow(ctx, WIDTH / 2, HEIGHT / 2, 820, DEEP_TURQUOISE, 0.30)

for band, (top, moment) in enumerate(zip(TOPS, MOMENTS)):
    group = largest_group(history[moment])
    shift = WORLD / 2 - centre_of(history[moment][group])
    view = [(p + shift) % WORLD for p in history[moment - TRAIL:moment + 1]]

    def screen(p, top=top):
        return BAND_X0 + p[0] * SCALE, top + p[1] * SCALE

    # the band's frame: faint corner marks, since the world has no walls
    tick = 26
    corners = []
    for x, y, sx, sy in ((BAND_X0, top, 1, 1), (BAND_X1, top, -1, 1),
                         (BAND_X0, top + BAND_H, 1, -1), (BAND_X1, top + BAND_H, -1, -1)):
        corners.append([(x + sx * tick, y), (x, y), (x, y + sy * tick)])
    polyline(ctx, corners, mix(DEEP_TURQUOISE, TURQUOISE, 0.5), 0.6, 1.0)

    # trails, broken where an agent crosses an edge and comes back on the other side
    trails = []
    for a in range(AGENTS):
        piece = [screen(view[0][a])]
        for s in range(1, TRAIL + 1):
            p, q = view[s - 1][a], view[s][a]
            if abs(p[0] - q[0]) > WORLD[0] / 2 or abs(p[1] - q[1]) > WORLD[1] / 2:
                trails.append(piece)
                piece = []
            piece.append(screen(q))
        trails.append(piece)
    luminous(ctx, trails, TURQUOISE, 0.55, 1.3)

    # heads: a dot, and a short stroke along the heading
    heads = []
    for a in range(AGENTS):
        x, y = screen(view[-1][a])
        u = headings[moment][a] / np.linalg.norm(headings[moment][a])
        heads.append([(x, y), (x + u[0] * 11, y + u[1] * 11)])
        glow(ctx, x, y, 16, TURQUOISE, 0.35)
        glow(ctx, x, y, 3.2, mix(PALE_TURQUOISE, WHITE_HOT, 0.5), 0.95)
    polyline(ctx, heads, PALE_TURQUOISE, 0.85, 1.4)

    print(f"band {band + 1}: step {moment}, polarization {polarization(headings[moment]):.3f}, largest group {len(group)}")

vignette(ctx, WIDTH, HEIGHT)

surface.write_to_png("cc_pycairo/gen/seven_levels/chaos_05_turquoise_flock.png")
print("Saved chaos_05_turquoise_flock.png")
