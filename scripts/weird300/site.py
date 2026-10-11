"""Where things live in the repo, and the site-wide lists the tools check against.

There are two kinds of page: places (the Weird 300, in _places/) and journal
posts (everything else, in _posts/). Each keeps its photos in its own folder.
"""

from datetime import date
from pathlib import Path
from typing import Literal

import yaml

ROOT = Path(__file__).resolve().parents[2]
CATEGORIES_FILE = ROOT / "_data" / "categories.yml"

Kind = Literal["place", "post"]
PAGE_DIRS: dict[Kind, Path] = {"place": ROOT / "_places", "post": ROOT / "_posts"}
PHOTO_DIRS: dict[Kind, Path] = {"place": ROOT / "assets" / "photos", "post": ROOT / "assets" / "journal"}


def categories() -> list[str]:
    return [c["name"] for c in yaml.safe_load(CATEGORIES_FILE.read_text())]


def place_path(slug: str) -> Path:
    return PAGE_DIRS["place"] / f"{slug}.md"


def post_path(day: date, slug: str) -> Path:
    return PAGE_DIRS["post"] / f"{day.isoformat()}-{slug}.md"


def photo_dir(kind: Kind, slug: str) -> Path:
    return PHOTO_DIRS[kind] / slug
