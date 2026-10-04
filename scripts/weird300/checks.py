"""Validation rules for place pages. Each rule returns a list of problems."""

from datetime import date
from pathlib import Path

from PIL import Image

from . import exif, site
from .pages import PLACEHOLDER, Page

REQUIRED = ("title", "category", "region", "visited", "lat", "lng", "summary")
# Generous box around Great Britain, Northern Ireland and the islands.
LAT_RANGE, LNG_RANGE = (49.0, 61.5), (-11.0, 2.5)
BANNED_CHARACTERS = {"\u2014": "em dash", "\u2013": "en dash"}


def check_page(page: Page) -> list[str]:
    return [
        *_required_fields(page),
        *_category(page),
        *_date(page),
        *_coordinates(page),
        *_placeholders(page),
        *_writing(page),
        *_photos(page),
    ]


def _required_fields(page: Page) -> list[str]:
    return [f"missing `{k}`" for k in REQUIRED if page.meta.get(k) in (None, "")]


def _category(page: Page) -> list[str]:
    allowed = site.categories()
    cat = page.meta.get("category")
    return [] if cat in allowed else [f"category {cat!r} is not one of {allowed}"]


def _date(page: Page) -> list[str]:
    visited = page.meta.get("visited")
    if visited == PLACEHOLDER:
        return []  # reported by _placeholders
    return [] if isinstance(visited, date) else [f"`visited` must be YYYY-MM-DD, got {visited!r}"]


def _coordinates(page: Page) -> list[str]:
    lat, lng = page.meta.get("lat"), page.meta.get("lng")
    if PLACEHOLDER in (lat, lng):
        return []
    if not all(isinstance(v, (int, float)) for v in (lat, lng)):
        return [f"lat/lng must be numbers, got {lat!r}, {lng!r}"]
    if not (LAT_RANGE[0] <= lat <= LAT_RANGE[1] and LNG_RANGE[0] <= lng <= LNG_RANGE[1]):
        return [f"({lat}, {lng}) is outside Britain; are lat and lng swapped?"]
    return []


def _placeholders(page: Page) -> list[str]:
    fields = [k for k, v in page.meta.items() if isinstance(v, str) and PLACEHOLDER in v]
    problems = [f"`{k}` still says {PLACEHOLDER}" for k in fields]
    if PLACEHOLDER in page.body:
        problems.append(f"write-up still contains {PLACEHOLDER}")
    return problems


def _writing(page: Page) -> list[str]:
    text = page.path.read_text()
    return [f"contains an {name}; rewrite the sentence" for ch, name in BANNED_CHARACTERS.items() if ch in text]


def _photos(page: Page) -> list[str]:
    folder = site.photo_dir(page.slug)
    listed = [p.get("file") for p in page.photos]
    problems = [] if listed else ["no photos"]
    for name in listed:
        path = folder / name
        if not path.exists():
            problems.append(f"photo {name} is listed but missing from {folder.relative_to(site.ROOT)}")
            continue
        with Image.open(path) as img:
            if exif.has_metadata(img):
                problems.append(f"photo {name} still has metadata; re-import it with new_visit.py")
    unlisted = sorted(p.name for p in folder.glob("*") if p.is_file() and p.name not in listed) if folder.exists() else []
    problems += [f"photo {n} is in the folder but not on the page" for n in unlisted]
    return problems


def orphan_photo_dirs(slugs: set[str]) -> list[Path]:
    if not site.PHOTOS_DIR.exists():
        return []
    return [d for d in site.PHOTOS_DIR.iterdir() if d.is_dir() and d.name not in slugs]
