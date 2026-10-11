"""Validation rules for pages. Each rule returns a list of problems."""

from datetime import date
from pathlib import Path

from PIL import Image

from . import exif, renditions, site
from .shapes import shape_of
from .pages import PLACEHOLDER, POST_NAME, Page

REQUIRED = {
    "place": ("title", "category", "region", "visited", "published", "lat", "lng", "summary"),
    "post": ("title", "summary"),
}
# Generous box around Great Britain, Northern Ireland and the islands.
LAT_RANGE, LNG_RANGE = (49.0, 61.5), (-11.0, 2.5)
BANNED_CHARACTERS = {"\u2014": "em dash", "\u2013": "en dash"}


def check_page(page: Page) -> list[str]:
    common = [*_required_fields(page), *_placeholders(page), *_writing(page), *_photos(page)]
    if page.kind == "post":
        return [*_post_name(page), *_post_pin(page), *common]
    return [*_category(page), *_visited(page), *_coordinates(page), *common]


def _required_fields(page: Page) -> list[str]:
    return [f"missing `{k}`" for k in REQUIRED[page.kind] if page.meta.get(k) in (None, "")]


def _post_name(page: Page) -> list[str]:
    return [] if POST_NAME.match(page.path.stem) else ["post files must be named YYYY-MM-DD-slug.md"]


def _post_pin(page: Page) -> list[str]:
    """A journal post is mapped only if it carries a location name and both coordinates."""
    lat, lng = page.meta.get("lat"), page.meta.get("lng")
    if lat is None and lng is None:
        return []
    if lat is None or lng is None:
        return ["a mapped post needs both `lat` and `lng`"]
    if not page.meta.get("location"):
        return ["a mapped post needs a `location` to name its pin"]
    return _coordinates(page)


def _category(page: Page) -> list[str]:
    allowed = site.categories()
    cat = page.meta.get("category")
    return [] if cat in allowed else [f"category {cat!r} is not one of {allowed}"]


def _visited(page: Page) -> list[str]:
    problems = []
    for key in ("visited", "published"):
        value = page.meta.get(key)
        if value in (PLACEHOLDER, None):
            continue  # reported by _placeholders or _required_fields
        if not isinstance(value, date):
            problems.append(f"`{key}` must be YYYY-MM-DD, got {value!r}")
    visited, published = page.meta.get("visited"), page.meta.get("published")
    if isinstance(visited, date) and isinstance(published, date) and published < visited:
        problems.append("`published` is before `visited`")
    return problems


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
    folder = page.photo_dir
    listed = [p.get("file") for p in page.photos]
    problems = [] if listed else ["no photos"]
    for photo in page.photos:
        name, path = photo.get("file"), folder / str(photo.get("file"))
        if not path.exists():
            problems.append(f"photo {name} is listed but missing from {folder.relative_to(site.ROOT)}")
            continue
        with Image.open(path) as img:
            if exif.has_metadata(img):
                problems.append(f"photo {name} still has metadata; re-import it")
            if max(img.size) > renditions.MAIN_EDGE:
                problems.append(f"photo {name} is {max(img.size)}px; the budget is {renditions.MAIN_EDGE}px")
            actual = shape_of(img.size)
        if photo.get("shape") != actual:
            problems.append(f"photo {name} has shape {photo.get('shape')!r} but is actually {actual!r}")
        thumb = renditions.thumb_path(path)
        if not thumb.exists():
            problems.append(f"photo {name} has no thumbnail at {thumb.relative_to(site.ROOT)}")
            continue
        with Image.open(thumb) as img:
            if exif.has_metadata(img) or max(img.size) > renditions.THUMB_EDGE:
                problems.append(f"thumbnail for {name} has metadata or is over {renditions.THUMB_EDGE}px")
    files = [p for p in (folder.glob("*"), (folder / renditions.THUMB_DIR).glob("*")) for p in p] if folder.exists() else []
    unlisted = sorted(str(p.relative_to(folder)) for p in files if p.is_file() and p.name not in listed)
    problems += [f"photo {n} is in the folder but not on the page" for n in unlisted]
    return problems


def orphan_photo_dirs(pages: list[Page]) -> list[Path]:
    owned = {p.photo_dir for p in pages}
    return [
        d
        for root in site.PHOTO_DIRS.values()
        if root.exists()
        for d in root.iterdir()
        if d.is_dir() and d not in owned
    ]
