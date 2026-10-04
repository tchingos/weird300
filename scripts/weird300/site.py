"""Where things live in the repo, and the site-wide lists the tools check against."""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
PLACES_DIR = ROOT / "_places"
PHOTOS_DIR = ROOT / "assets" / "photos"
CATEGORIES_FILE = ROOT / "_data" / "categories.yml"


def categories() -> list[str]:
    return [c["name"] for c in yaml.safe_load(CATEGORIES_FILE.read_text())]


def page_path(slug: str) -> Path:
    return PLACES_DIR / f"{slug}.md"


def photo_dir(slug: str) -> Path:
    return PHOTOS_DIR / slug
