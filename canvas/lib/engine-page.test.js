// Run from the repository root with: node --test
const test = require('node:test');
const assert = require('node:assert/strict');

const { create, formatParam, fromSlider, toSlider } = require('./engine-page.js');
const attractor = require('../strange-attractor/sim.js');
const garden = require('../artificial-garden/sim.js');

// How each page showed its sliders' values before they shared this code
function attractorFormat(spec, value) {
    if (spec.log) {
        return value.toPrecision(2);
    }
    return Number.isInteger(spec.step) ? String(value) : value.toFixed(2);
}

function gardenFormat(spec, value) {
    if (Number.isInteger(spec.step)) {
        return String(value);
    }
    const places = Math.max(0, -Math.floor(Math.log10(spec.step)));
    return value.toFixed(places);
}

// Every value a slider can take, and a few between its steps
function sliderValues(spec) {
    if (spec.log) {
        const values = [];
        for (let position = 0; position <= 1000; position++) {
            values.push(fromSlider(spec, position));
        }
        return values;
    }
    const values = [];
    const count = Math.round((spec.max - spec.min) / spec.step);
    for (let i = 0; i <= count; i++) {
        values.push(spec.min + i * spec.step, spec.min + (i + 0.37) * spec.step);
    }
    return values;
}

for (const [name, sim, before] of [
    ['strange attractor', attractor, attractorFormat],
    ['artificial garden', garden, gardenFormat],
]) {
    test(`${name}'s sliders show their values as before`, () => {
        for (const [key, spec] of Object.entries(sim.PARAMS)) {
            if (key === 'seed') {
                continue;
            }
            for (const value of sliderValues(spec)) {
                const held = sim.clampParams({ ...sim.defaults(), [key]: value })[key];
                assert.equal(formatParam(spec, held), before(spec, held), `${key} at ${held}`);
            }
        }
    });
}

test('a log slider maps its ends onto the range, and back', () => {
    const spec = attractor.PARAMS.spread;
    assert.equal(fromSlider(spec, 0), spec.min);
    assert.ok(Math.abs(fromSlider(spec, 1000) - spec.max) < 1e-12);
    for (let position = 0; position <= 1000; position += 7) {
        assert.ok(Math.abs(toSlider(spec, fromSlider(spec, position)) - position) < 1e-9);
    }
});

test('a plain slider shows the value itself', () => {
    const spec = garden.PARAMS.reach;
    assert.equal(toSlider(spec, 0.16), 0.16);
    assert.equal(fromSlider(spec, 0.16), 0.16);
});

test('places overrides the step, and a whole step shows a whole number', () => {
    assert.equal(formatParam({ step: 0.1, places: 2 }, 28), '28.00');
    assert.equal(formatParam({ step: 0.1 }, 28), '28.0');
    assert.equal(formatParam({ step: 0.001 }, 0.012), '0.012');
    assert.equal(formatParam({ step: 10 }, 240), '240');
    assert.equal(formatParam({ log: true, step: 0.1 }, 0.000123456), '0.00012');
});

test('node gets the helpers without a page to run on', () => {
    assert.equal(typeof create, 'function');
    assert.equal(typeof globalThis.EnginePage, 'undefined');
});
