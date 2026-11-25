// Run from the repository root with: node --test
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const { mulberry32, paramSet, streamSeed } = require('./engine-sim.js');

// A small engine of its own, so these tests don't lean on either real one
const SPEC = {
    size: { default: 10, min: 1, max: 100, step: 1, integer: true },
    rate: { default: 0.5, min: 0, max: 1, step: 0.01 },
    seed: { default: 1, min: 0, max: 4294967295, step: 1, integer: true },
};
const PRESETS = [
    { id: 'small', label: 'small', note: '', params: { size: 2, rate: 0.5 } },
    { id: 'pinned', label: 'pinned', note: '', params: { size: 50, rate: 0.25, seed: 7 } },
];
const LINK_KEYS = ['seed', 'size', 'rate'];
const set = paramSet(SPEC, PRESETS, LINK_KEYS);

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

test('a stream seed matches known values, and streams and seeds differ', () => {
    assert.equal(streamSeed(1, 0x9e3779b9), streamSeed(1, 0x9e3779b9));
    assert.notEqual(streamSeed(1, 0x9e3779b9), streamSeed(1, 0x85ebca77));
    assert.notEqual(streamSeed(1, 0x9e3779b9), streamSeed(2, 0x9e3779b9));
    for (const seed of [0, 1, 4294967295]) {
        const value = streamSeed(seed, 0x85ebca77);
        assert.ok(Number.isInteger(value) && value >= 0 && value <= 4294967295);
    }
});

test('both engines use this one copy, not one of their own', () => {
    for (const engine of ['strange-attractor', 'artificial-garden']) {
        const sim = require(`../${engine}/sim.js`);
        assert.equal(sim.mulberry32, mulberry32, engine);
        assert.equal(sim.streamSeed, streamSeed, engine);
    }
});

test('a link must list every parameter once', () => {
    assert.throws(() => paramSet(SPEC, PRESETS, ['seed', 'size']), /every parameter once/);
    assert.throws(() => paramSet(SPEC, PRESETS, ['seed', 'size', 'size']), /every parameter once/);
    assert.throws(() => paramSet(SPEC, PRESETS, ['seed', 'size', 'rate', 'extra']), /every parameter once/);
});

test('clampParams fills gaps, holds values to their ranges and rounds integers', () => {
    assert.deepEqual(set.defaults(), { size: 10, rate: 0.5, seed: 1 });
    assert.deepEqual(set.clampParams(), set.defaults());
    assert.deepEqual(set.clampParams({ size: 'oops', rate: NaN, seed: '' }), set.defaults());
    assert.deepEqual(set.clampParams({ size: 1e9, rate: -1, seed: 2.6 }), { size: 100, rate: 0, seed: 3 });
    assert.equal(set.clampParams({ rate: '0.25' }).rate, 0.25);
    assert.deepEqual(Object.keys(set.clampParams({ nope: 1 })), Object.keys(SPEC));
});

test('a link writes every key in its order, and reads back to the same bits', () => {
    assert.equal(set.encodeLink({ size: 3, rate: 1 / 3, seed: 9 }), 'seed=9&size=3&rate=0.3333333333333333');
    const random = mulberry32(2026);
    for (let i = 0; i < 200; i++) {
        const params = set.clampParams({
            size: 1 + Math.floor(random() * 100),
            rate: random(),
            seed: Math.floor(random() * 4294967296),
        });
        const back = set.decodeLink(set.encodeLink(params));
        assert.deepEqual(back.params, params);
        assert.deepEqual(back.problems, []);
    }
});

test('a link names a preset only when it keeps every value the preset sets', () => {
    assert.equal(set.decodeLink('seed=4&size=2&rate=0.5').preset, 'small');
    assert.equal(set.decodeLink('seed=7&size=50&rate=0.25').preset, 'pinned');
    assert.equal(set.decodeLink('seed=8&size=50&rate=0.25').preset, null);
    assert.equal(set.matchPreset(set.defaults()), null);
});

test('a short link takes a named preset, or the defaults, for what it leaves out', () => {
    assert.deepEqual(set.decodeLink('#preset=pinned'), {
        params: { size: 50, rate: 0.25, seed: 7 }, preset: 'pinned', problems: [],
    });
    assert.deepEqual(set.decodeLink('?size=4').params, { size: 4, rate: 0.5, seed: 1 });
    assert.deepEqual(set.decodeLink(null).params, set.defaults());
});

test('a value it can’t use as written is listed as a problem', () => {
    const link = set.decodeLink('preset=nope&size=0x10&rate=2&seed=1.5&extra=1');
    assert.deepEqual(link.problems.sort(), ['preset', 'rate', 'seed', 'size']);
    assert.deepEqual(link.params, { size: 10, rate: 1, seed: 2 });
    for (const bad of ['abc', 'Infinity', '1e999', '']) {
        assert.deepEqual(set.decodeLink(`size=${bad}`).problems, ['size'], bad);
    }
});

test('it needs no DOM or timers, only URLSearchParams, which browsers and node both have', () => {
    const context = vm.createContext({ URLSearchParams });
    vm.runInContext(fs.readFileSync(path.join(__dirname, 'engine-sim.js'), 'utf8'), context);
    const bare = context.EngineSim;
    assert.equal(typeof context.setTimeout, 'undefined');
    assert.equal(bare.mulberry32(12345)(), 0.9797282677609473);
    const bareSet = bare.paramSet(SPEC, PRESETS, LINK_KEYS);
    assert.equal(bareSet.encodeLink({ size: 3 }), set.encodeLink({ size: 3 }));
});
