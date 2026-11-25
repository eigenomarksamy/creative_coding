// What every engine's page shares: the loop and its lifecycle, the panels,
// the preset menu, the seed box, the sliders, and the share controls.
//
// A classic script, not a module, because the gallery has to work from
// file://. The page loads it after engine-sim.js and its own sim.js, and
// before its own script, which calls EnginePage.create with what only the
// engine knows: its simulation, how it draws, how it steps and when it is
// at rest. Everything else is here, written once. Node gets the few pure
// helpers below, so `node --test` can check them.
//
// The page's markup is the contract: the ids and classes engine.css styles,
// listed in the README's section on adding an engine.

(function (root) {
    'use strict';

    // Never more than this much time in one frame, so a stall can't turn
    // into a burst
    const MAX_FRAME_MS = 100;
    const REDUCED_MOTION_SPEED = 0.25;
    const MAX_PIXEL_RATIO = 2;
    const READOUT_MS = 200;

    // The address follows the settings, but not on every step of a slider:
    // browsers throttle a page that rewrites its URL too often
    const LINK_DELAY_MS = 250;
    const LINK_PROBLEM_NOTE = 'part of this link couldn’t be used, so those settings are at their defaults or limits';
    const NO_CLIPBOARD = 'couldn’t copy here: the link above is selected, ready to copy';

    // A log slider runs from 0 to this, and maps onto the range
    const LOG_STEPS = 1000;

    // Sliders show a parameter's value, or a log parameter's position
    function toSlider(spec, value) {
        return spec.log
            ? (Math.log(value / spec.min) / Math.log(spec.max / spec.min)) * LOG_STEPS
            : value;
    }

    function fromSlider(spec, value) {
        return spec.log ? spec.min * Math.pow(spec.max / spec.min, value / LOG_STEPS) : value;
    }

    // A value as its slider shows it: two figures on a log slider, a whole
    // number on a whole step, and otherwise as many places as the step has,
    // or as many as the parameter's places asks for
    function formatParam(spec, value) {
        if (spec.log) {
            return value.toPrecision(2);
        }
        if (Number.isInteger(spec.step)) {
            return String(value);
        }
        const places = spec.places !== undefined
            ? spec.places
            : Math.max(0, -Math.floor(Math.log10(spec.step)));
        return value.toFixed(places);
    }

    // engine, what only it knows:
    //
    // - name: the folder's name, which save image puts in the file's name
    // - sim: its sim.js, with PARAMS, PRESETS, clampParams, encodeLink and
    //   decodeLink. PARAMS needs a seed.
    // - sliders: [{ heading, keys }] in panel order, heading optional
    // - restartKeys: the parameters that decide the initial state, so a
    //   change to one starts the run again
    // - maxStepsPerFrame: the most steps page.steps gives one frame
    // - restart(): build the state again from page.params
    // - fit(): place the picture in page.width by page.height, between the
    //   header and the bar
    // - step(elapsed): move the run on by elapsed milliseconds, and call
    //   page.changed() if the picture changed
    // - draw(): the whole picture, setting every context state it uses,
    //   because a resize resets them
    // - readout(): the numbers under the note
    // - atRest(): checked after every frame. true stops the loop until the
    //   visitor does something.
    //
    // and, if it needs them:
    //
    // - drawStill(): draw with the loop stopped, if that differs from draw
    // - drawPicture(): the picture save image keeps, without anything drawn
    //   over it for the visitor only
    // - measured(ratio): the canvas has a new size
    // - stayAtRest(): when the visitor does something, whether the run is
    //   still at rest. Without it, anything the visitor does wakes it.
    // - onRest(), onWake(): the run stopped, or started again
    // - onRefresh(): the visitor did something, before the loop decides
    //   whether to wake
    // - paramChanged(key, restarted): after a slider set page.params[key]
    // - restarted(): after a reset, a preset, a new seed or a link
    // - copied(): what copy link says once the link is copied: what the
    //   link can't rebuild of this run
    // - heldKey(event): a key that may repeat while held. true if handled.
    // - key(event): any other key, before the shared ones. true if handled.
    // - escape(): escape with no panel open
    // - ready(): after the first restart, before the first frame
    function create(engine) {
        const { PARAMS, PRESETS, clampParams, decodeLink, encodeLink } = engine.sim;
        const restartKeys = engine.restartKeys || [];
        const drawStill = engine.drawStill || engine.draw;

        const byId = (id) => document.getElementById(id);
        const canvas = byId('stage');
        const ctx = canvas.getContext('2d', { alpha: false });
        const noteEl = byId('note');
        const pauseButton = byId('pause');
        const presetSelect = byId('preset');
        const seedInput = byId('seed');
        const linkInput = byId('link');
        const shareStatus = byId('share-status');
        const controlsPanel = byId('controls');
        const controlsBody = controlsPanel.querySelector('.panel');
        const header = document.querySelector('.header');
        const bar = document.querySelector('.bar');
        const panels = [...document.querySelectorAll('.bar details')];
        const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

        let params = clampParams(PRESETS[0].params);
        let width = 0;
        let height = 0;

        let frame = null;
        let lastFrame = null;
        let lastReadout = 0;
        let budget = 0;
        let paused = false;
        let pageVisible = !document.hidden;
        let onScreen = true;

        // A frame is drawn only when the picture has changed, and the loop
        // stops while the run is at rest
        let dirty = true;
        let resting = false;

        // The hash this page last read or wrote, and a pending write.
        // Nothing is written until the visitor changes a setting.
        let linkShown = location.hash.replace(/^#/, '');
        let linkTimer = null;

        // The loop

        // Starting again from the seed: the same parameters and seed always
        // give the same state
        function restart() {
            budget = 0;
            engine.restart();
        }

        // Whole steps for this frame at perSecond, slower under reduced
        // motion. What is left over waits for the next frame.
        function steps(elapsed, perSecond) {
            const speed = perSecond * (reducedMotion.matches ? REDUCED_MOTION_SPEED : 1);
            budget += (elapsed / 1000) * speed;
            const count = Math.min(Math.floor(budget), engine.maxStepsPerFrame);
            budget = budget - count >= 1 ? 0 : budget - count;
            return count;
        }

        function rest() {
            resting = true;
            if (engine.onRest) {
                engine.onRest();
            }
            drawStill();
            engine.readout();
            updateRunning();
        }

        // The loop runs only while there is something to see: not paused,
        // the page visible, the canvas on screen, and the run not at rest
        function tick(now) {
            frame = requestAnimationFrame(tick);
            const elapsed = lastFrame === null ? 0 : Math.min(now - lastFrame, MAX_FRAME_MS);
            lastFrame = now;

            engine.step(elapsed);
            if (dirty) {
                dirty = false;
                engine.draw();
            }
            if (now - lastReadout >= READOUT_MS) {
                lastReadout = now;
                engine.readout();
            }
            if (engine.atRest()) {
                rest();
            }
        }

        function updateRunning() {
            const shouldRun = !paused && pageVisible && onScreen && !resting;
            if (shouldRun && frame === null) {
                lastFrame = null;
                frame = requestAnimationFrame(tick);
            } else if (!shouldRun && frame !== null) {
                cancelAnimationFrame(frame);
                frame = null;
            }
        }

        // Anything the visitor does may set the run going again, and with
        // the loop stopped, a change still has to reach the screen
        function refresh() {
            if (engine.onRefresh) {
                engine.onRefresh();
            }
            dirty = true;
            if (resting && !(engine.stayAtRest && engine.stayAtRest())) {
                resting = false;
                if (engine.onWake) {
                    engine.onWake();
                }
                updateRunning();
            }
            if (frame === null) {
                drawStill();
            }
            engine.readout();
        }

        function setPaused(value) {
            paused = value;
            pauseButton.textContent = paused ? 'play' : 'pause';
            updateRunning();
        }

        // The canvas at the screen's resolution, up to twice its CSS size
        function measure() {
            const ratio = Math.min(window.devicePixelRatio || 1, MAX_PIXEL_RATIO);
            width = canvas.clientWidth;
            height = canvas.clientHeight;
            canvas.width = Math.round(width * ratio);
            canvas.height = Math.round(height * ratio);
            ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
            if (engine.measured) {
                engine.measured(ratio);
            }
            document.documentElement.style.setProperty('--bar-height', `${bar.offsetHeight}px`);
        }

        function resize() {
            measure();
            engine.fit();
            drawStill();
        }

        // Controls

        const sliders = new Map();

        function buildSliders() {
            const parent = byId('sliders');

            for (const { heading, keys } of engine.sliders) {
                if (heading) {
                    const title = document.createElement('p');
                    title.className = 'group';
                    title.textContent = heading;
                    parent.append(title);
                }

                for (const key of keys) {
                    const spec = PARAMS[key];
                    const row = document.createElement('div');
                    row.className = 'row';

                    const label = document.createElement('label');
                    label.htmlFor = `param-${key}`;
                    label.textContent = spec.label;

                    const output = document.createElement('output');
                    output.htmlFor = `param-${key}`;

                    const input = document.createElement('input');
                    input.id = `param-${key}`;
                    input.type = 'range';
                    input.min = spec.log ? 0 : spec.min;
                    input.max = spec.log ? LOG_STEPS : spec.max;
                    input.step = spec.log ? 1 : spec.step;

                    input.addEventListener('input', () => {
                        const value = fromSlider(spec, Number(input.value));
                        params = clampParams({ ...params, [key]: value });
                        output.value = formatParam(spec, params[key]);
                        leavePreset();
                        const restarting = restartKeys.includes(key);
                        if (restarting) {
                            restart();
                        }
                        if (engine.paramChanged) {
                            engine.paramChanged(key, restarting);
                        }
                        refresh();
                        settingsChanged();
                    });

                    row.append(label, output, input);
                    parent.append(row);
                    sliders.set(key, { input, output });
                }
            }
        }

        function syncControls() {
            for (const [key, { input, output }] of sliders) {
                input.value = toSlider(PARAMS[key], params[key]);
                output.value = formatParam(PARAMS[key], params[key]);
            }
            seedInput.value = params.seed;
        }

        function restarted() {
            if (engine.restarted) {
                engine.restarted();
            }
        }

        function applyPreset(preset) {
            params = clampParams({ ...params, ...preset.params });
            presetSelect.value = preset.id;
            noteEl.textContent = preset.note;
            syncControls();
            restart();
            refresh();
            restarted();
            settingsChanged();
        }

        function leavePreset() {
            presetSelect.value = '';
            noteEl.textContent = '';
        }

        function setSeed(value) {
            params = clampParams({ ...params, seed: value });
            seedInput.value = params.seed;

            // A preset with its own seed only keeps its promise on that seed
            const preset = PRESETS.find(({ id }) => id === presetSelect.value);
            if (preset && 'seed' in preset.params && preset.params.seed !== params.seed) {
                leavePreset();
            }
            restart();
            refresh();
            restarted();
            settingsChanged();
        }

        function nextSeed() {
            setSeed(params.seed >= PARAMS.seed.max ? PARAMS.seed.min : params.seed + 1);
        }

        function resetRun() {
            restart();
            refresh();
            restarted();
        }

        // Share links: the hash holds the run's initial configuration, in
        // the format engine-sim.js describes

        function linkUrl() {
            return `${location.href.split('#')[0]}#${encodeLink(params)}`;
        }

        function writeLink() {
            clearTimeout(linkTimer);
            linkTimer = null;
            const text = encodeLink(params);
            if (text === linkShown) {
                return;
            }
            linkShown = text;
            try {
                history.replaceState(history.state, '', `#${text}`);
            } catch (error) {
                // Changing only the hash doesn't reload the page
                location.replace(`#${text}`);
            }
        }

        function settingsChanged() {
            shareStatus.textContent = '';
            linkInput.hidden = true;
            clearTimeout(linkTimer);
            linkTimer = setTimeout(writeLink, LINK_DELAY_MS);
        }

        // Settings from a link: on load, or when a link is pasted into the
        // open page, which changes the hash without a reload
        function applyLink(text) {
            const link = decodeLink(text);
            shareStatus.textContent = '';
            linkInput.hidden = true;
            params = link.params;
            if (link.preset) {
                presetSelect.value = link.preset;
                noteEl.textContent = PRESETS.find(({ id }) => id === link.preset).note;
            } else {
                leavePreset();
            }
            if (link.problems.length > 0) {
                noteEl.textContent = LINK_PROBLEM_NOTE;
            }
            syncControls();
        }

        window.addEventListener('hashchange', () => {
            const text = location.hash.replace(/^#/, '');
            if (text === linkShown) {
                return;
            }
            clearTimeout(linkTimer);
            linkTimer = null;
            linkShown = text;
            applyLink(text);
            restart();
            refresh();
            restarted();
        });

        // The answer shows in the controls panel, which a key may have left
        // closed. It is cleared first, so the same words are announced
        // again. In a small frame the panel scrolls, and the answer is at
        // its end, under the link.
        function setStatus(text) {
            controlsPanel.open = true;
            shareStatus.textContent = '';
            setTimeout(() => {
                shareStatus.textContent = text;
                controlsBody.scrollTop = controlsBody.scrollHeight;
            }, 50);
        }

        async function copyLink() {
            writeLink();
            const url = linkUrl();
            let copied = false;
            try {
                await navigator.clipboard.writeText(url);
                copied = true;
            } catch (error) {
                // No clipboard here, as in some frames: the field below
                // holds the link, selected, to copy by hand
            }

            linkInput.value = url;
            linkInput.hidden = false;
            controlsPanel.open = true;
            if (!copied) {
                linkInput.focus();
                linkInput.select();
                setStatus(NO_CLIPBOARD);
            } else {
                setStatus(engine.copied());
            }
        }

        // The picture as it is now, at the canvas's own resolution. toBlob
        // copies the canvas when it's called, so anything drawn over the
        // picture for the visitor can come back straight after.
        function saveImage() {
            const name = `${engine.name}-${params.seed}.png`;
            (engine.drawPicture || engine.draw)();
            canvas.toBlob((blob) => {
                if (!blob) {
                    setStatus('couldn’t save the image here');
                    return;
                }
                const url = URL.createObjectURL(blob);
                const anchor = document.createElement('a');
                anchor.href = url;
                anchor.download = name;
                document.body.append(anchor);
                anchor.click();
                anchor.remove();
                setTimeout(() => URL.revokeObjectURL(url), 10000);
                setStatus(`image saved as ${name}`);
            }, 'image/png');
            if (engine.drawPicture) {
                engine.draw();
            }
        }

        byId('copy-link').addEventListener('click', copyLink);
        byId('save-image').addEventListener('click', saveImage);

        for (const preset of PRESETS) {
            presetSelect.add(new Option(preset.label, preset.id));
        }
        const customOption = new Option('custom', '');
        customOption.disabled = true;
        presetSelect.add(customOption);

        presetSelect.addEventListener('change', () => {
            applyPreset(PRESETS.find((preset) => preset.id === presetSelect.value));
        });

        seedInput.min = PARAMS.seed.min;
        seedInput.max = PARAMS.seed.max;
        seedInput.step = PARAMS.seed.step;
        seedInput.addEventListener('change', () => setSeed(seedInput.value));

        byId('next-seed').addEventListener('click', nextSeed);
        byId('reset').addEventListener('click', resetRun);
        pauseButton.addEventListener('click', () => setPaused(!paused));

        // One panel at a time: they open in the same place
        for (const panel of panels) {
            panel.addEventListener('toggle', () => {
                if (panel.open) {
                    for (const other of panels) {
                        if (other !== panel) {
                            other.open = false;
                        }
                    }
                }
            });
        }

        // Keys reach the page only while it has focus, so every action also
        // has a button
        document.addEventListener('keydown', (event) => {
            if (event.ctrlKey || event.metaKey || event.altKey) {
                return;
            }
            if (engine.heldKey && engine.heldKey(event)) {
                return;
            }

            // Any other held key must not restart the run over and over
            if (event.repeat) {
                return;
            }

            const target = event.target;

            // Escape closes an open panel, from anywhere inside it too, and
            // leaves focus on its button
            if (event.key === 'Escape') {
                const open = panels.find((panel) => panel.open);
                if (open) {
                    open.open = false;
                    open.querySelector('summary').focus();
                } else if (engine.escape) {
                    engine.escape();
                }
                return;
            }

            if (target.closest('input[type="number"], input[type="text"], select')) {
                return;
            }
            if (engine.key && engine.key(event)) {
                return;
            }

            const key = event.key.toLowerCase();
            if (event.key === ' ') {
                // Space already presses whatever button has focus
                if (target.closest('button, summary')) {
                    return;
                }
                event.preventDefault();
                setPaused(!paused);
            } else if (key === 'r') {
                resetRun();
            } else if (key === 'n') {
                nextSeed();
            } else if (key === 'c') {
                copyLink();
            } else if (key === 's') {
                saveImage();
            } else if (PRESETS[Number(event.key) - 1]) {
                applyPreset(PRESETS[Number(event.key) - 1]);
            }
        });

        // Lifecycle: stop when hidden, off screen or torn down

        function onVisibilityChange() {
            pageVisible = !document.hidden;
            updateRunning();
        }

        const resizeObserver = new ResizeObserver(resize);
        const screenObserver = 'IntersectionObserver' in window
            ? new IntersectionObserver((entries) => {
                onScreen = entries[entries.length - 1].isIntersecting;
                updateRunning();
            })
            : null;

        function connect() {
            document.addEventListener('visibilitychange', onVisibilityChange);
            resizeObserver.observe(canvas);
            if (screenObserver) {
                screenObserver.observe(canvas);
            }
        }

        function disconnect() {
            document.removeEventListener('visibilitychange', onVisibilityChange);
            resizeObserver.disconnect();
            if (screenObserver) {
                screenObserver.disconnect();
            }
            if (frame !== null) {
                cancelAnimationFrame(frame);
                frame = null;
            }
        }

        window.addEventListener('pagehide', disconnect);
        window.addEventListener('pageshow', (event) => {
            // Back from the page cache, where pagehide has stopped everything
            if (event.persisted) {
                connect();
                updateRunning();
            }
        });

        // The title and concept come from the meta block in the head, which
        // the gallery reads too, so they're written once
        try {
            const meta = JSON.parse(byId('meta').textContent);
            if (meta.title) {
                byId('title').textContent = meta.title;
                byId('about-title').textContent = meta.title;
            }
            byId('about-concept').textContent = meta.concept || '';
        } catch (error) {
            // The names written in the page stay as they are
        }

        // Comparing windows works across origins, also from file://
        document.documentElement.classList.toggle('framed', window.self !== window.top);

        // The first preset, or the link the page was opened with, then the
        // first frame
        function start() {
            buildSliders();
            syncControls();
            presetSelect.value = PRESETS[0].id;
            noteEl.textContent = PRESETS[0].note;
            if (linkShown !== '') {
                applyLink(linkShown);
            }
            restart();
            if (engine.ready) {
                engine.ready();
            }
            measure();
            engine.fit();
            engine.readout();
            engine.draw();
            connect();
            updateRunning();
        }

        return {
            canvas,
            ctx,
            header,
            bar,
            reducedMotion,
            get params() {
                return params;
            },
            get width() {
                return width;
            },
            get height() {
                return height;
            },
            // Whether a frame is coming, so a change will be drawn by itself
            get running() {
                return frame !== null;
            },
            get resting() {
                return resting;
            },
            changed() {
                dirty = true;
            },
            refresh,
            start,
            steps,
        };
    }

    const api = { create, formatParam, fromSlider, toSlider };

    if (typeof module !== 'undefined' && module.exports) {
        module.exports = api;
    } else {
        root.EnginePage = api;
    }
})(typeof globalThis !== 'undefined' ? globalThis : this);
