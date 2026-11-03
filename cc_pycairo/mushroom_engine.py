"""
Tuneable engine for drawings of mushroom-like shapes.

Built the same way as render_engine.py: scene configs crossed with palette
presets, geometry and color seeded separately, layered Bézier brushwork.
Unlike render_engine.py it is meant to be imported, so every layer is a
function you can call on your own cairo context.

Quick use from another script in cc_pycairo/:

    import mushroom_engine as me

    me.render_scene("fairy_ring_at_dusk", "amanita_night", geometry_seed=3)

    cfg = me.make_scene("the_quiet_colony", mushroom_count=24, spore_mode="rise")
    me.render_scene(cfg, "bioluminescent_hollow", output_name="colony.png")

Run this file directly to render every scene × palette × variation.
"""

import colorsys
import copy
import math
import random
from pathlib import Path

import cairo
import noise

# Resolved from this file so the output lands in the same place whichever
# script imports the engine, and wherever that script is run from.
SAVE_DIR = Path(__file__).resolve().parent / "gen" / "mushroom_engine_output"
BASE_SEED = 7

# Only used when this file is run directly. Set either value to a tuple of
# names to render only a subset.
# Example: RENDER_SCENE_NAMES = ("fairy_ring_at_dusk", "the_quiet_colony")
# Example: RENDER_PALETTE_NAMES = ("amanita_night", "spore_print")
RENDER_SCENE_NAMES = None
RENDER_PALETTE_NAMES = None

# Number of color variants to render for each palette preset.
PALETTE_VARIATIONS_PER_PRESET = 3

# If True, every color variation of the same scene shares the same geometry.
# Only the palette shifts. If False, geometry also changes across variations.
KEEP_GEOMETRY_CONSTANT_PER_SCENE = True

# Keep v01 as the exact base palette. Later variants rotate the entire cap
# family around the color wheel before applying smaller per-color mutations.
KEEP_FIRST_VARIATION_AS_BASE = True
RANDOMIZE_CAP_BASE_HUE = True

# Minimum and maximum shared hue rotation for the cap family. Hue is in the
# normalized HLS range, so 0.10 is 36 degrees and 0.50 is 180 degrees.
# The sign is chosen randomly, giving access to the full color wheel.
CAP_BASE_HUE_SHIFT_MIN = 0.06
CAP_BASE_HUE_SHIFT_MAX = 0.40

# Rotate the glow family together with the caps, so each cap keeps the aura
# it was designed with. Set False to keep the glow independent.
LINK_GLOW_HUE_TO_CAPS = True

PALETTE_ROLES = ("glow", "caps", "stems", "gills", "spots", "mycelium", "spores")

# Palette mutation settings. These create subtle-to-moderate shifts around
# each base palette so the renders feel related, not completely different.
COLOR_VARIATION = {
    "background": {"h": 0.010, "l": 0.020, "s": 0.030, "rgb": 0.008},
    "glow": {"h": 0.025, "l": 0.050, "s": 0.080, "rgb": 0.015},
    "caps": {"h": 0.025, "l": 0.060, "s": 0.090, "rgb": 0.020},
    "stems": {"h": 0.010, "l": 0.040, "s": 0.040, "rgb": 0.012},
    "gills": {"h": 0.015, "l": 0.045, "s": 0.060, "rgb": 0.015},
    "spots": {"h": 0.010, "l": 0.030, "s": 0.040, "rgb": 0.010},
    "mycelium": {"h": 0.030, "l": 0.050, "s": 0.100, "rgb": 0.020},
    "spores": {"h": 0.015, "l": 0.040, "s": 0.060, "rgb": 0.015},
}

# Per-element live jitter inside a single render, applied on top of the
# palette variation above. Keeps caps and threads from feeling too flat.
ELEMENT_COLOR_JITTER = {
    "glow": {"h": 0.020, "l": 0.030, "s": 0.050, "rgb": 0.010},
    "cap": {"h": 0.018, "l": 0.040, "s": 0.060, "rgb": 0.012},
    "stem": {"h": 0.008, "l": 0.030, "s": 0.025, "rgb": 0.010},
    "gill": {"h": 0.010, "l": 0.030, "s": 0.040, "rgb": 0.010},
    "spot": {"h": 0.008, "l": 0.025, "s": 0.030, "rgb": 0.008},
    "mycelium": {"h": 0.015, "l": 0.035, "s": 0.060, "rgb": 0.012},
    "spore": {"h": 0.010, "l": 0.030, "s": 0.030, "rgb": 0.010},
}

# ==========================================================
# PALETTE PRESETS
# ==========================================================
#
# caps, stems and mycelium run dark to light. The last two mycelium colors
# are the accent threads that light up near the mushrooms.

PALETTE_PRESETS = {
    # Fly agaric red against the dark, bone stems, cyan signal underground.
    "amanita_night": {
        "background": (0.010, 0.008, 0.012),
        "glow": [
            (0.50, 0.05, 0.04),
            (0.75, 0.18, 0.08),
            (0.30, 0.03, 0.06),
        ],
        "caps": [
            (0.30, 0.02, 0.02),
            (0.52, 0.04, 0.03),
            (0.74, 0.08, 0.05),
            (0.90, 0.22, 0.10),
            (0.96, 0.62, 0.42),
        ],
        "stems": [
            (0.32, 0.29, 0.27),
            (0.55, 0.51, 0.46),
            (0.78, 0.74, 0.67),
            (0.93, 0.90, 0.84),
        ],
        "gills": [
            (0.30, 0.26, 0.24),
            (0.56, 0.50, 0.45),
            (0.80, 0.74, 0.66),
        ],
        "spots": [
            (0.92, 0.90, 0.84),
            (0.98, 0.96, 0.90),
            (0.84, 0.80, 0.72),
        ],
        "mycelium": [
            (0.18, 0.20, 0.23),
            (0.40, 0.44, 0.48),
            (0.06, 0.52, 0.60),
            (0.16, 0.76, 0.84),
        ],
        "spores": [
            (0.86, 0.87, 0.90),
            (0.16, 0.76, 0.84),
            (0.95, 0.80, 0.66),
        ],
    },

    # Cold teal light from the caps themselves, deep blue night.
    "bioluminescent_hollow": {
        "background": (0.004, 0.012, 0.018),
        "glow": [
            (0.04, 0.40, 0.42),
            (0.10, 0.70, 0.62),
            (0.06, 0.22, 0.40),
        ],
        "caps": [
            (0.02, 0.16, 0.18),
            (0.04, 0.32, 0.34),
            (0.08, 0.55, 0.52),
            (0.30, 0.85, 0.72),
            (0.78, 0.98, 0.88),
        ],
        "stems": [
            (0.10, 0.18, 0.20),
            (0.24, 0.36, 0.38),
            (0.46, 0.62, 0.62),
            (0.72, 0.88, 0.84),
        ],
        "gills": [
            (0.04, 0.26, 0.26),
            (0.12, 0.56, 0.52),
            (0.50, 0.95, 0.80),
        ],
        "spots": [
            (0.70, 1.00, 0.86),
            (0.90, 1.00, 0.95),
            (0.50, 0.90, 0.95),
        ],
        "mycelium": [
            (0.08, 0.16, 0.20),
            (0.16, 0.36, 0.42),
            (0.20, 0.70, 0.70),
            (0.60, 0.98, 0.86),
        ],
        "spores": [
            (0.60, 1.00, 0.86),
            (0.85, 1.00, 0.95),
            (0.40, 0.80, 1.00),
        ],
    },

    # Earthy and muted, like a field guide plate left in the sun.
    "spore_print": {
        "background": (0.020, 0.016, 0.012),
        "glow": [
            (0.40, 0.24, 0.10),
            (0.62, 0.42, 0.20),
            (0.22, 0.14, 0.08),
        ],
        "caps": [
            (0.20, 0.10, 0.05),
            (0.36, 0.19, 0.09),
            (0.54, 0.32, 0.16),
            (0.72, 0.50, 0.28),
            (0.90, 0.78, 0.60),
        ],
        "stems": [
            (0.30, 0.26, 0.20),
            (0.52, 0.46, 0.37),
            (0.74, 0.68, 0.56),
            (0.90, 0.85, 0.74),
        ],
        "gills": [
            (0.22, 0.16, 0.12),
            (0.44, 0.34, 0.26),
            (0.68, 0.56, 0.44),
        ],
        "spots": [
            (0.88, 0.82, 0.70),
            (0.80, 0.72, 0.58),
            (0.95, 0.92, 0.84),
        ],
        "mycelium": [
            (0.24, 0.20, 0.16),
            (0.46, 0.40, 0.32),
            (0.70, 0.62, 0.50),
            (0.88, 0.82, 0.70),
        ],
        "spores": [
            (0.70, 0.56, 0.40),
            (0.86, 0.76, 0.60),
            (0.95, 0.90, 0.80),
        ],
    },

    # Violet caps with gold threads and gold spores.
    "violet_mycelium": {
        "background": (0.012, 0.008, 0.020),
        "glow": [
            (0.30, 0.10, 0.48),
            (0.56, 0.24, 0.74),
            (0.80, 0.56, 0.22),
        ],
        "caps": [
            (0.18, 0.05, 0.26),
            (0.34, 0.10, 0.46),
            (0.52, 0.20, 0.66),
            (0.74, 0.42, 0.84),
            (0.92, 0.80, 0.96),
        ],
        "stems": [
            (0.24, 0.20, 0.30),
            (0.44, 0.40, 0.52),
            (0.68, 0.64, 0.76),
            (0.88, 0.85, 0.92),
        ],
        "gills": [
            (0.20, 0.10, 0.28),
            (0.42, 0.26, 0.54),
            (0.70, 0.54, 0.80),
        ],
        "spots": [
            (0.98, 0.86, 0.52),
            (0.96, 0.94, 0.86),
            (0.90, 0.70, 0.36),
        ],
        "mycelium": [
            (0.20, 0.16, 0.28),
            (0.40, 0.34, 0.52),
            (0.86, 0.66, 0.30),
            (0.98, 0.86, 0.52),
        ],
        "spores": [
            (0.98, 0.86, 0.52),
            (0.88, 0.80, 0.96),
            (0.96, 0.94, 0.90),
        ],
    },

    # Charcoal caps that only light up underneath, embers in the soil.
    "ash_and_ember": {
        "background": (0.010, 0.010, 0.012),
        "glow": [
            (0.60, 0.14, 0.02),
            (0.90, 0.36, 0.06),
            (0.98, 0.62, 0.20),
        ],
        "caps": [
            (0.10, 0.10, 0.11),
            (0.22, 0.21, 0.22),
            (0.38, 0.36, 0.36),
            (0.60, 0.56, 0.54),
            (0.86, 0.82, 0.78),
        ],
        "stems": [
            (0.20, 0.19, 0.19),
            (0.38, 0.36, 0.35),
            (0.60, 0.57, 0.54),
            (0.82, 0.78, 0.74),
        ],
        "gills": [
            (0.40, 0.10, 0.02),
            (0.78, 0.30, 0.06),
            (0.98, 0.62, 0.22),
        ],
        "spots": [
            (0.98, 0.60, 0.20),
            (0.90, 0.36, 0.06),
            (0.98, 0.84, 0.60),
        ],
        "mycelium": [
            (0.18, 0.18, 0.19),
            (0.36, 0.35, 0.36),
            (0.80, 0.32, 0.06),
            (0.98, 0.62, 0.20),
        ],
        "spores": [
            (0.98, 0.62, 0.20),
            (0.98, 0.84, 0.60),
            (0.80, 0.78, 0.76),
        ],
    },
}

# ==========================================================
# CAP PROFILES
# ==========================================================
#
# The cap silhouette is a superellipse with a few extras:
#   shoulder  higher values give squarer shoulders
#   crown     below 1 the sides flare out like a bell, above 1 they bulge
#   umbo      central bump on top
#   dip       central depression, for funnel shapes
#   curl      margin hanging down (negative lifts it)
#   height    cap height as a multiple of the cap radius

CAP_PROFILES = {
    "dome": {
        "shoulder": 2.0, "crown": 2.0, "umbo": 0.0, "dip": 0.0,
        "curl": 0.06, "height": (0.55, 0.75),
    },
    "bell": {
        "shoulder": 1.6, "crown": 0.65, "umbo": 0.0, "dip": 0.0,
        "curl": 0.10, "height": (0.95, 1.30),
    },
    "conical": {
        "shoulder": 1.15, "crown": 0.85, "umbo": 0.10, "dip": 0.0,
        "curl": 0.05, "height": (1.10, 1.55),
    },
    "umbonate": {
        "shoulder": 2.4, "crown": 2.2, "umbo": 0.22, "dip": 0.0,
        "curl": 0.04, "height": (0.40, 0.55),
    },
    "flat": {
        "shoulder": 4.0, "crown": 3.0, "umbo": 0.0, "dip": 0.0,
        "curl": 0.02, "height": (0.22, 0.34),
    },
    "funnel": {
        "shoulder": 3.5, "crown": 3.0, "umbo": 0.0, "dip": 0.70,
        "curl": -0.10, "height": (0.35, 0.50),
    },
    "parasol": {
        "shoulder": 2.6, "crown": 2.0, "umbo": 0.18, "dip": 0.0,
        "curl": 0.04, "height": (0.28, 0.40),
    },
}

# ==========================================================
# SCENE CONFIGS
# ==========================================================
#
# Sizes marked "of height" are fractions of the canvas height, so a scene
# keeps its proportions at any resolution. Values in pixels (thicknesses,
# segment lengths, noise scales) are for a canvas REFERENCE_HEIGHT tall and
# scale with the actual height.

REFERENCE_HEIGHT = 1600

LAYOUTS = ("scattered", "row", "cluster", "ring", "single")

# Base direction spores travel in, per spore_mode.
SPORE_DIRECTIONS = {"fall": math.pi / 2, "rise": -math.pi / 2, "drift": 0.0}

DEFAULT_SCENE = {
    "name": "untitled",

    # canvas
    "width": 2800,
    "height": 1600,

    # layout: "scattered", "row", "cluster", "ring" or "single"
    "layout": "scattered",
    "mushroom_count": 9,
    "ground_level": 0.80,         # ground line, of height
    "ground_band": 0.10,          # depth band the bases spread over, of height
    "margin": 0.08,               # left/right margin, of width
    "cluster_count": 3,
    "cluster_spread": 0.07,       # of width
    "ring_radius": 0.30,          # of width
    "ring_tilt": 0.16,            # vertical squash of the ring
    "hero_scale": 1.8,            # main mushroom size in "single"
    "depth_scale_min": 0.55,      # farthest mushroom size vs the nearest
    "size_variation": (0.80, 1.15),
    "fog": 0.45,                  # how far back mushrooms fade into the dark

    # caps, weights per profile name from CAP_PROFILES
    "cap_profiles": {"dome": 3.0, "bell": 1.0, "umbonate": 1.0},
    "cap_radius": (0.08, 0.12),   # of height
    "cap_height_scale": 1.0,
    "cap_tilt": 0.10,             # random extra tilt, radians
    "cap_follow_stem": 0.7,       # how much the cap follows the stem tip
    "cap_wobble": 0.06,           # irregular, wavy margin
    "cap_wobble_freq": 2.5,
    "cap_streaks": 40,            # radial brush fibres on the cap
    "cap_streak_alpha": 0.22,
    "spot_prob": 0.35,
    "spot_count": (6, 18),
    "spot_size": (0.05, 0.11),    # of cap radius
    "rim_light": 0.45,
    "cap_glow": 0.16,             # aura behind each cap
    "cap_glow_size": 2.6,         # of cap radius

    # gills, seen on the underside of the cap
    "gill_depth": (0.10, 0.18),   # underside depth, of cap radius
    "gill_count": (30, 48),
    "gill_alpha": 0.38,

    # stems
    "stem_height": (0.20, 0.34),  # of height
    "stem_width": (0.24, 0.36),   # of cap radius
    "stem_taper": (0.65, 0.95),   # top width / base width
    "stem_lean": 0.14,
    "stem_bend": 0.10,
    "bulb_prob": 0.30,
    "bulb_size": (0.25, 0.60),
    "ring_prob": 0.30,
    "stem_fibers": 18,

    # mycelium, below the ground line
    "mycelium_count": 260,
    "mycelium_from_bases": 0.7,   # share of threads that start at a stem
    "mycelium_segments": 6,
    "mycelium_segment_length": (30, 90),
    "mycelium_curl": 0.30,        # how much each segment bows, render_engine uses 0.55
    "mycelium_thickness": (1.5, 5.0),
    "mycelium_alpha": 0.30,
    "mycelium_branch_prob": 0.18,
    "mycelium_noise_scale": 0.0016,
    "mycelium_noise_multiplier": math.pi * 1.6,
    "mycelium_angle": math.pi / 2,  # mostly downward
    "mycelium_depth": 0.22,       # of height
    "mycelium_links": 10,         # sagging strands between nearby stems
    "mycelium_link_sag": (0.18, 0.40),
    "mycelium_link_alpha": 0.30,
    "mycelium_nodes": 3,          # glowing knots per link

    # atmosphere
    "background_noise": 7000,
    "vignette": 0.55,
    "glow_count": 64,
    "glow_size": (0.06, 0.18),    # of height
    "glow_alpha": 0.28,
    "ground_shade": 0.60,
    "ground_strokes": 14,

    # air currents: render_engine style brushwork above the ground,
    # bending around the caps
    "air_line_count": 220,
    "air_segments": 5,
    "air_segment_length": (60, 160),
    "air_thickness": (5, 16),
    "air_alpha": 0.18,
    "air_angle": -0.10,
    "air_noise_scale": 0.0010,
    "air_noise_multiplier": math.pi * 1.4,
    "air_curve_radius": 3.0,      # of cap radius
    "air_curve_strength": 0.85,

    "spore_count": 160,           # per mushroom at full size
    "spore_mode": "fall",         # "fall", "rise" or "drift"
    "spore_spread": 0.22,         # of height
    "spore_alpha": 0.32,
    "particle_count": 1400,
}

# Each scene only lists what it changes from DEFAULT_SCENE.
SCENES = {
    "forest_floor_choir": {
        "name": "forest_floor_choir",
        "layout": "scattered",
        "mushroom_count": 13,
        "cap_profiles": {
            "dome": 3.0, "bell": 2.0, "umbonate": 1.5,
            "conical": 1.0, "flat": 1.0,
        },
        "spot_prob": 0.25,
    },

    "the_quiet_colony": {
        "name": "the_quiet_colony",
        "layout": "cluster",
        "mushroom_count": 20,
        "cluster_count": 3,
        "cap_profiles": {"conical": 3.0, "bell": 2.0, "dome": 0.5},
        "cap_radius": (0.05, 0.08),
        "stem_height": (0.22, 0.40),
        "stem_width": (0.20, 0.28),
        "stem_lean": 0.28,
        "stem_bend": 0.18,
        "gill_depth": (0.08, 0.14),
        "spot_prob": 0.0,
        "ring_prob": 0.15,
        "bulb_prob": 0.0,
        "spore_mode": "rise",
        "spore_count": 120,
        "spore_spread": 0.35,
    },

    "fairy_ring_at_dusk": {
        "name": "fairy_ring_at_dusk",
        "layout": "ring",
        "mushroom_count": 16,
        "ground_level": 0.68,
        "ring_radius": 0.32,
        "ring_tilt": 0.20,
        "cap_profiles": {"dome": 2.0, "umbonate": 2.0, "flat": 1.0},
        "cap_radius": (0.06, 0.09),
        "stem_height": (0.14, 0.24),
        "depth_scale_min": 0.45,
        "spot_prob": 0.5,
        "mycelium_links": 20,
        "mycelium_depth": 0.30,
        "spore_mode": "drift",
    },

    "solitary_specimen": {
        "name": "solitary_specimen",
        "width": 1800,
        "height": 2200,
        "layout": "single",
        "mushroom_count": 5,
        "ground_level": 0.80,
        "hero_scale": 2.0,
        "cap_profiles": {"dome": 1.0},
        "cap_radius": (0.10, 0.11),
        "stem_height": (0.18, 0.20),
        "stem_lean": 0.06,
        "spot_prob": 1.0,
        "ring_prob": 0.6,
        "bulb_prob": 0.8,
        "cap_streaks": 70,
        "mycelium_count": 260,
        "mycelium_links": 8,
        "spore_count": 260,
    },

    "underground_network": {
        "name": "underground_network",
        "layout": "row",
        "mushroom_count": 11,
        "ground_level": 0.42,
        "ground_band": 0.06,
        "cap_profiles": {"dome": 2.0, "bell": 1.0, "conical": 1.0},
        "cap_radius": (0.04, 0.065),
        "stem_height": (0.10, 0.18),
        "depth_scale_min": 0.7,
        "mycelium_count": 620,
        "mycelium_from_bases": 0.5,
        "mycelium_segments": 8,
        "mycelium_depth": 0.55,
        "mycelium_alpha": 0.36,
        "mycelium_links": 34,
        "mycelium_link_sag": (0.25, 0.80),
        "mycelium_nodes": 5,
        "spore_count": 90,
    },

    "parasol_grove": {
        "name": "parasol_grove",
        "layout": "row",
        "mushroom_count": 7,
        "ground_level": 0.86,
        "cap_profiles": {"parasol": 3.0, "flat": 1.0, "funnel": 1.0},
        "cap_radius": (0.09, 0.13),
        "stem_height": (0.36, 0.52),
        "stem_width": (0.12, 0.18),
        "stem_taper": (0.55, 0.75),
        "stem_bend": 0.06,
        "gill_depth": (0.07, 0.12),
        "bulb_prob": 0.9,
        "ring_prob": 0.8,
        "spot_prob": 0.6,
        "spot_size": (0.03, 0.06),
        "spot_count": (14, 28),
        "spore_mode": "fall",
        "spore_spread": 0.30,
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

    All cap colors receive one shared hue rotation first. This changes the
    actual cap color family while preserving its dark-to-light hierarchy.
    Smaller independent mutations are applied afterwards.
    """
    variant = copy.deepcopy(base_palette)

    use_exact_base = KEEP_FIRST_VARIATION_AS_BASE and variant_index == 1

    if RANDOMIZE_CAP_BASE_HUE and not use_exact_base:
        cap_hue_shift = random_signed_hue_shift(
            rng,
            CAP_BASE_HUE_SHIFT_MIN,
            CAP_BASE_HUE_SHIFT_MAX,
        )
    else:
        cap_hue_shift = 0.0

    rotated_roles = {"caps"}
    if LINK_GLOW_HUE_TO_CAPS:
        rotated_roles.add("glow")

    sources = {}
    for key in PALETTE_ROLES:
        colors = base_palette[key]
        if key in rotated_roles:
            colors = [rotate_hue(color, cap_hue_shift) for color in colors]
        sources[key] = list(colors)

    if use_exact_base:
        # v01 remains an untouched reference render. Live per-element jitter
        # still gives the individual marks some variation.
        variant.update(sources)
        variant["cap_hue_shift"] = cap_hue_shift
        return variant

    variant["background"] = jitter_color(
        base_palette["background"],
        rng,
        **COLOR_VARIATION["background"],
    )

    for key, source_colors in sources.items():
        variant[key] = [
            jitter_color(color, rng, **COLOR_VARIATION[key])
            for color in source_colors
        ]

    variant["cap_hue_shift"] = cap_hue_shift
    return variant

def resolve_palette(palette, variant_index=1, color_seed=None):
    """Turn a preset name or a palette dict into a ready-to-use variant."""
    base_palette = PALETTE_PRESETS[palette] if isinstance(palette, str) else palette

    missing = [key for key in ("background",) + PALETTE_ROLES if key not in base_palette]
    if missing:
        raise ValueError(f"Palette is missing roles: {missing}")

    rng = random.Random(BASE_SEED + variant_index if color_seed is None else color_seed)
    return build_palette_variant(base_palette, rng, variant_index)

def maybe_jitter_live(color, role, rng=random):
    return jitter_color(color, rng, **ELEMENT_COLOR_JITTER[role])

def lerp(a, b, t):
    return a + (b - a) * t

def lerp_color(c1, c2, t):
    return tuple(lerp(a, b, t) for a, b in zip(c1, c2))

def distance(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)

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

def bezier_point(p0, p1, p2, p3, t):
    mt = 1.0 - t
    a, b, c, d = mt * mt * mt, 3 * mt * mt * t, 3 * mt * t * t, t * t * t
    return (
        a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0],
        a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1],
    )

def bezier_tangent(p0, p1, p2, p3, t):
    mt = 1.0 - t
    a, b, c = 3 * mt * mt, 6 * mt * t, 3 * t * t
    return (
        a * (p1[0] - p0[0]) + b * (p2[0] - p1[0]) + c * (p3[0] - p2[0]),
        a * (p1[1] - p0[1]) + b * (p2[1] - p1[1]) + c * (p3[1] - p2[1]),
    )

def polyline_to_path(points):
    """Smooth a polyline into one Bézier path (Catmull-Rom)."""
    segments = []
    n = len(points)

    for i in range(n - 1):
        p0 = points[i - 1] if i > 0 else points[i]
        p1 = points[i]
        p2 = points[i + 1]
        p3 = points[i + 2] if i + 2 < n else p2

        cx1 = p1[0] + (p2[0] - p0[0]) / 6
        cy1 = p1[1] + (p2[1] - p0[1]) / 6
        cx2 = p2[0] - (p3[0] - p1[0]) / 6
        cy2 = p2[1] - (p3[1] - p1[1]) / 6

        segments.append((cx1, cy1, cx2, cy2, p2[0], p2[1]))

    return (points[0], segments)

def to_world(origin_x, origin_y, angle, lx, ly):
    """Map a point from a rotated local frame back to canvas coordinates."""
    c, s = math.cos(angle), math.sin(angle)
    return origin_x + c * lx - s * ly, origin_y + s * lx + c * ly

def ellipse_path(ctx, cx, cy, rx, ry):
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(rx, ry)
    ctx.new_sub_path()
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()

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

def unit(cfg):
    """Pixel scale of this canvas relative to REFERENCE_HEIGHT."""
    return cfg["height"] / REFERENCE_HEIGHT

def make_scene(base=None, **overrides):
    """
    Build a full scene config: DEFAULT_SCENE, then a preset, then overrides.

    base is a name from SCENES, a dict of overrides, or None for the
    defaults alone. Unknown keys raise, so typos do not pass silently.
    """
    cfg = copy.deepcopy(DEFAULT_SCENE)
    preset = SCENES[base] if isinstance(base, str) else (base or {})

    for source in (preset, overrides):
        unknown = [key for key in source if key not in DEFAULT_SCENE]
        if unknown:
            raise ValueError(f"Unknown scene keys: {unknown}")
        cfg.update(copy.deepcopy(source))

    unknown_profiles = [p for p in cfg["cap_profiles"] if p not in CAP_PROFILES]
    if unknown_profiles:
        raise ValueError(
            f"Unknown cap profiles: {unknown_profiles}. "
            f"Available values: {', '.join(CAP_PROFILES)}"
        )

    for key, choices in (("layout", LAYOUTS), ("spore_mode", SPORE_DIRECTIONS)):
        if cfg[key] not in choices:
            raise ValueError(
                f"Unknown {key}: {cfg[key]}. Available values: {', '.join(choices)}"
            )

    return cfg

# ==========================================================
# CORE DRAWING PRIMITIVES
# ==========================================================

def create_surface(cfg):
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, cfg["width"], cfg["height"])
    ctx = cairo.Context(surface)
    return surface, ctx

def draw_background(ctx, cfg, palette):
    W, H = cfg["width"], cfg["height"]
    noise_count = cfg["background_noise"]

    ctx.set_source_rgb(*palette["background"])
    ctx.paint()

    bg_r, bg_g, bg_b = palette["background"]

    for _ in range(noise_count):
        x = random.uniform(0, W)
        y = random.uniform(0, H)

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
        x = random.uniform(0, W)
        y = random.uniform(0, H)

        base = random.uniform(0.03, 0.11)
        alpha = random.uniform(0.02, 0.07)
        r = random.uniform(0.4, 1.1)

        ctx.set_source_rgba(base, base, base, alpha)
        ctx.arc(x, y, r, 0, 2 * math.pi)
        ctx.fill()

    # pull the corners into the dark
    vignette = cairo.RadialGradient(
        W * 0.5, H * 0.5, min(W, H) * 0.30,
        W * 0.5, H * 0.5, max(W, H) * 0.75,
    )
    vignette.add_color_stop_rgba(0.0, 0, 0, 0, 0.0)
    vignette.add_color_stop_rgba(1.0, 0, 0, 0, cfg["vignette"])
    ctx.set_source(vignette)
    ctx.paint()

def draw_gradient_blob(ctx, x, y, size, color, inner_alpha=0.42, mid_alpha=0.18):
    pat = cairo.RadialGradient(x, y, size * 0.12, x, y, size)
    r, g, b = color
    pat.add_color_stop_rgba(0.0, r, g, b, inner_alpha)
    pat.add_color_stop_rgba(0.45, r, g, b, mid_alpha)
    pat.add_color_stop_rgba(1.0, r, g, b, 0.0)

    ctx.set_source(pat)
    ctx.arc(x, y, size, 0, 2 * math.pi)
    ctx.fill()

def stroke_brush_paths(ctx, paths, color, base_thickness, base_alpha, falloff=None):
    """Layer three strokes over the same Bézier geometry.

    paths = [((start_x, start_y), [(cx1, cy1, cx2, cy2, x2, y2), ...]), ...]
    """
    r, g, b = color
    if falloff is None:
        falloff = base_thickness * 0.3

    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)

    for pass_index in range(3):
        thickness = base_thickness - pass_index * falloff
        if thickness <= 0:
            continue

        # Wide outer haze, medium body, brighter narrow core.
        alpha_factor = 0.52 + pass_index * 0.24
        alpha = clamp(base_alpha * alpha_factor)

        ctx.set_line_width(thickness)
        ctx.set_source_rgba(r, g, b, alpha)

        for (start_x, start_y), segments in paths:
            ctx.new_path()
            ctx.move_to(start_x, start_y)

            for cx1, cy1, cx2, cy2, x2, y2 in segments:
                ctx.curve_to(cx1, cy1, cx2, cy2, x2, y2)

            ctx.stroke()

def build_brush_geometry(start_x, start_y, segments, segment_length, angle_at, branch_prob=0.0, curl=0.55):
    """
    Build a flowing curve once, so every brush pass follows the same path.

    angle_at(x, y) gives the flow direction at a point. curl is how far the
    control points swing off that direction, so how much each segment bows.
    Returns the path and the points where a branch may sprout.
    """
    path_segments = []
    branch_points = []
    x_curr, y_curr = start_x, start_y

    for _ in range(segments):
        angle = angle_at(x_curr, y_curr)
        length = random.uniform(*segment_length)

        x2 = x_curr + math.cos(angle) * length
        y2 = y_curr + math.sin(angle) * length

        offset_angle = random.uniform(-0.08, 0.08)

        cx1 = x_curr + math.cos(angle + curl + offset_angle) * length / 2
        cy1 = y_curr + math.sin(angle + curl + offset_angle) * length / 2

        cx2 = x_curr + math.cos(angle - curl - offset_angle) * length / 2
        cy2 = y_curr + math.sin(angle - curl - offset_angle) * length / 2

        path_segments.append((cx1, cy1, cx2, cy2, x2, y2))

        if random.random() < branch_prob:
            branch_points.append((x2, y2))

        x_curr, y_curr = x2, y2

    return ((start_x, start_y), path_segments), branch_points

# ==========================================================
# LAYOUT
# ==========================================================

def place_mushrooms(cfg):
    """
    Return mushroom bases as [(x, y, depth, size), ...], back to front.

    depth runs from 0 (farthest) to 1 (nearest). size is a multiplier on
    top of the depth scaling, used by clusters and the "single" hero.
    """
    W, H = cfg["width"], cfg["height"]
    n = cfg["mushroom_count"]
    layout = cfg["layout"]

    ground_y = H * cfg["ground_level"]
    band = H * cfg["ground_band"]
    margin = W * cfg["margin"]

    spots = []

    if layout == "scattered":
        for _ in range(n):
            x = random.uniform(margin, W - margin)
            y = ground_y + random.uniform(-0.5, 0.5) * band
            spots.append((x, y, 1.0))

    elif layout == "row":
        step = (W - 2 * margin) / max(1, n)
        for i in range(n):
            x = margin + (i + 0.5) * step + random.uniform(-0.3, 0.3) * step
            y = ground_y + random.uniform(-0.5, 0.5) * band
            spots.append((x, y, 1.0))

    elif layout == "cluster":
        k = max(1, cfg["cluster_count"])
        spread = W * cfg["cluster_spread"]
        centers = [
            (
                lerp(margin, W - margin, (i + 0.5) / k) + random.uniform(-1, 1) * W * 0.04,
                ground_y + random.uniform(-0.3, 0.3) * band,
            )
            for i in range(k)
        ]
        for _ in range(n):
            cx, cy = random.choice(centers)
            offset = random.gauss(0, spread * 0.5)
            x = clamp(cx + offset, margin * 0.5, W - margin * 0.5)
            y = cy + random.uniform(-0.3, 0.3) * band
            # The middle of a cluster grows tallest.
            size = lerp(1.0, 0.55, min(1.0, abs(offset) / spread))
            spots.append((x, y, size))

    elif layout == "ring":
        rx = W * cfg["ring_radius"]
        ry = rx * cfg["ring_tilt"]
        for i in range(n):
            angle = (i + random.uniform(-0.25, 0.25)) * 2 * math.pi / n
            x = W * 0.5 + math.cos(angle) * rx
            y = ground_y + math.sin(angle) * ry
            spots.append((x, y, 1.0))

    elif layout == "single":
        spots.append((W * 0.5 + random.uniform(-0.03, 0.03) * W, ground_y + band * 0.3, cfg["hero_scale"]))
        for _ in range(n - 1):
            side = random.choice((-1, 1))
            x = W * 0.5 + side * random.uniform(0.10, 0.36) * W
            y = ground_y + random.uniform(-0.5, 0.2) * band
            spots.append((x, y, random.uniform(0.30, 0.60)))

    else:
        raise ValueError(f"Unknown layout: {layout}. Available values: {', '.join(LAYOUTS)}")

    ys = [y for _, y, _ in spots]
    y_min, y_max = min(ys), max(ys)

    placed = []
    for x, y, size in spots:
        depth = 1.0 if y_max - y_min < 1e-6 else (y - y_min) / (y_max - y_min)
        placed.append((x, y, depth, size))

    placed.sort(key=lambda p: p[1])
    return placed

# ==========================================================
# MUSHROOM SHAPES
# ==========================================================

# Keys of a mushroom dict measured in pixels, scaled together.
MUSHROOM_SIZE_KEYS = ("cap_radius", "cap_height", "gill_depth", "stem_height", "stem_width")

def scale_mushroom(m, factor):
    for key in MUSHROOM_SIZE_KEYS:
        m[key] *= factor
    m["scale"] *= factor

def make_mushroom(cfg, palette, x, y, depth=1.0, scale=1.0, **overrides):
    """
    Roll one mushroom from the scene config. Returns a plain dict that
    draw_mushroom() renders; any key of it can be overridden here, e.g.
    profile="bell", cap_radius=220, stem_lean=-0.2, colors={"cap": (1, 0, 0)}.
    Sizes in the returned dict are in pixels.
    """
    H = cfg["height"]

    profile_name = weighted_choice([(w, name) for name, w in cfg["cap_profiles"].items()])
    profile_name = overrides.get("profile", profile_name)
    profile = CAP_PROFILES[profile_name]

    caps = palette["caps"]
    stems = palette["stems"]
    gills = palette["gills"]

    cap_color = maybe_jitter_live(caps[weighted_choice([(1.5, 1), (3.0, 2), (2.0, 3)])], "cap")
    stem_color = maybe_jitter_live(
        weighted_choice([(1.0, stems[1]), (2.0, stems[2]), (1.5, stems[3])]),
        "stem",
    )
    colors = {
        "cap": cap_color,
        "cap_dark": lerp_color(cap_color, caps[0], 0.65),
        "cap_light": lerp_color(cap_color, caps[4], 0.60),
        "stem": stem_color,
        "stem_dark": lerp_color(stem_color, stems[0], 0.70),
        "stem_light": lerp_color(stem_color, stems[3], 0.60),
        "gill_dark": maybe_jitter_live(gills[0], "gill"),
        "gill": maybe_jitter_live(gills[1], "gill"),
        "gill_light": maybe_jitter_live(gills[2], "gill"),
        "spot": maybe_jitter_live(random.choice(palette["spots"]), "spot"),
        "glow": maybe_jitter_live(
            weighted_choice([(3.0, palette["glow"][0]), (2.0, palette["glow"][1]), (1.0, palette["glow"][2])]),
            "glow",
        ),
        "rim": lerp_color(caps[4], palette["spores"][0], 0.5),
    }

    # Atmospheric perspective: far mushrooms sink into the background.
    fog = cfg["fog"] * (1.0 - depth)
    colors = {
        key: lerp_color(color, palette["background"], fog)
        for key, color in colors.items()
    }

    cap_radius = H * random.uniform(*cfg["cap_radius"]) * scale

    m = {
        "x": x,
        "y": y,
        "depth": depth,
        "scale": scale,

        "profile": profile_name,
        "shoulder": profile["shoulder"],
        "crown": profile["crown"],
        "umbo": profile["umbo"],
        "dip": profile["dip"],
        "curl": profile["curl"],
        "cap_radius": cap_radius,
        "cap_height": cap_radius * random.uniform(*profile["height"]) * cfg["cap_height_scale"],
        "cap_tilt": random.uniform(-1, 1) * cfg["cap_tilt"],
        "cap_follow": cfg["cap_follow_stem"],
        "wobble": cfg["cap_wobble"] * random.uniform(0.5, 1.5),
        "wobble_freq": cfg["cap_wobble_freq"] * random.uniform(0.7, 1.3),
        "streaks": cfg["cap_streaks"],
        "streak_alpha": cfg["cap_streak_alpha"],
        "spots": random.randint(*cfg["spot_count"]) if random.random() < cfg["spot_prob"] else 0,
        "spot_size": cfg["spot_size"],
        "rim_light": cfg["rim_light"],
        "glow": cfg["cap_glow"],
        "glow_size": cfg["cap_glow_size"],

        "gill_depth": cap_radius * random.uniform(*cfg["gill_depth"]),
        "gill_count": random.randint(*cfg["gill_count"]),
        "gill_alpha": cfg["gill_alpha"],

        "stem_height": H * random.uniform(*cfg["stem_height"]) * scale,
        "stem_width": cap_radius * random.uniform(*cfg["stem_width"]),
        "stem_taper": random.uniform(*cfg["stem_taper"]),
        "stem_lean": random.uniform(-1, 1) * cfg["stem_lean"],
        "stem_bend": random.uniform(-1, 1) * cfg["stem_bend"],
        "bulb": random.uniform(*cfg["bulb_size"]) if random.random() < cfg["bulb_prob"] else 0.0,
        "ring": random.uniform(0.70, 0.85) if random.random() < cfg["ring_prob"] else 0.0,
        "fibers": cfg["stem_fibers"],

        "noise_offset": random.uniform(0, 500),
        "colors": colors,
    }

    # Shrink anything that would grow off the top of the canvas.
    reach = m["stem_height"] + m["cap_height"] * (1.0 + m["umbo"])
    room = y - H * 0.03
    if reach > room > 0:
        scale_mushroom(m, room / reach)

    color_overrides = overrides.pop("colors", None)
    unknown = [key for key in overrides if key not in m]
    if unknown:
        raise ValueError(f"Unknown mushroom keys: {unknown}")

    m.update(overrides)
    if color_overrides:
        m["colors"].update(color_overrides)

    return m

def cap_profile(u, m):
    """Height of the cap top at u in [-1, 1], as a fraction of cap height."""
    a = abs(u)
    height = max(0.0, 1.0 - a ** m["shoulder"]) ** (1.0 / m["crown"])
    height *= 1.0 - m["dip"] * math.exp(-((u / 0.45) ** 2))
    height += m["umbo"] * math.exp(-((u / 0.16) ** 2))
    return height

def stem_bezier(m):
    bx, by, h = m["x"], m["y"], m["stem_height"]
    lean, bend = m["stem_lean"], m["stem_bend"]

    p0 = (bx, by)
    p1 = (bx + bend * h, by - h * 0.35)
    p2 = (bx + lean * h + bend * h * 0.5, by - h * 0.72)
    p3 = (bx + lean * h, by - h)
    return p0, p1, p2, p3

def cap_frame(m):
    """Where the cap sits: (x, y, angle) of the top of the stem."""
    _, _, p2, p3 = stem_bezier(m)
    tip_angle = math.atan2(p3[1] - p2[1], p3[0] - p2[0]) + math.pi / 2
    return p3[0], p3[1], tip_angle * m["cap_follow"] + m["cap_tilt"]

def stem_samples(m, steps=48):
    """Points along the stem: (x, y, normal_x, normal_y, width)."""
    p0, p1, p2, p3 = stem_bezier(m)
    w_base = m["stem_width"]
    w_top = w_base * m["stem_taper"]

    samples = []
    for i in range(steps + 1):
        t = i / steps
        x, y = bezier_point(p0, p1, p2, p3, t)
        dx, dy = bezier_tangent(p0, p1, p2, p3, t)
        length = math.hypot(dx, dy) or 1.0

        w = lerp(w_base, w_top, t)
        w *= 1.0 + 0.06 * noise.pnoise1(t * 3.0 + m["noise_offset"])
        # swollen foot and a slight flare where the stem meets the cap
        w += w_base * m["bulb"] * math.exp(-(((t - 0.05) / 0.10) ** 2))
        w += w_top * 0.18 * math.exp(-(((1.0 - t) / 0.05) ** 2))

        samples.append((x, y, -dy / length, dx / length, w))

    return samples

def cap_outline(m, steps=72):
    """
    Cap silhouette in the cap's own frame: origin at the top of the stem,
    y pointing down. Returns the top curve and the near rim, both left to
    right. The near rim arcs up by the gill depth, as the cap is seen from
    slightly below.
    """
    R, Hc, d = m["cap_radius"], m["cap_height"], m["gill_depth"]
    offset = m["noise_offset"]

    top, bottom = [], []
    for i in range(steps + 1):
        u = -1.0 + 2.0 * i / steps
        edge = math.sqrt(max(0.0, 1.0 - u * u))
        curl = m["curl"] * Hc * abs(u) ** 6

        wobble = m["wobble"] * noise.pnoise1(u * m["wobble_freq"] + offset)
        rim_wobble = m["wobble"] * noise.pnoise1(u * m["wobble_freq"] * 2.3 + offset + 31.0)

        x = u * R * (1.0 + wobble * 0.4)
        y_bottom = -d * edge + curl + rim_wobble * R * 0.25
        y_top = -Hc * cap_profile(u, m) * (1.0 + wobble) + curl
        # keep some thickness at the margin so the ends stay blunt
        y_top = min(y_top, y_bottom - Hc * (0.03 + 0.05 * edge))

        top.append((x, y_top))
        bottom.append((x, y_bottom))

    return top, bottom

def cap_surface_point(top, bottom, r, phi):
    """
    A point on the visible face of the cap, in the cap frame. r runs from
    the crown (0) to the margin (1), phi around the cap with pi/2 facing the
    viewer. top and bottom come from cap_outline().
    """
    u = r * math.cos(phi)
    v = 1.0 - r ** 1.3

    f = (u + 1.0) / 2.0 * (len(top) - 1)
    i = int(clamp(f, 0, len(top) - 2))
    t = f - i

    x = lerp(top[i][0], top[i + 1][0], t)
    y_top = lerp(top[i][1], top[i + 1][1], t)
    y_bottom = lerp(bottom[i][1], bottom[i + 1][1], t)
    return x, lerp(y_bottom, y_top, v)

# ==========================================================
# MUSHROOM DRAWING
# ==========================================================

def draw_contact_shadow(ctx, m, palette_background=(0.0, 0.0, 0.0)):
    r = m["stem_width"] * 1.8
    dr, dg, db = (c * 0.3 for c in palette_background)

    ctx.save()
    ctx.translate(m["x"], m["y"])
    ctx.scale(1.0, 0.28)
    shadow = cairo.RadialGradient(0, 0, 0, 0, 0, r)
    shadow.add_color_stop_rgba(0.0, dr, dg, db, 0.60)
    shadow.add_color_stop_rgba(1.0, dr, dg, db, 0.0)
    ctx.set_source(shadow)
    ctx.new_path()
    ctx.arc(0, 0, r, 0, 2 * math.pi)
    ctx.fill()
    ctx.restore()

def draw_gills(ctx, m, cap_x, cap_y, cap_angle):
    """The underside: a disk of gills radiating out from the stem."""
    colors = m["colors"]
    R = m["cap_radius"] * 0.97
    d = m["gill_depth"]
    stem_r = m["stem_width"] * m["stem_taper"] * 0.5

    ctx.save()
    ctx.translate(cap_x, cap_y)
    ctx.rotate(cap_angle)

    ctx.new_path()
    ellipse_path(ctx, 0, 0, R, d)
    ctx.clip()

    # deep near the stem, catching light towards the margin
    ctx.save()
    ctx.scale(1.0, d / R)
    under = cairo.RadialGradient(0, 0, stem_r * 0.5, 0, 0, R)
    under.add_color_stop_rgb(0.0, *colors["gill_dark"])
    under.add_color_stop_rgb(0.65, *lerp_color(colors["gill_dark"], colors["gill"], 0.5))
    under.add_color_stop_rgb(1.0, *colors["gill"])
    ctx.set_source(under)
    ctx.paint()
    ctx.restore()

    count = m["gill_count"]
    step = 2 * math.pi / count
    ratio = d / R

    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for color, alpha, shift in (
        (colors["gill_dark"], m["gill_alpha"] * 0.9, 0.18),
        (colors["gill_light"], m["gill_alpha"], 0.0),
    ):
        ctx.new_path()
        for i in range(count):
            theta = (i + shift) * step
            c, s = math.cos(theta), math.sin(theta)
            ctx.move_to(stem_r * c, stem_r * ratio * s)
            ctx.line_to(R * c, d * s)

            # shorter gills fill the gaps out at the margin
            theta += step * 0.5
            c, s = math.cos(theta), math.sin(theta)
            ctx.move_to(R * 0.55 * c, d * 0.55 * s)
            ctx.line_to(R * c, d * s)

        ctx.set_source_rgba(*color, alpha)
        ctx.set_line_width(max(0.6, R * 0.007))
        ctx.stroke()

    # the overhanging margin shades the near side
    shade = cairo.LinearGradient(0, -d, 0, d * 0.3)
    dr, dg, db = colors["gill_dark"]
    shade.add_color_stop_rgba(0.0, dr, dg, db, 0.65)
    shade.add_color_stop_rgba(1.0, dr, dg, db, 0.0)
    ctx.set_source(shade)
    ctx.paint()

    ctx.restore()

def trace_stem(ctx, samples, m, cap_angle):
    left = [(x - nx * w / 2, y - ny * w / 2) for x, y, nx, ny, w in samples]
    right = [(x + nx * w / 2, y + ny * w / 2) for x, y, nx, ny, w in samples]

    ctx.new_path()
    ctx.move_to(*left[0])
    for point in left[1:]:
        ctx.line_to(*point)

    # The top edge is the near half of the stem's cut, bulging up with the
    # same perspective as the gill disk it meets.
    w_top = samples[-1][4]
    bulge = m["gill_depth"] * (w_top / 2) / m["cap_radius"] * 1.33
    ux, uy = math.sin(cap_angle) * bulge, -math.cos(cap_angle) * bulge
    ctx.curve_to(
        left[-1][0] + ux, left[-1][1] + uy,
        right[-1][0] + ux, right[-1][1] + uy,
        *right[-1],
    )

    for point in reversed(right[:-1]):
        ctx.line_to(*point)

    # rounded into the soil
    _, _, nx0, ny0, w0 = samples[0]
    dx, dy = -ny0 * w0 * 0.3, nx0 * w0 * 0.3
    ctx.curve_to(
        right[0][0] + dx, right[0][1] + dy,
        left[0][0] + dx, left[0][1] + dy,
        *left[0],
    )
    ctx.close_path()

def draw_stem(ctx, m, cap_angle):
    colors = m["colors"]
    samples = stem_samples(m)

    ctx.save()
    trace_stem(ctx, samples, m, cap_angle)

    # cylindrical shading, lit from the left
    x, y, nx, ny, w = samples[len(samples) // 2]
    body = cairo.LinearGradient(x - nx * w / 2, y - ny * w / 2, x + nx * w / 2, y + ny * w / 2)
    body.add_color_stop_rgb(0.0, *colors["stem"])
    body.add_color_stop_rgb(0.28, *colors["stem_light"])
    body.add_color_stop_rgb(0.62, *colors["stem"])
    body.add_color_stop_rgb(1.0, *colors["stem_dark"])
    ctx.set_source(body)
    ctx.fill_preserve()
    ctx.clip()

    # shadow under the cap
    tx, ty = samples[-1][:2]
    mx, my = samples[int(len(samples) * 0.68)][:2]
    under = cairo.LinearGradient(tx, ty, mx, my)
    dr, dg, db = colors["gill_dark"]
    under.add_color_stop_rgba(0.0, dr, dg, db, 0.80)
    under.add_color_stop_rgba(1.0, dr, dg, db, 0.0)
    ctx.set_source(under)
    ctx.paint()

    # long fibres running up the stem
    for k in range(m["fibers"]):
        side = random.uniform(-0.42, 0.42)
        start = random.randint(0, len(samples) // 3)
        end = random.randint(len(samples) * 2 // 3, len(samples) - 1)

        points = []
        for i in range(start, end + 1, 4):
            sx, sy, snx, sny, sw = samples[i]
            wander = side + 0.05 * noise.pnoise1(i * 0.15 + m["noise_offset"] + k * 7.3)
            points.append((sx + snx * sw * wander, sy + sny * sw * wander))

        if len(points) < 2:
            continue

        color = weighted_choice([(2.0, colors["stem_dark"]), (1.0, colors["stem_light"])])
        thickness = max(0.8, m["stem_width"] * random.uniform(0.01, 0.04))
        stroke_brush_paths(
            ctx,
            [polyline_to_path(points)],
            color,
            thickness,
            random.uniform(0.08, 0.22),
        )

    ctx.restore()

    if m["ring"] > 0:
        draw_stem_ring(ctx, m, samples)

def draw_stem_ring(ctx, m, samples):
    """The annulus: a small drooping skirt around the stem."""
    colors = m["colors"]
    x, y, nx, ny, w = samples[int(m["ring"] * (len(samples) - 1))]
    rw = w * 0.5 * 1.45
    droop = w * 0.45

    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(math.atan2(ny, nx))

    ctx.new_path()
    ctx.move_to(-rw, 0)
    ctx.curve_to(-rw * 0.95, droop * 1.15, rw * 0.95, droop * 1.15, rw, 0)
    ctx.curve_to(rw * 0.6, droop * 0.35, -rw * 0.6, droop * 0.35, -rw, 0)
    ctx.close_path()

    skirt = cairo.LinearGradient(-rw, 0, rw, 0)
    skirt.add_color_stop_rgb(0.0, *colors["stem"])
    skirt.add_color_stop_rgb(0.3, *colors["stem_light"])
    skirt.add_color_stop_rgb(1.0, *colors["stem_dark"])
    ctx.set_source(skirt)
    ctx.fill_preserve()

    ctx.set_source_rgba(*colors["stem_dark"], 0.5)
    ctx.set_line_width(max(0.8, w * 0.03))
    ctx.stroke()
    ctx.restore()

def draw_cap(ctx, m, cap_x, cap_y, cap_angle):
    colors = m["colors"]
    R, Hc = m["cap_radius"], m["cap_height"]
    top, bottom = cap_outline(m)

    ctx.save()
    ctx.translate(cap_x, cap_y)
    ctx.rotate(cap_angle)

    ctx.new_path()
    ctx.move_to(*top[0])
    for point in top[1:]:
        ctx.line_to(*point)
    for point in reversed(bottom):
        ctx.line_to(*point)
    ctx.close_path()

    # lit from the upper left
    body = cairo.RadialGradient(-R * 0.35, -Hc * 0.80, 0, -R * 0.15, -Hc * 0.45, max(R, Hc) * 1.5)
    body.add_color_stop_rgb(0.0, *colors["cap_light"])
    body.add_color_stop_rgb(0.40, *colors["cap"])
    body.add_color_stop_rgb(1.0, *colors["cap_dark"])
    ctx.set_source(body)
    ctx.fill_preserve()

    ctx.save()
    ctx.clip()

    # the margin falls into the shadow of the underside
    rim_y = max(y for _, y in bottom)
    margin = cairo.LinearGradient(0, -Hc * 0.45, 0, rim_y)
    dr, dg, db = colors["cap_dark"]
    margin.add_color_stop_rgba(0.0, dr, dg, db, 0.0)
    margin.add_color_stop_rgba(1.0, dr, dg, db, 0.55)
    ctx.set_source(margin)
    ctx.paint()

    draw_cap_streaks(ctx, m, top, bottom)
    draw_cap_spots(ctx, m, top, bottom)
    ctx.restore()

    # rim light along the upper left of the silhouette
    if m["rim_light"] > 0:
        rr, rg, rb = colors["rim"]
        rim = cairo.LinearGradient(-R, -Hc * 0.5, R * 0.5, 0)
        rim.add_color_stop_rgba(0.0, rr, rg, rb, m["rim_light"])
        rim.add_color_stop_rgba(1.0, rr, rg, rb, 0.0)

        trim = len(top) // 25
        ctx.new_path()
        ctx.move_to(*top[trim])
        for point in top[trim + 1:len(top) - trim]:
            ctx.line_to(*point)
        ctx.set_source(rim)
        ctx.set_line_width(max(1.0, R * 0.014))
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()

    ctx.restore()

def draw_cap_streaks(ctx, m, top, bottom):
    """Radial brush fibres running from the crown down to the margin."""
    colors = m["colors"]
    R = m["cap_radius"]

    for _ in range(m["streaks"]):
        phi = random.uniform(0.05, math.pi - 0.05)
        r_start = random.uniform(0.0, 0.35)
        r_end = random.uniform(0.85, 1.0)

        points = [
            cap_surface_point(top, bottom, lerp(r_start, r_end, i / 6), phi)
            for i in range(7)
        ]

        color = weighted_choice([
            (2.0, colors["cap_dark"]),
            (1.0, colors["cap_light"]),
            (0.6, colors["cap"]),
        ])
        stroke_brush_paths(
            ctx,
            [polyline_to_path(points)],
            color,
            R * random.uniform(0.008, 0.030),
            m["streak_alpha"] * random.uniform(0.4, 1.0),
        )

def draw_cap_spots(ctx, m, top, bottom):
    """Warts on the cap, foreshortened as they turn away from the viewer."""
    colors = m["colors"]
    R = m["cap_radius"]
    sr, sg, sb = colors["spot"]
    dr, dg, db = colors["cap_dark"]

    for _ in range(m["spots"]):
        r = math.sqrt(random.random()) * 0.88
        phi = random.uniform(0.10, 0.90) * math.pi
        x, y = cap_surface_point(top, bottom, r, phi)

        # Squashed near the sides, where the cap turns away, and near the
        # crown, where it faces up.
        size = R * random.uniform(*m["spot_size"]) * lerp(1.25, 0.75, r)
        rx = size * (0.30 + 0.70 * math.sin(phi))
        ry = size * random.uniform(0.75, 1.0) * lerp(0.45, 0.80, r)

        ctx.new_path()
        ellipse_path(ctx, x, y + ry * 0.25, rx, ry)
        ctx.set_source_rgba(dr, dg, db, 0.35)
        ctx.fill()

        ctx.save()
        ctx.translate(x, y)
        ctx.scale(rx, ry)
        wart = cairo.RadialGradient(-0.3, -0.35, 0.05, 0, 0, 1)
        wart.add_color_stop_rgba(0.0, *lerp_color(colors["spot"], (1, 1, 1), 0.3), 0.95)
        wart.add_color_stop_rgba(0.7, sr, sg, sb, 0.85)
        wart.add_color_stop_rgba(1.0, sr, sg, sb, 0.0)
        ctx.set_source(wart)
        ctx.new_path()
        ctx.arc(0, 0, 1, 0, 2 * math.pi)
        ctx.fill()
        ctx.restore()

def draw_mushroom(ctx, m, background=(0.0, 0.0, 0.0)):
    """Draw one mushroom dict from make_mushroom(): aura, gills, stem, cap."""
    cap_x, cap_y, cap_angle = cap_frame(m)

    if m["glow"] > 0:
        cx, cy = to_world(cap_x, cap_y, cap_angle, 0, -m["cap_height"] * 0.4)
        draw_gradient_blob(
            ctx,
            cx,
            cy,
            m["cap_radius"] * m["glow_size"],
            m["colors"]["glow"],
            inner_alpha=m["glow"],
            mid_alpha=m["glow"] * 0.35,
        )

    draw_contact_shadow(ctx, m, background)
    draw_gills(ctx, m, cap_x, cap_y, cap_angle)
    draw_stem(ctx, m, cap_angle)
    draw_cap(ctx, m, cap_x, cap_y, cap_angle)

# ==========================================================
# ENVIRONMENT LAYERS
# ==========================================================

def draw_glow_field(ctx, cfg, palette, mushrooms):
    """Soft colored masses hanging in the air around the caps."""
    W, H = cfg["width"], cfg["height"]
    glow_palette = palette["glow"]

    for _ in range(cfg["glow_count"]):
        if mushrooms:
            m = random.choice(mushrooms)
            x = m["x"] + random.gauss(0, m["cap_radius"] * 1.6)
            y = m["y"] - m["stem_height"] * random.uniform(0.3, 1.3)
            size = H * random.uniform(*cfg["glow_size"]) * (0.6 + 0.4 * m["depth"])
        else:
            x = random.uniform(0, W)
            y = random.uniform(0, H * cfg["ground_level"])
            size = H * random.uniform(*cfg["glow_size"])

        color = weighted_choice([
            (3.0, glow_palette[0]),
            (2.0, glow_palette[1]),
            (1.0, glow_palette[2]),
        ])
        inner = cfg["glow_alpha"] * random.uniform(0.5, 1.0)
        draw_gradient_blob(
            ctx,
            x,
            y,
            size,
            maybe_jitter_live(color, "glow"),
            inner_alpha=inner,
            mid_alpha=inner * 0.4,
        )

def air_flow_angle(x, y, cfg, noise_base, caps):
    s = cfg["air_noise_scale"] / unit(cfg)
    n = noise.pnoise2(x * s, y * s, octaves=3, base=noise_base + 2)
    angle = cfg["air_angle"] + n * cfg["air_noise_multiplier"]

    # curve around nearby caps (tangential flow)
    best, best_d = None, 1e9
    for cx, cy, radius in caps:
        d = distance(x, y, cx, cy) / radius
        if d < best_d:
            best, best_d = (cx, cy), d

    if best is not None and best_d < 1.0:
        tangent = math.atan2(y - best[1], x - best[0]) + math.pi / 2
        diff = (tangent - angle + math.pi) % (2 * math.pi) - math.pi
        angle += diff * (1.0 - best_d) * cfg["air_curve_strength"]

    return angle

def draw_air_currents(ctx, cfg, palette, mushrooms, noise_base):
    """render_engine style flow-field brushwork in the air around the caps."""
    W, H = cfg["width"], cfg["height"]
    ground_y = H * cfg["ground_level"]
    soil_top = ground_y - H * cfg["ground_band"] * 0.5

    caps = []
    for m in mushrooms:
        cap_x, cap_y, cap_angle = cap_frame(m)
        cx, cy = to_world(cap_x, cap_y, cap_angle, 0, -m["cap_height"] * 0.4)
        caps.append((cx, cy, m["cap_radius"] * cfg["air_curve_radius"]))

    threads = palette["mycelium"]
    glow = palette["glow"]
    k = unit(cfg)
    seg_lo, seg_hi = cfg["air_segment_length"]

    # Drawn into a group so the whole layer can fade out towards the ground.
    ctx.push_group()

    for _ in range(cfg["air_line_count"]):
        x = random.uniform(-0.05, 1.0) * W
        y = random.uniform(0, soil_top)

        color = weighted_choice([
            (3.0, threads[0]),
            (2.0, threads[1]),
            (1.2, glow[0]),
            (0.8, glow[1]),
            (0.4, threads[3]),
        ])

        path, _ = build_brush_geometry(
            x,
            y,
            cfg["air_segments"],
            (seg_lo * k, seg_hi * k),
            lambda px, py: air_flow_angle(px, py, cfg, noise_base, caps),
        )
        stroke_brush_paths(
            ctx,
            [path],
            maybe_jitter_live(color, "mycelium"),
            random.uniform(*cfg["air_thickness"]) * k,
            cfg["air_alpha"] * random.uniform(0.5, 1.0),
        )

    layer = ctx.pop_group()
    fade = cairo.LinearGradient(0, soil_top - H * 0.12, 0, soil_top)
    fade.add_color_stop_rgba(0.0, 0, 0, 0, 1.0)
    fade.add_color_stop_rgba(1.0, 0, 0, 0, 0.0)
    ctx.set_source(layer)
    ctx.mask(fade)

def draw_ground(ctx, cfg, palette):
    """Darker soil below the ground line, with a loose brushed horizon."""
    W, H = cfg["width"], cfg["height"]
    ground_y = H * cfg["ground_level"]
    band = H * cfg["ground_band"]
    soil_top = ground_y - band * 0.5

    dark = tuple(c * 0.35 for c in palette["background"])
    shade = cfg["ground_shade"]
    soil = cairo.LinearGradient(0, soil_top - H * 0.03, 0, H)
    soil.add_color_stop_rgba(0.0, *dark, 0.0)
    soil.add_color_stop_rgba(0.15, *dark, shade * 0.7)
    soil.add_color_stop_rgba(1.0, *dark, shade)
    ctx.set_source(soil)
    ctx.rectangle(0, soil_top - H * 0.03, W, H)
    ctx.fill()

    ground_colors = [palette["mycelium"][0], palette["mycelium"][1], palette["stems"][0]]
    k = unit(cfg)

    for _ in range(cfg["ground_strokes"]):
        x = random.uniform(-0.1, 0.9) * W
        y = ground_y + random.uniform(-0.5, 0.5) * band
        drift = random.uniform(-0.04, 0.04)

        path, _ = build_brush_geometry(
            x,
            y,
            random.randint(3, 6),
            (W * 0.015, W * 0.04),
            lambda px, py: drift + 0.12 * noise.pnoise2(px * 0.003 / k, py * 0.003 / k),
            curl=0.10,
        )
        stroke_brush_paths(
            ctx,
            [path],
            maybe_jitter_live(random.choice(ground_colors), "mycelium"),
            random.uniform(2.0, 6.0) * k,
            random.uniform(0.05, 0.13),
        )

    # loose dust along the floor
    for _ in range(int(W * 0.6)):
        x = random.uniform(0, W)
        y = ground_y + random.gauss(0, band * 0.35)
        r, g, b = maybe_jitter_live(random.choice(ground_colors), "mycelium")
        ctx.set_source_rgba(r, g, b, random.uniform(0.05, 0.20))
        ctx.arc(x, y, random.uniform(0.5, 1.8), 0, 2 * math.pi)
        ctx.fill()

def mycelium_flow_angle(x, y, cfg, noise_base):
    s = cfg["mycelium_noise_scale"] / unit(cfg)
    n = noise.pnoise2(x * s, y * s, octaves=3, base=noise_base)
    return cfg["mycelium_angle"] + n * cfg["mycelium_noise_multiplier"]

def choose_thread_color(palette, near_stem):
    threads = palette["mycelium"]
    accent = 1.6 if near_stem else 0.6
    color = weighted_choice([
        (3.0, threads[0]),
        (2.5, threads[1]),
        (accent, threads[2]),
        (accent * 0.6, threads[3]),
    ])
    return maybe_jitter_live(color, "mycelium")

def draw_mycelium(ctx, cfg, palette, mushrooms, noise_base):
    """Flow-field threads in the soil, with sagging links between stems."""
    W, H = cfg["width"], cfg["height"]
    ground_y = H * cfg["ground_level"]
    soil_top = ground_y - H * cfg["ground_band"] * 0.5

    ctx.save()
    ctx.rectangle(0, soil_top, W, H - soil_top)
    ctx.clip()

    def angle_at(x, y):
        return mycelium_flow_angle(x, y, cfg, noise_base)

    k = unit(cfg)
    seg_lo, seg_hi = cfg["mycelium_segment_length"]
    seg_lo, seg_hi = seg_lo * k, seg_hi * k

    for _ in range(cfg["mycelium_count"]):
        near_stem = bool(mushrooms) and random.random() < cfg["mycelium_from_bases"]
        if near_stem:
            m = random.choice(mushrooms)
            x = m["x"] + random.gauss(0, m["stem_width"] * 0.6)
            y = m["y"] + random.uniform(0, m["stem_width"] * 0.5)
        else:
            x = random.uniform(0, W)
            y = random.uniform(ground_y, ground_y + H * cfg["mycelium_depth"])

        color = choose_thread_color(palette, near_stem)
        thickness = random.uniform(*cfg["mycelium_thickness"]) * k

        path, branch_points = build_brush_geometry(
            x,
            y,
            cfg["mycelium_segments"],
            (seg_lo, seg_hi),
            angle_at,
            cfg["mycelium_branch_prob"],
            cfg["mycelium_curl"],
        )
        stroke_brush_paths(ctx, [path], color, thickness, cfg["mycelium_alpha"])

        for bx, by in branch_points:
            deviation = random.choice((-1, 1)) * random.uniform(0.4, 0.9)
            branch, _ = build_brush_geometry(
                bx,
                by,
                max(2, cfg["mycelium_segments"] // 2),
                (seg_lo * 0.5, seg_hi * 0.6),
                lambda px, py, dev=deviation: angle_at(px, py) + dev,
                curl=cfg["mycelium_curl"],
            )
            stroke_brush_paths(ctx, [branch], color, thickness * 0.55, cfg["mycelium_alpha"] * 0.8)

    draw_mycelium_links(ctx, cfg, palette, mushrooms)
    ctx.restore()

def draw_mycelium_links(ctx, cfg, palette, mushrooms):
    if len(mushrooms) < 2:
        return

    accents = palette["mycelium"][2:]
    k = unit(cfg)

    for _ in range(cfg["mycelium_links"]):
        a = random.choice(mushrooms)
        others = sorted(
            (m for m in mushrooms if m is not a),
            key=lambda m: distance(a["x"], a["y"], m["x"], m["y"]),
        )
        b = random.choice(others[:3])

        ax, ay = a["x"], a["y"] + a["stem_width"] * 0.3
        bx, by = b["x"], b["y"] + b["stem_width"] * 0.3
        sag = distance(ax, ay, bx, by) * random.uniform(*cfg["mycelium_link_sag"])
        color = maybe_jitter_live(random.choice(accents), "mycelium")

        # a few strands braided along the same route
        for _ in range(random.randint(2, 4)):
            s = sag * random.uniform(0.75, 1.25)
            j = sag * 0.25
            p0 = (ax + random.uniform(-6, 6) * k, ay)
            p1 = (lerp(ax, bx, 0.2) + random.uniform(-j, j), ay + s + random.uniform(-j, j))
            p2 = (lerp(ax, bx, 0.8) + random.uniform(-j, j), by + s + random.uniform(-j, j))
            p3 = (bx + random.uniform(-6, 6) * k, by)

            ctx.new_path()
            ctx.move_to(*p0)
            ctx.curve_to(*p1, *p2, *p3)
            ctx.set_source_rgba(*color, cfg["mycelium_link_alpha"] * random.uniform(0.4, 1.0))
            ctx.set_line_width(random.uniform(0.8, 2.6) * k)
            ctx.stroke()

        for _ in range(cfg["mycelium_nodes"]):
            nx, ny = bezier_point((ax, ay), (lerp(ax, bx, 0.2), ay + sag), (lerp(ax, bx, 0.8), by + sag), (bx, by), random.random())
            draw_gradient_blob(ctx, nx, ny, random.uniform(5, 14) * k, color, inner_alpha=0.45, mid_alpha=0.15)
            ctx.set_source_rgba(*color, 0.8)
            ctx.arc(nx, ny, random.uniform(0.8, 2.0) * k, 0, 2 * math.pi)
            ctx.fill()

def draw_spores(ctx, cfg, palette, mushrooms, noise_base):
    """Spores leaving the caps: falling from the gills, rising or drifting."""
    H = cfg["height"]
    mode = cfg["spore_mode"]
    base_angle = SPORE_DIRECTIONS[mode]

    spore_palette = palette["spores"]
    spread = H * cfg["spore_spread"]
    k = unit(cfg)

    for m in mushrooms:
        cap_x, cap_y, cap_angle = cap_frame(m)
        R, d = m["cap_radius"], m["gill_depth"]
        top, bottom = cap_outline(m)

        for _ in range(int(cfg["spore_count"] * m["scale"])):
            if mode == "rise":
                lx, ly = cap_surface_point(top, bottom, random.random(), random.uniform(0, math.pi))
            else:
                a = random.uniform(0, 2 * math.pi)
                r = math.sqrt(random.random())
                lx, ly = math.cos(a) * R * r, math.sin(a) * d * r
            x, y = to_world(cap_x, cap_y, cap_angle, lx, ly)

            travel = spread * random.random() ** 1.6
            for _ in range(4):
                angle = base_angle + 1.6 * noise.pnoise2(x * 0.002 / k, y * 0.002 / k, base=noise_base + 1)
                x += math.cos(angle) * travel / 4
                y += math.sin(angle) * travel / 4

            fade = 1.0 - 0.7 * travel / spread
            alpha = cfg["spore_alpha"] * random.uniform(0.3, 1.0) * fade * lerp(0.5, 1.0, m["depth"])
            radius = random.uniform(0.5, 2.0) * (0.6 + 0.4 * min(1.0, m["scale"])) * k

            color = maybe_jitter_live(
                weighted_choice([(3.0, spore_palette[0]), (1.5, spore_palette[1]), (1.0, spore_palette[2])]),
                "spore",
            )

            if random.random() < 0.08:
                draw_gradient_blob(ctx, x, y, radius * 5, color, inner_alpha=alpha * 0.5, mid_alpha=alpha * 0.15)

            ctx.set_source_rgba(*color, alpha)
            ctx.arc(x, y, radius, 0, 2 * math.pi)
            ctx.fill()

def draw_general_particles(ctx, cfg, palette):
    W, H = cfg["width"], cfg["height"]
    spore_palette = palette["spores"]
    accents = palette["mycelium"][2:]

    for _ in range(cfg["particle_count"]):
        x = random.uniform(0, W)
        y = random.uniform(0, H)

        if random.random() < 0.18:
            r, g, b = maybe_jitter_live(random.choice(accents), "mycelium")
        else:
            r, g, b = maybe_jitter_live(random.choice(spore_palette), "spore")

        ctx.set_source_rgba(r, g, b, random.uniform(0.02, 0.12))
        ctx.arc(x, y, random.uniform(0.5, 1.6), 0, 2 * math.pi)
        ctx.fill()

# ==========================================================
# RENDER
# ==========================================================

def draw_scene(ctx, cfg, palette):
    """
    Draw every layer of a scene onto ctx and return the mushrooms placed.
    Seed `random` first for repeatable results.
    """
    noise_base = random.randint(0, 200)

    draw_background(ctx, cfg, palette)

    mushrooms = [
        make_mushroom(cfg, palette, x, y, depth, lerp(cfg["depth_scale_min"], 1.0, depth) * size * random.uniform(*cfg["size_variation"]))
        for x, y, depth, size in place_mushrooms(cfg)
    ]

    # 1) atmosphere behind everything
    draw_glow_field(ctx, cfg, palette, mushrooms)
    draw_air_currents(ctx, cfg, palette, mushrooms, noise_base)

    # 2) soil and the network inside it
    draw_ground(ctx, cfg, palette)
    draw_mycelium(ctx, cfg, palette, mushrooms, noise_base)

    # 3) the mushrooms, back to front
    for m in mushrooms:
        draw_mushroom(ctx, m, palette["background"])

    # 4) foreground air
    draw_spores(ctx, cfg, palette, mushrooms, noise_base)
    draw_general_particles(ctx, cfg, palette)

    return mushrooms

def save_surface(surface, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    surface.write_to_png(str(output_path))
    surface.finish()
    print(f"Saved {output_path}")
    return output_path

def render_scene(
    scene,
    palette,
    geometry_seed=BASE_SEED,
    color_seed=None,
    variant_index=1,
    output_name=None,
    save_dir=None,
):
    """
    Render one scene/palette/color-variation combination to a PNG.

    scene is a name from SCENES or a config dict (see make_scene). palette
    is a name from PALETTE_PRESETS or a palette dict with the same roles.
    geometry_seed controls composition. color_seed mutates the palette.
    Returns the path of the saved image.
    """
    cfg = make_scene(scene)
    palette_name = palette if isinstance(palette, str) else "custom"

    print(f"Rendering: {cfg['name']} / {palette_name} / v{variant_index:02d}")

    palette = resolve_palette(palette, variant_index, color_seed)

    hue_degrees = palette.get("cap_hue_shift", 0.0) * 360.0
    print(f"  cap hue rotation: {hue_degrees:+.1f}°")

    random.seed(geometry_seed)

    surface, ctx = create_surface(cfg)
    draw_scene(ctx, cfg, palette)

    if output_name is None:
        output_name = f"{cfg['name']}__{palette_name}__v{variant_index:02d}.png"

    return save_surface(surface, Path(save_dir or SAVE_DIR) / output_name)


def render_batch(scene_names=None, palette_names=None, variations=None, save_dir=None):
    """Render scenes × palettes × color variations. None means all of them."""
    scene_names = validate_selection(scene_names, SCENES.keys(), "scene names")
    palette_names = validate_selection(palette_names, PALETTE_PRESETS.keys(), "palette names")
    if variations is None:
        variations = PALETTE_VARIATIONS_PER_PRESET

    total = len(scene_names) * len(palette_names) * variations
    print(
        f"Rendering {len(scene_names)} scenes × "
        f"{len(palette_names)} palettes × "
        f"{variations} color variations = "
        f"{total} images"
    )

    i = 0

    for scene_index, scene_name in enumerate(scene_names):
        base_geometry_seed = BASE_SEED + scene_index * 1000

        for palette_index, palette_name in enumerate(palette_names):
            for variation_index in range(variations):
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
                    palette_name,
                    geometry_seed=geometry_seed,
                    color_seed=color_seed,
                    variant_index=variation_index + 1,
                    save_dir=save_dir,
                )

                i += 1
                print(f"Progress: {i}/{total} images rendered\n")

# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":
    render_batch(RENDER_SCENE_NAMES, RENDER_PALETTE_NAMES)
