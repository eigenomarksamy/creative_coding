# creative_coding
a repo where i'm learning creative coding

## gallery

`gallery/index.html` browses everything in this repo, grouped by toolkit:
pygame, pycairo (the `12.` series, the sketches, the render engine output)
and the interactive canvas sketches.

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

### linking to a view

Every view has its own address, so any of these can be opened directly:

```
gallery/index.html#/pygame
gallery/index.html#/pycairo/12
gallery/index.html#/pycairo/render-engine?scene=fault line&palette=ember cobalt
```
