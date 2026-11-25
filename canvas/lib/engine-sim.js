// What every engine's simulation shares: a seeded generator, separate
// streams from one seed, and a parameter set with its presets and share
// links.
//
// Numbers only, no canvas and no DOM, so `node --test` can check all of it.
// A classic script, not a module, because the gallery has to work from
// file://: the browser gets the global EngineSim, loaded before an engine's
// sim.js, and node gets module.exports. Every function depends only on its
// arguments, and uses only integer operations and + - * /, which give the
// same bits in every browser.

(function (root) {
    'use strict';

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

    // One seed gives each part of an engine a stream of its own, an idea
    // from render_engine.py: a change to the colors never moves the shape.
    // An engine names its streams with constants of its own.
    function streamSeed(seed, stream) {
        let h = Math.imul((seed ^ stream) >>> 0, 0x9e3779b1);
        h = Math.imul(h ^ (h >>> 16), 0x85ebca6b);
        return (h ^ (h >>> 13)) >>> 0;
    }

    // A plain decimal number, as String writes one or a visitor types it
    const LINK_NUMBER = /^[+-]?(\d+\.?\d*|\.\d+)(e[+-]?\d+)?$/i;

    // An engine's parameters, from three declarations:
    //
    // - spec: every parameter with its default, min and max, and integer
    //   for a whole number. clampParams enforces them. A seed is a
    //   parameter like any other, a whole number from 0 to 4294967295.
    // - presets: named parameter sets, each { id, label, note, params }. A
    //   preset leaves out what it doesn't care about, so the visitor's
    //   other values survive a change of preset, and one that sets a seed
    //   keeps its promise only on that seed.
    // - linkKeys: every key of spec once, in the order a share link writes
    //   them.
    //
    // A share link holds a run's initial configuration: the seed and every
    // parameter, which give the same start in every browser, and never
    // what a visitor did during the run, which parameters can't rebuild.
    // The text is a URL hash, read with URLSearchParams. Every value is a
    // decimal number, written as String writes it, so it reads back to the
    // same bits. A link lists every parameter, so it keeps its run if a
    // default or a preset changes later.
    function paramSet(spec, presets, linkKeys) {
        const keys = Object.keys(spec);
        if (linkKeys.length !== keys.length || keys.some((key) => !linkKeys.includes(key))) {
            throw new Error('linkKeys must list every parameter once');
        }

        function defaults() {
            const params = {};
            for (const key of keys) {
                params[key] = spec[key].default;
            }
            return params;
        }

        // A complete, valid parameter set from any input: missing or
        // non-numeric values take their default, the rest are held to their
        // range
        function clampParams(input) {
            const source = input || {};
            const params = {};
            for (const key of keys) {
                const range = spec[key];
                const raw = source[key];
                const value = typeof raw === 'string' && raw.trim() !== '' ? Number(raw) : raw;
                if (typeof value !== 'number' || !Number.isFinite(value)) {
                    params[key] = range.default;
                    continue;
                }
                const held = Math.min(range.max, Math.max(range.min, value));
                params[key] = range.integer ? Math.round(held) : held;
            }
            return params;
        }

        function encodeLink(input) {
            const params = clampParams(input);
            const query = new URLSearchParams();
            for (const key of linkKeys) {
                query.set(key, String(params[key]));
            }
            return query.toString();
        }

        // A preset whose every value the parameters keep, or null
        function matchPreset(params) {
            return presets.find((preset) =>
                Object.keys(preset.params).every((key) => params[key] === preset.params[key])) || null;
        }

        // Any text, from a link or typed by hand, to a complete, valid
        // parameter set. A link may also name a preset (preset=<id>) for the
        // values it leaves out. A value that isn't a plain decimal number
        // takes its default, one outside its range is held to it, and
        // unknown keys are ignored. problems lists every key that couldn't
        // be used as it was written.
        function decodeLink(text) {
            const query = new URLSearchParams(String(text || '').replace(/^[#?]+/, ''));
            const problems = [];

            let named = null;
            if (query.has('preset')) {
                named = presets.find(({ id }) => id === query.get('preset')) || null;
                if (!named) {
                    problems.push('preset');
                }
            }

            const given = {};
            for (const key of keys) {
                if (!query.has(key)) {
                    continue;
                }
                const raw = query.get(key).trim();
                const value = Number(raw);
                if (!LINK_NUMBER.test(raw) || !Number.isFinite(value)) {
                    problems.push(key);
                    continue;
                }
                given[key] = value;
            }

            const params = clampParams({ ...(named ? named.params : {}), ...given });
            for (const key of Object.keys(given)) {
                if (params[key] !== given[key]) {
                    problems.push(key);
                }
            }

            const preset = matchPreset(params);
            return { params, preset: preset ? preset.id : null, problems };
        }

        return { clampParams, decodeLink, defaults, encodeLink, matchPreset };
    }

    const api = {
        mulberry32,
        paramSet,
        streamSeed,
    };

    if (typeof module !== 'undefined' && module.exports) {
        module.exports = api;
    } else {
        root.EngineSim = api;
    }
})(typeof globalThis !== 'undefined' ? globalThis : this);
