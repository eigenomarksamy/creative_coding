#!/usr/bin/env python3

"""
Find PNG and JPG files that are not referenced in README.md and add them
to the appropriate image section.

Files inside:
    cc_pygame  -> ### pygame
    cc_pycairo -> ### pycairo

Usage:
    python update_readme_images.py

Check without modifying README.md:
    python update_readme_images.py --check
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Iterable


SUPPORTED_EXTENSIONS = {".png", ".jpg"}

SECTION_DIRECTORIES = {
    "pygame": "cc_pygame",
    "pycairo": "cc_pycairo",
}

IGNORED_DIRECTORIES = {
    ".git",
    ".idea",
    ".vscode",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
}

# Matches local Markdown image references such as:
# ![name](path/to/image.png)
# ![name](<path/to/image.png>)
MARKDOWN_IMAGE_PATTERN = re.compile(
    r"!\[[^\]]*]"
    r"\(\s*"
    r"<?([^)\s>]+)>?"
    r"(?:\s+[\"'][^\"']*[\"'])?"
    r"\s*\)",
    re.IGNORECASE,
)


def natural_sort_key(value: str) -> list[object]:
    """
    Sort paths containing numbers naturally.

    Example:
        gen_2.jpg comes before gen_10.jpg
    """
    return [
        int(part) if part.isdigit() else part.casefold()
        for part in re.split(r"(\d+)", value)
    ]


def normalize_markdown_path(path: str) -> str:
    """Normalize a Markdown path for comparison with repository paths."""
    normalized = path.strip().replace("\\", "/")

    while normalized.startswith("./"):
        normalized = normalized[2:]

    return PurePosixPath(normalized).as_posix()


def find_existing_image_paths(readme_text: str) -> set[str]:
    """Extract all image paths currently referenced in the README."""
    return {
        normalize_markdown_path(match.group(1))
        for match in MARKDOWN_IMAGE_PATTERN.finditer(readme_text)
    }


def should_ignore(path: Path) -> bool:
    return any(part in IGNORED_DIRECTORIES for part in path.parts)


def find_images_for_section(
    repo_root: Path,
    directory_name: str,
) -> list[str]:
    """
    Find supported images whose relative path contains the requested directory.
    """
    found_images: list[str] = []

    for path in repo_root.rglob("*"):
        if not path.is_file():
            continue

        relative_path = path.relative_to(repo_root)

        if should_ignore(relative_path):
            continue

        if path.suffix.casefold() not in SUPPORTED_EXTENSIONS:
            continue

        if directory_name not in relative_path.parts:
            continue

        found_images.append(relative_path.as_posix())

    return sorted(found_images, key=natural_sort_key)


def find_missing_images(
    repo_root: Path,
    existing_paths: set[str],
) -> dict[str, list[str]]:
    """Return missing images grouped by README section."""
    missing_by_section: dict[str, list[str]] = {}

    for section, directory_name in SECTION_DIRECTORIES.items():
        repository_images = find_images_for_section(
            repo_root=repo_root,
            directory_name=directory_name,
        )

        missing_by_section[section] = [
            image_path
            for image_path in repository_images
            if normalize_markdown_path(image_path) not in existing_paths
        ]

    return missing_by_section


def find_section_heading(
    readme_text: str,
    section_name: str,
) -> re.Match[str] | None:
    pattern = re.compile(
        rf"^###\s+{re.escape(section_name)}\s*$",
        re.IGNORECASE | re.MULTILINE,
    )
    return pattern.search(readme_text)


def find_images_heading(readme_text: str) -> re.Match[str] | None:
    return re.search(
        r"^##\s+images\s*$",
        readme_text,
        re.IGNORECASE | re.MULTILINE,
    )


def insert_text(
    source: str,
    index: int,
    inserted_text: str,
) -> str:
    before = source[:index].rstrip()
    after = source[index:].lstrip("\n")

    result = f"{before}\n\n{inserted_text.rstrip()}\n"

    if after:
        result += f"\n{after}"

    return result


def ensure_section_exists(
    readme_text: str,
    section_name: str,
) -> str:
    """
    Create a missing section under ## images.

    pygame is inserted before pycairo when possible.
    pycairo is inserted at the end of the images block.
    """
    if find_section_heading(readme_text, section_name):
        return readme_text

    images_heading = find_images_heading(readme_text)

    if images_heading is None:
        readme_text = (
            readme_text.rstrip()
            + "\n\n## images\n"
        )
        images_heading = find_images_heading(readme_text)

    assert images_heading is not None

    # Keep pygame before pycairo.
    if section_name == "pygame":
        pycairo_heading = find_section_heading(readme_text, "pycairo")

        if pycairo_heading is not None:
            return insert_text(
                readme_text,
                pycairo_heading.start(),
                "### pygame",
            )

    # Find the end of the ## images block.
    search_start = images_heading.end()

    next_top_level_heading = re.search(
        r"^#{1,2}\s+.+$",
        readme_text[search_start:],
        re.MULTILINE,
    )

    if next_top_level_heading is None:
        insertion_index = len(readme_text)
    else:
        insertion_index = search_start + next_top_level_heading.start()

    return insert_text(
        readme_text,
        insertion_index,
        f"### {section_name}",
    )


def markdown_entry(image_path: str) -> str:
    path = PurePosixPath(image_path)
    alt_text = path.stem

    return f"![{alt_text}]({image_path})"


def append_entries_to_section(
    readme_text: str,
    section_name: str,
    image_paths: Iterable[str],
) -> str:
    image_paths = list(image_paths)

    if not image_paths:
        return readme_text

    readme_text = ensure_section_exists(readme_text, section_name)

    section_heading = find_section_heading(readme_text, section_name)

    if section_heading is None:
        raise RuntimeError(
            f"Could not find or create README section: {section_name}"
        )

    section_content_start = section_heading.end()

    # Stop at the next heading at the same or higher level.
    next_heading = re.search(
        r"^#{1,3}\s+.+$",
        readme_text[section_content_start:],
        re.MULTILINE,
    )

    if next_heading is None:
        insertion_index = len(readme_text)
    else:
        insertion_index = (
            section_content_start
            + next_heading.start()
        )

    entries = "\n\n".join(
        markdown_entry(image_path)
        for image_path in image_paths
    )

    return insert_text(
        readme_text,
        insertion_index,
        entries,
    )


def update_readme(
    readme_text: str,
    missing_by_section: dict[str, list[str]],
) -> str:
    updated_text = readme_text

    # Explicit order keeps pygame before pycairo.
    for section_name in ("pygame", "pycairo"):
        updated_text = append_entries_to_section(
            readme_text=updated_text,
            section_name=section_name,
            image_paths=missing_by_section.get(section_name, []),
        )

    return updated_text


def print_missing_images(
    missing_by_section: dict[str, list[str]],
) -> None:
    for section_name in ("pygame", "pycairo"):
        images = missing_by_section.get(section_name, [])

        if not images:
            continue

        print(f"{section_name}:")

        for image_path in images:
            print(f"  + {image_path}")


def parse_arguments() -> argparse.Namespace:
    script_directory = Path(__file__).resolve().parent

    parser = argparse.ArgumentParser(
        description=(
            "Add missing cc_pygame and cc_pycairo images "
            "to the repository README."
        )
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
        "--readme",
        type=Path,
        default=Path("README.md"),
        help="README path, relative to the repository root.",
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help=(
            "Report missing images without modifying the README. "
            "Exits with status 1 when images are missing."
        ),
    )

    return parser.parse_args()


def main() -> int:
    args = parse_arguments()

    repo_root = args.repo.resolve()
    readme_path = args.readme

    if not readme_path.is_absolute():
        readme_path = repo_root / readme_path

    if not repo_root.is_dir():
        print(
            f"Repository directory does not exist: {repo_root}",
            file=sys.stderr,
        )
        return 2

    if not readme_path.is_file():
        print(
            f"README file does not exist: {readme_path}",
            file=sys.stderr,
        )
        return 2

    readme_text = readme_path.read_text(encoding="utf-8")
    existing_paths = find_existing_image_paths(readme_text)

    missing_by_section = find_missing_images(
        repo_root=repo_root,
        existing_paths=existing_paths,
    )

    missing_count = sum(
        len(images)
        for images in missing_by_section.values()
    )

    if missing_count == 0:
        print("README is already up to date.")
        return 0

    print(f"Found {missing_count} missing image(s):")
    print_missing_images(missing_by_section)

    if args.check:
        return 1

    updated_text = update_readme(
        readme_text=readme_text,
        missing_by_section=missing_by_section,
    )

    readme_path.write_text(updated_text, encoding="utf-8")

    print(f"\nUpdated {readme_path.relative_to(repo_root)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())