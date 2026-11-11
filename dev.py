#!/usr/bin/env python3

"""
The repository's everyday commands, the same on Windows, WSL, Linux and macOS.

    python dev.py setup    create .venv and install requirements.txt into it
    python dev.py build    build the gallery. other options, such as --force,
                           are passed to build_gallery.py
    python dev.py test     run the engines' tests with node --test
    python dev.py check    test, then build: run this before pushing
    python dev.py serve    serve the repository at http://127.0.0.1:8765/gallery/
    python dev.py open     open gallery/index.html from disk in the browser

Use python3 where there is no python, as on Ubuntu, or py on Windows. Only
the standard library is used, and nothing needs activating: the build runs
in the active virtual environment if there is one, then in .venv if it
exists, and otherwise in the Python running this script, like the
Cloudflare build.

This file only wraps the commands in README.md, which still work by hand,
and the Cloudflare build doesn't use it. It is not published (.assetsignore).
"""

from __future__ import annotations

import argparse
import os
import platform
import subprocess
import sys
import webbrowser
from pathlib import Path


ROOT = Path(__file__).resolve().parent
VENV = ROOT / ".venv"
GALLERY_PAGE = ROOT / "gallery" / "index.html"
DATA_FILE = ROOT / "gallery" / "gallery-data.js"


def venv_python() -> Path:
    """Where .venv keeps its interpreter on this operating system."""
    if os.name == "nt":
        return VENV / "Scripts" / "python.exe"

    return VENV / "bin" / "python"


def foreign_venv() -> bool:
    """
    True when .venv exists without an interpreter for this system.

    A checkout shared between Windows and WSL has one .venv, and an
    environment made on one side doesn't run on the other.
    """
    return VENV.is_dir() and not venv_python().is_file()


def build_python() -> str:
    """The interpreter the build runs in."""
    if sys.prefix != sys.base_prefix:
        return sys.executable

    if venv_python().is_file():
        return str(venv_python())

    return sys.executable


def shown(part: str) -> str:
    """A command part as printed, with paths inside the repo made relative."""
    path = Path(part)

    if path.is_absolute() and path.is_relative_to(ROOT):
        return str(path.relative_to(ROOT))

    return part


def run(command: list[str]) -> int:
    print("$ " + " ".join(shown(part) for part in command), flush=True)

    return subprocess.run(command, cwd=ROOT).returncode


def fail(message: str) -> int:
    print(f"dev.py: {message}", file=sys.stderr)

    return 1


def is_wsl() -> bool:
    return (
        "WSL_DISTRO_NAME" in os.environ
        or "microsoft" in platform.uname().release.casefold()
    )


def setup(args: argparse.Namespace, extra: list[str]) -> int:
    python = venv_python()

    if not python.is_file():
        if VENV.exists():
            return fail(
                f".venv has no {python.relative_to(ROOT)}, so it was made on "
                f"another system (Windows and WSL can't share one) or setup "
                f"was interrupted. Delete .venv and run setup again."
            )

        code = run([sys.executable, "-m", "venv", str(VENV)])

        if code:
            return code

    return run(
        [
            str(python),
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "-r",
            "requirements.txt",
        ]
    )


def build(args: argparse.Namespace, extra: list[str]) -> int:
    python = build_python()

    pillow = subprocess.run(
        [python, "-c", "import PIL"],
        capture_output=True,
    )

    if pillow.returncode:
        hint = (
            " .venv was made on another system, so delete it first."
            if foreign_venv()
            else ""
        )

        return fail(
            f"Pillow isn't installed for {shown(python)}. "
            f"Run: python dev.py setup.{hint}"
        )

    return run([python, "build_gallery.py", *extra])


def test(args: argparse.Namespace, extra: list[str]) -> int:
    try:
        return run(["node", "--test"])
    except FileNotFoundError:
        return fail(
            "node isn't on the PATH. The tests need node 20 or later, and "
            "no packages."
        )


def check(args: argparse.Namespace, extra: list[str]) -> int:
    code = test(args, [])

    if code:
        return fail("the tests failed, so the build was skipped.")

    code = build(args, extra)

    if code:
        return code

    print("\ncheck passed: the tests and the build are clean.")

    return 0


def serve(args: argparse.Namespace, extra: list[str]) -> int:
    if not DATA_FILE.is_file():
        print("note: the gallery isn't built yet. Run: python dev.py build")

    host = "127.0.0.1" if args.bind in ("0.0.0.0", "::") else args.bind

    # From the repository root, not gallery/: the tiles link to the full
    # size renders as ../cc_pycairo/... and the sketches as ../canvas/...
    print(f"gallery at http://{host}:{args.port}/gallery/, Ctrl-C stops it")

    try:
        return run(
            [
                sys.executable,
                "-m",
                "http.server",
                str(args.port),
                "--bind",
                args.bind,
                "--directory",
                str(ROOT),
            ]
        )
    except KeyboardInterrupt:
        return 0


def open_gallery(args: argparse.Namespace, extra: list[str]) -> int:
    if not DATA_FILE.is_file():
        return fail("the gallery isn't built yet. Run: python dev.py build")

    if is_wsl():
        # The browser runs on Windows, so hand it the Windows form of the
        # path, \\wsl.localhost\<distribution>\... for a checkout inside
        # WSL. explorer.exe exits with 1 even when it worked.
        target = subprocess.run(
            ["wslpath", "-w", str(GALLERY_PAGE)],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

        print(f"opening {target}")
        subprocess.run(["explorer.exe", target])

        return 0

    target = GALLERY_PAGE.as_uri()
    print(f"opening {target}")

    if not webbrowser.open(target):
        return fail(f"no browser was found. Open {target} by hand.")

    return 0


COMMANDS = {
    "setup": (setup, "create .venv and install requirements.txt into it"),
    "build": (
        build,
        "build the gallery. other options, such as --force, are passed to "
        "build_gallery.py",
    ),
    "test": (test, "run the engines' tests with node --test"),
    "check": (check, "test, then build: run this before pushing"),
    "serve": (serve, "serve the repository over http"),
    "open": (open_gallery, "open the gallery from disk in the browser"),
}

# The commands that pass options they don't know on to build_gallery.py.
PASSES_OPTIONS = ("build", "check")


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="dev.py",
        description="The repository's everyday commands, on any system.",
    )
    commands = parser.add_subparsers(
        dest="command",
        metavar="command",
        required=True,
    )

    for name, (_, help_text) in COMMANDS.items():
        command = commands.add_parser(name, help=help_text)

        if name == "serve":
            command.add_argument("--port", type=int, default=8765)
            command.add_argument(
                "--bind",
                default="127.0.0.1",
                help=(
                    "address to listen on. 0.0.0.0 shares the gallery with "
                    "the local network. defaults to 127.0.0.1"
                ),
            )

    args, extra = parser.parse_known_args()

    if extra and args.command not in PASSES_OPTIONS:
        parser.error(f"unrecognized arguments: {' '.join(extra)}")

    handler, _ = COMMANDS[args.command]

    return handler(args, extra)


if __name__ == "__main__":
    raise SystemExit(main())
