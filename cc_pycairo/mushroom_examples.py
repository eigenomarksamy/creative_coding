"""
Examples of driving mushroom_engine.py from another script.

Run from the repository root:
    python cc_pycairo/mushroom_examples.py

Each example is a function, comment out the calls at the bottom to run
only some of them. Everything is written to cc_pycairo/gen/mushroom_examples.
"""

import copy
import random
from pathlib import Path

import mushroom_engine as me

OUTPUT_DIR = Path(__file__).resolve().parent / "gen" / "mushroom_examples"

# ==========================================================
# 1. A PRESET, AS IS
# ==========================================================

def preset_scene():
    """One scene preset in one palette preset. geometry_seed picks the layout."""
    me.render_scene(
        "fairy_ring_at_dusk",
        "amanita_night",
        geometry_seed=3,
        save_dir=OUTPUT_DIR,
    )

# ==========================================================
# 2. A PRESET, TUNED
# ==========================================================

def tuned_scene():
    """
    Start from a preset and override any key of DEFAULT_SCENE. Unknown keys
    raise, so a typo will not silently do nothing.
    """
    cfg = me.make_scene(
        "the_quiet_colony",
        name="crowded_colony",
        mushroom_count=34,
        cluster_count=4,
        cluster_spread=0.05,
        cap_profiles={"conical": 2.0, "bell": 1.0, "umbonate": 1.0},
        cap_wobble=0.12,
        stem_lean=0.35,
        spore_mode="rise",
        spore_count=220,
        air_line_count=320,
        air_angle=-1.2,           # currents rise up and to the right
    )
    me.render_scene(cfg, "violet_mycelium", geometry_seed=12, save_dir=OUTPUT_DIR)

# ==========================================================
# 3. A CUSTOM PALETTE
# ==========================================================

def custom_palette():
    """
    A palette is a dict with a background and the roles in PALETTE_ROLES.
    Here one preset is copied and its caps and glow are swapped for moss.
    """
    moss = copy.deepcopy(me.PALETTE_PRESETS["spore_print"])
    moss["caps"] = [
        (0.10, 0.16, 0.06),
        (0.20, 0.30, 0.10),
        (0.34, 0.46, 0.16),
        (0.56, 0.66, 0.30),
        (0.86, 0.90, 0.66),
    ]
    moss["glow"] = [
        (0.20, 0.32, 0.08),
        (0.40, 0.52, 0.16),
        (0.62, 0.50, 0.18),
    ]

    cfg = me.make_scene("forest_floor_choir", name="moss_choir")

    # Three color variations of the same composition: v01 is the palette as
    # written, later ones rotate the cap hue (see CAP_BASE_HUE_SHIFT_*).
    for variant in (1, 2, 3):
        me.render_scene(
            cfg,
            moss,
            geometry_seed=5,
            color_seed=500 + variant,
            variant_index=variant,
            output_name=f"moss_choir__v{variant:02d}.png",
            save_dir=OUTPUT_DIR,
        )

# ==========================================================
# 4. A PARAMETER SWEEP
# ==========================================================

def profile_sweep():
    """
    Hold the seed still and change one thing: every cap profile on the
    same layout, on a smaller canvas so the series renders quickly.
    """
    for profile in me.CAP_PROFILES:
        cfg = me.make_scene(
            "forest_floor_choir",
            name=f"profile_{profile}",
            width=1400,
            height=800,
            mushroom_count=7,
            cap_profiles={profile: 1.0},
            spot_prob=0.5,
        )
        me.render_scene(cfg, "bioluminescent_hollow", geometry_seed=21, save_dir=OUTPUT_DIR)

# ==========================================================
# 5. A HAND-COMPOSED DRAWING
# ==========================================================

def hand_composed():
    """
    Skip the layout and place every mushroom yourself. The scene config
    still provides the defaults for anything not set by hand, and every
    layer of the engine is a function that draws onto your own context.
    """
    random.seed(11)

    cfg = me.make_scene(
        name="ember_trio",
        width=2000,
        height=2000,
        ground_level=0.76,
        air_line_count=180,
        air_angle=-0.5,
        mycelium_links=6,
    )
    palette = me.resolve_palette("ash_and_ember")
    W, H = cfg["width"], cfg["height"]
    ground_y = H * cfg["ground_level"]

    # Any key of the mushroom dict can be set here. Sizes are in pixels,
    # scale multiplies everything rolled from the config.
    trio = [
        me.make_mushroom(cfg, palette, W * 0.32, ground_y - 30, depth=0.6, scale=1.2,
                         profile="bell", stem_lean=-0.18, stem_bend=0.08),
        me.make_mushroom(cfg, palette, W * 0.52, ground_y + 20, depth=1.0, scale=2.0,
                         profile="dome", spots=26, ring=0.78, bulb=0.5, cap_tilt=-0.05),
        me.make_mushroom(cfg, palette, W * 0.71, ground_y - 10, depth=0.8, scale=1.3,
                         profile="conical", stem_lean=0.22,
                         colors={
                             "cap": (0.62, 0.20, 0.06),
                             "cap_dark": (0.22, 0.06, 0.02),
                             "cap_light": (0.98, 0.62, 0.30),
                         }),
    ]
    # A few small ones at the foot of the big one.
    for dx in (-0.08, -0.05, 0.06):
        trio.append(me.make_mushroom(cfg, palette, W * (0.52 + dx), ground_y + 40,
                                     depth=1.0, scale=0.35, profile="umbonate"))

    # Painter's order: back to front.
    trio.sort(key=lambda m: m["y"])
    noise_base = 9

    surface, ctx = me.create_surface(cfg)
    me.draw_background(ctx, cfg, palette)
    me.draw_glow_field(ctx, cfg, palette, trio)
    me.draw_air_currents(ctx, cfg, palette, trio, noise_base)
    me.draw_ground(ctx, cfg, palette)
    me.draw_mycelium(ctx, cfg, palette, trio, noise_base)

    for m in trio:
        me.draw_mushroom(ctx, m, palette["background"])

    me.draw_spores(ctx, cfg, palette, trio, noise_base)
    me.draw_general_particles(ctx, cfg, palette)

    me.save_surface(surface, OUTPUT_DIR / "ember_trio.png")

# ==========================================================
# 6. A BATCH
# ==========================================================

def small_batch():
    """
    Scenes × palettes × color variations, like running mushroom_engine.py
    directly. Module-level switches work from here too.
    """
    me.RANDOMIZE_CAP_BASE_HUE = False      # variations only jitter, no hue rotation
    try:
        me.render_batch(
            ["solitary_specimen"],
            ["spore_print", "bioluminescent_hollow"],
            variations=2,
            save_dir=OUTPUT_DIR / "batch",
        )
    finally:
        me.RANDOMIZE_CAP_BASE_HUE = True


if __name__ == "__main__":
    preset_scene()
    tuned_scene()
    custom_palette()
    profile_sweep()
    hand_composed()
    small_batch()
