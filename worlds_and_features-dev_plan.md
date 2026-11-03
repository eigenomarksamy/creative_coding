# creative coding: worlds and engines

dev plan for growing `creative_coding` (this repo) from a gallery grouped by toolkit into a collection of interactive generative engines. each engine explores one visual language, mathematical system, or idea, and visitors can watch it, steer it, or build with it.

**reading guide.** §0 is the current state. §1 describes the repo as it is. §2 and §3 are the rules and vocabulary that every ticket uses. §4 is the work. §5 is the checklist each ticket must pass. §6 records the design decisions (provisional, made 2026-11-03). §7 is the backlog. appendix A is work for a different repo. the log at the bottom records what has shipped.

**external references.** D2, D3, D5, D6 and L1–L8 are defined in the `eigenomar.com` dev plan, not in this repo.

---

## 0. state

- **next ticket:** CC1
- **milestone 1:** CC5, CC7 and CC10 are published, giving three engines in three worlds (dynamical, organic, mystic), built on the CC2–CC3 taxonomy.
- **scope of this repo:** CC1–CC11. EC1–EC2 and the changes to the main plan (appendix A) belong to `eigenomar.com` and are never implemented here.
- **repos:** `creative_coding` is the home of every engine, algorithm, renderer, control and gallery page, and no new repo is needed. `eigenomar.com` presents the project under art and links to it. `gallery.eigenomar.com` is served from this repo (see §1).
- **long-term direction:** independent engines connected by their concepts, whose systems and interactions might later be combined without losing what makes each one distinct. there is no general composer until the gates in §7 are met.

## 1. repo facts

these were observed on 2026-11-03 while restructuring this plan. CC1 confirms and extends this section, and it should be kept up to date afterwards.

| area | fact | what it means for the plan |
|---|---|---|
| stack | static site with no package.json, bundler, test runner or type checker. the only build step is `python build_gallery.py` (needs Pillow) | in §5, "tests, type checks and build pass" means the build runs clean and any tests a ticket adds pass |
| build output | the build writes `gallery/gallery-data.js` and `gallery/thumbs/`, both gitignored | run the build before viewing or deploying |
| deploy | Cloudflare Workers static assets (`wrangler.jsonc`). the whole repo is served at `gallery.eigenomar.com`, `_redirects` sends `/` to `/gallery/`, and `.assetsignore` keeps the rest out | answers CC1's deploy question: this repo is the gallery |
| current taxonomy | `CATEGORIES` in `build_gallery.py` groups pieces by toolkit: pygame, pycairo (12., sketches, render engine, cosmos) and canvas. the hierarchy is category → group → items, and each item has a `kind` (`image` or `sketch`) and a `meta` dict | worlds are a new axis that cuts across toolkits |
| current filtering | a group can declare `facets` (keys into `item.meta`), and `collect_facets` turns them into chips. filters live in hash params, e.g. `#/pycairo/render-engine?scene=fault line` | CC3 extends this mechanism rather than adding a second one |
| routing | `gallery/gallery.js` uses hash routes so the gallery works when opened from `file://` | the gallery must keep working from disk |
| interactive sketches | there are 3: `canvas/gol.html`, `canvas/snake1.html` and `canvas/snake2.html`. each is a single file of inline vanilla JS on Canvas 2D, using unseeded `Math.random` and a `requestAnimationFrame` loop, with no pause, reset, keyboard or reduced-motion handling. the title comes from `<title>` and `meta` is `{}` | these are the only existing experiments that are interactive |
| how sketches are found | `collect_sketch_items` scans only the top level of `canvas/*.html` | engines live in folders (Q5), so CC5 extends the scan to `canvas/<id>/index.html` |
| how sketches are shown | the gallery shows a ▶ poster, clicking it loads the sketch in an `<iframe>`, and "open ↗" links straight to the file | each sketch already has a stable direct URL: `/canvas/<name>.html` |
| static renders | hundreds of images from `cc_pycairo/` and `cc_pygame/`, none of them interactive | they get worlds, set once per series (Q1) |
| JS style | `gallery.js` is an ES5 IIFE using `var` and no modules | match this style unless a ticket gives a reason not to |
| theming | the gallery has no light/dark switch and no `prefers-reduced-motion` handling | the §5 theme check does not apply yet |
| local tools | node v20 is installed | `node --test` is the test runner, with no dependencies (Q4) |

## 2. constraints

these apply to every ticket. text in parentheses says how a rule applies in this repo.

- **minimal shell, rich insides.** the gallery interface stays restrained, while individual engines can be intricate, colorful and computationally expressive.
- **concept before aesthetics.** each engine investigates an idea, such as causality, emergence, perception, entropy or infinity, rather than only producing an attractive pattern.
- **reuse after the second use.** build one engine completely before extracting anything shared, and don't build a framework early.
- **independent experiences.** each published engine has a stable URL and runs without loading any other experiment (each engine is its own folder, `canvas/<id>/`, with `index.html` as its page).
- **deterministic where possible.** the same seed and parameters give the same initial state.
- **exploration without instruction.** a visitor understands the basic interaction within seconds. advanced controls are available but stay out of the way.
- **accessible by design.** support reduced motion, pause and reset, keyboard use and responsive canvases, give alternatives to anything that depends on audio, and never flash rapidly.
- **bounded performance.** scale workloads to the device, pause when the engine is hidden or off-screen, and release resources on teardown (here that means the tab is hidden, the iframe is removed, or the visitor leaves the page).
- **local-first.** no accounts and no backend. saved settings stay on the visitor's device.
- **preserve existing work.** audit before replacing structures, adding dependencies or rebuilding features. existing URLs and routes keep working.
- **works from disk.** this rule comes from §1, not from the original guardrails. the gallery opens from `file://`, and Chromium blocks ES-module imports there, so shared JS must be loaded as classic scripts or inlined.

## 3. vocabulary

### worlds

a world is an experiment's artistic identity. worlds are categories for discovery, not separate code architectures. each experiment has one primary world and any number of secondary worlds, and it appears once under every world it belongs to, without being duplicated.

| slug | identity | concepts |
|---|---|---|
| abstract | expressive, nonrepresentational compositions | chaos, emotion, entropy |
| geometric | patterns, symmetry, transformations, fractals | order, repetition, precision |
| mystic | sigils, celestial diagrams, symbolic structures | ritual, symbolism, transcendence |
| mechanical | gears, linkages, kinetic sculptures | causality, interdependence, rhythm |
| organic | growth, branching, evolving organisms | life, adaptation, emergence |
| fluid | liquid motion, turbulence, diffusion | flow, transformation, continuity |
| cosmic | orbits, gravitational systems, celestial structures | scale, infinity, spacetime |
| glitch | distortion, feedback, digital corruption | instability, noise, fragmentation |
| typographic | generative lettering, glyphs, procedural poetry | language, meaning, communication |
| perceptual | optical illusions, moiré patterns, impossible forms | ambiguity, perception, paradox |
| dynamical | attractors, phase spaces, nonlinear simulations | determinism, complexity, chaos |
| topographic | generative terrain, contours, imaginary landscapes | space, geography, formation |

### composition model

an experiment is described along three independent dimensions: its **world** (how it looks and feels), its **system** (the rules that drive it) and its **interaction** (how the visitor influences it). for now this is only a convention for metadata and design. a general-purpose composer is parked (§7).

the slugs below are proposals, and CC2 finalizes them.

| system slug | meaning |
|---|---|
| particle-fields | particle fields and flocking |
| attractors | attractors and dynamical systems |
| cellular-automata | cellular automata |
| reaction-diffusion | reaction-diffusion |
| recursive-growth | recursive growth and L-systems |
| oscillators | oscillators and coupled systems |
| procedural-geometry | procedural geometry |
| noise-fields | noise fields and turbulence |
| constraints | physical constraints and linkages |
| image-feedback | image transformations and feedback |

| interaction slug | meaning |
|---|---|
| pointer | pointer attraction and repulsion |
| gesture-drawing | gesture drawing |
| touch-drag | touch and drag |
| parameter-manipulation | parameter manipulation (the original metadata example said `parameter-mutation`; CC2 picks one) |
| rule-mutation | rule mutation |
| placement | placing obstacles or resources |
| sound-input | sound and rhythm input |
| autonomous | autonomous evolution |

**modes.** declare only the modes that give meaningful behavior:

- `observe`: the system evolves on its own, with optional parameter controls.
- `intervene`: the visitor disturbs or redirects the system.
- `compose`: the visitor builds patterns, structures or rules with the engine.

**example compositions** (world + system + interaction):

- mystic + particle-fields + gesture-drawing: procedural sigils that dissolve into constellations.
- mechanical + oscillators + sound-input: a kinetic machine that responds to rhythmic patterns.
- organic + cellular-automata + placement: an artificial ecosystem the visitor influences indirectly.
- cosmic + attractors + parameter-manipulation: a miniature universe whose trajectories change with its physical constants.

### metadata (Q1, Q2)

the vocabulary (the worlds and the tags above) lives as Python constants in `build_gallery.py`. the build rejects unknown values and passes the vocabulary into `gallery-data.js`.

**engines and live sketches** carry a JSON block in their own page. the build reads it, and the page can read it to show its own title and concept, which also works from disk:

```html
<script type="application/json" id="meta">
{
  "id": "strange-attractor",
  "title": "strange attractor",
  "world": "dynamical",
  "worlds": ["abstract", "geometric"],
  "systems": ["attractors", "particle-fields"],
  "interactions": ["parameter-manipulation", "pointer"],
  "modes": ["observe", "intervene"],
  "concept": "determinism and chaos"
}
</script>
```

`world` is the one primary world, `worlds` lists optional secondary worlds, and `concept` is a short line on what the piece explores. live sketches must have `interactions` and `modes`.

**image series** set the same fields once on their group in `CATEGORIES`, and every image in the group inherits them. `interactions` and `modes` don't apply. per-image overrides can come later if a series needs them.

```python
{
    "id": "cosmos",
    # ...existing fields...
    "world": "cosmic",                 # example values, CC2 sets the real ones
    "worlds": ["geometric"],
    "systems": ["oscillators", "procedural-geometry"],
    "concept": "the universe as mathematical structure",
}
```

---

## 4. tickets

sizes: **S** takes under an hour and **M** fills one session. anything larger is split before work starts. in the "needs" column, a ticket ID is a hard dependency, and "after X" is only a choice of order.

| ID | ticket | size | needs | status |
|---|---|---|---|---|
| CC1 | repository and gallery audit | S | none | todo |
| CC2 | worlds taxonomy and metadata | S | CC1 | todo |
| CC3 | world-based gallery discovery | M | CC2 | todo |
| CC4 | strange attractor: core | M | CC1 | todo |
| CC5 | strange attractor: publish | M | CC3, CC4 | todo |
| CC6 | artificial garden: core | M | after CC5 | todo |
| CC7 | artificial garden: publish | M | CC6 | todo |
| CC8 | reusable engine conventions | M | CC5, CC7, CC11 | todo |
| CC9 | sigil laboratory: core | M | CC8 | todo |
| CC10 | sigil laboratory: publish | M | CC9 | todo |
| CC11 | share links and image export | M | CC5 | todo |

**order:** CC1 → CC2 → CC3 → CC4 → CC5 → CC6 → CC7 → CC11 → CC8 → CC9 → CC10, then EC1 → EC2 in `eigenomar.com`. CC4 needs only CC1, so it can run alongside CC2–CC3. CC11 comes before CC8 so that share links and export exist in two engines before anything is extracted (Q6).

### CC1 · repository and gallery audit · S

- **do:**
  - inspect the repo structure, rendering technologies, how experiments are organized, routing and deployment. §1 is a first pass.
  - list the existing engines with the visual style, system and interaction of each.
  - check what exists for parameters, presets, seeds, animation lifecycle, export and mobile interaction.
  - confirm the deployment target. this is already answered in §1: the repo deploys to `gallery.eigenomar.com`.
  - record which proposed capabilities already exist and which are genuinely missing.
  - document the current architecture and conventions.
- **output:** an updated §1 in this file, plus the README if a convention is worth stating there.
- **done when:** the structure, deployment, existing experiments and gaps are documented, and existing features are mapped to this plan without being rebuilt.
- **not here:** rewrites, new dependencies, new experiments.

### CC2 · worlds taxonomy and metadata · S

- **decided:** Q1, Q2 (format in §3).
- **do:**
  - define the 12 worlds and the tags from §3 as Python constants in `build_gallery.py`, finalizing the slugs.
  - pass the vocabulary into `gallery-data.js`.
  - read the JSON metadata block from each live sketch page, and the series-level fields from each group in `CATEGORIES`, into `item.meta`.
  - require `interactions` and `modes` for live sketches only.
  - give pieces with incomplete metadata a fallback.
  - classify the existing image series and the three existing sketches.
- **done when:** existing pieces are classified without any change to how they run, and unknown or invalid values fail the build.
- **not here:** generating experiments from metadata, or changing the gallery interface.

### CC3 · world-based gallery discovery · M

- **decided:** Q3.
- **do:**
  - add a `#/worlds` view that gathers pieces from every toolkit, and reserve `worlds` as a route name. the toolkit views stay as they are.
  - make it the "all" view, filtered with the existing chips through query params, e.g. `#/worlds?world=dynamical&system=attractors`.
  - make a world filter match a piece's primary or secondary worlds. `applyFilters` in `gallery.js` currently needs an exact match, so it must also match values inside lists.
  - link to the worlds view from the home page.
  - show each experiment's title, preview, world and short concept.
  - link related experiments through shared worlds, systems or interactions.
  - keep the controls compact and the existing minimal look.
  - give each experiment a stable URL.
  - make filtering usable with the keyboard and keep motion low.
- **done when:** visitors can find experiments by world, open them directly and move between related pieces, and all existing gallery routes still work, including from `file://`.
- **not here:** a recommendation engine, complex multi-dimensional search, automatic visual generation, making worlds the home page (revisit after milestone 1).

### CC4 · strange attractor: core · M

world **dynamical** · concept: determinism, chaos and sensitivity to initial conditions.

- **decided:** Q4, Q5.
- **layout:** `canvas/strange-attractor/` holds `index.html` (the page), `sim.js` (the simulation) and `sim.test.js` (the tests).
- **do:**
  - implement one nonlinear attractor with deterministic initialization, using a small seeded random-number generator instead of `Math.random` and a fixed time step.
  - keep numerical integration in `sim.js`, separate from canvas rendering. write it as a classic script that sets a global in the browser and assigns `module.exports` under node.
  - render evolving trajectories with adjustable parameters.
  - support basic pointer interaction or parameter manipulation.
  - add pause, reset and a small set of presets.
  - test the integration behavior and the deterministic initialization with `node --test`. an attractor built only from `+ − ×` (Lorenz-type) gives identical trajectories in every browser, so its tests can check exact values. `sin`/`cos`-based ones (Clifford, de Jong) can drift between browsers.
  - add `*.test.js` to `.assetsignore` so tests aren't published.
- **done when:** a visitor can watch a working attractor, change its behavior and reset it to a reproducible initial state.
- **not here:** more than one attractor family, 3D navigation, audio reactivity, a generic simulation framework.

### CC5 · strange attractor: publish · M

- **do:**
  - integrate the engine into the gallery: extend `collect_sketch_items` to pick up `canvas/<id>/index.html` (folders without an `index.html`, like `canvas/lib/`, are skipped), and link to `index.html` explicitly, because a folder link opened from disk shows a file listing.
  - add metadata, a concept description and interaction instructions.
  - polish the trajectories, visual hierarchy and presets.
  - optimize how particles and trails are rendered.
  - check mobile interaction, reduced motion and teardown.
  - provide a stable direct link.
- **done when:** strange attractor is a complete, published, accessible experiment whose behavior can be reproduced.
- **not here:** more attractors, or composition across engines.

### CC6 · artificial garden: core · M

world **organic** · concept: emergence, adaptation and indirect control.

- **do:**
  - implement a small growth simulation driven by rules.
  - add environmental parameters such as growth rate, branching and resource availability.
  - let visitors influence growth indirectly by placing resources or obstacles.
  - keep the simulation rules separate from rendering, in `canvas/artificial-garden/sim.js`, laid out and tested like CC4 (Q4, Q5).
  - test growth constraints, resource interactions and deterministic initialization.
- **done when:** the organism evolves under consistent rules, and a visitor's intervention changes how it develops in a way that matters.
- **not here:** a full ecosystem, genetic evolution, multiplayer.

### CC7 · artificial garden: publish · M

- **do:**
  - add the finished engine to the gallery.
  - create starting presets that are worth exploring.
  - show visible feedback when the visitor intervenes.
  - balance visual complexity against performance.
  - add metadata and a short concept description.
  - check mobile and keyboard interaction.
- **done when:** visitors can grow, influence, reset and explore the garden as a complete experience.
- **not here:** competitive goals, elaborate organism editors, game progression.

### CC8 · reusable engine conventions · M

- **gate:** at least two engines have shipped (CC5 and CC7), CC11 has added share links and export to both, and they show real chances for reuse.
- **do:**
  - compare the strange attractor and artificial garden implementations.
  - extract only the lifecycle code they genuinely share.
  - standardize initialization, animation, pause, reset and teardown, plus the URL serialization and PNG export that CC11 built into both engines.
  - use a shared way of declaring parameters only where it helps both engines.
  - keep pure simulation logic testable on its own.
  - keep room for rendering and interactions specific to each engine.
  - document how to add a new experiment.
  - put shared code in `canvas/lib/` and load it as classic scripts (§2, works from disk).
- **done when:** both published engines still behave exactly as before, and a new experiment can use the conventions without copying lifecycle code.
- **not here:** a visual programming system, a node editor, a plugin marketplace, a broad engine rewrite.

### CC9 · sigil laboratory: core · M

world **mystic** · concept: symbolism, pattern-making and the search for meaning.

- **do:**
  - generate symbolic geometry procedurally from strokes, symmetry and transformation rules.
  - let visitors draw or manipulate simple symbols.
  - turn the visitor's input into generated structures.
  - make variations deterministic through seeds.
  - keep input geometry, transformations and rendering clearly separate, with the testable parts in `canvas/sigil-laboratory/sim.js` (Q4, Q5).
- **done when:** visitors can create distinct procedural sigils through interaction that matters, and the results can be reproduced.
- **not here:** a formal symbolic language, interpreting meaning, AI-generated imagery.

### CC10 · sigil laboratory: publish · M

- **do:**
  - publish it under mystic, with geometric as a possible secondary world.
  - add a curated set of visual presets.
  - keep the drawing controls clear and minimal.
  - apply whichever CC8 conventions fit.
  - add reset and clear, plus share links and image export through the CC8 conventions. a share link rebuilds only the seed and preset, because drawn strokes are an interaction history (CC11), so PNG export is how a visitor keeps a sigil.
  - present it as a study of pattern-making and symbolism, and never claim that invented symbols are historically authentic.
- **done when:** visitors can create and explore procedural symbols in a complete, responsive experience.
- **not here:** complex notation systems, accounts, cloud storage.

### CC11 · share links and image export · M

- **do:**
  - check CC1's audit for what already exists before building anything.
  - build it into both strange attractor and artificial garden, accepting some duplication for now. CC8 extracts it afterwards (Q6).
  - make configurations shareable through a seed and parameters encoded in the URL.
  - validate restored values and clamp them to their allowed ranges.
  - add randomize, reset and copy-link controls where they fit.
  - export the canvas as a PNG whose filename includes the experiment name and seed.
  - distinguish initial configurations, which can be reproduced, from interaction histories, which parameters alone cannot rebuild.
  - keep everything on the visitor's device.
- **done when:** a shared link reproduces the same supported initial configuration, image export works, and malformed URL parameters fail safely.
- **not here:** video export, replay recording, cloud storage, public galleries of visitor submissions.

---

## 5. definition of done

**every ticket in this repo:**

- existing experiments and URLs keep working, including the gallery's hash routes and opening from `file://`.
- `python build_gallery.py` runs clean, and `node --test` passes once tests exist.
- no unnecessary frameworks or dependencies are added.
- the change follows the repo's existing conventions.
- light and dark themes are checked where supported (the gallery has none yet).
- controls work with keyboard, pointer and touch as applicable.
- docs are updated if a convention changes.
- the ticket's status in §4 and the log at the bottom are updated.

**every published engine, in addition:**

- it communicates a clear concept, not only a visual effect.
- a short interaction is enough to understand its basic behavior.
- pause and reset work.
- reduced motion is supported.
- simulation workloads are bounded and stay responsive.
- animation frames, observers and other resources are released correctly.
- deterministic configurations can be reproduced.
- interactions produce changes that matter.
- it has a direct URL.
- it has world, system and interaction metadata.
- it can be used without sound.
- the canvas works on mobile and desktop.
- there is no rapid flashing and no needlessly aggressive motion.

## 6. decisions

made 2026-11-03 and provisional. revisit one if a ticket shows it doesn't hold, and record the change here.

| # | question | decision | why | shapes |
|---|---|---|---|---|
| Q1 | do the static renders get worlds? | yes, set once per series rather than per image. `interactions` and `modes` apply only to live sketches | the worlds fit the existing art, world pages aren't empty at launch, and setting them per series keeps CC2 small | CC2, CC3 |
| Q2 | where does metadata live? | live sketches: a `<script type="application/json" id="meta">` block in the page. image series: fields on their group in `CATEGORIES`. vocabulary: Python constants in `build_gallery.py`. no YAML | each engine stays self-contained, the page can read its own metadata even from disk (a separate file can't be fetched from `file://`), and no dependency is added | CC2 |
| Q3 | how do world and toolkit navigation relate? | both stay. a new `#/worlds` view filters across all toolkits, and the toolkit views are unchanged | no link breaks. the toolkit view tells the learning story and worlds serve visitors. making worlds the home page is revisited after milestone 1 | CC3 |
| Q4 | how is simulation code tested? | `node --test`, with each simulation in a classic-script `sim.js` that also exports for node | node 20 is installed, nothing is added, and it enforces the split between simulation and rendering | CC4, CC6, CC9 |
| Q5 | how is an engine laid out? | one folder per engine: `canvas/<id>/index.html`, `sim.js`, `sim.test.js`. shared code goes in `canvas/lib/` | keeps `canvas/` tidy as engines multiply. the URL becomes permanent at CC5, so it's decided now | CC4, CC5, CC8 |
| Q6 | where does CC11 go? | after CC7 and before CC8 | share links and export exist in two engines before CC8 extracts them, and the sigil lab inherits export | CC8, CC10, CC11 |

## 7. backlog

### future engines

these are proposed concepts, not committed tickets. promote each one separately once milestone 1 has shipped.

| engine | primary world | concept | core mechanic |
|---|---|---|---|
| the impossible machine | mechanical | causality | build interconnected kinetic mechanisms |
| perception trap | perceptual | the limits of perception | manipulate optical illusions and contradictory geometry |
| memory of water | fluid | impermanence | leave disturbances that slowly diffuse and disappear |
| orbital dreams | cosmic | infinity and scale | manipulate interacting celestial trajectories |
| signal decay | glitch | entropy | deform and corrupt procedural visual signals |
| living typography | typographic | language and meaning | create letters that behave like evolving organisms |
| imaginary geography | topographic | formation and exploration | generate and reshape procedural landscapes |
| symmetry studies | geometric | order and repetition | construct and transform generative patterns |
| emotional noise | abstract | expression and chance | guide an evolving composition through forces and noise |

### parked

each item waits until its gate is met.

| item | gate |
|---|---|
| general composer for world, system and interaction | at least three published engines show compatible systems and interactions |
| engine hybridization | two engines expose compatible, reusable simulation interfaces |
| audio-reactive experiments | audio input and analysis are built, and an experiment justifies them |
| video and animated-loop export | still-image export is reliable and there is a concrete use case |
| generative sound | a published experiment genuinely benefits from synthesis beyond decorative feedback |
| visitor-created presets | URL sharing is established and creating presets adds clear value |
| interactive gallery map | enough engines are published, with meaningful relationships between them |
| advanced WebGL rendering | Canvas 2D performance or visual needs justify the extra complexity |
| replayable interaction histories | deterministic simulation and input recording are shown working in a concrete experiment |
| shared engine package across repos | two independent consumers need the same tested simulation logic |

---

## appendix A · `eigenomar.com` work (not this repo)

this is kept here for context. apply it in the main website repo and its dev plan.

| ID | ticket | size | needs | status |
|---|---|---|---|---|
| EC1 | creative coding entry and discovery | S | CC3, CC5 | todo |
| EC2 | related entries and journeys | S | EC1, D5 | todo |

### EC1 · creative coding entry and discovery · S

- **do:**
  - keep the existing creative coding entry in the art section.
  - update its description to introduce creative coding worlds as a collection of interactive generative pieces.
  - link to `gallery.eigenomar.com` and its world-based navigation.
  - feature representative experiments only if the gallery gives them stable direct URLs.
  - keep the main site static and independent of the gallery's runtime.
  - don't duplicate the gallery's rendering code or interactive controls.
- **done when:** the art section clearly introduces the collection, sends visitors to the gallery, and still works when the gallery is down.
- **not here:** rebuilding the gallery on the main site, loading a gallery framework, adding a new top-level navigation item.

### EC2 · related entries and journeys · S

- **gate:** EC1 and D5 are complete, and the relevant engines are published.
- **do:**
  - connect the creative coding entry to related writings and interactive pieces.
  - link strange attractor to the existing phase portrait and the mathematical writings that fit.
  - link artificial garden to writings on emergence, recursion or complexity, once they exist.
  - link sigil laboratory to geometric or symbolic explorations where relevant.
  - add an optional guided journey through selected concepts once there are enough meaningful stops.
  - use the site's existing related-entry system.
- **done when:** visitors can follow curated links between creative coding, mathematics, philosophy and other published work, with no new navigation system.
- **not here:** automatic semantic recommendations, a knowledge graph, duplicating the gallery's filters.

### changes to the main dev plan

the main plan currently puts several creative coding experiments in the website under `src/experiments/`. reconcile that with this repo before implementing any of them.

- **D2:** `src/experiments/` is for interactive pieces that must run inside `eigenomar.com` itself, such as embedded demos and experiments tied to a game. standalone gallery engines belong in `creative_coding`.
- **D3:** keep the local experiment registry for those native pieces. gallery experiments stay independent and are reached through stable external URLs.
- **D6:** keep website-specific helpers in `src/lib/`. don't copy the gallery's engine architecture just to share similar utilities.

| existing ticket | proposed treatment |
|---|---|
| L1: experiment host | keep, for native website experiments and games |
| L2: parameters and seeds | keep for native experiments, and build gallery equivalents only where needed |
| L3: PNG export | keep if native experiments need it. CC11 covers export in the gallery |
| L4: symmetry canvas | keep its tested drawing logic where Symmetry Thief needs it |
| L5: flow field | move the gallery-focused work to `creative_coding`, and scope any game-specific version separately |
| L6: recursive growth | move the gallery-focused work to `creative_coding`, and review what Garden of Possibilities depends on |
| L7: glitch lab | build it in `creative_coding` rather than duplicating it on the main site |
| L8: artificial organisms | CC6–CC7 replace the gallery-focused work. keep any separate game-specific requirements |

**sharing code across repos:** don't create a shared package yet. if both repos genuinely need the same simulation core, first get a second consumer working, then consider extracting a small independent package. create another repo only once that need is shown.

### definition of done for the main site, in addition to §5

- the existing art structure and navigation are preserved.
- the site works without the gallery running.
- no gallery source is copied into the main repo.
- all internal and external links are checked.
- the site stays static.

---

## log

| date | ticket | note |
|---|---|---|
