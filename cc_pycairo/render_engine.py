import colorsys
import copy
import math
import random
from pathlib import Path

import cairo
import noise

SAVE_DIR = Path("cc_pycairo/gen/render_engine_output")
BASE_SEED = 42

# Set either value to a tuple of names to render only a subset.
# Example: RENDER_SCENE_NAMES = ("fault_line", "red_weather_inside")
# Example: RENDER_PALETTE_NAMES = ("blood_signal", "submerged_wound")
RENDER_SCENE_NAMES = None
RENDER_PALETTE_NAMES = None

# Number of color variants to render for each palette preset.
PALETTE_VARIATIONS_PER_PRESET = 3

# If True, every color variation of the same scene shares the same geometry.
# Only the palette shifts. If False, geometry also changes across variations.
KEEP_GEOMETRY_CONSTANT_PER_SCENE = True

# Keep v01 as the exact base palette. Later variants rotate the entire blob
# family around the color wheel before applying smaller per-color mutations.
KEEP_FIRST_VARIATION_AS_BASE = True
RANDOMIZE_BLOB_BASE_HUE = True

# Minimum and maximum shared hue rotation for the blob family. Hue is in the
# normalized HLS range, so 0.10 is 36 degrees and 0.50 is 180 degrees.
# The sign is chosen randomly, giving access to the full color wheel.
BLOB_BASE_HUE_SHIFT_MIN = 0.10
BLOB_BASE_HUE_SHIFT_MAX = 0.50

# Keep this False when you want the cyan/accent family to stay independent.
# Set it True to rotate the accent family by the same amount as the blobs.
LINK_ACCENT_HUE_TO_BLOBS = False

# Palette mutation settings. These create subtle-to-moderate shifts around
# each base palette so the renders feel related, not completely different.
COLOR_VARIATION = {
    "background": {"h": 0.010, "l": 0.025, "s": 0.030, "rgb": 0.010},
    "blobs": {"h": 0.025, "l": 0.060, "s": 0.090, "rgb": 0.020},
    "neutral_lines": {"h": 0.010, "l": 0.045, "s": 0.045, "rgb": 0.015},
    "accent_lines": {"h": 0.030, "l": 0.055, "s": 0.120, "rgb": 0.020},
    "particles": {"h": 0.015, "l": 0.040, "s": 0.060, "rgb": 0.015},
}

# Per-element live jitter inside a single render, applied on top of the
# palette variation above. Keeps strokes/blobs from feeling too flat.
ELEMENT_COLOR_JITTER = {
    "blob": {"h": 0.022, "l": 0.030, "s": 0.050, "rgb": 0.012},
    "neutral_line": {"h": 0.008, "l": 0.025, "s": 0.020, "rgb": 0.010},
    "accent_line": {"h": 0.015, "l": 0.035, "s": 0.060, "rgb": 0.012},
    "particle": {"h": 0.010, "l": 0.030, "s": 0.030, "rgb": 0.010},
}

# ==========================================================
# CANVAS
# ==========================================================

WIDTH, HEIGHT = 2800, 1600

# ==========================================================
# PALETTE PRESETS
# ==========================================================

PALETTE_PRESETS = {
    # Original visual language:
    # red pressure systems, grey structure, cyan signal
    "blood_signal": {
        "background": (0.008, 0.008, 0.012),

        "blobs": [
            (0.34, 0.01, 0.02),
            (0.52, 0.02, 0.03),
            (0.72, 0.05, 0.05),
            (0.90, 0.16, 0.12),
            (0.92, 0.78, 0.74),
        ],

        "neutral_lines": [
            (0.14, 0.15, 0.17),
            (0.28, 0.30, 0.34),
            (0.45, 0.48, 0.54),
            (0.66, 0.70, 0.76),
            (0.82, 0.85, 0.88),
        ],

        "accent_lines": [
            (0.04, 0.32, 0.38),
            (0.06, 0.52, 0.60),
            (0.16, 0.76, 0.84),
        ],

        "particles": [
            (0.72, 0.75, 0.80),
            (0.86, 0.87, 0.90),
            (0.92, 0.93, 0.95),
        ],
    },

    # Muted, bodily, intimate.
    "bruise_and_breath": {
        "background": (0.018, 0.015, 0.022),

        "blobs": [
            (0.25, 0.03, 0.08),
            (0.43, 0.06, 0.13),
            (0.62, 0.12, 0.19),
            (0.78, 0.29, 0.31),
            (0.88, 0.73, 0.70),
        ],

        "neutral_lines": [
            (0.16, 0.15, 0.18),
            (0.29, 0.28, 0.33),
            (0.45, 0.44, 0.50),
            (0.64, 0.63, 0.69),
            (0.80, 0.79, 0.83),
        ],

        "accent_lines": [
            (0.12, 0.34, 0.38),
            (0.21, 0.52, 0.55),
            (0.42, 0.72, 0.72),
        ],

        "particles": [
            (0.68, 0.64, 0.69),
            (0.82, 0.77, 0.79),
            (0.91, 0.86, 0.85),
        ],
    },

    # Hotter and more energetic: embers against cold cobalt.
    "ember_cobalt": {
        "background": (0.008, 0.010, 0.018),

        "blobs": [
            (0.38, 0.025, 0.015),
            (0.60, 0.07, 0.025),
            (0.82, 0.17, 0.04),
            (0.96, 0.36, 0.08),
            (0.96, 0.79, 0.59),
        ],

        "neutral_lines": [
            (0.12, 0.15, 0.20),
            (0.24, 0.29, 0.37),
            (0.39, 0.46, 0.56),
            (0.59, 0.66, 0.74),
            (0.78, 0.82, 0.87),
        ],

        "accent_lines": [
            (0.04, 0.20, 0.48),
            (0.05, 0.36, 0.72),
            (0.18, 0.62, 0.92),
        ],

        "particles": [
            (0.61, 0.69, 0.80),
            (0.78, 0.83, 0.89),
            (0.96, 0.88, 0.73),
        ],
    },

    # Pale, ghostly and quieter, with bone-white structures.
    "bone_transmission": {
        "background": (0.015, 0.015, 0.017),

        "blobs": [
            (0.27, 0.035, 0.035),
            (0.43, 0.075, 0.070),
            (0.61, 0.16, 0.14),
            (0.75, 0.37, 0.33),
            (0.89, 0.83, 0.76),
        ],

        "neutral_lines": [
            (0.18, 0.18, 0.18),
            (0.34, 0.34, 0.33),
            (0.52, 0.51, 0.48),
            (0.72, 0.70, 0.65),
            (0.90, 0.87, 0.79),
        ],

        "accent_lines": [
            (0.18, 0.38, 0.40),
            (0.32, 0.58, 0.58),
            (0.57, 0.78, 0.76),
        ],

        "particles": [
            (0.70, 0.68, 0.64),
            (0.84, 0.81, 0.75),
            (0.94, 0.91, 0.84),
        ],
    },

    # Colder and submerged: oxblood thermal masses under icy current.
    "submerged_wound": {
        "background": (0.006, 0.012, 0.018),

        "blobs": [
            (0.25, 0.015, 0.025),
            (0.40, 0.025, 0.045),
            (0.58, 0.055, 0.075),
            (0.76, 0.14, 0.14),
            (0.82, 0.62, 0.58),
        ],

        "neutral_lines": [
            (0.10, 0.16, 0.20),
            (0.20, 0.29, 0.34),
            (0.34, 0.44, 0.49),
            (0.53, 0.63, 0.67),
            (0.73, 0.80, 0.82),
        ],

        "accent_lines": [
            (0.03, 0.34, 0.44),
            (0.06, 0.55, 0.67),
            (0.28, 0.79, 0.86),
        ],

        "particles": [
            (0.56, 0.67, 0.72),
            (0.72, 0.80, 0.83),
            (0.88, 0.91, 0.91),
        ],
    },

    # More surreal and synthetic while retaining the red/cyan relationship.
    "synthetic_fever": {
        "background": (0.012, 0.006, 0.014),

        "blobs": [
            (0.32, 0.01, 0.08),
            (0.52, 0.015, 0.12),
            (0.76, 0.035, 0.17),
            (0.94, 0.12, 0.22),
            (0.94, 0.68, 0.70),
        ],

        "neutral_lines": [
            (0.15, 0.13, 0.17),
            (0.29, 0.27, 0.32),
            (0.47, 0.45, 0.51),
            (0.67, 0.65, 0.70),
            (0.84, 0.82, 0.86),
        ],

        "accent_lines": [
            (0.02, 0.38, 0.44),
            (0.03, 0.64, 0.70),
            (0.20, 0.88, 0.88),
        ],

        "particles": [
            (0.68, 0.65, 0.71),
            (0.82, 0.79, 0.84),
            (0.94, 0.87, 0.88),
        ],
    },
}

# ==========================================================
# HELPERS
# ==========================================================

def clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, v))

def jitter_color(color, rng, h=0.0, l=0.0, s=0.0, rgb=0.0):
    """Jitter one RGB color in HLS space, then optionally in RGB space."""
    r, g, b = color
    hh, ll, ss = colorsys.rgb_to_hls(r, g, b)

    hh = (hh + rng.uniform(-h, h)) % 1.0
    ll = clamp(ll + rng.uniform(-l, l))
    ss = clamp(ss + rng.uniform(-s, s))

    r, g, b = colorsys.hls_to_rgb(hh, ll, ss)

    if rgb > 0.0:
        r = clamp(r + rng.uniform(-rgb, rgb))
        g = clamp(g + rng.uniform(-rgb, rgb))
        b = clamp(b + rng.uniform(-rgb, rgb))

    return (r, g, b)

def rotate_hue(color, shift):
    """Rotate an RGB color around the HLS hue wheel."""
    r, g, b = color
    h, l, s = colorsys.rgb_to_hls(r, g, b)

    # Nearly neutral colors have no meaningful hue. Keep them neutral so pale
    # highlights do not suddenly become strongly saturated.
    if s < 0.035:
        return color

    h = (h + shift) % 1.0
    return colorsys.hls_to_rgb(h, l, s)


def random_signed_hue_shift(rng, minimum, maximum):
    magnitude = rng.uniform(minimum, maximum)
    return magnitude if rng.random() < 0.5 else -magnitude


def build_palette_variant(base_palette, rng, variant_index):
    """Build one coherent color variant of a palette preset.

    All blob colors receive one shared hue rotation first. This changes the
    actual blob color family while preserving its dark-to-light hierarchy.
    Smaller independent mutations are applied afterwards.
    """
    variant = copy.deepcopy(base_palette)

    use_exact_base = KEEP_FIRST_VARIATION_AS_BASE and variant_index == 1

    if RANDOMIZE_BLOB_BASE_HUE and not use_exact_base:
        blob_hue_shift = random_signed_hue_shift(
            rng,
            BLOB_BASE_HUE_SHIFT_MIN,
            BLOB_BASE_HUE_SHIFT_MAX,
        )
    else:
        blob_hue_shift = 0.0

    background_source = base_palette["background"]
    blob_source = [
        rotate_hue(color, blob_hue_shift)
        for color in base_palette["blobs"]
    ]
    neutral_source = base_palette["neutral_lines"]

    if LINK_ACCENT_HUE_TO_BLOBS:
        accent_source = [
            rotate_hue(color, blob_hue_shift)
            for color in base_palette["accent_lines"]
        ]
    else:
        accent_source = base_palette["accent_lines"]

    particle_source = base_palette["particles"]

    if use_exact_base:
        # v01 remains an untouched reference render. Live per-element jitter
        # still gives the individual marks some variation.
        return {
            "background": background_source,
            "blobs": list(blob_source),
            "neutral_lines": list(neutral_source),
            "accent_lines": list(accent_source),
            "particles": list(particle_source),
            "blob_hue_shift": blob_hue_shift,
        }

    bg_cfg = COLOR_VARIATION["background"]
    variant["background"] = jitter_color(
        background_source,
        rng,
        h=bg_cfg["h"],
        l=bg_cfg["l"],
        s=bg_cfg["s"],
        rgb=bg_cfg["rgb"],
    )

    sources = {
        "blobs": blob_source,
        "neutral_lines": neutral_source,
        "accent_lines": accent_source,
        "particles": particle_source,
    }

    for key, source_colors in sources.items():
        cfg = COLOR_VARIATION[key]
        variant[key] = [
            jitter_color(
                color,
                rng,
                h=cfg["h"],
                l=cfg["l"],
                s=cfg["s"],
                rgb=cfg["rgb"],
            )
            for color in source_colors
        ]

    variant["blob_hue_shift"] = blob_hue_shift
    return variant

def maybe_jitter_live(color, role, rng=random):
    cfg = ELEMENT_COLOR_JITTER[role]
    return jitter_color(
        color,
        rng,
        h=cfg["h"],
        l=cfg["l"],
        s=cfg["s"],
        rgb=cfg["rgb"],
    )

def lerp(a, b, t):
    return a + (b - a) * t

def distance(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)

def lerp_angle(a, b, t):
    """Interpolate angles safely."""
    diff = (b - a + math.pi) % (2 * math.pi) - math.pi
    return a + diff * t

def weighted_choice(weighted_items):
    """
    weighted_items = [(weight, item), ...]
    """
    total = sum(w for w, _ in weighted_items)
    r = random.uniform(0, total)
    acc = 0.0
    for w, item in weighted_items:
        acc += w
        if r <= acc:
            return item
    return weighted_items[-1][1]

def point_in_ellipse(cx, cy, rx, ry):
    """Sample a random point inside an ellipse."""
    angle = random.uniform(0, 2 * math.pi)
    rad = math.sqrt(random.random())
    x = cx + math.cos(angle) * rx * rad
    y = cy + math.sin(angle) * ry * rad
    return x, y

def nearest_blob(x, y, blob_centers):
    if not blob_centers:
        return None, None, 1e9
    best = None
    best_d = 1e9
    for cx, cy in blob_centers:
        d = distance(x, y, cx, cy)
        if d < best_d:
            best_d = d
            best = (cx, cy)
    return best[0], best[1], best_d

def point_line_distance(px, py, x1, y1, x2, y2):
    """Distance from point to line segment."""
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        return distance(px, py, x1, y1)
    t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
    t = clamp(t, 0.0, 1.0)
    proj_x = x1 + t * dx
    proj_y = y1 + t * dy
    return distance(px, py, proj_x, proj_y)

# ==========================================================
# CORE DRAWING PRIMITIVES
# ==========================================================

def create_surface():
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
    ctx = cairo.Context(surface)
    return surface, ctx

def draw_background(ctx, palette, noise_count=7000):
    ctx.set_source_rgb(*palette["background"])
    ctx.paint()

    bg_r, bg_g, bg_b = palette["background"]

    for _ in range(noise_count):
        x = random.uniform(0, WIDTH)
        y = random.uniform(0, HEIGHT)

        lift = random.uniform(0.015, 0.08)
        alpha = random.uniform(0.02, 0.07)
        radius = random.uniform(0.4, 1.1)

        ctx.set_source_rgba(
            clamp(bg_r + lift),
            clamp(bg_g + lift),
            clamp(bg_b + lift),
            alpha,
        )
        ctx.arc(x, y, radius, 0, 2 * math.pi)
        ctx.fill()

    # subtle dark grain
    for _ in range(noise_count):
        x = random.uniform(0, WIDTH)
        y = random.uniform(0, HEIGHT)

        base = random.uniform(0.03, 0.11)
        alpha = random.uniform(0.02, 0.07)
        r = random.uniform(0.4, 1.1)

        ctx.set_source_rgba(base, base, base, alpha)
        ctx.arc(x, y, r, 0, 2 * math.pi)
        ctx.fill()

def draw_gradient_blob(ctx, x, y, size, color, inner_alpha=0.42, mid_alpha=0.18):
    pat = cairo.RadialGradient(x, y, size * 0.12, x, y, size)
    r, g, b = maybe_jitter_live(color, "blob")
    pat.add_color_stop_rgba(0.0, r, g, b, inner_alpha)
    pat.add_color_stop_rgba(0.45, r, g, b, mid_alpha)
    pat.add_color_stop_rgba(1.0, r, g, b, 0.0)

    ctx.set_source(pat)
    ctx.arc(x, y, size, 0, 2 * math.pi)
    ctx.fill()

def scatter_fragments(ctx, x, y, color, alpha_base=0.14, count=3, spread=14):
    r, g, b = color
    for _ in range(count):
        px = x + random.uniform(-spread, spread)
        py = y + random.uniform(-spread, spread)
        pr = random.uniform(0.6, 1.8)
        alpha = alpha_base * random.uniform(0.4, 1.0)
        ctx.set_source_rgba(r, g, b, alpha)
        ctx.arc(px, py, pr, 0, 2 * math.pi)
        ctx.fill()

# ==========================================================
# SCENE STRUCTURE
# ==========================================================

def get_scene_anchors(scene_name):
    """
    Return list of anchor ellipses:
    [(cx, cy, rx, ry), ...]
    """
    W, H = WIDTH, HEIGHT

    if scene_name == "red_weather_inside":
        return [
            (W * 0.18, H * 0.28, 260, 220),
            (W * 0.42, H * 0.47, 320, 250),
            (W * 0.70, H * 0.69, 300, 230),
        ]

    elif scene_name == "machine_mourning":
        return [
            (W * 0.20, H * 0.45, 200, 160),
            (W * 0.42, H * 0.40, 220, 180),
            (W * 0.62, H * 0.50, 200, 160),
            (W * 0.80, H * 0.44, 180, 150),
        ]

    elif scene_name == "wound_learning_to_speak":
        return [
            (W * 0.52, H * 0.52, 360, 300),  # dominant wound
            (W * 0.28, H * 0.36, 120, 100),
            (W * 0.73, H * 0.33, 110, 90),
            (W * 0.73, H * 0.73, 130, 110),
        ]

    elif scene_name == "radio_garden_at_midnight":
        return [
            (W * 0.18, H * 0.70, 110, 90),
            (W * 0.32, H * 0.62, 100, 85),
            (W * 0.48, H * 0.72, 125, 100),
            (W * 0.62, H * 0.58, 110, 90),
            (W * 0.78, H * 0.70, 120, 95),
        ]

    elif scene_name == "ocean_beneath_circuit":
        return [
            (W * 0.18, H * 0.78, 150, 90),
            (W * 0.35, H * 0.82, 170, 100),
            (W * 0.52, H * 0.76, 180, 105),
            (W * 0.72, H * 0.81, 160, 95),
            (W * 0.87, H * 0.77, 145, 90),
        ]

    elif scene_name == "fault_line":
        return [
            (W * 0.20, H * 0.25, 120, 90),
            (W * 0.32, H * 0.36, 140, 100),
            (W * 0.44, H * 0.49, 150, 110),
            (W * 0.56, H * 0.61, 160, 110),
            (W * 0.69, H * 0.73, 140, 100),
        ]

    elif scene_name == "the_last_warm_place":
        return [
            (W * 0.73, H * 0.72, 180, 140),
            (W * 0.80, H * 0.64, 110, 90),
            (W * 0.66, H * 0.80, 100, 80),
        ]

    return []

def draw_blob_field(ctx, cfg, anchors, palette):
    blob_centers = []

    for _ in range(cfg["blob_count"]):
        anchor = random.choice(anchors)
        cx, cy, rx, ry = anchor
        x, y = point_in_ellipse(cx, cy, rx, ry)

        size = random.uniform(*cfg["blob_size"])
        blob_palette = palette["blobs"]

        color = weighted_choice([
            (3.0, blob_palette[0]),
            (3.0, blob_palette[1]),
            (2.5, blob_palette[2]),
            (1.5, blob_palette[3]),
            (0.8, blob_palette[4]),
        ])
        draw_gradient_blob(
            ctx,
            x,
            y,
            size,
            color,
            inner_alpha=random.uniform(0.28, 0.48),
            mid_alpha=random.uniform(0.10, 0.22)
        )
        blob_centers.append((x, y))

    return blob_centers

# ==========================================================
# FLOW + LINE COLOR LOGIC
# ==========================================================

def flow_angle(x, y, cfg, blob_centers):
    # base noise field
    n = noise.pnoise2(
        x * cfg["noise_scale"],
        y * cfg["noise_scale"],
        octaves=cfg["octaves"]
    )
    angle = cfg["global_angle"] + n * cfg["noise_multiplier"]

    # curve around nearby blobs (tangential flow)
    if cfg.get("curve_around_blobs", False) and blob_centers:
        bx, by, d = nearest_blob(x, y, blob_centers)
        radius = cfg.get("curve_radius", 360)
        if d < radius:
            tangent = math.atan2(y - by, x - bx) + math.pi / 2
            w = (1.0 - d / radius) * cfg.get("curve_strength", 0.75)
            angle = lerp_angle(angle, tangent, w)

    # for the fault line: bias along the diagonal corridor
    if cfg.get("fault_bias", False):
        x1, y1, x2, y2 = cfg["fault_line"]
        d = point_line_distance(x, y, x1, y1, x2, y2)
        if d < cfg.get("fault_thickness", 180):
            line_ang = math.atan2(y2 - y1, x2 - x1)
            w = 1.0 - d / cfg.get("fault_thickness", 180)
            angle = lerp_angle(angle, line_ang, w * 0.8)

    return angle

def choose_line_color(cfg, x, y, blob_centers, palette):
    neutral_palette = palette["neutral_lines"]
    accent_palette = palette["accent_lines"]

    neutral = weighted_choice([
        (2.4, neutral_palette[0]),
        (2.6, neutral_palette[1]),
        (2.3, neutral_palette[2]),
        (1.2, neutral_palette[3]),
        (0.5, neutral_palette[4]),
    ])

    accent = random.choice(accent_palette)

    accent_prob = cfg.get("base_cyan_prob", 0.06)

    if blob_centers:
        bx, by, d = nearest_blob(x, y, blob_centers)

        if d < cfg.get("cyan_near_blob_radius", 220):
            accent_prob += cfg.get("cyan_blob_bonus", 0.18)

    if cfg.get("fault_bias", False):
        x1, y1, x2, y2 = cfg["fault_line"]
        d = point_line_distance(x, y, x1, y1, x2, y2)

        if d < cfg.get("fault_thickness", 180) * 0.65:
            accent_prob += 0.28

    if cfg["name"] == "radio_garden_at_midnight":
        accent_prob += 0.10

    if cfg["name"] == "machine_mourning":
        accent_prob -= 0.02

    if cfg["name"] == "the_last_warm_place":
        accent_prob -= 0.03

    accent_prob = clamp(accent_prob, 0.0, 0.75)

    if random.random() < accent_prob:
        return maybe_jitter_live(accent, "accent_line")
    return maybe_jitter_live(neutral, "neutral_line")

# ==========================================================
# LINE START REGIONS
# ==========================================================

def sample_start(cfg, anchors):
    W, H = WIDTH, HEIGHT
    region = cfg["start_region"]

    if region == "full":
        return random.uniform(0, W), random.uniform(0, H)

    elif region == "lower":
        return random.uniform(0, W), random.uniform(H * 0.45, H)

    elif region == "edges":
        side = random.choice(["top", "bottom", "left", "right"])
        if side == "top":
            return random.uniform(0, W), random.uniform(0, H * 0.08)
        elif side == "bottom":
            return random.uniform(0, W), random.uniform(H * 0.92, H)
        elif side == "left":
            return random.uniform(0, W * 0.08), random.uniform(0, H)
        else:
            return random.uniform(W * 0.92, W), random.uniform(0, H)

    elif region == "band":
        return random.uniform(W * 0.1, W * 0.9), random.uniform(H * 0.32, H * 0.75)

    elif region == "near_anchors":
        cx, cy, rx, ry = random.choice(anchors)
        return point_in_ellipse(cx, cy, rx * 1.4, ry * 1.4)

    return random.uniform(0, W), random.uniform(0, H)

# ==========================================================
# BRUSH CURVES
# ==========================================================

def build_brush_geometry(start_x, start_y, cfg, blob_centers):
    """
    Build the curve geometry once so all three brush passes follow the
    exact same path. Interrupted strokes become separate subpaths.
    """
    paths = []
    fragment_points = []

    x_curr, y_curr = start_x, start_y
    path_start = (x_curr, y_curr)
    path_segments = []

    for seg in range(cfg["segments"]):
        # Split before calculating the next Bézier segment so an interrupted
        # curve does not accidentally reuse control points from the old path.
        if seg > 0 and random.random() < cfg.get("interrupt_prob", 0.0):
            if path_segments:
                paths.append((path_start, path_segments))

            x_curr += random.uniform(-20, 20)
            y_curr += random.uniform(-20, 20)
            path_start = (x_curr, y_curr)
            path_segments = []

        angle = flow_angle(x_curr, y_curr, cfg, blob_centers)
        length = random.uniform(*cfg["segment_length"])

        x2 = x_curr + math.cos(angle) * length
        y2 = y_curr + math.sin(angle) * length

        offset_angle = random.uniform(-0.08, 0.08)

        cx1 = x_curr + math.cos(angle + 0.55 + offset_angle) * length / 2
        cy1 = y_curr + math.sin(angle + 0.55 + offset_angle) * length / 2

        cx2 = x_curr + math.cos(angle - 0.55 - offset_angle) * length / 2
        cy2 = y_curr + math.sin(angle - 0.55 - offset_angle) * length / 2

        path_segments.append((cx1, cy1, cx2, cy2, x2, y2))

        if random.random() < cfg.get("fragment_prob", 0.0):
            fragment_points.append(
                (
                    (x_curr + x2) / 2,
                    (y_curr + y2) / 2,
                    random.randint(2, 5),
                    random.uniform(8, 18),
                )
            )

        x_curr, y_curr = x2, y2

    if path_segments:
        paths.append((path_start, path_segments))

    return paths, fragment_points


def stroke_brush_paths(ctx, paths, color, base_thickness, cfg):
    """Layer three strokes over the same Bézier geometry."""
    r, g, b = color
    falloff = cfg.get("thickness_falloff", 2.2)
    base_alpha = cfg["line_alpha"]

    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)

    for pass_index in range(3):
        thickness = base_thickness - pass_index * falloff
        if thickness <= 0:
            continue

        # Wide outer haze, medium body, brighter narrow core.
        alpha_factor = 0.52 + pass_index * 0.24
        alpha = clamp(base_alpha * alpha_factor, 0.04, 1.0)

        ctx.set_line_width(thickness)
        ctx.set_source_rgba(r, g, b, alpha)

        for (start_x, start_y), segments in paths:
            ctx.new_path()
            ctx.move_to(start_x, start_y)

            for cx1, cy1, cx2, cy2, x2, y2 in segments:
                ctx.curve_to(cx1, cy1, cx2, cy2, x2, y2)

            ctx.stroke()


def draw_brush_curve(ctx, start_x, start_y, cfg, blob_centers, palette):
    """Draw one layered flow-field brush curve."""
    color = choose_line_color(
        cfg,
        start_x,
        start_y,
        blob_centers,
        palette,
    )
    base_thickness = random.uniform(*cfg["line_thickness"])

    paths, fragment_points = build_brush_geometry(
        start_x,
        start_y,
        cfg,
        blob_centers,
    )

    stroke_brush_paths(
        ctx,
        paths,
        color,
        base_thickness,
        cfg,
    )

    for x, y, count, spread in fragment_points:
        scatter_fragments(
            ctx,
            x,
            y,
            color,
            alpha_base=cfg["line_alpha"] * 0.22,
            count=count,
            spread=spread,
        )


def draw_line_field(ctx, cfg, anchors, blob_centers, palette):
    for _ in range(cfg["line_count"]):
        x, y = sample_start(cfg, anchors)
        draw_brush_curve(
            ctx,
            x,
            y,
            cfg,
            blob_centers,
            palette,
        )

# ==========================================================
# EXTRA LAYERS
# ==========================================================

def draw_red_dust(ctx, anchors, palette, count=2800):
    blob_palette = palette["blobs"]

    for _ in range(count):
        cx, cy, rx, ry = random.choice(anchors)
        x, y = point_in_ellipse(cx, cy, rx * 1.5, ry * 1.5)

        r, g, b = maybe_jitter_live(random.choice(blob_palette[:4]), "blob")
        alpha = random.uniform(0.04, 0.18)
        radius = random.uniform(0.5, 2.0)

        ctx.set_source_rgba(r, g, b, alpha)
        ctx.arc(x, y, radius, 0, 2 * math.pi)
        ctx.fill()


def draw_radio_rings(ctx, anchors, palette):
    accent_palette = palette["accent_lines"]

    for cx, cy, rx, ry in anchors:
        if random.random() < 0.2:
            continue

        for i in range(random.randint(2, 4)):
            ring_rx = rx * (0.35 + i * 0.18)
            ring_ry = ry * (0.30 + i * 0.16)
            r, g, b = maybe_jitter_live(random.choice(accent_palette), "accent_line")

            ctx.save()
            ctx.translate(cx, cy)
            ctx.scale(ring_rx, ring_ry)
            ctx.new_path()
            ctx.set_line_width(2.0 / max(ring_rx, ring_ry))
            ctx.set_source_rgba(r, g, b, max(0.04, 0.18 - i * 0.03))
            ctx.arc(0, 0, 1, 0, 2 * math.pi)
            ctx.stroke()
            ctx.restore()


def draw_rising_particles(ctx, anchors, palette, count=2400):
    particle_palette = palette["particles"]
    accent_palette = palette["accent_lines"]

    for _ in range(count):
        cx, cy, rx, ry = random.choice(anchors)
        x = random.uniform(cx - rx * 0.7, cx + rx * 0.7)
        y = random.uniform(cy - ry * 0.4, HEIGHT)

        size = random.uniform(0.6, 1.7)
        alpha = random.uniform(0.04, 0.18)
        base_color = random.choice(particle_palette + accent_palette)
        role = "accent_line" if base_color in accent_palette else "particle"
        r, g, b = maybe_jitter_live(base_color, role)

        ctx.set_source_rgba(r, g, b, alpha)
        ctx.arc(x, y, size, 0, 2 * math.pi)
        ctx.fill()


def draw_fault_filaments(ctx, cfg, palette):
    x1, y1, x2, y2 = cfg["fault_line"]
    accent_palette = palette["accent_lines"]

    for _ in range(140):
        t1 = random.uniform(0.0, 1.0)
        t2 = clamp(t1 + random.uniform(-0.12, 0.12), 0.0, 1.0)

        sx = lerp(x1, x2, t1) + random.uniform(-40, 40)
        sy = lerp(y1, y2, t1) + random.uniform(-40, 40)

        ex = lerp(x1, x2, t2) + random.uniform(-60, 60)
        ey = lerp(y1, y2, t2) + random.uniform(-60, 60)

        mx = (sx + ex) / 2 + random.uniform(-50, 50)
        my = (sy + ey) / 2 + random.uniform(-50, 50)

        r, g, b = maybe_jitter_live(random.choice(accent_palette), "accent_line")
        ctx.set_line_width(random.uniform(1.2, 3.4))
        ctx.set_source_rgba(r, g, b, random.uniform(0.10, 0.28))

        ctx.new_path()
        ctx.move_to(sx, sy)
        ctx.curve_to(mx, my, mx, my, ex, ey)
        ctx.stroke()


def draw_general_particles(ctx, cfg, palette, count=1800):
    particle_palette = palette["particles"]
    accent_palette = palette["accent_lines"]

    for _ in range(count):
        x = random.uniform(0, WIDTH)
        y = random.uniform(0, HEIGHT)

        colors = accent_palette if random.random() < 0.18 else particle_palette
        role = "accent_line" if colors is accent_palette else "particle"
        r, g, b = maybe_jitter_live(random.choice(colors), role)

        alpha = random.uniform(0.02, 0.12)
        radius = random.uniform(0.5, 1.6)

        ctx.set_source_rgba(r, g, b, alpha)
        ctx.arc(x, y, radius, 0, 2 * math.pi)
        ctx.fill()

# ==========================================================
# SCENE CONFIGS
# ==========================================================

SCENES = {
    "red_weather_inside": {
        "name": "red_weather_inside",
        "blob_count": 105,
        "blob_size": (170, 360),
        "line_count": 420,
        "segments": 5,
        "segment_length": (70, 180),
        "line_thickness": (8, 22),
        "line_alpha": 0.42,
        "thickness_falloff": 2.4,
        "noise_scale": 0.0010,
        "octaves": 3,
        "noise_multiplier": math.pi * 2.5,
        "global_angle": -0.15,
        "curve_around_blobs": True,
        "curve_radius": 420,
        "curve_strength": 0.85,
        "start_region": "full",
        "fragment_prob": 0.11,
        "interrupt_prob": 0.02,
        "base_cyan_prob": 0.05,
        "cyan_near_blob_radius": 220,
        "cyan_blob_bonus": 0.16,
        "extra_red_dust": True,
    },

    "machine_mourning": {
        "name": "machine_mourning",
        "blob_count": 92,
        "blob_size": (130, 260),
        "line_count": 360,
        "segments": 5,
        "segment_length": (60, 150),
        "line_thickness": (7, 18),
        "line_alpha": 0.38,
        "thickness_falloff": 2.0,
        "noise_scale": 0.0012,
        "octaves": 4,
        "noise_multiplier": math.pi * 2.1,
        "global_angle": 0.04,
        "curve_around_blobs": True,
        "curve_radius": 280,
        "curve_strength": 0.60,
        "start_region": "band",
        "fragment_prob": 0.14,
        "interrupt_prob": 0.22,
        "base_cyan_prob": 0.03,
        "cyan_near_blob_radius": 140,
        "cyan_blob_bonus": 0.10,
        "extra_red_dust": False,
    },

    "wound_learning_to_speak": {
        "name": "wound_learning_to_speak",
        "blob_count": 96,
        "blob_size": (120, 340),
        "line_count": 390,
        "segments": 6,
        "segment_length": (65, 170),
        "line_thickness": (7, 20),
        "line_alpha": 0.40,
        "thickness_falloff": 2.2,
        "noise_scale": 0.0010,
        "octaves": 3,
        "noise_multiplier": math.pi * 2.6,
        "global_angle": 0.10,
        "curve_around_blobs": True,
        "curve_radius": 380,
        "curve_strength": 0.92,
        "start_region": "edges",
        "fragment_prob": 0.10,
        "interrupt_prob": 0.05,
        "base_cyan_prob": 0.06,
        "cyan_near_blob_radius": 180,
        "cyan_blob_bonus": 0.22,
        "extra_red_dust": True,
    },

    "radio_garden_at_midnight": {
        "name": "radio_garden_at_midnight",
        "blob_count": 84,
        "blob_size": (100, 220),
        "line_count": 430,
        "segments": 5,
        "segment_length": (70, 160),
        "line_thickness": (6, 18),
        "line_alpha": 0.38,
        "thickness_falloff": 2.0,
        "noise_scale": 0.0010,
        "octaves": 3,
        "noise_multiplier": math.pi * 2.2,
        "global_angle": -math.pi / 2 + 0.20,  # mostly upward-growing
        "curve_around_blobs": True,
        "curve_radius": 260,
        "curve_strength": 0.52,
        "start_region": "near_anchors",
        "fragment_prob": 0.08,
        "interrupt_prob": 0.02,
        "base_cyan_prob": 0.10,
        "cyan_near_blob_radius": 200,
        "cyan_blob_bonus": 0.16,
        "extra_radio_rings": True,
    },

    "ocean_beneath_circuit": {
        "name": "ocean_beneath_circuit",
        "blob_count": 90,
        "blob_size": (110, 250),
        "line_count": 460,
        "segments": 5,
        "segment_length": (80, 190),
        "line_thickness": (6, 16),
        "line_alpha": 0.34,
        "thickness_falloff": 1.8,
        "noise_scale": 0.0009,
        "octaves": 3,
        "noise_multiplier": math.pi * 1.8,
        "global_angle": 0.03,  # mostly horizontal current
        "curve_around_blobs": True,
        "curve_radius": 300,
        "curve_strength": 0.45,
        "start_region": "lower",
        "fragment_prob": 0.07,
        "interrupt_prob": 0.03,
        "base_cyan_prob": 0.14,
        "cyan_near_blob_radius": 220,
        "cyan_blob_bonus": 0.12,
        "extra_rising_particles": True,
        "extra_red_dust": True,
    },

    "fault_line": {
        "name": "fault_line",
        "blob_count": 82,
        "blob_size": (110, 240),
        "line_count": 420,
        "segments": 5,
        "segment_length": (70, 170),
        "line_thickness": (7, 18),
        "line_alpha": 0.38,
        "thickness_falloff": 2.0,
        "noise_scale": 0.0011,
        "octaves": 4,
        "noise_multiplier": math.pi * 2.2,
        "global_angle": 0.50,
        "curve_around_blobs": True,
        "curve_radius": 260,
        "curve_strength": 0.40,
        "start_region": "band",
        "fragment_prob": 0.10,
        "interrupt_prob": 0.08,
        "base_cyan_prob": 0.08,
        "cyan_near_blob_radius": 150,
        "cyan_blob_bonus": 0.08,
        "fault_bias": True,
        "fault_line": (WIDTH * 0.15, HEIGHT * 0.18, WIDTH * 0.82, HEIGHT * 0.82),
        "fault_thickness": 180,
        "extra_fault_filaments": True,
        "extra_red_dust": True,
    },

    "the_last_warm_place": {
        "name": "the_last_warm_place",
        "blob_count": 58,
        "blob_size": (110, 250),
        "line_count": 260,
        "segments": 5,
        "segment_length": (70, 180),
        "line_thickness": (6, 16),
        "line_alpha": 0.30,
        "thickness_falloff": 1.8,
        "noise_scale": 0.0010,
        "octaves": 3,
        "noise_multiplier": math.pi * 2.0,
        "global_angle": -0.06,
        "curve_around_blobs": True,
        "curve_radius": 420,
        "curve_strength": 0.95,
        "start_region": "full",
        "fragment_prob": 0.06,
        "interrupt_prob": 0.05,
        "base_cyan_prob": 0.02,
        "cyan_near_blob_radius": 140,
        "cyan_blob_bonus": 0.05,
        "extra_red_dust": False,
        "particle_count": 1200,
    },
}

# ==========================================================
# RENDER
# ==========================================================

def render_scene(scene_name, cfg, palette_name, base_palette, geometry_seed, color_seed, variant_index=1):
    """
    Render one scene/palette/color-variation combination.

    geometry_seed controls composition. color_seed mutates the palette.
    """
    print(f"Rendering: {scene_name} / {palette_name} / v{variant_index:02d}")

    palette_rng = random.Random(color_seed)
    palette = build_palette_variant(
        base_palette,
        palette_rng,
        variant_index,
    )

    hue_degrees = palette.get("blob_hue_shift", 0.0) * 360.0
    print(f"  blob hue rotation: {hue_degrees:+.1f}°")

    random.seed(geometry_seed)

    surface, ctx = create_surface()
    draw_background(ctx, palette, noise_count=8000)

    anchors = get_scene_anchors(scene_name)

    # 1) atmospheric masses / pressure systems / chambers / vents
    blob_centers = draw_blob_field(ctx, cfg, anchors, palette)

    # 2) concept-specific structures behind the line field
    if cfg.get("extra_radio_rings", False):
        draw_radio_rings(ctx, anchors, palette)

    if cfg.get("extra_red_dust", False):
        draw_red_dust(ctx, anchors, palette, count=2600)

    # 3) flow-field brushwork
    draw_line_field(ctx, cfg, anchors, blob_centers, palette)

    # 4) concept-specific foreground layers
    if cfg.get("extra_rising_particles", False):
        draw_rising_particles(ctx, anchors, palette, count=2200)

    if cfg.get("extra_fault_filaments", False):
        draw_fault_filaments(ctx, cfg, palette)

    # 5) general atmosphere
    draw_general_particles(
        ctx,
        cfg,
        palette,
        count=cfg.get("particle_count", 1800),
    )

    # 6) save
    SAVE_DIR.mkdir(parents=True, exist_ok=True)

    output_name = f"{scene_name}__{palette_name}__v{variant_index:02d}.png"
    output_path = SAVE_DIR / output_name

    surface.write_to_png(str(output_path))
    surface.finish()

    print(f"Saved {output_path}")


def validate_selection(requested_names, available_names, label):
    """Validate optional scene/palette selection lists."""
    if requested_names is None:
        return list(available_names)

    unknown = [name for name in requested_names if name not in available_names]
    if unknown:
        choices = ", ".join(available_names)
        raise ValueError(
            f"Unknown {label}: {unknown}. Available values: {choices}"
        )

    return list(requested_names)


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":
    scene_names = validate_selection(
        RENDER_SCENE_NAMES,
        SCENES.keys(),
        "scene names",
    )
    palette_names = validate_selection(
        RENDER_PALETTE_NAMES,
        PALETTE_PRESETS.keys(),
        "palette names",
    )

    total = (
        len(scene_names)
        * len(palette_names)
        * PALETTE_VARIATIONS_PER_PRESET
    )
    print(
        f"Rendering {len(scene_names)} scenes × "
        f"{len(palette_names)} palettes × "
        f"{PALETTE_VARIATIONS_PER_PRESET} color variations = "
        f"{total} images"
    )

    i = 0

    for scene_index, scene_name in enumerate(scene_names):
        cfg = SCENES[scene_name]
        base_geometry_seed = BASE_SEED + scene_index * 1000

        for palette_index, palette_name in enumerate(palette_names):
            base_palette = PALETTE_PRESETS[palette_name]

            for variation_index in range(PALETTE_VARIATIONS_PER_PRESET):
                geometry_seed = (
                    base_geometry_seed
                    if KEEP_GEOMETRY_CONSTANT_PER_SCENE
                    else (
                        base_geometry_seed
                        + palette_index * 100
                        + variation_index
                    )
                )

                color_seed = (
                    BASE_SEED
                    + scene_index * 100_000
                    + palette_index * 1_000
                    + variation_index
                )

                render_scene(
                    scene_name,
                    cfg,
                    palette_name,
                    base_palette,
                    geometry_seed=geometry_seed,
                    color_seed=color_seed,
                    variant_index=variation_index + 1,
                )

                i += 1
                print(f"Progress: {i}/{total} images rendered\n")
