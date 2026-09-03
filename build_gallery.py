#!/usr/bin/env python3

"""
Build the static gallery in gallery/.

Scans the generated artwork directories, writes downscaled thumbnails and
emits gallery/gallery-data.js, which gallery/index.html reads directly.

The generated data file is plain JavaScript rather than JSON so the gallery
also works when index.html is opened straight from disk, without a server.

Usage:
    python build_gallery.py

Rebuild every thumbnail, ignoring timestamps:
    python build_gallery.py --force
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

from PIL import Image


IMAGE_EXTENSIONS = {".png", ".jpg"}
SKETCH_EXTENSIONS = {".html"}

GALLERY_DIRECTORY = "gallery"
THUMBNAIL_DIRECTORY = "thumbs"
DATA_FILENAME = "gallery-data.js"

DEFAULT_THUMBNAIL_SIZE = 640
THUMBNAIL_QUALITY = 80

# Matches render engine output such as:
# fault_line__blood_signal__v01.png
RENDER_ENGINE_PATTERN = re.compile(
    r"^(?P<scene>[a-z_]+)__(?P<palette>[a-z_]+)__v(?P<variant>\d+)$"
)

# Most sketches name their own output file, which is a more reliable link
# back to the source than matching stems. Covers both:
#   surface.write_to_png("cc_pycairo/gen/symmetric_art.png")
#   pygame.image.save(screen, 'cc_pygame/gen/jpger_03.jpg')
OUTPUT_PATH_PATTERN = re.compile(
    r"""(?:write_to_png|image\.save)\(\s*"""
    r"""(?:[^,()"']+,\s*)?"""
    r"""["'](?P<path>[^"']+\.(?:png|jpg))["']""",
    re.IGNORECASE,
)

# Directories holding sketch scripts, searched for output declarations.
SCRIPT_DIRECTORIES = ("cc_pygame", "cc_pycairo")

# Each group reads one directory. Groups exist so a category can be split
# further later on without touching the page itself.
CATEGORIES = [
    {
        "id": "pygame",
        "title": "pygame",
        "blurb": (
            "numbered studies in shape and polar math. every sketch draws "
            "once, saves a JPG and exits."
        ),
        "groups": [
            {
                "id": "sketches",
                "title": "sketches",
                "blurb": (
                    "jpger_NN.jpg is rendered by the pnger_NN.py of the "
                    "same number."
                ),
                "directory": "cc_pygame/gen",
                "kind": "image",
                "source": "pygame_sketch",
            },
        ],
    },
    {
        "id": "pycairo",
        "title": "pycairo",
        "blurb": (
            "flow fields, layered Bézier brushwork and gradient masses, "
            "first as one-off sketches and then as a parameterised engine."
        ),
        "groups": [
            {
                "id": "12",
                "title": "12.",
                "blurb": (
                    "a selected series, in the order and under the titles "
                    "set out in 12.txt."
                ),
                "manifest": "12.txt",
                "search": ["cc_pycairo/gen"],
                "kind": "image",
                "source": "pycairo_sketch",
            },
            {
                "id": "sketches",
                "title": "sketches",
                "blurb": (
                    "one script, one image. each file hardcodes its own "
                    "palette and composition. the pieces selected for 12. "
                    "are listed there rather than here."
                ),
                "directory": "cc_pycairo/gen",
                "exclude_manifests": ["12.txt"],
                "kind": "image",
                "source": "pycairo_sketch",
            },
            {
                "id": "render-engine",
                "title": "render engine",
                "blurb": (
                    "scenes crossed with palettes. geometry is held constant "
                    "per scene, so a row of variants is the same composition "
                    "in a different key."
                ),
                "directory": "cc_pycairo/gen/render_engine_output",
                "kind": "image",
                "source": "render_engine",
                "facets": [
                    {"key": "scene", "label": "Scene"},
                    {"key": "palette", "label": "Palette"},
                    {"key": "variant", "label": "Variant"},
                ],
            },
        ],
    },
    {
        "id": "canvas",
        "title": "canvas",
        "blurb": (
            "live sketches in plain JavaScript. these run in the page "
            "instead of rendering to a file."
        ),
        "groups": [
            {
                "id": "sketches",
                "title": "sketches",
                "blurb": "click a preview to interact with it.",
                "directory": "canvas",
                "kind": "sketch",
            },
        ],
    },
]


def natural_sort_key(value: str) -> list[object]:
    """
    Sort names containing numbers naturally.

    Example:
        jpger_2.jpg comes before jpger_10.jpg
    """
    return [
        int(part) if part.isdigit() else part.casefold()
        for part in re.split(r"(\d+)", value)
    ]


def normalize_path(path: str) -> str:
    """Normalize a path written inside a script for comparison."""
    normalized = path.strip().replace("\\", "/")

    while normalized.startswith("./"):
        normalized = normalized[2:]

    return PurePosixPath(normalized).as_posix()


def humanize(value: str) -> str:
    """Turn a file or scene stem into a readable label."""
    spaced = value.replace("_", " ").replace("-", " ")
    return re.sub(r"\s+", " ", spaced).strip()


def title_for(image_stem: str, metadata: dict[str, str]) -> str:
    """
    Build a tile label.

    Render engine names carry three fields, so they read better separated
    than run together: "fault line · blood signal · v01".
    """
    if metadata:
        return " · ".join(
            metadata[key]
            for key in ("scene", "palette", "variant")
            if metadata.get(key)
        )

    return humanize(image_stem)


def relative_to_gallery(repo_relative_path: str) -> str:
    """Rewrite a repository path for use inside gallery/index.html."""
    return f"../{repo_relative_path}"


def build_output_index(repo_root: Path) -> dict[str, str]:
    """
    Map generated image paths to the script that declares them.

    Scripts that build their output path at runtime are simply absent, and
    fall back to the per group heuristics in find_source_script.
    """
    index: dict[str, str] = {}

    for directory_name in SCRIPT_DIRECTORIES:
        directory = repo_root / directory_name

        if not directory.is_dir():
            continue

        scripts = sorted(directory.glob("*.py"), key=lambda p: p.name)

        for script in scripts:
            script_relative = script.relative_to(repo_root).as_posix()
            contents = script.read_text(encoding="utf-8", errors="ignore")

            for match in OUTPUT_PATH_PATTERN.finditer(contents):
                output_path = normalize_path(match.group("path"))

                # First declaration wins, so a later copy of a sketch does
                # not steal attribution from the original.
                index.setdefault(output_path, script_relative)

    return index


def find_source_script(
    repo_root: Path,
    output_index: dict[str, str],
    source_kind: str | None,
    image_stem: str,
    repo_relative_image: str,
) -> str | None:
    """
    Locate the script that produced an image.

    Returns a repository relative path, or None when no match exists.
    """
    declared = output_index.get(normalize_path(repo_relative_image))

    if declared:
        return declared

    if source_kind == "render_engine":
        candidates = ["cc_pycairo/render_engine.py"]

    elif source_kind == "pycairo_sketch":
        candidates = [f"cc_pycairo/{image_stem}.py"]

    elif source_kind == "pygame_sketch":
        match = re.match(r"^jpger_(\d+)$", image_stem)

        if match is None:
            return None

        candidates = [f"cc_pygame/pnger_{match.group(1)}.py"]

    else:
        return None

    for candidate in candidates:
        if (repo_root / candidate).is_file():
            return candidate

    return None


def describe_image(image_stem: str, source_kind: str | None) -> dict[str, str]:
    """Extract facet metadata from a filename."""
    if source_kind != "render_engine":
        return {}

    match = RENDER_ENGINE_PATTERN.match(image_stem)

    if match is None:
        return {}

    return {
        "scene": humanize(match.group("scene")),
        "palette": humanize(match.group("palette")),
        "variant": f"v{match.group('variant')}",
    }


def read_manifest(manifest_path: Path) -> list[dict[str, str]]:
    """
    Read a curated list of images.

    One entry per line, blank lines and # comments ignored:

        00: 12: bezier_brush_12
        01: the rope holding the wind: textural_forest

    The last field is the image stem. Anything before it is an optional
    position and an optional title, so titles may themselves contain colons.
    """
    entries: list[dict[str, str]] = []

    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        text = line.split("#", 1)[0].strip()

        if not text:
            continue

        fields = [field.strip() for field in text.split(":")]

        if len(fields) >= 3:
            entry = {
                "index": fields[0],
                "title": ":".join(fields[1:-1]).strip(),
                "stem": fields[-1],
            }
        elif len(fields) == 2:
            entry = {"index": "", "title": fields[0], "stem": fields[1]}
        else:
            entry = {"index": "", "title": "", "stem": fields[0]}

        if entry["stem"]:
            entries.append(entry)

    return entries


def manifest_stems(repo_root: Path, manifest_names: list[str]) -> set[str]:
    """Collect the image stems named by one or more manifests."""
    stems: set[str] = set()

    for name in manifest_names:
        path = repo_root / name

        if path.is_file():
            stems.update(entry["stem"] for entry in read_manifest(path))

    return stems


def resolve_manifest_stem(
    repo_root: Path,
    search_directories: list[str],
    stem: str,
) -> Path | None:
    """Find the image a manifest entry names."""
    for directory_name in search_directories:
        for extension in sorted(IMAGE_EXTENSIONS):
            candidate = repo_root / directory_name / f"{stem}{extension}"

            if candidate.is_file():
                return candidate

    return None


def thumbnail_relative_path(
    category_id: str,
    repo_relative_image: str,
    registry: dict[str, str],
) -> str:
    """
    Choose a thumbnail path for an image.

    Thumbnails are keyed per category rather than per group, so an image
    listed in a curated group reuses the thumbnail the directory scan
    already produced instead of duplicating it.
    """
    stem = PurePosixPath(repo_relative_image).stem
    candidate = f"{THUMBNAIL_DIRECTORY}/{category_id}/{stem}.jpg"

    owner = registry.get(candidate)

    if owner is None or owner == repo_relative_image:
        registry[candidate] = repo_relative_image
        return candidate

    # Two different images share a stem, so keep them apart.
    digest = hashlib.sha1(repo_relative_image.encode("utf-8")).hexdigest()[:8]
    candidate = f"{THUMBNAIL_DIRECTORY}/{category_id}/{stem}-{digest}.jpg"
    registry[candidate] = repo_relative_image

    return candidate


def build_thumbnail(
    source_path: Path,
    thumbnail_path: Path,
    max_size: int,
    force: bool,
) -> tuple[int, int]:
    """
    Write a downscaled thumbnail and return the original pixel size.

    Existing thumbnails newer than their source are left alone.
    """
    with Image.open(source_path) as image:
        original_size = image.size

        is_current = (
            thumbnail_path.exists()
            and thumbnail_path.stat().st_mtime >= source_path.stat().st_mtime
        )

        if is_current and not force:
            return original_size

        # Lets Pillow decode large JPEGs at a reduced size.
        image.draft("RGB", (max_size * 2, max_size * 2))

        if image.mode in {"RGBA", "LA", "P"}:
            image = image.convert("RGBA")
            flattened = Image.new("RGB", image.size, (0, 0, 0))
            flattened.paste(image, mask=image.split()[-1])
            image = flattened
        else:
            image = image.convert("RGB")

        image.thumbnail((max_size, max_size), Image.LANCZOS)

        thumbnail_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(
            thumbnail_path,
            format="JPEG",
            quality=THUMBNAIL_QUALITY,
            optimize=True,
            progressive=True,
        )

    return original_size


def build_image_item(
    repo_root: Path,
    gallery_root: Path,
    category_id: str,
    group: dict,
    path: Path,
    context: dict,
    title: str | None = None,
    extra_meta: dict[str, str] | None = None,
) -> dict:
    """Build one gallery item from one image file."""
    repo_relative = path.relative_to(repo_root).as_posix()

    thumbnail_relative = thumbnail_relative_path(
        category_id=category_id,
        repo_relative_image=repo_relative,
        registry=context["thumbnails"],
    )

    width, height = build_thumbnail(
        source_path=path,
        thumbnail_path=gallery_root / thumbnail_relative,
        max_size=context["max_size"],
        force=context["force"],
    )

    source_script = find_source_script(
        repo_root=repo_root,
        output_index=context["output_index"],
        source_kind=group.get("source"),
        image_stem=path.stem,
        repo_relative_image=repo_relative,
    )

    metadata = describe_image(path.stem, group.get("source"))
    metadata.update(extra_meta or {})

    return {
        "id": path.stem,
        "kind": "image",
        "title": title or title_for(path.stem, metadata),
        "thumb": thumbnail_relative,
        "full": relative_to_gallery(repo_relative),
        "width": width,
        "height": height,
        "bytes": path.stat().st_size,
        "meta": metadata,
        "source": (
            relative_to_gallery(source_script) if source_script else None
        ),
        "sourceLabel": source_script,
    }


def collect_image_items(
    repo_root: Path,
    gallery_root: Path,
    category_id: str,
    group: dict,
    context: dict,
) -> list[dict]:
    """Build one item per image in a group directory, in natural order."""
    directory = repo_root / group["directory"]

    if not directory.is_dir():
        print(f"  skipped, directory not found: {group['directory']}")
        return []

    # Images promoted into a curated group are left out here, so a piece
    # appears in one place rather than twice.
    excluded = manifest_stems(
        repo_root,
        group.get("exclude_manifests", []),
    )

    paths = sorted(
        (
            path
            for path in directory.iterdir()
            if path.is_file()
            and path.suffix.casefold() in IMAGE_EXTENSIONS
            and path.stem not in excluded
        ),
        key=lambda path: natural_sort_key(path.name),
    )

    if excluded:
        print(f"  {group['id']}: {len(excluded)} excluded by manifest")

    return [
        build_image_item(
            repo_root=repo_root,
            gallery_root=gallery_root,
            category_id=category_id,
            group=group,
            path=path,
            context=context,
        )
        for path in paths
    ]


def collect_manifest_items(
    repo_root: Path,
    gallery_root: Path,
    category_id: str,
    group: dict,
    context: dict,
) -> list[dict]:
    """
    Build one item per manifest entry, keeping the listed order.

    The manifest is the running order of a series, so it is never sorted.
    """
    manifest_path = repo_root / group["manifest"]

    if not manifest_path.is_file():
        print(f"  skipped, manifest not found: {group['manifest']}")
        return []

    items: list[dict] = []

    for entry in read_manifest(manifest_path):
        path = resolve_manifest_stem(
            repo_root=repo_root,
            search_directories=group.get("search", []),
            stem=entry["stem"],
        )

        if path is None:
            print(
                f"  warning: {group['manifest']} lists "
                f"{entry['stem']!r}, which was not found"
            )
            continue

        extra_meta = {"file": entry["stem"]}

        if entry["index"]:
            extra_meta = {"no": entry["index"], **extra_meta}

        items.append(
            build_image_item(
                repo_root=repo_root,
                gallery_root=gallery_root,
                category_id=category_id,
                group=group,
                path=path,
                context=context,
                title=entry["title"] or humanize(entry["stem"]),
                extra_meta=extra_meta,
            )
        )

    return items


def collect_sketch_items(
    repo_root: Path,
    group: dict,
) -> list[dict]:
    """Build one item per interactive HTML sketch."""
    directory = repo_root / group["directory"]

    if not directory.is_dir():
        print(f"  skipped, directory not found: {group['directory']}")
        return []

    paths = sorted(
        (
            path
            for path in directory.iterdir()
            if path.is_file() and path.suffix.casefold() in SKETCH_EXTENSIONS
        ),
        key=lambda path: natural_sort_key(path.name),
    )

    items: list[dict] = []

    for path in paths:
        repo_relative = path.relative_to(repo_root).as_posix()
        title = extract_html_title(path) or humanize(path.stem)

        items.append(
            {
                "id": path.stem,
                "kind": "sketch",
                "title": title,
                "full": relative_to_gallery(repo_relative),
                "bytes": path.stat().st_size,
                "meta": {},
                "source": relative_to_gallery(repo_relative),
                "sourceLabel": repo_relative,
            }
        )

    return items


def extract_html_title(path: Path) -> str | None:
    match = re.search(
        r"<title>(.*?)</title>",
        path.read_text(encoding="utf-8", errors="ignore"),
        re.IGNORECASE | re.DOTALL,
    )

    if match is None:
        return None

    return match.group(1).strip() or None


def collect_facets(group: dict, items: list[dict]) -> list[dict]:
    """
    Build the filter chips for a group.

    Only facets that every listed key actually populates are kept.
    """
    facets = []

    for facet in group.get("facets", []):
        values = sorted(
            {
                item["meta"][facet["key"]]
                for item in items
                if item["meta"].get(facet["key"])
            },
            key=natural_sort_key,
        )

        if len(values) > 1:
            facets.append({**facet, "values": values})

    return facets


def build_gallery_data(
    repo_root: Path,
    gallery_root: Path,
    max_size: int,
    force: bool,
) -> dict:
    categories = []

    context = {
        "output_index": build_output_index(repo_root),
        "thumbnails": {},
        "max_size": max_size,
        "force": force,
    }

    for category in CATEGORIES:
        print(f"{category['id']}:")

        groups = []

        for group in category["groups"]:
            if group["kind"] != "image":
                items = collect_sketch_items(
                    repo_root=repo_root,
                    group=group,
                )
            elif group.get("manifest"):
                items = collect_manifest_items(
                    repo_root=repo_root,
                    gallery_root=gallery_root,
                    category_id=category["id"],
                    group=group,
                    context=context,
                )
            else:
                items = collect_image_items(
                    repo_root=repo_root,
                    gallery_root=gallery_root,
                    category_id=category["id"],
                    group=group,
                    context=context,
                )

            if not items:
                continue

            print(f"  {group['id']}: {len(items)} item(s)")

            groups.append(
                {
                    "id": group["id"],
                    "title": group["title"],
                    "blurb": group["blurb"],
                    "kind": group["kind"],
                    "directory": group.get("directory") or group["manifest"],
                    "facets": collect_facets(group, items),
                    "items": items,
                }
            )

        if not groups:
            continue

        cover = next(
            (
                item.get("thumb")
                for group in groups
                for item in group["items"]
                if item.get("thumb")
            ),
            None,
        )

        categories.append(
            {
                "id": category["id"],
                "title": category["title"],
                "blurb": category["blurb"],
                "count": sum(len(group["items"]) for group in groups),
                "cover": cover,
                "groups": groups,
            }
        )

    return {
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "categories": categories,
    }


def prune_thumbnails(gallery_root: Path, data: dict) -> int:
    """
    Delete thumbnails no longer referenced by the gallery data.

    Keeps the directory honest when artwork is renamed or removed. Only
    files under gallery/thumbs are ever considered.
    """
    thumbnail_root = gallery_root / THUMBNAIL_DIRECTORY

    if not thumbnail_root.is_dir():
        return 0

    referenced = {
        item["thumb"]
        for category in data["categories"]
        for group in category["groups"]
        for item in group["items"]
        if item.get("thumb")
    }

    removed = 0

    for path in sorted(thumbnail_root.rglob("*.jpg")):
        relative = path.relative_to(gallery_root).as_posix()

        if relative not in referenced:
            path.unlink()
            removed += 1

    # Clear out any directories the pruning emptied.
    for directory in sorted(
        thumbnail_root.rglob("*"), key=lambda p: len(p.parts), reverse=True
    ):
        if directory.is_dir() and not any(directory.iterdir()):
            directory.rmdir()

    return removed


def read_existing_data(data_path: Path) -> dict | None:
    """Read back a previously written data file, or None if unusable."""
    if not data_path.is_file():
        return None

    text = data_path.read_text(encoding="utf-8")
    match = re.search(r"window\.GALLERY_DATA\s*=\s*", text)

    if match is None:
        return None

    try:
        return json.loads(text[match.end():].rstrip().rstrip(";"))
    except json.JSONDecodeError:
        return None


def comparable_payload(data: dict) -> str:
    """Serialise the data with the build time left out."""
    return json.dumps(
        {key: value for key, value in data.items() if key != "generated"},
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )


def write_data_file(gallery_root: Path, data: dict) -> tuple[Path, bool]:
    """
    Write the data file, and report whether it actually changed.

    Only the build time moves on a rebuild that found nothing new, which
    would otherwise leave the file permanently modified in git. Leave it
    untouched unless the gallery itself changed.
    """
    data_path = gallery_root / DATA_FILENAME
    previous = read_existing_data(data_path)

    is_unchanged = (
        previous is not None
        and comparable_payload(previous) == comparable_payload(data)
    )

    if is_unchanged:
        return data_path, False

    payload = json.dumps(data, indent=2, ensure_ascii=False)

    contents = (
        "// Generated by build_gallery.py. Do not edit by hand.\n"
        f"window.GALLERY_DATA = {payload};\n"
    )

    data_path.write_text(contents, encoding="utf-8")

    return data_path, True


def parse_arguments() -> argparse.Namespace:
    script_directory = Path(__file__).resolve().parent

    parser = argparse.ArgumentParser(
        description="Build thumbnails and data for the static gallery."
    )

    parser.add_argument(
        "--repo",
        type=Path,
        default=script_directory,
        help=(
            "Repository root. Defaults to the directory "
            "containing this script."
        ),
    )

    parser.add_argument(
        "--thumb-size",
        type=int,
        default=DEFAULT_THUMBNAIL_SIZE,
        help=(
            "Longest edge of a generated thumbnail, in pixels. "
            f"Defaults to {DEFAULT_THUMBNAIL_SIZE}."
        ),
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Rebuild every thumbnail, even when it looks up to date.",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_arguments()

    repo_root = args.repo.resolve()

    if not repo_root.is_dir():
        print(
            f"Repository directory does not exist: {repo_root}",
            file=sys.stderr,
        )
        return 2

    gallery_root = repo_root / GALLERY_DIRECTORY

    if not gallery_root.is_dir():
        print(
            f"Gallery directory does not exist: {gallery_root}",
            file=sys.stderr,
        )
        return 2

    data = build_gallery_data(
        repo_root=repo_root,
        gallery_root=gallery_root,
        max_size=args.thumb_size,
        force=args.force,
    )

    removed = prune_thumbnails(gallery_root, data)

    if removed:
        print(f"\nRemoved {removed} stale thumbnail(s).")

    data_path, changed = write_data_file(gallery_root, data)

    total = sum(category["count"] for category in data["categories"])
    relative_data_path = data_path.relative_to(repo_root)

    if changed:
        print(
            f"\nWrote {relative_data_path} "
            f"with {total} item(s) across "
            f"{len(data['categories'])} categories."
        )
    else:
        print(
            f"\n{relative_data_path} is already up to date, "
            f"{total} item(s) across "
            f"{len(data['categories'])} categories."
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
