// Artificial garden simulation: a branching organism that grows toward food.
//
// The garden is the unit disk, seen from above, with the organism's root at
// its center. Food lies in the soil, and every step each piece of food pulls
// on the nearest part of the organism within reach. A part that is pulled
// grows one short segment toward the food pulling it, and food that a branch
// reaches is eaten. Where food pulls one part in two directions at once, it
// may split. This is space colonization (Runions, Lane and Prusinkiewicz,
// 2007): nothing in the rules says where a branch goes, only what it grows
// toward. The visitor steers it the same way, by adding food and stones.
//
// Numbers only, no canvas and no DOM, so `node --test` can check all of it.
// A classic script, not a module, because the gallery has to work from
// file://: the browser gets the global ArtificialGarden and node gets
// module.exports. step, feed and the stone functions depend only on their
// arguments: no DOM, canvas, timers or globals, so the logic can be shared.
//
// The state uses + - * /, integer operations and Math.sqrt, which IEEE 754
// rounds exactly and every engine computes with the same instruction, so a
// seed and parameters reproduce a garden exactly. Math.sin, Math.log and
// friends can differ between browsers, so they stay out of anything that
// feeds the state.

(function (root) {
    'use strict';

    // Food is scattered inside this radius, and nothing grows past the edge
    const SOIL_RADIUS = 0.94;
    const FIELD_RADIUS = 1;

    // Bounds on the work a step can do and on what the page draws
    const MAX_NODES = 6000;
    const MAX_FOOD = 4000;
    const MAX_STONES = 16;

    // A part of the organism grows at most this many branches
    const MAX_CHILDREN = 3;

    // A branch eats food closer than this many growth steps
    const EAT_RATIO = 2;

    // No new point closer than this many growth steps to any other, so a
    // part pulled the same way twice doesn't pile up on itself
    const CROWD_RATIO = 0.45;

    // How much of its parent's heading a new segment keeps
    const INERTIA = 0.35;

    // This many steps in a row without growing or eating, and the garden is
    // at rest: nothing it can reach is left to grow toward
    const IDLE_STEPS = 40;

    // What one feeding adds, and how big a stone is
    const FEED_COUNT = 36;
    const FEED_RADIUS = 0.09;
    const STONE_RADIUS = 0.075;

    // Every parameter has a default and a range, and clampParams enforces
    // them. reach never falls below what a branch eats at the largest
    // growth step, or food would be eaten before it could pull.
    const PARAMS = {
        food: { default: 500, min: 0, max: 1500, step: 10, integer: true, label: 'food in the soil' },
        symmetry: { default: 1, min: 1, max: 6, step: 1, integer: true, label: 'symmetry of the soil' },
        reach: { default: 0.16, min: 0.06, max: 0.4, step: 0.01, label: 'reach' },
        growth: { default: 0.012, min: 0.004, max: 0.025, step: 0.001, label: 'growth per step' },
        branching: { default: 0.5, min: 0, max: 1, step: 0.01, label: 'branching' },
        wander: { default: 0.15, min: 0, max: 1, step: 0.01, label: 'wander' },
        speed: { default: 20, min: 5, max: 120, step: 1, label: 'steps per second' },
        seed: { default: 1, min: 0, max: 4294967295, step: 1, integer: true, label: 'seed' },
    };

    // Named parameter sets. A preset leaves out what it doesn't care about,
    // so the visitor's seed survives a change of preset.
    const PRESETS = [
        {
            id: 'spreading',
            label: 'spreading',
            note: 'the garden spreads toward the richest soil, then rests',
            params: { food: 500, symmetry: 1, reach: 0.16, growth: 0.012, branching: 0.5, wander: 0.15 },
        },
        {
            id: 'lace',
            label: 'lace',
            note: 'rich soil and eager splitting: fine branches everywhere',
            params: { food: 1200, symmetry: 1, reach: 0.12, growth: 0.01, branching: 0.85, wander: 0.05 },
        },
        {
            id: 'runners',
            label: 'runners',
            note: 'poor soil: a few long runners reach far for scattered food',
            params: { food: 120, symmetry: 1, reach: 0.34, growth: 0.014, branching: 0.15, wander: 0.1 },
        },
        {
            id: 'mandala',
            label: 'mandala',
            note: 'six-fold soil and no wandering: six arms grow alike, and on some seeds a near tie sets them apart',
            params: { food: 720, symmetry: 6, reach: 0.16, growth: 0.012, branching: 0.5, wander: 0 },
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

    // The same generator, keeping its position in the state, so a step and
    // a feeding draw from it without a closure and a garden can be copied
    function nextRandom(state) {
        state.rand = (state.rand + 0x6d2b79f5) | 0;
        const a = state.rand;
        let t = Math.imul(a ^ (a >>> 15), 1 | a);
        t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    }

    // Soil, growth and color draw from separate streams of one seed, an idea
    // from render_engine.py: a change to the colors never moves a branch
    const SOIL_STREAM = 0x9e3779b9;
    const COLOR_STREAM = 0x85ebca77;
    const GROWTH_STREAM = 0xc2b2ae35;

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

    // A preset whose every value the parameters keep, or null
    function matchPreset(params) {
        return PRESETS.find((preset) =>
            Object.keys(preset.params).every((key) => params[key] === preset.params[key])) || null;
    }

    // The turns of a k-fold symmetry, as cosine and sine pairs. Each is the
    // one before it times the first, which is built from square roots
    // alone, so every browser gets the same turns.
    const SQRT3 = Math.sqrt(3);
    const SQRT5 = Math.sqrt(5);
    const FIRST_TURN = {
        1: [1, 0],
        2: [-1, 0],
        3: [-0.5, SQRT3 / 2],
        4: [0, 1],
        5: [(SQRT5 - 1) / 4, Math.sqrt(10 + 2 * SQRT5) / 4],
        6: [0.5, SQRT3 / 2],
    };

    function turns(k) {
        const [c1, s1] = FIRST_TURN[k];
        const out = [[1, 0]];
        for (let j = 1; j < k; j++) {
            const [c, s] = out[j - 1];
            out.push([c * c1 - s * s1, c * s1 + s * c1]);
        }
        return out;
    }

    // A point in the disk of a radius, drawn by rejection from its square
    function inDisk(random, radius) {
        let x, y;
        do {
            x = 2 * random() - 1;
            y = 2 * random() - 1;
        } while (x * x + y * y > 1);
        return [x * radius, y * radius];
    }

    // The soil's fertility: a few seeded patches over a thin floor, so food
    // lies in islands with poor ground between them. The first patch is
    // around the root, so the garden has something to start on. Each patch
    // is a bump, (1 - d²/s²)² inside its spread and nothing outside, which
    // needs no exp.
    const FERTILITY_FLOOR = 0.02;

    function fertilePatches(random) {
        const count = 3 + Math.floor(random() * 4);
        const patches = [];
        for (let i = 0; i < count; i++) {
            const [x, y] = inDisk(random, i === 0 ? 0.15 : 0.8);
            const spread = i === 0 ? 0.3 + 0.15 * random() : 0.18 + 0.2 * random();
            patches.push({ x, y, spread, weight: 0.6 + 0.8 * random() });
        }
        return patches;
    }

    function fertility(patches, x, y) {
        let total = FERTILITY_FLOOR;
        for (const { x: px, y: py, spread, weight } of patches) {
            const dx = x - px;
            const dy = y - py;
            const near = 1 - (dx * dx + dy * dy) / (spread * spread);
            if (near > 0) {
                total += weight * near * near;
            }
        }
        return total;
    }

    // The initial state for a seed and parameters: the root alone at the
    // center, and food scattered over the soil where it is fertile. With a
    // symmetry of k, one share of the food is drawn and turned k times, so
    // the soil holds food rounded down to a multiple of k.
    function createState(input) {
        const params = clampParams(input);
        const soil = mulberry32(streamSeed(params.seed, SOIL_STREAM));

        const state = {
            // the organism: one node per point, each with its parent
            nodeCount: 0,
            nodeX: new Float64Array(MAX_NODES),
            nodeY: new Float64Array(MAX_NODES),
            dirX: new Float64Array(MAX_NODES),
            dirY: new Float64Array(MAX_NODES),
            parent: new Int32Array(MAX_NODES),
            depth: new Int32Array(MAX_NODES),
            children: new Int32Array(MAX_NODES),
            // tips beyond each node, which sets how thick it is drawn
            leaves: new Int32Array(MAX_NODES),
            // food: kind 0 grew in the soil, kind 1 was fed by the visitor
            foodCount: 0,
            foodLeft: 0,
            foodX: new Float64Array(MAX_FOOD),
            foodY: new Float64Array(MAX_FOOD),
            foodAlive: new Uint8Array(MAX_FOOD),
            foodKind: new Uint8Array(MAX_FOOD),
            stones: [],
            patches: fertilePatches(soil),
            steps: 0,
            idle: 0,
            eaten: 0,
            rand: streamSeed(params.seed, GROWTH_STREAM) | 0,
            // the spatial grid over the nodes, built for one reach
            gridReach: 0,
            gridSize: 0,
            gridCell: 0,
            gridHead: null,
            gridNext: new Int32Array(MAX_NODES),
            // scratch for a step
            pullX: new Float64Array(MAX_NODES),
            pullY: new Float64Array(MAX_NODES),
            pullCount: new Int32Array(MAX_NODES),
            splitting: new Uint8Array(MAX_NODES),
            leftX: new Float64Array(MAX_NODES),
            leftY: new Float64Array(MAX_NODES),
            rightX: new Float64Array(MAX_NODES),
            rightY: new Float64Array(MAX_NODES),
            pulledBy: new Int32Array(MAX_FOOD),
            unitX: new Float64Array(MAX_FOOD),
            unitY: new Float64Array(MAX_FOOD),
        };

        const k = params.symmetry;
        const share = Math.floor(params.food / k);
        // No point is more fertile than the floor and every patch's peak
        const top = FERTILITY_FLOOR + state.patches.reduce((sum, p) => sum + p.weight, 0);
        const shareX = [];
        const shareY = [];
        while (shareX.length < share) {
            const [x, y] = inDisk(soil, SOIL_RADIUS);
            if (soil() * top < fertility(state.patches, x, y)) {
                shareX.push(x);
                shareY.push(y);
            }
        }
        for (const [c, s] of turns(k)) {
            for (let i = 0; i < share; i++) {
                addFood(state, c * shareX[i] - s * shareY[i], s * shareX[i] + c * shareY[i], 0);
            }
        }

        // The root has no heading of its own, so it leans no way. With a
        // symmetry of k it starts with k shoots, one per turn of a seeded
        // heading, so the arms begin alike and meet alike soil.
        addNode(state, 0, 0, 0, 0, -1);
        if (k > 1) {
            const shoots = mulberry32(streamSeed(params.seed, SOIL_STREAM ^ GROWTH_STREAM));
            let [hx, hy] = inDisk(shoots, 1);
            const length = Math.sqrt(hx * hx + hy * hy) || 1;
            hx /= length;
            hy /= length;
            for (const [c, s] of turns(k)) {
                const dx = c * hx - s * hy;
                const dy = s * hx + c * hy;
                addNode(state, dx * params.growth, dy * params.growth, dx, dy, 0);
            }
        }
        return state;
    }

    function addFood(state, x, y, kind) {
        const i = state.foodCount++;
        state.foodX[i] = x;
        state.foodY[i] = y;
        state.foodAlive[i] = 1;
        state.foodKind[i] = kind;
        state.foodLeft++;
    }

    // Drop eaten food from the arrays, keeping the order of what's left
    function compactFood(state) {
        let kept = 0;
        for (let i = 0; i < state.foodCount; i++) {
            if (state.foodAlive[i]) {
                state.foodX[kept] = state.foodX[i];
                state.foodY[kept] = state.foodY[i];
                state.foodKind[kept] = state.foodKind[i];
                state.foodAlive[kept] = 1;
                kept++;
            }
        }
        state.foodAlive.fill(0, kept, state.foodCount);
        state.foodCount = kept;
    }

    // The grid holds every node in a cell as wide as the reach, so the
    // nearest node to a point within reach is in its cell or the 8 around it
    function ensureGrid(state, reach) {
        if (state.gridReach === reach) {
            return;
        }
        const size = Math.ceil((2 * FIELD_RADIUS) / reach);
        state.gridReach = reach;
        state.gridSize = size;
        state.gridCell = (2 * FIELD_RADIUS) / size;
        state.gridHead = new Int32Array(size * size).fill(-1);
        for (let n = 0; n < state.nodeCount; n++) {
            gridInsert(state, n);
        }
    }

    function cellOf(state, value) {
        const cell = Math.floor((value + FIELD_RADIUS) / state.gridCell);
        return Math.min(state.gridSize - 1, Math.max(0, cell));
    }

    function gridInsert(state, n) {
        if (state.gridHead === null) {
            return;
        }
        const cell = cellOf(state, state.nodeY[n]) * state.gridSize + cellOf(state, state.nodeX[n]);
        state.gridNext[n] = state.gridHead[cell];
        state.gridHead[cell] = n;
    }

    // The nearest node closer than the square root of limit2, or -1. Ties go
    // to the lower index, so the answer doesn't depend on the grid's order.
    function nearestNode(state, x, y, limit2) {
        const column = cellOf(state, x);
        const row = cellOf(state, y);
        const size = state.gridSize;
        let best = -1;
        let bestD2 = limit2;
        for (let r = Math.max(0, row - 1); r <= Math.min(size - 1, row + 1); r++) {
            for (let c = Math.max(0, column - 1); c <= Math.min(size - 1, column + 1); c++) {
                for (let n = state.gridHead[r * size + c]; n !== -1; n = state.gridNext[n]) {
                    const dx = state.nodeX[n] - x;
                    const dy = state.nodeY[n] - y;
                    const d2 = dx * dx + dy * dy;
                    if (d2 < bestD2 || (d2 === bestD2 && best !== -1 && n < best)) {
                        best = n;
                        bestD2 = d2;
                    }
                }
            }
        }
        return best;
    }

    function addNode(state, x, y, dx, dy, parent) {
        const n = state.nodeCount++;
        state.nodeX[n] = x;
        state.nodeY[n] = y;
        state.dirX[n] = dx;
        state.dirY[n] = dy;
        state.parent[n] = parent;
        state.children[n] = 0;
        state.leaves[n] = 1;
        state.depth[n] = parent === -1 ? 0 : state.depth[parent] + 1;
        if (parent !== -1) {
            // A tip that grows on stays one tip. A second branch adds a tip
            // to every node it hangs from.
            if (state.children[parent] > 0) {
                for (let p = parent; p !== -1; p = state.parent[p]) {
                    state.leaves[p]++;
                }
            }
            state.children[parent]++;
        }
        gridInsert(state, n);
        return n;
    }

    function insideStone(state, x, y) {
        for (const stone of state.stones) {
            const dx = x - stone.x;
            const dy = y - stone.y;
            if (dx * dx + dy * dy < stone.r * stone.r) {
                return true;
            }
        }
        return false;
    }

    // Grow node n one segment toward a pull. The segment keeps some of the
    // node's heading, wanders by a seeded amount, and slides along a stone
    // it would run into. It doesn't grow into a stone, past the edge, or
    // onto another node. Returns whether it grew.
    function grow(state, params, n, pullX, pullY) {
        // Pulls that cancel out, or a side of a split with none, grow nothing
        let dx = pullX;
        let dy = pullY;
        let length = Math.sqrt(dx * dx + dy * dy);
        if (length < 1e-9) {
            return false;
        }
        dx /= length;
        dy /= length;
        dx += INERTIA * state.dirX[n];
        dy += INERTIA * state.dirY[n];

        // A draw is made whether or not it is used, so the random sequence
        // doesn't depend on the wander
        let jx, jy;
        do {
            jx = 2 * nextRandom(state) - 1;
            jy = 2 * nextRandom(state) - 1;
        } while (jx * jx + jy * jy > 1);
        dx += params.wander * jx;
        dy += params.wander * jy;

        length = Math.sqrt(dx * dx + dy * dy);
        if (length < 1e-9) {
            return false;
        }
        dx /= length;
        dy /= length;

        const x0 = state.nodeX[n];
        const y0 = state.nodeY[n];
        let x = x0 + dx * params.growth;
        let y = y0 + dy * params.growth;

        for (const stone of state.stones) {
            const sx = x - stone.x;
            const sy = y - stone.y;
            if (sx * sx + sy * sy >= stone.r * stone.r) {
                continue;
            }
            // Take away the part of the heading that points into the stone
            let rx = x0 - stone.x;
            let ry = y0 - stone.y;
            const away = Math.sqrt(rx * rx + ry * ry);
            if (away < 1e-9) {
                return false;
            }
            rx /= away;
            ry /= away;
            const into = dx * rx + dy * ry;
            if (into < 0) {
                dx -= into * rx;
                dy -= into * ry;
                length = Math.sqrt(dx * dx + dy * dy);
                if (length < 1e-9) {
                    return false;
                }
                dx /= length;
                dy /= length;
                x = x0 + dx * params.growth;
                y = y0 + dy * params.growth;
            }
            break;
        }

        if (insideStone(state, x, y) || x * x + y * y > FIELD_RADIUS * FIELD_RADIUS) {
            return false;
        }
        const crowd = CROWD_RATIO * params.growth;
        if (nearestNode(state, x, y, crowd * crowd) !== -1) {
            return false;
        }
        addNode(state, x, y, dx, dy, n);
        return true;
    }

    // One step of the garden. Every piece of food pulls on the nearest node
    // within reach, or is eaten if a node is close enough. Each node that
    // is pulled grows one segment toward the average of its pulls, or, if
    // they disagree by more than the branching allows, one toward each side.
    // Nodes grown in this step wait for the next. Returns how many grew.
    function step(state, params) {
        ensureGrid(state, params.reach);
        const reach2 = params.reach * params.reach;
        const eatAt = EAT_RATIO * params.growth;
        const eat2 = eatAt * eatAt;
        const nodes = state.nodeCount;
        const { pullX, pullY, pullCount, pulledBy, unitX, unitY } = state;

        pullX.fill(0, 0, nodes);
        pullY.fill(0, 0, nodes);
        pullCount.fill(0, 0, nodes);

        let eaten = 0;
        for (let i = 0; i < state.foodCount; i++) {
            pulledBy[i] = -1;
            if (!state.foodAlive[i]) {
                continue;
            }
            const fx = state.foodX[i];
            const fy = state.foodY[i];
            const n = nearestNode(state, fx, fy, reach2);
            if (n === -1) {
                continue;
            }
            const dx = fx - state.nodeX[n];
            const dy = fy - state.nodeY[n];
            const d2 = dx * dx + dy * dy;
            if (d2 < eat2) {
                state.foodAlive[i] = 0;
                state.foodLeft--;
                eaten++;
                continue;
            }
            const d = Math.sqrt(d2);
            unitX[i] = dx / d;
            unitY[i] = dy / d;
            pulledBy[i] = n;
            pullX[n] += unitX[i];
            pullY[n] += unitY[i];
            pullCount[n]++;
        }

        // A node splits when its pulls point so many ways that their average
        // is shorter than the branching. Each side of the average then pulls
        // on its own.
        const { splitting, leftX, leftY, rightX, rightY } = state;
        splitting.fill(0, 0, nodes);
        let anySplit = false;
        for (let n = 0; n < nodes; n++) {
            if (pullCount[n] < 2 || state.children[n] > MAX_CHILDREN - 2) {
                continue;
            }
            const mx = pullX[n] / pullCount[n];
            const my = pullY[n] / pullCount[n];
            if (mx * mx + my * my < params.branching * params.branching) {
                splitting[n] = 1;
                leftX[n] = leftY[n] = rightX[n] = rightY[n] = 0;
                anySplit = true;
            }
        }
        if (anySplit) {
            for (let i = 0; i < state.foodCount; i++) {
                const n = pulledBy[i];
                if (n === -1 || !splitting[n]) {
                    continue;
                }
                if (pullX[n] * unitY[i] - pullY[n] * unitX[i] >= 0) {
                    leftX[n] += unitX[i];
                    leftY[n] += unitY[i];
                } else {
                    rightX[n] += unitX[i];
                    rightY[n] += unitY[i];
                }
            }
        }

        let grown = 0;
        for (let n = 0; n < nodes && state.nodeCount < MAX_NODES; n++) {
            if (pullCount[n] === 0 || state.children[n] >= MAX_CHILDREN) {
                continue;
            }
            if (splitting[n]) {
                grown += grow(state, params, n, leftX[n], leftY[n]) ? 1 : 0;
                if (state.nodeCount < MAX_NODES) {
                    grown += grow(state, params, n, rightX[n], rightY[n]) ? 1 : 0;
                }
            } else {
                grown += grow(state, params, n, pullX[n], pullY[n]) ? 1 : 0;
            }
        }

        state.steps++;
        state.eaten += eaten;
        state.idle = grown === 0 && eaten === 0 ? state.idle + 1 : 0;
        return grown;
    }

    // Several steps. The result depends only on the number of steps, never
    // on how they're batched into frames.
    function advance(state, params, steps) {
        let grown = 0;
        for (let s = 0; s < steps; s++) {
            grown += step(state, params);
        }
        return grown;
    }

    // At rest: nothing within reach is left to grow toward, or the organism
    // is as large as it may get. Only the visitor can change that.
    function atRest(state) {
        return state.idle >= IDLE_STEPS || state.nodeCount >= MAX_NODES;
    }

    // Food dropped by the visitor: a patch of pieces around a point inside
    // the garden, drawn from the garden's own generator. Returns how many
    // were added, which is fewer when the food arrays are full.
    function feed(state, x, y) {
        if (state.foodCount + FEED_COUNT > MAX_FOOD) {
            compactFood(state);
        }
        let added = 0;
        let tries = 0;
        while (added < FEED_COUNT && state.foodCount < MAX_FOOD && tries < FEED_COUNT * 8) {
            tries++;
            let jx, jy;
            do {
                jx = 2 * nextRandom(state) - 1;
                jy = 2 * nextRandom(state) - 1;
            } while (jx * jx + jy * jy > 1);
            const fx = x + jx * FEED_RADIUS;
            const fy = y + jy * FEED_RADIUS;
            if (fx * fx + fy * fy > SOIL_RADIUS * SOIL_RADIUS || insideStone(state, fx, fy)) {
                continue;
            }
            addFood(state, fx, fy, 1);
            added++;
        }
        if (added > 0) {
            state.idle = 0;
        }
        return added;
    }

    // The stone under a point, the last placed first, or -1
    function stoneAt(state, x, y) {
        for (let i = state.stones.length - 1; i >= 0; i--) {
            const { x: sx, y: sy, r } = state.stones[i];
            if ((x - sx) * (x - sx) + (y - sy) * (y - sy) < r * r) {
                return i;
            }
        }
        return -1;
    }

    // A stone at a point inside the garden. Food under it is gone. It can't
    // cover the root, and there are at most MAX_STONES. Returns whether it
    // was placed.
    function placeStone(state, x, y) {
        const r = STONE_RADIUS;
        if (state.stones.length >= MAX_STONES || x * x + y * y > FIELD_RADIUS * FIELD_RADIUS
            || x * x + y * y < r * r) {
            return false;
        }
        state.stones.push({ x, y, r });
        for (let i = 0; i < state.foodCount; i++) {
            if (state.foodAlive[i] && (state.foodX[i] - x) ** 2 + (state.foodY[i] - y) ** 2 < r * r) {
                state.foodAlive[i] = 0;
                state.foodLeft--;
            }
        }
        state.idle = 0;
        return true;
    }

    // Lift the stone under a point. Returns whether there was one.
    function removeStone(state, x, y) {
        const i = stoneAt(state, x, y);
        if (i === -1) {
            return false;
        }
        state.stones.splice(i, 1);
        state.idle = 0;
        return true;
    }

    // The number of tips: nodes with no branch growing from them
    function tips(state) {
        return state.leaves[0];
    }

    // The garden's colors, as hue, saturation and lightness: the old wood
    // near the root, the fresh growth at the tips, the soil's food and the
    // visitor's food. Greens and teals with seeded shifts, never one hue.
    function palette(seed) {
        const random = mulberry32(streamSeed(seed, COLOR_STREAM));
        const stem = 70 + random() * 100;
        const tip = stem + 30 + random() * 60;
        return {
            stem: { h: stem % 360, s: 25 + random() * 15, l: 34 + random() * 8 },
            tip: { h: tip % 360, s: 60 + random() * 20, l: 62 + random() * 10 },
            soil: { h: (stem + 180 + random() * 40) % 360, s: 35, l: 52 },
            fed: { h: (stem + 200 + random() * 40) % 360, s: 75, l: 66 },
        };
    }

    const api = {
        EAT_RATIO,
        FEED_COUNT,
        FEED_RADIUS,
        FIELD_RADIUS,
        IDLE_STEPS,
        MAX_CHILDREN,
        MAX_FOOD,
        MAX_NODES,
        MAX_STONES,
        CROWD_RATIO,
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
        removeStone,
        step,
        stoneAt,
        streamSeed,
        tips,
        turns,
    };

    if (typeof module !== 'undefined' && module.exports) {
        module.exports = api;
    } else {
        root.ArtificialGarden = api;
    }
})(typeof globalThis !== 'undefined' ? globalThis : this);
