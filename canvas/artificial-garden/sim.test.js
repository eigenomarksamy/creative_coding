// Run from the repository root with: node --test
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const {
    CROWD_RATIO,
    EAT_RATIO,
    FEED_COUNT,
    FIELD_RADIUS,
    IDLE_STEPS,
    MAX_CHILDREN,
    MAX_FOOD,
    MAX_NODES,
    MAX_STONES,
    PARAMS,
    PRESETS,
    SOIL_RADIUS,
    STONE_RADIUS,
    advance,
    atRest,
    clampParams,
    createState,
    defaults,
    feed,
    fertility,
    matchPreset,
    mulberry32,
    nextRandom,
    palette,
    placeStone,
    pullTargets,
    removeStone,
    step,
    stoneAt,
    streamSeed,
    tips,
    turns,
} = require('./sim.js');

const presetParams = (id, extra) => {
    const preset = PRESETS.find((candidate) => candidate.id === id);
    return clampParams({ ...defaults(), ...preset.params, ...extra });
};

function growToRest(state, params, limit = 3000) {
    while (!atRest(state) && state.steps < limit) {
        step(state, params);
    }
    return state;
}

function nodesOf(state) {
    const nodes = [];
    for (let n = 0; n < state.nodeCount; n++) {
        nodes.push({ n, x: state.nodeX[n], y: state.nodeY[n], parent: state.parent[n] });
    }
    return nodes;
}

function nearestDistance(state, x, y) {
    let best = Infinity;
    for (let n = 0; n < state.nodeCount; n++) {
        best = Math.min(best, Math.hypot(state.nodeX[n] - x, state.nodeY[n] - y));
    }
    return best;
}

// The share of nodes, besides the root, with a twin exactly one turn of a
// k-fold symmetry away
function twinShare(state, k) {
    const [, [c, s]] = turns(k);
    let twins = 0;
    for (let n = 1; n < state.nodeCount; n++) {
        const x = c * state.nodeX[n] - s * state.nodeY[n];
        const y = s * state.nodeX[n] + c * state.nodeY[n];
        for (let m = 1; m < state.nodeCount; m++) {
            if (Math.abs(state.nodeX[m] - x) < 1e-9 && Math.abs(state.nodeY[m] - y) < 1e-9) {
                twins++;
                break;
            }
        }
    }
    return twins / (state.nodeCount - 1);
}

test('the generator matches known values', () => {
    const random = mulberry32(12345);
    assert.equal(random(), 0.9797282677609473);
    assert.equal(random(), 0.3067522644996643);
    assert.equal(random(), 0.484205421525985);
});

test('the state keeps its own generator, the same sequence as mulberry32', () => {
    const state = { rand: 12345 };
    const random = mulberry32(12345);
    for (let i = 0; i < 1000; i++) {
        assert.equal(nextRandom(state), random());
    }
});

test('streams of one seed differ, and so do seeds of one stream', () => {
    assert.notEqual(streamSeed(1, 0x9e3779b9), streamSeed(1, 0x85ebca77));
    assert.notEqual(streamSeed(1, 0x9e3779b9), streamSeed(2, 0x9e3779b9));
});

test('every symmetry has its turns, of unit length, and a half or quarter turn is exact', () => {
    for (let k = 1; k <= 6; k++) {
        const all = turns(k);
        assert.equal(all.length, k);
        for (const [c, s] of all) {
            assert.ok(Math.abs(c * c + s * s - 1) < 1e-15, `k ${k}`);
        }
    }
    assert.deepEqual(turns(2), [[1, 0], [-1, 0]]);
    assert.deepEqual(turns(4).map(([c, s]) => [c + 0, s + 0]), [[1, 0], [0, 1], [-1, 0], [0, -1]]);
});

test('every parameter has a default inside its range', () => {
    for (const [key, spec] of Object.entries(PARAMS)) {
        assert.ok(spec.min < spec.max, key);
        assert.ok(spec.default >= spec.min && spec.default <= spec.max, key);
    }
});

test('a branch eats closer than the smallest reach, so food always pulls first', () => {
    assert.ok(EAT_RATIO * PARAMS.growth.max < PARAMS.reach.min);
});

test('clampParams fills gaps and holds values to their ranges', () => {
    assert.deepEqual(clampParams(), defaults());
    assert.deepEqual(clampParams({ food: 'oops', reach: NaN, growth: null, wander: '' }), defaults());

    const held = clampParams({ food: 1e9, reach: -5, symmetry: 2.6, seed: 2 ** 40 });
    assert.equal(held.food, PARAMS.food.max);
    assert.equal(held.reach, PARAMS.reach.min);
    assert.equal(held.symmetry, 3);
    assert.equal(held.seed, PARAMS.seed.max);

    // Strings are what a share link will hand back
    assert.equal(clampParams({ branching: '0.25' }).branching, 0.25);
});

test('clampParams drops unknown keys', () => {
    assert.deepEqual(Object.keys(clampParams({ nope: 1 })), Object.keys(PARAMS));
});

test('every preset is inside the ranges, and is found again from its values', () => {
    for (const preset of PRESETS) {
        const params = presetParams(preset.id);
        for (const [key, value] of Object.entries(preset.params)) {
            assert.equal(params[key], value, `${preset.id} ${key}`);
        }
        assert.equal(matchPreset(params).id, preset.id);
    }
    assert.equal(matchPreset(clampParams({ branching: 0.33 })), null);
});

test('the initial state is exactly reproducible', () => {
    const params = clampParams({ food: 40 });
    const state = createState(params);
    assert.deepEqual(state.patches[0], {
        x: 0.0722632308723405,
        y: -0.01945171379484236,
        spread: 0.4185565771884285,
        weight: 0.7986259263008832,
    });
    assert.equal(state.foodCount, 40);
    assert.equal(state.foodX[0], 0.6613267097994685);
    assert.equal(state.foodY[0], 0.5874277203436941);
    assert.equal(state.foodX[1], -0.06361955573782324);
    assert.equal(state.foodY[1], 0.21114336115308105);
    assert.equal(state.nodeCount, 1);
    assert.deepEqual(createState(params), createState(params));
});

test('the same seed and parameters grow exactly the same garden', () => {
    const params = clampParams({});
    const state = createState(params);
    advance(state, params, 60);
    assert.equal(state.nodeCount, 839);
    assert.equal(state.foodLeft, 115);
    assert.equal(tips(state), 82);
    assert.equal(state.nodeX[838], -0.6032627488903873);
    assert.equal(state.nodeY[838], -0.32775711468752106);

    const again = createState(params);
    advance(again, params, 60);
    assert.deepEqual(again, state);
});

test('growth depends on the number of steps, not how they are batched', () => {
    const params = clampParams({ seed: 7 });
    const batched = createState(params);
    const single = createState(params);
    advance(batched, params, 25);
    advance(batched, params, 45);
    for (let i = 0; i < 70; i++) {
        step(single, params);
    }
    assert.deepEqual(batched, single);
});

test('the simulation needs no DOM, canvas, timers or globals of its own', () => {
    // A bare context has the language's built-ins and nothing else: no
    // window, document, setTimeout or performance
    const source = fs.readFileSync(path.join(__dirname, 'sim.js'), 'utf8');
    const context = vm.createContext({});
    vm.runInContext(source, context);
    const bare = context.ArtificialGarden;
    assert.equal(typeof context.setTimeout, 'undefined');

    const params = clampParams({ seed: 11 });
    const inBare = bare.createState(params);
    bare.advance(inBare, params, 80);
    bare.feed(inBare, 0.3, 0.3);
    bare.placeStone(inBare, -0.3, 0.2);
    bare.advance(inBare, params, 40);

    const here = createState(params);
    advance(here, params, 80);
    feed(here, 0.3, 0.3);
    placeStone(here, -0.3, 0.2);
    advance(here, params, 40);

    assert.equal(inBare.nodeCount, here.nodeCount);
    assert.deepEqual(Array.from(inBare.nodeX.subarray(0, inBare.nodeCount)),
        Array.from(here.nodeX.subarray(0, here.nodeCount)));
    assert.deepEqual(Array.from(inBare.nodeY.subarray(0, inBare.nodeCount)),
        Array.from(here.nodeY.subarray(0, here.nodeCount)));
});

test('the soil holds its food, rounded down to the symmetry, inside the plot', () => {
    for (let k = 1; k <= 6; k++) {
        const state = createState({ food: 500, symmetry: k, seed: 3 });
        assert.equal(state.foodCount, Math.floor(500 / k) * k);
        assert.equal(state.foodLeft, state.foodCount);
        for (let i = 0; i < state.foodCount; i++) {
            assert.ok(Math.hypot(state.foodX[i], state.foodY[i]) <= SOIL_RADIUS + 1e-12);
        }
    }
});

test('four-fold soil comes in exact quarter turns, with four shoots from the root', () => {
    const state = createState({ food: 400, symmetry: 4, seed: 5 });
    const share = 100;
    for (let i = 0; i < share; i++) {
        assert.equal(state.foodX[share + i], -state.foodY[i]);
        assert.equal(state.foodY[share + i], state.foodX[i]);
    }
    assert.equal(state.nodeCount, 5);
    assert.equal(state.children[0], 4);
    assert.equal(state.nodeX[2], -state.nodeY[1]);
    assert.equal(state.nodeY[2], state.nodeX[1]);
});

test('without symmetry the root starts alone, leaning no way', () => {
    const state = createState({ seed: 9 });
    assert.equal(state.nodeCount, 1);
    assert.equal(state.dirX[0], 0);
    assert.equal(state.dirY[0], 0);
});

test('the soil lies in patches, and the root sits in one', () => {
    for (let seed = 1; seed <= 20; seed++) {
        const { patches } = createState({ seed });
        assert.ok(patches.length >= 3 && patches.length <= 6);
        assert.ok(Math.hypot(patches[0].x, patches[0].y) < patches[0].spread);
        assert.ok(fertility(patches, 0, 0) > 0.1);
        // Outside every patch only the thin floor is left
        assert.equal(fertility([patches[0]], patches[0].x + patches[0].spread, patches[0].y), 0.02);
    }
});

test('a growing garden keeps every rule of growth', () => {
    for (const id of ['spreading', 'lace', 'runners']) {
        for (let seed = 1; seed <= 4; seed++) {
            const params = presetParams(id, { seed });
            const state = growToRest(createState(params), params);
            const crowd = CROWD_RATIO * params.growth;
            const label = `${id} ${seed}`;

            for (let n = 0; n < state.nodeCount; n++) {
                const x = state.nodeX[n];
                const y = state.nodeY[n];
                assert.ok(x * x + y * y <= FIELD_RADIUS * FIELD_RADIUS, label);
                assert.ok(state.children[n] <= MAX_CHILDREN, label);
                if (n === 0) {
                    continue;
                }
                const p = state.parent[n];
                assert.ok(p >= 0 && p < n, label);
                assert.equal(state.depth[n], state.depth[p] + 1, label);
                const length = Math.hypot(x - state.nodeX[p], y - state.nodeY[p]);
                assert.ok(Math.abs(length - params.growth) < 1e-12, label);
            }

            // No new point lands on another: every two nodes are at least
            // the crowd distance apart
            const cell = new Map();
            for (const { n, x, y } of nodesOf(state)) {
                const key = `${Math.floor(x / crowd)},${Math.floor(y / crowd)}`;
                for (let dx = -1; dx <= 1; dx++) {
                    for (let dy = -1; dy <= 1; dy++) {
                        const near = cell.get(`${Math.floor(x / crowd) + dx},${Math.floor(y / crowd) + dy}`) || [];
                        for (const m of near) {
                            const gap = Math.hypot(x - state.nodeX[m], y - state.nodeY[m]);
                            assert.ok(gap >= crowd, `${label}: nodes ${m} and ${n} are ${gap} apart`);
                        }
                    }
                }
                cell.set(key, [...(cell.get(key) || []), n]);
            }

            // Every node carries the tips beyond it
            const carried = new Int32Array(state.nodeCount);
            for (let n = state.nodeCount - 1; n >= 0; n--) {
                carried[n] = Math.max(1, carried[n]);
                if (n > 0) {
                    carried[state.parent[n]] += carried[n];
                }
            }
            let childless = 0;
            for (let n = 0; n < state.nodeCount; n++) {
                assert.equal(state.leaves[n], carried[n], label);
                childless += state.children[n] === 0 ? 1 : 0;
            }
            assert.equal(tips(state), childless, label);
        }
    }
});

test('food is eaten only where a branch reached it, and none within reach of a mouth is left', () => {
    for (let seed = 1; seed <= 6; seed++) {
        const params = clampParams({ seed });
        const state = growToRest(createState(params), params);
        const eatAt = EAT_RATIO * params.growth;
        let eaten = 0;
        for (let i = 0; i < state.foodCount; i++) {
            const distance = nearestDistance(state, state.foodX[i], state.foodY[i]);
            if (state.foodAlive[i]) {
                assert.ok(distance >= eatAt, `seed ${seed}: food ${i} left at ${distance}`);
            } else {
                assert.ok(distance < eatAt, `seed ${seed}: food ${i} eaten from ${distance}`);
                eaten++;
            }
        }
        assert.equal(state.foodCount - state.foodLeft, eaten);
        assert.equal(state.eaten, eaten);
    }
});

test('with nothing to grow toward, the garden is at rest after its idle steps', () => {
    const params = clampParams({ food: 0 });
    const state = createState(params);
    for (let i = 1; i < IDLE_STEPS; i++) {
        step(state, params);
        assert.equal(atRest(state), false);
    }
    step(state, params);
    assert.equal(atRest(state), true);
    assert.equal(state.nodeCount, 1);
});

test('every preset comes to rest, without the node cap, on many seeds', () => {
    for (const preset of PRESETS) {
        for (let seed = 1; seed <= 12; seed++) {
            const params = presetParams(preset.id, { seed });
            const state = growToRest(createState(params), params, 400);
            assert.ok(atRest(state), `${preset.id} ${seed}`);
            assert.ok(state.nodeCount < MAX_NODES, `${preset.id} ${seed}`);
        }
    }
});

test('the garden never grows past its node cap', () => {
    const params = clampParams({ food: 1500, growth: 0.004, branching: 1, reach: 0.4 });
    const state = growToRest(createState(params), params);
    assert.equal(state.nodeCount, MAX_NODES);
    assert.ok(atRest(state));
    assert.equal(step(state, params), 0);
});

test('food within reach draws the garden to it, and food out of reach waits', () => {
    const params = clampParams({ food: 0 });

    const near = createState(params);
    assert.equal(feed(near, 0.2, 0), FEED_COUNT);
    assert.equal(atRest(near), false);
    growToRest(near, params);
    assert.ok(near.nodeCount > 10);
    assert.equal(near.foodLeft, 0);

    const far = createState(params);
    feed(far, 0.8, 0);
    growToRest(far, params);
    assert.equal(far.nodeCount, 1);
    assert.equal(far.foodLeft, FEED_COUNT);

    // A trail of food carries the garden out to it
    for (const x of [0.2, 0.35, 0.5, 0.65]) {
        feed(far, x, 0);
    }
    growToRest(far, params);
    assert.equal(far.foodLeft, 0);
    assert.ok(Math.max(...far.nodeX.subarray(0, far.nodeCount)) > 0.7);
});

test('feeding changes how a garden at rest develops', () => {
    const params = clampParams({ seed: 1 });
    const left = growToRest(createState(params), params);
    const fed = growToRest(createState(params), params);
    assert.deepEqual(fed, left);

    // Food dropped just past the reach of a tip grows the garden toward it
    let tip = 0;
    for (let n = 0; n < fed.nodeCount; n++) {
        if (fed.children[n] === 0 && Math.hypot(fed.nodeX[n], fed.nodeY[n]) > Math.hypot(fed.nodeX[tip], fed.nodeY[tip])) {
            tip = n;
        }
    }
    const x = fed.nodeX[tip] * 0.92;
    const y = fed.nodeY[tip] * 0.92;
    const before = fed.nodeCount;
    assert.ok(feed(fed, x, y) > 0);
    growToRest(fed, params);
    assert.ok(fed.nodeCount > before);
    assert.ok(tips(fed) !== tips(left) || fed.nodeCount !== left.nodeCount);
});

test('a stone takes the food under it, and nothing grows into it', () => {
    const params = clampParams({ seed: 2 });
    const state = createState(params);
    const stones = [[0.3, 0.1], [-0.25, -0.2], [0.05, -0.35], [-0.1, 0.4]];
    for (const [x, y] of stones) {
        assert.equal(placeStone(state, x, y), true);
    }
    for (let i = 0; i < state.foodCount; i++) {
        if (state.foodAlive[i]) {
            assert.equal(stoneAt(state, state.foodX[i], state.foodY[i]), -1);
        }
    }
    growToRest(state, params);
    for (let n = 1; n < state.nodeCount; n++) {
        assert.equal(stoneAt(state, state.nodeX[n], state.nodeY[n]), -1, `node ${n}`);
    }
});

test('a garden grows around a stone to reach food behind it', () => {
    for (const wander of [0, 0.15]) {
        const params = clampParams({ food: 0, reach: 0.3, wander });
        const state = createState(params);
        placeStone(state, 0.1, 0);
        feed(state, 0.22, 0);
        growToRest(state, params);
        assert.equal(state.foodLeft, 0, `wander ${wander}`);
        for (let n = 1; n < state.nodeCount; n++) {
            assert.equal(stoneAt(state, state.nodeX[n], state.nodeY[n]), -1);
        }
    }
});

test('a stone can’t cover the root or leave the plot, and there are only so many', () => {
    const state = createState({ food: 0 });
    assert.equal(placeStone(state, STONE_RADIUS / 2, 0), false);
    assert.equal(placeStone(state, 0.9, 0.9), false);
    for (let i = 0; i < MAX_STONES; i++) {
        assert.equal(placeStone(state, -0.8 + 0.1 * i, 0.5), true);
    }
    assert.equal(placeStone(state, 0, -0.5), false);
    assert.equal(state.stones.length, MAX_STONES);
});

test('a stone lifts again, and the garden wakes to grow where it was', () => {
    const params = clampParams({ food: 0 });
    const state = createState(params);
    placeStone(state, 0.15, 0);
    growToRest(state, params);

    // Food dropped on a stone lands around it, never under it
    assert.equal(feed(state, 0.15, 0), FEED_COUNT);
    for (let i = 0; i < state.foodCount; i++) {
        assert.equal(stoneAt(state, state.foodX[i], state.foodY[i]), -1);
    }
    growToRest(state, params);
    assert.equal(removeStone(state, 0.9, 0.9), false);
    assert.equal(removeStone(state, 0.15, 0), true);
    assert.equal(state.stones.length, 0);
    assert.equal(atRest(state), false);

    assert.equal(feed(state, 0.15, 0), FEED_COUNT);
    growToRest(state, params);
    assert.equal(state.foodLeft, 0);
    assert.ok(state.nodeCount > 1);
});

test('feeding stops at the food cap, keeping what is left in order', () => {
    const state = createState({ food: 0 });
    let added = 0;
    for (let i = 0; i < MAX_FOOD / FEED_COUNT + 5; i++) {
        added += feed(state, 0.5, 0.2);
    }
    assert.equal(state.foodCount, MAX_FOOD);
    assert.equal(added, MAX_FOOD);
    assert.equal(feed(state, 0.5, 0.2), 0);

    // Eaten food makes room again, and the food left keeps its order
    const keptX = [];
    for (let i = 0; i < state.foodCount; i += 2) {
        state.foodAlive[i] = 0;
        state.foodLeft--;
    }
    for (let i = 1; i < state.foodCount; i += 2) {
        keptX.push(state.foodX[i]);
    }
    assert.equal(feed(state, -0.5, 0.2), FEED_COUNT);
    assert.deepEqual(Array.from(state.foodX.subarray(0, keptX.length)), keptX);
    assert.equal(state.foodLeft, keptX.length + FEED_COUNT);
});

test('lace branches more than spreading, and runners less, reaching far', () => {
    for (let seed = 1; seed <= 8; seed++) {
        const spreading = growToRest(createState(presetParams('spreading', { seed })), presetParams('spreading', { seed }));
        const lace = growToRest(createState(presetParams('lace', { seed })), presetParams('lace', { seed }));
        const runners = growToRest(createState(presetParams('runners', { seed })), presetParams('runners', { seed }));
        assert.ok(tips(lace) > tips(spreading), `seed ${seed}`);
        assert.ok(tips(runners) < tips(spreading), `seed ${seed}`);
        let farthest = 0;
        for (let n = 0; n < runners.nodeCount; n++) {
            farthest = Math.max(farthest, Math.hypot(runners.nodeX[n], runners.nodeY[n]));
        }
        assert.ok(farthest > 0.6, `seed ${seed}`);
    }
});

test('spreading grows toward the richest soil', () => {
    for (let seed = 1; seed <= 8; seed++) {
        const params = presetParams('spreading', { seed });
        const state = growToRest(createState(params), params);
        let onNodes = 0;
        for (let n = 0; n < state.nodeCount; n++) {
            onNodes += fertility(state.patches, state.nodeX[n], state.nodeY[n]);
        }
        const random = mulberry32(99);
        let onSoil = 0;
        let count = 0;
        while (count < 4000) {
            const x = 2 * random() - 1;
            const y = 2 * random() - 1;
            if (x * x + y * y <= SOIL_RADIUS * SOIL_RADIUS) {
                onSoil += fertility(state.patches, x, y);
                count++;
            }
        }
        assert.ok(onNodes / state.nodeCount > onSoil / count, `seed ${seed}`);
    }
});

test('mandala, on its own seed, grows six arms exactly alike', () => {
    const params = presetParams('mandala');
    assert.equal(params.seed, 3);
    assert.equal(twinShare(growToRest(createState(params), params), 6), 1);

    // On another seed the preset no longer shows
    assert.equal(matchPreset(presetParams('mandala', { seed: 4 })), null);
});

test('six-fold soil stays exactly six-fold on some seeds, and not on others', () => {
    // Seeds 2-5 stay exactly six-fold to rest. Seed 1 is one where a near
    // tie, rounded differently in different arms, sets them apart.
    for (const seed of [2, 3, 4, 5]) {
        const params = presetParams('mandala', { seed });
        assert.equal(twinShare(growToRest(createState(params), params), 6), 1, `seed ${seed}`);
    }
    const params = presetParams('mandala', { seed: 1 });
    const early = createState(params);
    advance(early, params, 10);
    assert.equal(twinShare(early, 6), 1);
    assert.ok(twinShare(growToRest(early, params), 6) < 1);
});

test('islands stops with food out of reach, and a trail of food leads it there', () => {
    for (let seed = 1; seed <= 12; seed++) {
        const params = presetParams('islands', { seed });
        const state = growToRest(createState(params), params);
        const targets = new Int32Array(MAX_FOOD);
        pullTargets(state, params, targets);

        // Food is left, all of it out of reach
        const stranded = [];
        for (let i = 0; i < state.foodCount; i++) {
            if (targets[i] === -1) {
                stranded.push(i);
            }
            assert.ok(targets[i] < 0, `seed ${seed}: food ${i} still pulls at rest`);
        }
        assert.ok(stranded.length > 0, `seed ${seed}`);

        // Lay a trail from the nearest node to the farthest stranded piece
        let goal = stranded[0];
        for (const i of stranded) {
            if (Math.hypot(state.foodX[i], state.foodY[i]) > Math.hypot(state.foodX[goal], state.foodY[goal])) {
                goal = i;
            }
        }
        const gx = state.foodX[goal];
        const gy = state.foodY[goal];
        let from = 0;
        for (let n = 0; n < state.nodeCount; n++) {
            if (Math.hypot(state.nodeX[n] - gx, state.nodeY[n] - gy) < Math.hypot(state.nodeX[from] - gx, state.nodeY[from] - gy)) {
                from = n;
            }
        }
        const sx = state.nodeX[from];
        const sy = state.nodeY[from];
        const drops = Math.ceil(Math.hypot(gx - sx, gy - sy) / 0.06);
        for (let k = 1; k <= drops; k++) {
            feed(state, sx + ((gx - sx) * k) / drops, sy + ((gy - sy) * k) / drops);
            growToRest(state, params, state.steps + 2000);
        }
        assert.equal(state.foodAlive[goal], 0, `seed ${seed}: the trail didn't reach the food`);
    }
});

test('pullTargets tells which node each piece pulls, changing nothing', () => {
    const params = clampParams({ seed: 6 });
    const state = createState(params);
    advance(state, params, 50);
    const targets = new Int32Array(MAX_FOOD);
    pullTargets(state, params, targets);
    const before = structuredClone(state);
    const pulling = pullTargets(state, params, targets);
    assert.deepEqual(state, before);

    let counted = 0;
    for (let i = 0; i < state.foodCount; i++) {
        if (!state.foodAlive[i]) {
            assert.equal(targets[i], -2);
            continue;
        }
        let nearest = -1;
        let best = params.reach;
        for (let n = 0; n < state.nodeCount; n++) {
            const d = Math.hypot(state.nodeX[n] - state.foodX[i], state.nodeY[n] - state.foodY[i]);
            if (d < best) {
                best = d;
                nearest = n;
            }
        }
        assert.equal(targets[i], nearest, `food ${i}`);
        counted += nearest === -1 ? 0 : 1;
    }
    assert.equal(pulling, counted);
});

test('the palette is reproducible and its colors valid', () => {
    assert.deepEqual(palette(4), palette(4));
    assert.notDeepEqual(palette(4), palette(5));
    for (let seed = 0; seed < 50; seed++) {
        for (const { h, s, l } of Object.values(palette(seed))) {
            assert.ok(h >= 0 && h < 360);
            assert.ok(s >= 0 && s <= 100);
            assert.ok(l >= 0 && l <= 100);
        }
    }
});
