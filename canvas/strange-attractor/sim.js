// Strange attractor simulation: the Lorenz system on a fixed time step.
//
// Numbers only, no canvas and no DOM, so `node --test` can check all of it.
// A classic script, not a module, because the gallery has to work from
// file://: the browser gets the global StrangeAttractor and node gets
// module.exports.
//
// The state uses only + - * / and integer operations, which give the same
// bits in every browser, so a seed and parameters reproduce a trajectory
// exactly. Math.sin, Math.log and friends can differ between browsers, so
// they stay out of anything that feeds the state.

(function (root) {
    'use strict';

    // Fixed step of the integrator, in the system's own time units
    const DT = 0.005;

    // How far the orbit behind fitBounds runs: 60 time units
    const PROBE_STEPS = 12000;

    // Half the smallest view, so a system that settles doesn't zoom to a point
    const MIN_HALF_EXTENT = 2;

    // Every parameter has a default and a range, and clampParams enforces them
    const PARAMS = {
        rho: { default: 28, min: 0, max: 200, step: 0.1, label: 'ρ heat' },
        sigma: { default: 10, min: 0.1, max: 30, step: 0.1, label: 'σ viscosity' },
        beta: { default: 8 / 3, min: 0.1, max: 8, step: 0.01, label: 'β geometry' },
        spread: { default: 0.01, min: 0.000001, max: 1, log: true, label: 'starting gap' },
        tracers: { default: 24, min: 2, max: 64, step: 1, integer: true, label: 'paths' },
        speed: { default: 240, min: 30, max: 960, step: 10, label: 'steps per second' },
        seed: { default: 1, min: 0, max: 4294967295, step: 1, integer: true, label: 'seed' },
    };

    // Named parameter sets. A preset leaves out what it doesn't care about,
    // so the visitor's seed and number of paths survive a change of preset.
    // Fading chaos keeps a seed of its own: at this heat about half of all
    // starts fall straight to rest without wandering at all.
    const PRESETS = [
        {
            id: 'butterfly',
            label: 'butterfly',
            note: 'chaos: paths that start together end up anywhere',
            params: { rho: 28, sigma: 10, beta: 8 / 3, spread: 0.01, speed: 240 },
        },
        {
            id: 'settling',
            label: 'settling',
            note: 'too little heat for chaos: every path comes to rest',
            params: { rho: 15, sigma: 10, beta: 8 / 3, spread: 1, speed: 240 },
        },
        {
            id: 'fading-chaos',
            label: 'fading chaos',
            note: 'chaos that runs out: paths wander, then each settles on one of two points',
            params: { rho: 22, sigma: 10, beta: 8 / 3, spread: 0.05, speed: 480, seed: 59 },
        },
        {
            id: 'closed-loops',
            label: 'closed loops',
            note: 'order past the chaos: every path falls onto one of two mirrored loops',
            params: { rho: 100, sigma: 10, beta: 8 / 3, spread: 0.5, speed: 240 },
        },
    ];

    // Small seeded generator, the same in every browser: mulberry32
    function mulberry32(seed) {
        let a = seed >>> 0;
        return function next() {
            a = (a + 0x6d2b79f5) | 0;
            let t = Math.imul(a ^ (a >>> 15), 1 | a);
            t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
            return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
        };
    }

    // Geometry and color draw from separate streams of one seed, an idea from
    // render_engine.py: a change to the colors never moves a trajectory
    const GEOMETRY_STREAM = 0x9e3779b9;
    const COLOR_STREAM = 0x85ebca77;

    function streamSeed(seed, stream) {
        let h = Math.imul((seed ^ stream) >>> 0, 0x9e3779b1);
        h = Math.imul(h ^ (h >>> 16), 0x85ebca6b);
        return (h ^ (h >>> 13)) >>> 0;
    }

    function defaults() {
        const params = {};
        for (const key of Object.keys(PARAMS)) {
            params[key] = PARAMS[key].default;
        }
        return params;
    }

    // A complete, valid parameter set from any input: missing or non-numeric
    // values take their default, the rest are held to their range
    function clampParams(input) {
        const source = input || {};
        const params = {};
        for (const key of Object.keys(PARAMS)) {
            const spec = PARAMS[key];
            const raw = source[key];
            const value = typeof raw === 'string' && raw.trim() !== '' ? Number(raw) : raw;
            if (typeof value !== 'number' || !Number.isFinite(value)) {
                params[key] = spec.default;
                continue;
            }
            const held = Math.min(spec.max, Math.max(spec.min, value));
            params[key] = spec.integer ? Math.round(held) : held;
        }
        return params;
    }

    // One classical Runge-Kutta step of the point at positions[i..i+2]
    function rk4Step(positions, i, sigma, rho, beta, dt) {
        const x = positions[i];
        const y = positions[i + 1];
        const z = positions[i + 2];
        const half = dt / 2;

        const ax = sigma * (y - x);
        const ay = x * (rho - z) - y;
        const az = x * y - beta * z;

        const bx0 = x + half * ax;
        const by0 = y + half * ay;
        const bz0 = z + half * az;
        const bx = sigma * (by0 - bx0);
        const by = bx0 * (rho - bz0) - by0;
        const bz = bx0 * by0 - beta * bz0;

        const cx0 = x + half * bx;
        const cy0 = y + half * by;
        const cz0 = z + half * bz;
        const cx = sigma * (cy0 - cx0);
        const cy = cx0 * (rho - cz0) - cy0;
        const cz = cx0 * cy0 - beta * cz0;

        const dx0 = x + dt * cx;
        const dy0 = y + dt * cy;
        const dz0 = z + dt * cz;
        const dx = sigma * (dy0 - dx0);
        const dy = dx0 * (rho - dz0) - dy0;
        const dz = dx0 * dy0 - beta * dz0;

        const sixth = dt / 6;
        positions[i] = x + sixth * (ax + 2 * bx + 2 * cx + dx);
        positions[i + 1] = y + sixth * (ay + 2 * by + 2 * cy + dy);
        positions[i + 2] = z + sixth * (az + 2 * bz + 2 * cz + dz);
    }

    // The initial state for a seed and parameters: a bundle of paths around
    // one starting point, each a tiny seeded offset away from it. Offsets are
    // drawn by rejection from a cube rather than with sin and log, and each
    // path's offset doesn't depend on how many paths there are.
    function createState(input) {
        const params = clampParams(input);
        const random = mulberry32(streamSeed(params.seed, GEOMETRY_STREAM));
        const rho = params.rho;

        const origin = [
            (2 * random() - 1) * 0.4 * rho,
            (2 * random() - 1) * 0.4 * rho,
            (0.6 + 0.6 * random()) * rho,
        ];

        const count = params.tracers;
        const offsets = new Float64Array(count * 3);
        for (let i = 0; i < offsets.length; i += 3) {
            let x, y, z;
            do {
                x = 2 * random() - 1;
                y = 2 * random() - 1;
                z = 2 * random() - 1;
            } while (x * x + y * y + z * z > 1);
            offsets[i] = x;
            offsets[i + 1] = y;
            offsets[i + 2] = z;
        }

        const state = {
            count,
            origin,
            offsets,
            positions: new Float64Array(count * 3),
            steps: 0,
        };
        release(state, params, origin[0], origin[1], origin[2]);
        return state;
    }

    // Send every path back to a tight bundle around a point. Time restarts,
    // because the interesting clock is the one since the paths were together.
    function release(state, params, x, y, z) {
        const { offsets, positions } = state;
        const spread = params.spread;
        for (let i = 0; i < positions.length; i += 3) {
            positions[i] = x + offsets[i] * spread;
            positions[i + 1] = y + offsets[i + 1] * spread;
            positions[i + 2] = z + offsets[i + 2] * spread;
        }
        state.steps = 0;
    }

    // Move every path forward. The result depends only on the number of
    // steps, never on how they're batched into frames.
    function advance(state, params, steps) {
        const { sigma, rho, beta } = params;
        const positions = state.positions;
        for (let s = 0; s < steps; s++) {
            for (let i = 0; i < positions.length; i += 3) {
                rk4Step(positions, i, sigma, rho, beta, DT);
            }
        }
        state.steps += steps;
    }

    // How far apart the paths are: the root mean square distance from their
    // center. For the readout, so it may use Math.sqrt.
    function separation(state) {
        const { count, positions } = state;
        let mx = 0;
        let my = 0;
        let mz = 0;
        for (let i = 0; i < positions.length; i += 3) {
            mx += positions[i];
            my += positions[i + 1];
            mz += positions[i + 2];
        }
        mx /= count;
        my /= count;
        mz /= count;

        let sum = 0;
        for (let i = 0; i < positions.length; i += 3) {
            const dx = positions[i] - mx;
            const dy = positions[i + 1] - my;
            const dz = positions[i + 2] - mz;
            sum += dx * dx + dy * dy + dz * dz;
        }
        return Math.sqrt(sum / count);
    }

    // The speed of the fastest path, in units per unit of time: zero only
    // when every path sits on a rest point. For the page to tell when the
    // picture has stopped changing, so it may use Math.sqrt. A path that
    // has become NaN gives NaN, which never counts as at rest.
    function fastest(state, params) {
        const { sigma, rho, beta } = params;
        const positions = state.positions;
        let most = 0;
        for (let i = 0; i < positions.length; i += 3) {
            const x = positions[i];
            const y = positions[i + 1];
            const z = positions[i + 2];
            const dx = sigma * (y - x);
            const dy = x * (rho - z) - y;
            const dz = x * y - beta * z;
            most = Math.max(most, dx * dx + dy * dy + dz * dz);
        }
        return Math.sqrt(most);
    }

    // Follow one orbit from a start point, for the page to fit its view and
    // draw the shape behind the live paths. path holds x, z pairs, one for
    // every `stride` steps; the bounds cover every step.
    function probeOrbit(input, start, stride) {
        const { sigma, rho, beta } = clampParams(input);
        const every = stride || 4;
        const point = Float64Array.from(start);
        const path = new Float32Array(Math.floor(PROBE_STEPS / every) * 2);

        let minX = point[0];
        let maxX = point[0];
        let minZ = point[2];
        let maxZ = point[2];
        let filled = 0;

        for (let s = 1; s <= PROBE_STEPS; s++) {
            rk4Step(point, 0, sigma, rho, beta, DT);
            minX = Math.min(minX, point[0]);
            maxX = Math.max(maxX, point[0]);
            minZ = Math.min(minZ, point[2]);
            maxZ = Math.max(maxZ, point[2]);
            if (s % every === 0) {
                path[filled++] = point[0];
                path[filled++] = point[2];
            }
        }

        const centerX = (minX + maxX) / 2;
        const centerZ = (minZ + maxZ) / 2;
        const halfX = Math.max((maxX - minX) / 2, MIN_HALF_EXTENT);
        const halfZ = Math.max((maxZ - minZ) / 2, MIN_HALF_EXTENT);

        return {
            path,
            bounds: {
                minX: centerX - halfX,
                maxX: centerX + halfX,
                minZ: centerZ - halfZ,
                maxZ: centerZ + halfZ,
            },
        };
    }

    // One color per path, as hue, saturation and lightness: an arc of nearby
    // hues, so paths that are still together read as one bright thread
    function palette(seed, count) {
        const random = mulberry32(streamSeed(seed, COLOR_STREAM));
        const start = random() * 360;
        const arc = 110 + random() * 80;
        const colors = [];
        for (let i = 0; i < count; i++) {
            const along = count > 1 ? i / (count - 1) : 0;
            colors.push({
                h: (start + arc * along) % 360,
                s: 70 + random() * 20,
                l: 58 + random() * 10,
            });
        }
        return colors;
    }

    const api = {
        DT,
        PARAMS,
        PRESETS,
        advance,
        clampParams,
        createState,
        defaults,
        fastest,
        mulberry32,
        palette,
        probeOrbit,
        release,
        rk4Step,
        separation,
        streamSeed,
    };

    if (typeof module !== 'undefined' && module.exports) {
        module.exports = api;
    } else {
        root.StrangeAttractor = api;
    }
})(typeof globalThis !== 'undefined' ? globalThis : this);
