// Run from the repository root with: node --test
const test = require('node:test');
const assert = require('node:assert/strict');

const {
    DT,
    PARAMS,
    PRESETS,
    advance,
    clampParams,
    createState,
    defaults,
    mulberry32,
    palette,
    probeOrbit,
    release,
    rk4Step,
    separation,
    streamSeed,
} = require('./sim.js');

const presetParams = (id, extra) => {
    const preset = PRESETS.find((candidate) => candidate.id === id);
    return clampParams({ ...defaults(), ...preset.params, ...extra });
};

// Largest Lyapunov exponent: follow an orbit and a shadow a tiny step away,
// and average how fast the gap grows, shrinking it back every few steps
function lyapunov(params) {
    const { sigma, rho, beta } = params;
    const orbit = Float64Array.from(createState(params).origin);
    for (let i = 0; i < 40000; i++) {
        rk4Step(orbit, 0, sigma, rho, beta, DT);
    }

    const gap = 1e-8;
    const shadow = Float64Array.of(orbit[0] + gap, orbit[1], orbit[2]);
    const rounds = 6000;
    const stepsPerRound = 20;
    let total = 0;

    for (let round = 0; round < rounds; round++) {
        for (let i = 0; i < stepsPerRound; i++) {
            rk4Step(orbit, 0, sigma, rho, beta, DT);
            rk4Step(shadow, 0, sigma, rho, beta, DT);
        }
        const dx = shadow[0] - orbit[0];
        const dy = shadow[1] - orbit[1];
        const dz = shadow[2] - orbit[2];
        const distance = Math.hypot(dx, dy, dz);
        total += Math.log(distance / gap);
        shadow[0] = orbit[0] + (dx * gap) / distance;
        shadow[1] = orbit[1] + (dy * gap) / distance;
        shadow[2] = orbit[2] + (dz * gap) / distance;
    }
    return total / (rounds * stepsPerRound * DT);
}

test('the generator matches known values', () => {
    const random = mulberry32(12345);
    assert.equal(random(), 0.9797282677609473);
    assert.equal(random(), 0.3067522644996643);
    assert.equal(random(), 0.484205421525985);
});

test('the generator stays in [0, 1) and repeats for a seed', () => {
    const first = mulberry32(7);
    const second = mulberry32(7);
    for (let i = 0; i < 10000; i++) {
        const value = first();
        assert.ok(value >= 0 && value < 1);
        assert.equal(value, second());
    }
});

test('streams of one seed differ, and so do seeds of one stream', () => {
    assert.notEqual(streamSeed(1, 0x9e3779b9), streamSeed(1, 0x85ebca77));
    assert.notEqual(streamSeed(1, 0x9e3779b9), streamSeed(2, 0x9e3779b9));
});

test('every parameter has a default inside its range', () => {
    for (const [key, spec] of Object.entries(PARAMS)) {
        assert.ok(spec.min < spec.max, key);
        assert.ok(spec.default >= spec.min && spec.default <= spec.max, key);
    }
});

test('clampParams fills gaps and holds values to their ranges', () => {
    assert.deepEqual(clampParams(), defaults());
    assert.deepEqual(clampParams({ rho: 'oops', sigma: NaN, beta: null, spread: '' }), defaults());

    const held = clampParams({ rho: 1e9, sigma: -5, tracers: 2.6, seed: 2 ** 40 });
    assert.equal(held.rho, PARAMS.rho.max);
    assert.equal(held.sigma, PARAMS.sigma.min);
    assert.equal(held.tracers, 3);
    assert.equal(held.seed, PARAMS.seed.max);

    // Strings are what a share link will hand back
    assert.equal(clampParams({ rho: '42.5' }).rho, 42.5);
});

test('clampParams drops unknown keys', () => {
    assert.deepEqual(Object.keys(clampParams({ nope: 1 })), Object.keys(PARAMS));
});

test('the initial state is exactly reproducible', () => {
    const params = clampParams({ tracers: 3 });
    const state = createState(params);
    assert.deepEqual(state.origin, [-1.3070959992706777, 5.395654571801424, 24.110704027488826]);
    assert.deepEqual(Array.from(state.positions), [
        -1.301288455645554, 5.390620219958946, 24.113851054189723,
        -1.3129967006994412, 5.392187485080212, 24.105952329654244,
        -1.3119096861965955, 5.400988640412689, 24.116769152614285,
    ]);
    assert.deepEqual(createState(params), createState(params));
});

test('a different seed gives a different initial state', () => {
    const one = createState(clampParams({ seed: 1 }));
    const two = createState(clampParams({ seed: 2 }));
    assert.notDeepEqual(one.origin, two.origin);
    assert.notDeepEqual(one.offsets, two.offsets);
});

test('adding paths keeps the ones already there', () => {
    const few = createState(clampParams({ tracers: 4 }));
    const many = createState(clampParams({ tracers: 40 }));
    assert.deepEqual(Array.from(many.positions.subarray(0, 12)), Array.from(few.positions));
});

test('every path starts within the starting gap', () => {
    const params = clampParams({ tracers: 64, spread: 0.25 });
    const state = createState(params);
    for (let i = 0; i < state.positions.length; i += 3) {
        const distance = Math.hypot(
            state.positions[i] - state.origin[0],
            state.positions[i + 1] - state.origin[1],
            state.positions[i + 2] - state.origin[2],
        );
        assert.ok(distance <= params.spread);
    }
});

test('a trajectory is exactly reproducible, even in chaos', () => {
    const params = clampParams({ tracers: 3 });
    const state = createState(params);
    advance(state, params, 2000);
    // Matches an independent Python version of the same arithmetic, bit for bit
    assert.deepEqual(Array.from(state.positions), [
        3.1805085007327913, 5.702533127243988, 11.08495360164062,
        -1.4303480169775604, -1.5812885562851788, 17.662361942029694,
        -2.8602481614302184, -5.198484323702575, 22.660214227983644,
    ]);
});

test('the result depends on the step count, not on how steps are batched', () => {
    const params = clampParams({ tracers: 5 });
    const once = createState(params);
    const inFrames = createState(params);
    advance(once, params, 1000);
    for (const batch of [1, 3, 7, 64, 200, 725]) {
        advance(inFrames, params, batch);
    }
    assert.equal(once.steps, 1000);
    assert.equal(inFrames.steps, 1000);
    assert.deepEqual(once.positions, inFrames.positions);
});

test('the integrator keeps the rest points of the system', () => {
    const { sigma, rho, beta } = defaults();

    const atOrigin = new Float64Array(3);
    rk4Step(atOrigin, 0, sigma, rho, beta, DT);
    assert.deepEqual(Array.from(atOrigin), [0, 0, 0]);

    // The two points at the eyes of the butterfly
    const eye = Math.sqrt(beta * (rho - 1));
    const point = Float64Array.of(eye, eye, rho - 1);
    for (let i = 0; i < 100; i++) {
        rk4Step(point, 0, sigma, rho, beta, DT);
    }
    assert.ok(Math.abs(point[0] - eye) < 1e-9);
    assert.ok(Math.abs(point[2] - (rho - 1)) < 1e-9);
});

test('the integrator is fourth order', () => {
    const { sigma, rho, beta } = defaults();
    const span = 0.5;
    const run = (dt) => {
        const point = Float64Array.of(1, 1, 20);
        const steps = Math.round(span / dt);
        for (let i = 0; i < steps; i++) {
            rk4Step(point, 0, sigma, rho, beta, dt);
        }
        return point;
    };

    const truth = run(span / 16384);
    const error = (dt) => {
        const point = run(dt);
        return Math.hypot(point[0] - truth[0], point[1] - truth[1], point[2] - truth[2]);
    };

    // Halving the step should cut the error by about 2^4
    const ratio = error(span / 256) / error(span / 512);
    assert.ok(ratio > 13 && ratio < 19, `error ratio ${ratio}`);
});

test('the classic system has the published Lyapunov exponent', () => {
    const exponent = lyapunov(presetParams('butterfly'));
    assert.ok(Math.abs(exponent - 0.906) < 0.05, `exponent ${exponent}`);
});

test('butterfly: paths that start together end up far apart', () => {
    for (const seed of [1, 2, 3, 4, 5]) {
        const params = presetParams('butterfly', { seed });
        const state = createState(params);
        const start = separation(state);
        assert.ok(start < params.spread);
        advance(state, params, Math.round(20 / DT));
        assert.ok(separation(state) > 1000 * start, `seed ${seed}`);
    }
});

test('settling: every path comes to rest', () => {
    // Not always on the same point: the bundle of seed 2 straddles the
    // boundary between the two rest points, so it splits between them
    for (const seed of [1, 2, 3, 4, 5]) {
        const params = presetParams('settling', { seed });
        const state = createState(params);
        advance(state, params, Math.round(60 / DT));

        const eye = Math.sqrt(params.beta * (params.rho - 1));
        for (let i = 0; i < state.positions.length; i += 3) {
            const x = state.positions[i];
            const z = state.positions[i + 2];
            assert.ok(Math.abs(Math.abs(x) - eye) < 0.001, `seed ${seed} x ${x}`);
            assert.ok(Math.abs(z - (params.rho - 1)) < 0.001, `seed ${seed} z ${z}`);
        }
    }
    assert.ok(lyapunov(presetParams('settling')) < -0.2);
});

test('fading chaos: paths spread out, then rest on the two fixed points', () => {
    const params = presetParams('fading-chaos');
    const state = createState(params);
    const eye = Math.sqrt(params.beta * (params.rho - 1));
    const resting = () => {
        for (let i = 0; i < state.positions.length; i += 3) {
            const nearEye = Math.abs(Math.abs(state.positions[i]) - eye) < 0.5;
            const nearHeight = Math.abs(state.positions[i + 2] - (params.rho - 1)) < 0.5;
            if (!nearEye || !nearHeight) {
                return false;
            }
        }
        return true;
    };

    let spreadBy = null;
    let time = 0;
    while (!resting() && time < 200) {
        advance(state, params, Math.round(1 / DT));
        time += 1;
        if (spreadBy === null && separation(state) > 5) {
            spreadBy = time;
        }
    }

    assert.ok(spreadBy !== null && spreadBy <= 10, `spread by ${spreadBy}`);
    assert.ok(time > 40 && time < 200, `at rest by ${time}`);

    let onPositive = 0;
    for (let i = 0; i < state.positions.length; i += 3) {
        onPositive += state.positions[i] > 0 ? 1 : 0;
    }
    assert.ok(onPositive > 0 && onPositive < state.count, 'both points are used');
});

test('closed loops: every path ends on one of two mirrored orbits', () => {
    const params = presetParams('closed-loops');
    assert.ok(Math.abs(lyapunov(params)) < 0.05);

    for (const seed of [1, 2, 3]) {
        const seeded = { ...params, seed };
        const state = createState(seeded);
        advance(state, seeded, Math.round(400 / DT));

        // The x range of a path over a full turn names its orbit: the mirror
        // image of an orbit swaps the two ends of the range
        const lowest = new Array(state.count).fill(Infinity);
        const highest = new Array(state.count).fill(-Infinity);
        for (let step = 0; step < 3000; step++) {
            advance(state, seeded, 1);
            for (let i = 0; i < state.count; i++) {
                lowest[i] = Math.min(lowest[i], state.positions[i * 3]);
                highest[i] = Math.max(highest[i], state.positions[i * 3]);
            }
        }

        const wide = Math.max(...highest);
        const narrow = Math.min(...highest);
        assert.ok(wide - narrow > 5, `seed ${seed}: expected two orbits`);
        for (let i = 0; i < state.count; i++) {
            const onFirst = Math.abs(highest[i] - wide) < 0.1 && Math.abs(lowest[i] + narrow) < 0.1;
            const onSecond = Math.abs(highest[i] - narrow) < 0.1 && Math.abs(lowest[i] + wide) < 0.1;
            assert.ok(onFirst || onSecond, `seed ${seed}: ${lowest[i]}..${highest[i]}`);
        }
    }
});

test('every preset is inside the parameter ranges', () => {
    assert.ok(PRESETS.length >= 3 && PRESETS.length <= 5);
    for (const preset of PRESETS) {
        for (const key of Object.keys(preset.params)) {
            assert.ok(key in PARAMS, `${preset.id}: ${key}`);
        }
        assert.deepEqual(clampParams({ ...defaults(), ...preset.params }), {
            ...defaults(),
            ...preset.params,
        });
    }
});

test('paths stay finite at the corners of the parameter ranges', () => {
    for (const rho of [PARAMS.rho.min, PARAMS.rho.max]) {
        for (const sigma of [PARAMS.sigma.min, PARAMS.sigma.max]) {
            for (const beta of [PARAMS.beta.min, PARAMS.beta.max]) {
                const params = clampParams({ rho, sigma, beta, spread: PARAMS.spread.max, tracers: 4 });
                const state = createState(params);
                const { bounds } = probeOrbit(params, state.origin);

                // The farthest place a visitor can release the paths
                release(state, params, bounds.maxX, bounds.maxX, bounds.maxZ);
                advance(state, params, 20000);
                for (const value of state.positions) {
                    assert.ok(Number.isFinite(value), `rho ${rho} sigma ${sigma} beta ${beta}`);
                }
            }
        }
    }
});

test('release gathers the paths at a point and restarts the clock', () => {
    const params = clampParams({ tracers: 8, spread: 0.1 });
    const state = createState(params);
    advance(state, params, 500);
    release(state, params, 3, 4, 5);
    assert.equal(state.steps, 0);
    for (let i = 0; i < state.positions.length; i += 3) {
        const distance = Math.hypot(
            state.positions[i] - 3,
            state.positions[i + 1] - 4,
            state.positions[i + 2] - 5,
        );
        assert.ok(distance <= params.spread);
    }
});

test('a release from the same point is reproducible', () => {
    const params = clampParams({ tracers: 8 });
    const run = () => {
        const state = createState(params);
        advance(state, params, 123);
        release(state, params, -6, -6, 30);
        advance(state, params, 1000);
        return state.positions;
    };
    assert.deepEqual(run(), run());
});

test('separation is zero for one point and measures the gap for two', () => {
    const state = {
        count: 2,
        positions: Float64Array.of(1, 2, 3, 1, 2, 3),
    };
    assert.equal(separation(state), 0);
    state.positions[0] = 7;
    assert.equal(separation(state), 3);
});

test('the probe contains the butterfly and matches its known shape', () => {
    const params = clampParams();
    const { bounds, path } = probeOrbit(params, createState(params).origin);
    assert.ok(bounds.minX < -15 && bounds.minX > -25);
    assert.ok(bounds.maxX > 15 && bounds.maxX < 25);
    assert.ok(bounds.maxZ > 40 && bounds.maxZ < 55);
    assert.equal(path.length, 6000);
    for (const value of path) {
        assert.ok(Number.isFinite(value));
    }
});

test('the probe never fits a view to a point', () => {
    const params = clampParams({ rho: 0 });
    const { bounds } = probeOrbit(params, [0, 0, 0]);
    assert.ok(bounds.maxX - bounds.minX >= 4);
    assert.ok(bounds.maxZ - bounds.minZ >= 4);
});

test('colors repeat for a seed, and never touch the trajectories', () => {
    assert.deepEqual(palette(9, 24), palette(9, 24));
    assert.notDeepEqual(palette(9, 24), palette(10, 24));
    assert.equal(palette(9, 24).length, 24);
    assert.equal(palette(9, 1).length, 1);

    for (const color of palette(9, 24)) {
        assert.ok(color.h >= 0 && color.h < 360);
    }

    const params = clampParams({ tracers: 3 });
    const before = createState(params);
    palette(params.seed, 64);
    assert.deepEqual(createState(params), before);
});
