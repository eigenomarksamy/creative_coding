#!/usr/bin/env python3

"""
Build the static gallery in gallery/.

Scans the generated artwork directories, writes downscaled thumbnails and
emits gallery/gallery-data.js, which gallery/index.html reads directly.

The generated data file is plain JavaScript rather than JSON so the gallery
also works when index.html is opened straight from disk, without a server.

Every piece is also classified by world, system and interaction, using the
vocabulary below. An image series sets these fields once on its group in
CATEGORIES. A live sketch sets them in its own page, in a
<script type="application/json" id="meta"> block. The build fails on any
value outside the vocabulary, and each item carries the result as
item["taxonomy"], or None when its piece is not classified yet.

Usage:
    python build_gallery.py

Rebuild every thumbnail, ignoring timestamps:
    python build_gallery.py --force
"""

from __future__ import annotations

import argparse
import copy
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

# A live sketch classifies itself in its own page, in a block such as:
#   <script type="application/json" id="meta">{"world": ...}</script>
SCRIPT_TAG_PATTERN = re.compile(
    r"<script\b(?P<attributes>[^>]*)>(?P<body>.*?)</script\s*>",
    re.IGNORECASE | re.DOTALL,
)
META_ID_PATTERN = re.compile(r"""(?:^|\s)id\s*=\s*["']meta["']""")
JSON_TYPE_PATTERN = re.compile(
    r"""(?:^|\s)type\s*=\s*["']application/json["']""",
    re.IGNORECASE,
)

# A world is a piece's artistic identity: slug -> (identity, concepts).
WORLDS = {
    "abstract": (
        "expressive, nonrepresentational compositions",
        "chaos, emotion, entropy",
    ),
    "geometric": (
        "patterns, symmetry, transformations, fractals",
        "order, repetition, precision",
    ),
    "mystic": (
        "sigils, celestial diagrams, symbolic structures",
        "ritual, symbolism, transcendence",
    ),
    "mechanical": (
        "gears, linkages, kinetic sculptures",
        "causality, interdependence, rhythm",
    ),
    "organic": (
        "growth, branching, evolving organisms",
        "life, adaptation, emergence",
    ),
    "fluid": (
        "liquid motion, turbulence, diffusion",
        "flow, transformation, continuity",
    ),
    "cosmic": (
        "orbits, gravitational systems, celestial structures",
        "scale, infinity, spacetime",
    ),
    "glitch": (
        "distortion, feedback, digital corruption",
        "instability, noise, fragmentation",
    ),
    "typographic": (
        "generative lettering, glyphs, procedural poetry",
        "language, meaning, communication",
    ),
    "perceptual": (
        "optical illusions, moiré patterns, impossible forms",
        "ambiguity, perception, paradox",
    ),
    "dynamical": (
        "attractors, phase spaces, nonlinear simulations",
        "determinism, complexity, chaos",
    ),
    "topographic": (
        "generative terrain, contours, imaginary landscapes",
        "space, geography, formation",
    ),
}

# The rules that drive a piece.
SYSTEMS = {
    "particle-fields": "particle fields and flocking",
    "attractors": "attractors and dynamical systems",
    "cellular-automata": "cellular automata",
    "reaction-diffusion": "reaction-diffusion",
    "recursive-growth": "recursive growth and L-systems",
    "oscillators": "oscillators and coupled systems",
    "procedural-geometry": "procedural geometry",
    "noise-fields": "noise fields and turbulence",
    "constraints": "physical constraints and linkages",
    "image-feedback": "image transformations and feedback",
    "agents": "autonomous agents following simple rules",
}

# How a visitor influences a live sketch.
INTERACTIONS = {
    "pointer": "pointer attraction and repulsion",
    "gesture-drawing": "gesture drawing",
    "touch-drag": "touch and drag",
    "parameter-manipulation": "parameter manipulation",
    "rule-mutation": "rule mutation",
    "placement": "placing obstacles or resources",
    "sound-input": "sound and rhythm input",
    "autonomous": "autonomous evolution",
}

# What a live sketch lets a visitor do. Declare only the meaningful ones.
MODES = {
    "observe": "the system evolves on its own",
    "intervene": "the visitor disturbs or redirects the system",
    "compose": "the visitor builds patterns, structures or rules with it",
}

# Classification fields an image series may set on its group.
SERIES_FIELDS = ("world", "worlds", "systems", "concept")

# Fields that only make sense for something a visitor can run.
LIVE_FIELDS = ("interactions", "modes")

# Everything a live sketch's meta block may contain.
PAGE_FIELDS = ("id", "title") + SERIES_FIELDS + LIVE_FIELDS

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
                "world": "geometric",
                "worlds": ["abstract", "perceptual"],
                "systems": ["procedural-geometry"],
                "concept": (
                    "order from repetition: simple shapes multiplied by a "
                    "rule"
                ),
            },
        ],
    },
    {
        "id": "pycairo",
        "title": "pycairo",
        "blurb": (
            "flow fields, layered Bézier brushwork and gradient masses, "
            "first as one-off sketches and then as a parameterised engine, "
            "then a series drawn from mathematical models."
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
                "world": "abstract",
                "worlds": ["organic", "fluid"],
                "systems": ["noise-fields", "recursive-growth"],
                "concept": (
                    "the elements as motion: wind, heat, soil and water "
                    "traced in strokes"
                ),
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
                "world": "abstract",
                "worlds": ["organic", "geometric"],
                "systems": [
                    "noise-fields",
                    "procedural-geometry",
                    "recursive-growth",
                ],
                "concept": (
                    "texture, flow and branching, explored one script at "
                    "a time"
                ),
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
                "world": "abstract",
                "worlds": ["fluid"],
                "systems": ["noise-fields", "procedural-geometry"],
                "concept": (
                    "one composition in many keys: how palette alone "
                    "changes feeling"
                ),
            },
            {
                "id": "cosmos",
                "title": "cosmos",
                "blurb": (
                    "seven pieces built on mathematical models instead of "
                    "Bézier strokes: spiral galaxies, coupled oscillators, "
                    "Platonic solids, curved spacetime, field lines, drum "
                    "modes and spherical harmonics. in the order set out "
                    "in cosmos.txt."
                ),
                "manifest": "cosmos.txt",
                "search": ["cc_pycairo/gen/cosmos"],
                "kind": "image",
                "source": "pycairo_sketch",
                "world": "cosmic",
                "worlds": ["geometric", "mystic"],
                "systems": ["oscillators", "procedural-geometry"],
                "concept": "the universe as mathematical structure",
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
                "blurb": "click a preview to run it.",
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


class MetadataError(ValueError):
    """A piece's classification is malformed or uses an unknown value."""


def check_slugs(
    value: object,
    vocabulary: dict,
    field: str,
    where: str,
) -> list[str]:
    """Return a list of known slugs, or raise if any entry is unknown."""
    if not isinstance(value, list) or not all(
        isinstance(entry, str) for entry in value
    ):
        raise MetadataError(f"{where}: {field} must be a list of slugs")

    unknown = [entry for entry in value if entry not in vocabulary]

    if unknown:
        raise MetadataError(
            f"{where}: unknown {field} {', '.join(map(repr, unknown))}. "
            f"known: {', '.join(vocabulary)}"
        )

    if len(set(value)) != len(value):
        raise MetadataError(f"{where}: {field} lists the same slug twice")

    return list(value)


def build_taxonomy(fields: dict, where: str, live: bool) -> dict:
    """
    Validate one piece's classification and fill in what it leaves out.

    world is required. A live sketch also needs interactions and modes,
    which an image series may not declare. worlds and systems default to
    empty lists, and concept to None.
    """
    world = fields.get("world")

    if not isinstance(world, str) or world not in WORLDS:
        raise MetadataError(
            f"{where}: world must be one of {', '.join(WORLDS)}, "
            f"not {world!r}"
        )

    worlds = check_slugs(fields.get("worlds", []), WORLDS, "worlds", where)

    if world in worlds:
        raise MetadataError(
            f"{where}: {world!r} is the primary world, so it cannot also "
            f"be a secondary one"
        )

    systems = check_slugs(
        fields.get("systems", []), SYSTEMS, "systems", where
    )

    if live:
        missing = [field for field in LIVE_FIELDS if not fields.get(field)]

        if missing:
            raise MetadataError(
                f"{where}: a live sketch needs {' and '.join(missing)}"
            )

        interactions = check_slugs(
            fields["interactions"], INTERACTIONS, "interactions", where
        )
        modes = check_slugs(fields["modes"], MODES, "modes", where)
    else:
        declared = [field for field in LIVE_FIELDS if field in fields]

        if declared:
            raise MetadataError(
                f"{where}: {' and '.join(declared)} apply only to live "
                f"sketches"
            )

        interactions, modes = [], []

    concept = fields.get("concept")

    if concept is not None and (
        not isinstance(concept, str) or not concept.strip()
    ):
        raise MetadataError(f"{where}: concept must be a line of text")

    return {
        "world": world,
        "worlds": worlds,
        "systems": systems,
        "interactions": interactions,
        "modes": modes,
        "concept": concept.strip() if concept else None,
    }


def series_taxonomy(category_id: str, group: dict) -> dict | None:
    """
    Validate the classification an image series sets on its group.

    A series that sets none of the fields yet returns None, which leaves
    its pieces unclassified rather than failing the build.
    """
    where = f"CATEGORIES {category_id}/{group['id']}"

    declared = {
        field: group[field]
        for field in SERIES_FIELDS + LIVE_FIELDS
        if field in group
    }

    if group["kind"] != "image":
        if declared:
            raise MetadataError(
                f"{where}: live sketches classify themselves in their own "
                f"page, so remove {', '.join(declared)} from the group"
            )

        return None

    if not declared:
        return None

    return build_taxonomy(declared, where, live=False)


def read_page_metadata(text: str, where: str) -> dict | None:
    """Read the meta block of a live sketch page, or None if it has none."""
    blocks = [
        match
        for match in SCRIPT_TAG_PATTERN.finditer(text)
        if META_ID_PATTERN.search(match.group("attributes"))
    ]

    if not blocks:
        return None

    if len(blocks) > 1:
        raise MetadataError(f"{where}: the page has more than one meta block")

    block = blocks[0]

    if not JSON_TYPE_PATTERN.search(block.group("attributes")):
        raise MetadataError(
            f'{where}: the meta block needs type="application/json", '
            f"or the browser runs it as a script"
        )

    try:
        fields = json.loads(block.group("body"))
    except json.JSONDecodeError as error:
        raise MetadataError(
            f"{where}: the meta block is not valid JSON ({error})"
        ) from None

    if not isinstance(fields, dict):
        raise MetadataError(f"{where}: the meta block must be a JSON object")

    unknown = sorted(set(fields) - set(PAGE_FIELDS))

    if unknown:
        raise MetadataError(
            f"{where}: unknown field(s) {', '.join(unknown)} in the meta "
            f"block. known: {', '.join(PAGE_FIELDS)}"
        )

    return fields


def check_unique_ids(categories: list[dict]) -> None:
    """
    Fail when two pieces share an id.

    Ids come from file names, and the worlds view gathers pieces from every
    toolkit, so an id has to be unique across the whole gallery.
    """
    seen: dict[str, str] = {}

    for category in categories:
        for group in category["groups"]:
            where = f"{category['id']}/{group['id']}"

            for item in group["items"]:
                if item["id"] in seen:
                    raise MetadataError(
                        f"two pieces share the id {item['id']!r}, in "
                        f"{seen[item['id']]} and {where}. rename one file"
                    )

                seen[item["id"]] = where


def vocabulary_payload() -> dict:
    """The classification vocabulary, in the shape the gallery reads."""
    return {
        "worlds": [
            {"id": slug, "identity": identity, "concepts": concepts}
            for slug, (identity, concepts) in WORLDS.items()
        ],
        "systems": [
            {"id": slug, "label": label} for slug, label in SYSTEMS.items()
        ],
        "interactions": [
            {"id": slug, "label": label}
            for slug, label in INTERACTIONS.items()
        ],
        "modes": [
            {"id": slug, "label": label} for slug, label in MODES.items()
        ],
    }


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

        fields = read_page_metadata(
            path.read_text(encoding="utf-8", errors="ignore"),
            repo_relative,
        )

        if fields is None:
            print(
                f"  warning: {repo_relative} has no meta block, "
                f"so it is unclassified"
            )
            fields = {}
            taxonomy = None
        else:
            taxonomy = build_taxonomy(fields, repo_relative, live=True)

        if fields.get("id", path.stem) != path.stem:
            raise MetadataError(
                f"{repo_relative}: the meta block's id {fields['id']!r} "
                f"must match the page's id {path.stem!r}"
            )

        title = fields.get("title")

        if title is not None and (
            not isinstance(title, str) or not title.strip()
        ):
            raise MetadataError(
                f"{repo_relative}: title must be a line of text"
            )

        items.append(
            {
                "id": path.stem,
                "kind": "sketch",
                "title": (
                    (title or "").strip()
                    or extract_html_title(path)
                    or humanize(path.stem)
                ),
                "full": relative_to_gallery(repo_relative),
                "bytes": path.stat().st_size,
                "meta": {},
                "taxonomy": taxonomy,
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

    # Checked before any thumbnail is built, so a typo fails fast.
    series = {
        (category["id"], group["id"]): series_taxonomy(category["id"], group)
        for category in CATEGORIES
        for group in category["groups"]
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

            if group["kind"] == "image":
                taxonomy = series[(category["id"], group["id"])]

                if taxonomy is None:
                    print(
                        f"  warning: {group['id']} sets no world, "
                        f"so its pieces are unclassified"
                    )

                # Resolved per piece, so the gallery reads one place and a
                # series can later override single pieces.
                for item in items:
                    item["taxonomy"] = copy.deepcopy(taxonomy)

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

    check_unique_ids(categories)

    return {
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "vocabulary": vocabulary_payload(),
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

    # Nothing is pruned or written when the metadata is invalid.
    try:
        data = build_gallery_data(
            repo_root=repo_root,
            gallery_root=gallery_root,
            max_size=args.thumb_size,
            force=args.force,
        )
    except MetadataError as error:
        print(f"\nmetadata error: {error}", file=sys.stderr)
        return 1

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
