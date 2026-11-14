# creative_coding
a repo where i'm learning creative coding

## gallery

`gallery/index.html` browses everything in this repo, grouped by kind of
work: engines (the interactive engines and the render engine output), raw
(the pygame and pycairo sketches), illustrations (the `12.` series and 7
levels) and animated (the canvas sketches). The worlds view cuts across all
of them.

The thumbnails and the data the page reads are not kept in the repository.
Build them once after cloning, and again after adding new renders.

### commands

`dev.py` runs the everyday commands the same way on Windows, Linux and macOS. It needs only Python, and nothing has to be activated first: the
build runs in `.venv` when there is one, and otherwise in the Python running
`dev.py`.

```bash
python dev.py setup          # create .venv and install requirements.txt into it
python dev.py build          # build the thumbnails and the gallery data
python dev.py build --force  # rebuild every thumbnail
python dev.py test           # run the engines' tests with node --test
python dev.py check          # test, then build: run this before pushing
python dev.py open           # open the gallery from disk
python dev.py serve          # serve it at http://127.0.0.1:8765/gallery/
```

Use `python3` where there's no `python` on the path, as on Ubuntu, and on
Windows `py` works too. Each command prints what it runs, and the sections
below give the same steps by hand.

### Windows

The repository is developed from one clone on Windows. `.gitattributes`
keeps every text file LF, whatever Git's `core.autocrlf` says, so a Windows
build writes the same gallery data as Cloudflare's build, which is the
build's run on Linux for every push to `main`.

### setup

`python dev.py setup` does this. By hand, create a virtual environment in
the repository root, activate it, then install the one dependency the build
needs:

```bash
python -m venv .venv
```

Activate it. Linux and macOS:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Windows cmd:

```bat
.venv\Scripts\activate.bat
```

Then, on every platform:

```bash
python -m pip install -r requirements.txt
```

Use `python3` instead of `python` if your system has no `python` on the
path. Inside an activated environment `python` always works.

### the sketches

The sketches in `cc_pycairo/` and `cc_pygame/` aren't part of the gallery's
build, and need their own packages: `pycairo` and `noise` for `cc_pycairo/`,
`pygame` for `cc_pygame/`, and `numpy` for the seven levels' grid
simulations. Install them into an environment of their own, or into `.venv`
beside Pillow:

```bash
python -m pip install pycairo noise pygame numpy
```

What each platform needs first:

- **Windows:** `pycairo`, `pygame` and `numpy` install from wheels. `noise`
  has no wheel and compiles, so it needs the Microsoft C++ Build Tools, with
  the "Desktop development with C++" workload. With them installed, the
  command above takes about half a minute.
- **Linux:** `pygame` and `numpy` install from wheels. `pycairo` builds
  against the system's cairo, so it needs cairo's headers and `pkg-config`
  (on Ubuntu, `sudo apt install libcairo2-dev pkg-config python3-dev`), or
  use the distribution's own `python3-cairo`. `noise` compiles too, with a C
  compiler and Python's headers (`build-essential` and `python3-dev`).

Each script writes its image under its folder's `gen/`, by a path relative
to the repository root, so run it from there:
`python cc_pycairo/cosmos_origin.py`. A pygame script opens a window while
it draws.

Renders don't reproduce byte for byte across platforms. On 2026-11-14, a
Windows render of the seven cosmos scripts matched four of their committed
PNGs, which were made on Linux, exactly. One differed in 0.001% of its
pixels by at most 2 levels, from the cairo that the Windows wheel bundles,
and the two that use `noise` differed visibly in about 1.2% of their pixels,
from `noise` built by another compiler. So a check that compares a re-render
with a committed PNG uses a tolerance: the same size, and under 2% of its
pixels differing.

### building

```bash
python build_gallery.py          # incremental, skips unchanged thumbnails
python build_gallery.py --force  # rebuild every thumbnail
```

This writes `gallery/thumbs/`, `gallery/gallery-data.js` and
`cc_pycairo/gen/seven_levels/manifest.json`, all ignored by git. A rebuild
that finds nothing new leaves them untouched.

### opening it

No server is needed, the gallery data is a plain `.js` file.
`python dev.py open` opens it in the default browser. By hand, open `gallery/index.html` in a browser, or from the
repository root:

```bash
xdg-open gallery/index.html   # Linux
open gallery/index.html       # macOS
start gallery\index.html      # Windows
```

### serving it

Needed only to view the gallery over http, or from another machine.
`python dev.py serve` listens on 127.0.0.1 only, and
`python dev.py serve --bind 0.0.0.0` shares it with the local network. By
hand, run this from the repository root, not from `gallery/`, because the
tiles reference the full size images as `../cc_pycairo/...`:

```bash
python -m http.server 8765
```

Then open <http://localhost:8765/gallery/>. Ctrl-C stops it. Note that
`http.server` listens on every interface, so add `--bind 127.0.0.1` to
keep it off the local network.

### deploying it

The gallery is published at <https://gallery.eigenomar.com> by Cloudflare
Workers, configured in `wrangler.jsonc`. The whole repository is the site,
because the tiles link to the full size renders and sources outside
`gallery/`. `.assetsignore` keeps `.git`, environments and config out of it,
and `_redirects` sends `/` to `/gallery/`.

In the Cloudflare dashboard, import this repository under *Workers & Pages →
Create → Import a repository* with:

- build command: `python3 -m pip install -r requirements.txt && python3 build_gallery.py`
- deploy command: `npx wrangler deploy`

Every push to `main` then rebuilds the thumbnails and redeploys. The
Cloudflare build doesn't use `dev.py`, and it doesn't run the tests, so run
`python dev.py check` before pushing.

### linking to a view

Every view has its own address, so any of these can be opened directly:

```
gallery/index.html#/raw
gallery/index.html#/engines/interactive
gallery/index.html#/illustrations/12
gallery/index.html#/illustrations/7-levels/cosmos
gallery/index.html#/engines/render-engine?scene=fault line&palette=ember cobalt
gallery/index.html#/worlds
gallery/index.html#/worlds?world=cosmic&system=oscillators
gallery/index.html#/worlds/cosmos_origin
gallery/index.html#/worlds/strange-attractor
```

`#/worlds` gathers every piece in the gallery and filters it by world,
system and interaction. A world filter matches a piece's primary world or
any of its secondary ones. `#/worlds/<id>` is one piece, with its
classification and related pieces.

A live sketch or engine also has its own page outside the gallery, such as
`canvas/gol.html` or `canvas/strange-attractor/index.html`. Link to an
engine's `index.html` itself rather than its folder, because a folder
opened from disk shows a file listing.

Addresses from when the gallery was grouped by toolkit (`#/pygame`,
`#/pycairo/...`, `#/canvas`) redirect to where those pieces live now, and
keep their filters. `MOVED_ROUTES` in `gallery/gallery.js` lists them.
Because of these routes, no category in `CATEGORIES` can use the id `worlds`,
`pygame`, `pycairo` or `canvas`.

### adding work

- **an image series** is a group in `CATEGORIES` in `build_gallery.py`. A
  group reads either a `directory` (every `.png` and `.jpg` in it, in
  natural order) or a `manifest` plus the `search` directories to look in.
  `exclude_manifests` keeps curated pieces out of a directory group, so each
  piece appears once. `facets` turns filename fields into filter chips.
  `world`, `worlds`, `systems` and `concept` classify every piece in the
  series at once.
- **a section** is a folder inside a group, one level down, at
  `#/<category>/<group>/<section>`. A group lists its folders in `sections`,
  each with an `id`, a `title` and an optional `blurb`, and each piece names
  its folder in a `section` field. The pieces stay in the group's `items`. A
  section with no pieces isn't shown, a piece with no section sits on the
  group's page below the cards, and a group can't have both `sections` and
  `facets`.
- **a manifest** (`12.txt`, `cosmos.txt`) sets the order and titles of a
  series, one piece per line as `position: title: image_stem`. Position and
  title are optional, and `#` starts a comment.
- **the seven levels** are read from a registry, `seven_levels.json`, which
  lists all 49 levels, track by track in reading order, and the two
  connection diagrams, whether or not their images exist yet. Each image is
  `cc_pycairo/gen/seven_levels/<stem>.png`, made by `cc_pycairo/<stem>.py`.
  A level's stem is `<track>_<NN>_<color>_<form>`, such as
  `time_03_orange_bloom`, and a diagram's is `connections_<label>`.
  - Each track sets its folder, `gallery_label`, and its classification,
    `world`, `worlds`, `systems` and `concept`, for all seven of its levels.
    A level's title is its `label`. Its `alt` and `caption` are `null` until
    the image exists, and the gallery uses the title as alt text until then.
  - An image that isn't on disk is skipped with a warning, so the registry can
    list work that's still to come.
  - The build checks the registry and `seven_levels_connections.json`, and
    fails on a duplicate or misnumbered id, a stem that breaks the naming rule, a
    value outside the vocabulary, or a connection to a track or level the
    registry doesn't list.
  - It writes `cc_pycairo/gen/seven_levels/manifest.json`, which is served
    with the images. It lists all 51 images in registry order, each with its
    `status`, `planned` or `generated`, its `width` and `height`, and its
    `public_url`. Those three are `null` while it's `planned`. The site reads
    this manifest, so a field it uses is renamed only together with the
    site's build.
  - Until the universe migration, the cosmos folder shows the seven pieces in
    `cosmos.txt` under their first names, classified as the universe track.
- **source links** are found from the literal output path a script passes to
  `write_to_png(...)` or `image.save(...)`. Scripts that build the path at
  runtime fall back to a script with the image's name, or `pnger_NN.py` for
  `jpger_NN.jpg`.
- **a live sketch** is a self-contained `.html` file at the top level of
  `canvas/`, listed under animated, canvas. Its `<title>` is its title in
  the gallery. It classifies
  itself in a block in its `<head>`, which the browser ignores:

  ```html
  <script type="application/json" id="meta">
  {
      "world": "organic",
      "worlds": ["geometric"],
      "systems": ["cellular-automata"],
      "interactions": ["autonomous"],
      "modes": ["observe"],
      "concept": "lifelike behavior emerging from simple local rules"
  }
  </script>
  ```

  `world`, `interactions` and `modes` are required. `title` overrides
  `<title>`, and `id`, if given, must match the file name.
- **an engine** is an interactive piece with a folder of its own,
  `canvas/<id>/`: `index.html` is the page, `sim.js` holds the simulation with
  no canvas code, and `sim.test.js` tests it. `sim.js` is a classic script, not
  a module, so the page still works from disk. It sets a global in the browser
  and assigns `module.exports` under node. Run the tests from the repository
  root with `node --test` (or `python dev.py test`), which needs no install.
  Files ending in `.test.js`
  aren't published. `index.html` carries the same meta block as a live
  sketch, and the build lists every folder in `canvas/` that has an
  `index.html` under engines, interactive (`#/engines/interactive`), with
  the folder name as its id. A folder without one, such as shared code in
  `canvas/lib/`, is skipped. The gallery's piece page links `sim.js` as the
  engine's source. In `CATEGORIES`, `"pages": "folders"` reads engines and
  `"pages": "files"` reads sketches. Engines are public at their URL as soon
  as they're on `main`.
- **the vocabulary** (12 worlds, systems, interactions and modes) is defined
  at the top of `build_gallery.py`. The build fails on any value it doesn't
  list. A piece with no classification at all still builds, as unclassified,
  with a warning.
- **everything committed is public.** Every file not listed in
  `.assetsignore` is served at gallery.eigenomar.com. The plans and
  `CLAUDE.md` stay off the site, but they're still readable in the public
  GitHub repository.
