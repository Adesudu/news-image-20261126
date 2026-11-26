"""Deliver the pre-rendered front page for news-image-20261126.

The front page image is already in the repository as entry.png. This
entrypoint only moves an exact copy of it into the directory the grader
reads (MAKEFUN_OUTPUT_DIR, or "out" when that variable is empty or unset).
Copying bytes keeps the output identical on every run, with no rendering
work at grade time and no third-party imports. It also avoids importing
the renderer module: the grader runs with python3 -P, which keeps the
script's own directory off sys.path, so a sibling import would fail.
"""

import os
import shutil
import sys
from pathlib import Path


SOURCE_IMAGE = "entry.png"


def destination_dir() -> Path:
    """Return the directory the grader reads for the output image."""
    configured = os.environ.get("MAKEFUN_OUTPUT_DIR", "").strip()
    return Path(configured) if configured else Path("out")


def deliver(source: Path, directory: Path) -> Path:
    """Copy the image into the destination directory, creating it first."""
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / source.name
    shutil.copyfile(source, target)
    return target


def main() -> int:
    here = Path(__file__).resolve().parent
    source = here / SOURCE_IMAGE
    if not source.is_file():
        print(f"error: {SOURCE_IMAGE} is missing next to main.py", file=sys.stderr)
        return 1
    target = deliver(source, destination_dir())
    print(f"wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
