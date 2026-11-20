"""
The seven levels' shared drawing kit (dev_plan.md §4.2.1, SL3).

It began with what the cosmos scripts already repeat: a glow, a color mix,
luminous lines, marching-squares contours, the dark background and the
vignette. Every image script imports it by name, run from the repository
root, as `python cc_pycairo/<stem>.py`:

    from seven_levels_kit import background, glow, luminous, vignette

Each drawing function takes the cairo context first and leaves its operator
as it found it. Randomness comes from the `rng` the script passes, the
seeded `random` module by default, so an image depends only on its own SEED.

The kit is additive once the pilot is signed off: a helper may be added,
but changing one changes every image that uses it, which needs a re-render
and a review of all of them. A helper joins at its second use: `rk4`,
`axes`, `blur` and `raster` joined with the chaos track (SL4).
"""

import math
import random

import cairo


def mix(a, b, t):
    """The color t of the way from a to b, as an (r, g, b) tuple."""
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def glow(ctx, x, y, radius, color, alpha):
    """A soft radial light: bright at the centre, gone at the radius."""
    r, g, b = color
    pat = cairo.RadialGradient(x, y, 0, x, y, radius)
    pat.add_color_stop_rgba(0.0, r, g, b, alpha)
    pat.add_color_stop_rgba(0.25, r, g, b, alpha * 0.3)
    pat.add_color_stop_rgba(1.0, r, g, b, 0.0)
    ctx.set_source(pat)
    ctx.arc(x, y, radius, 0, 2 * math.pi)
    ctx.fill()


def polyline(ctx, paths, color, alpha, width):
    """
    Stroke a list of paths, each a list of (x, y) points, as one stroke.

    One stroke covers every pixel once, so paths that touch or cross
    don't brighten where they meet, even under OPERATOR_ADD.
    """
    ctx.set_line_width(width)
    ctx.set_source_rgba(*color, alpha)
    for points in paths:
        if len(points) < 2:
            continue
        ctx.move_to(*points[0])
        for p in points[1:]:
            ctx.line_to(*p)
    ctx.stroke()


def luminous(ctx, paths, color, alpha, width):
    """A line with a halo: a wide faint stroke, a middle one, then the core."""
    polyline(ctx, paths, color, alpha * 0.08, width * 6)
    polyline(ctx, paths, color, alpha * 0.25, width * 2.5)
    polyline(ctx, paths, color, alpha, width)


def contour(field, level, cell, x0=0.0, y0=0.0):
    """
    Marching squares over a grid of values, field[row][column], which may
    be nested lists or a 2D numpy array. Returns the level's crossing as
    a list of segments, [(x, y), (x, y)] each, with grid point (i, j) at
    (x0 + i * cell, y0 + j * cell). Draw them with polyline or luminous.
    """
    rows = len(field)
    cols = len(field[0])
    segments = []

    def lerp(a, b, va, vb):
        return a + (b - a) * (level - va) / (vb - va)

    for j in range(rows - 1):
        ya, yb = y0 + j * cell, y0 + (j + 1) * cell
        row0, row1 = field[j], field[j + 1]
        for i in range(cols - 1):
            a, b, c, d = float(row0[i]), float(row0[i + 1]), float(row1[i + 1]), float(row1[i])
            above = (a > level, b > level, c > level, d > level)
            if all(above) or not any(above):
                continue
            xa, xb = x0 + i * cell, x0 + (i + 1) * cell
            points = []
            if above[0] != above[1]:
                points.append((lerp(xa, xb, a, b), ya))
            if above[1] != above[2]:
                points.append((xb, lerp(ya, yb, b, c)))
            if above[2] != above[3]:
                points.append((lerp(xb, xa, c, d), yb))
            if above[3] != above[0]:
                points.append((xa, lerp(yb, ya, d, a)))
            for k in range(0, len(points) - 1, 2):
                segments.append([points[k], points[k + 1]])
    return segments


def rk4(f, state, h):
    """
    One classic fourth-order Runge-Kutta step of ds/dt = f(s) from state.

    The state is anything that adds and scales like a vector, such as a
    numpy array, which may hold a whole ensemble: one row per member.
    """
    k1 = f(state)
    k2 = f(state + h / 2 * k1)
    k3 = f(state + h / 2 * k2)
    k4 = f(state + h * k3)
    return state + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


def axes(ctx, screen, x_range, y_range, step, color, alpha, tick=7):
    """
    A phase-plane frame: the two axes through the origin across the given
    ranges, in model units, with a short tick every `step` along each.
    `screen` maps a model point (x, y) to pixels.
    """
    (x0, x1), (y0, y1) = x_range, y_range
    lines = [[screen((x0, 0.0)), screen((x1, 0.0))], [screen((0.0, y0)), screen((0.0, y1))]]
    for lo, hi, along_x in ((x0, x1, True), (y0, y1, False)):
        k = math.ceil(lo / step)
        while k * step <= hi:
            if k:
                px, py = screen((k * step, 0.0) if along_x else (0.0, k * step))
                if along_x:
                    lines.append([(px, py - tick), (px, py + tick)])
                else:
                    lines.append([(px - tick, py), (px + tick, py)])
            k += 1
    polyline(ctx, lines, color, alpha, 1.0)


def blur(field, sigma):
    """
    A gaussian blur of a 2D numpy array by FFT, sigma in cells. The weights
    sum to one, so the total is kept, and the edges wrap, so keep anything
    that matters well inside the array.
    """
    import numpy as np

    ky = np.fft.fftfreq(field.shape[0])[:, None]
    kx = np.fft.rfftfreq(field.shape[1])[None, :]
    gain = np.exp(-2 * (math.pi * sigma) ** 2 * (kx ** 2 + ky ** 2))
    return np.maximum(np.fft.irfft2(np.fft.rfft2(field) * gain, s=field.shape), 0.0)


def raster(ctx, light, x0=0.0, y0=0.0, cell=1.0):
    """
    Paint a computed image, light[row][column] = (r, g, b) in 0..1, a numpy
    array, with its top-left corner at (x0, y0) and each value `cell`
    pixels wide, under the current operator, OPERATOR_ADD in every image.

    For pictures made of many faint marks, such as a density: cairo rounds
    a very faint stroke to nothing, so the marks are summed in numpy and
    painted once.
    """
    import numpy as np

    rows, cols = light.shape[:2]
    rgb = np.clip(light, 0.0, 1.0)
    pixels = np.zeros((rows, cols, 4), dtype=np.uint8)
    # cairo's ARGB32 is premultiplied and stored B, G, R, A on little-endian machines
    pixels[..., 0] = np.round(rgb[..., 2] * 255)
    pixels[..., 1] = np.round(rgb[..., 1] * 255)
    pixels[..., 2] = np.round(rgb[..., 0] * 255)
    pixels[..., 3] = pixels[..., :3].max(axis=2)
    image = cairo.ImageSurface(cairo.FORMAT_ARGB32, cols, rows)
    stride = image.get_stride()
    data = image.get_data()
    for j in range(rows):
        data[j * stride:j * stride + cols * 4] = pixels[j].tobytes()
    image.mark_dirty()

    ctx.save()
    ctx.translate(x0, y0)
    ctx.scale(cell, cell)
    ctx.set_source_surface(image, 0, 0)
    ctx.get_source().set_filter(cairo.FILTER_GOOD if cell != 1.0 else cairo.FILTER_NEAREST)
    ctx.paint()
    ctx.restore()


def background(ctx, width, height, color, cx=None, cy=None, rng=random):
    """
    The shared ground: near-black tinted by the accent, a little lighter
    around (cx, cy), the centre by default, and a fine dust of specks.
    """
    cx = width / 2 if cx is None else cx
    cy = height / 2 if cy is None else cy
    reach = math.hypot(width, height) / 2 * 1.06

    bg = cairo.RadialGradient(cx, cy, 0, cx, cy, reach)
    bg.add_color_stop_rgb(0.0, *(c * 0.10 for c in color))
    bg.add_color_stop_rgb(0.5, *(c * 0.040 for c in color))
    bg.add_color_stop_rgb(1.0, *(c * 0.015 for c in color))
    ctx.save()
    ctx.set_operator(cairo.OPERATOR_OVER)
    ctx.set_source(bg)
    ctx.paint()

    dust = mix(color, (1.0, 1.0, 1.0), 0.5)
    for _ in range(int(width * height / 270)):
        x = rng.uniform(0, width)
        y = rng.uniform(0, height)
        ctx.set_source_rgba(*dust, rng.uniform(0.02, 0.06))
        ctx.arc(x, y, rng.uniform(0.4, 1.1), 0, 2 * math.pi)
        ctx.fill()
    ctx.restore()


def vignette(ctx, width, height, cx=None, cy=None, alpha=0.6):
    """Darken the corners, the last thing drawn."""
    cx = width / 2 if cx is None else cx
    cy = height / 2 if cy is None else cy
    half = math.hypot(width, height) / 2

    pat = cairo.RadialGradient(cx, cy, half * 0.45, cx, cy, half * 1.06)
    pat.add_color_stop_rgba(0.0, 0, 0, 0, 0.0)
    pat.add_color_stop_rgba(1.0, 0, 0, 0, alpha)
    ctx.save()
    ctx.set_operator(cairo.OPERATOR_OVER)
    ctx.set_source(pat)
    ctx.rectangle(0, 0, width, height)
    ctx.fill()
    ctx.restore()
