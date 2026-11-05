# creative_coding
a repo where i'm learning creative coding

## gallery

`gallery/index.html` browses everything in this repo, grouped by kind of
work: engines (the render engine output), raw (the pygame and pycairo
sketches), illustrations (the `12.` series and 7 levels) and animated (the
canvas sketches). The worlds view cuts across all of them.

The thumbnails and the data the page reads are not kept in the repository.
Build them once after cloning, and again after adding new renders.

### setup

Create a virtual environment in the repository root, activate it, then
install the one dependency the build needs:

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

### building

```bash
python build_gallery.py          # incremental, skips unchanged thumbnails
python build_gallery.py --force  # rebuild every thumbnail
```

This writes `gallery/thumbs/` and `gallery/gallery-data.js`, both ignored
by git. A rebuild that finds nothing new leaves them untouched.

### opening it

No server is needed, the gallery data is a plain `.js` file. Open
`gallery/index.html` in a browser, or from the repository root:

```bash
xdg-open gallery/index.html   # Linux
open gallery/index.html       # macOS
start gallery\index.html      # Windows
```

With the repo in WSL and the browser on Windows, open this address
instead, substituting your distribution name and path:

```
file://wsl.localhost/Ubuntu/home/eigenomar/dev_ws/creative_coding/gallery/index.html
```

### serving it

Needed only to view the gallery from another machine. Run this from the
repository root, not from `gallery/`, because the tiles reference the
full size images as `../cc_pycairo/...`:

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

Every push to `main` then rebuilds the thumbnails and redeploys.

### linking to a view

Every view has its own address, so any of these can be opened directly:

```
gallery/index.html#/raw
gallery/index.html#/illustrations/12
gallery/index.html#/illustrations/7-levels/cosmos
gallery/index.html#/engines/render-engine?scene=fault line&palette=ember cobalt
gallery/index.html#/worlds
gallery/index.html#/worlds?world=cosmic&system=oscillators
gallery/index.html#/worlds/cosmos_origin
```

`#/worlds` gathers every piece in the gallery and filters it by world,
system and interaction. A world filter matches a piece's primary world or
any of its secondary ones. `#/worlds/<id>` is one piece, with its
classification and related pieces.

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
  each with an `id`, a `title` and an optional `blurb`, and `section` on the
  group puts every piece it reads in one of them. The pieces stay in the
  group's `items`, each with a `section` field. A section with no pieces
  isn't shown, a piece with no section sits on the group's page below the
  cards, and a group can't have both `sections` and `facets`.
- **a manifest** (`12.txt`, `cosmos.txt`) sets the order and titles of a
  series, one piece per line as `position: title: image_stem`. Position and
  title are optional, and `#` starts a comment.
- **source links** are found from the literal output path a script passes to
  `write_to_png(...)` or `image.save(...)`. Scripts that build the path at
  runtime fall back to a script with the image's name, or `pnger_NN.py` for
  `jpger_NN.jpg`.
- **a live sketch** is a self-contained `.html` file at the top level of
  `canvas/`. Its `<title>` is its title in the gallery. It classifies
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
  root with `node --test`, which needs no install. Files ending in `.test.js`
  aren't published. Engines are public at their URL as soon as they're on
  `main`, and the gallery doesn't list them yet.
- **the vocabulary** (12 worlds, systems, interactions and modes) is defined
  at the top of `build_gallery.py`. The build fails on any value it doesn't
  list. A piece with no classification at all still builds, as unclassified,
  with a warning.
- **everything committed is public.** Every file not listed in
  `.assetsignore` is served at gallery.eigenomar.com. The plans and
  `CLAUDE.md` stay off the site, but they're still readable in the public
  GitHub repository.
