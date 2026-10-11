# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11", "pillow-heif>=0.20", "pyyaml>=6"]
# ///
"""Create a journal post (anything that is not one of the 300), or add photos to one.

    uv run scripts/new_post.py "The book arrives" inbox --date 2026-10-06

Photos are cleaned exactly as for places (upright, resized, metadata removed)
and stored in assets/journal/<slug>/. The date defaults to the earliest photo
date, then today. Prints a JSON summary of what it did.
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from weird300 import photos, site
from weird300.pages import Page, new_post, slugify


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("title", help="Post title")
    ap.add_argument("photos", nargs="*", type=Path, help="Photo files and/or folders")
    ap.add_argument("--date", type=date.fromisoformat, help="YYYY-MM-DD")
    ap.add_argument("--slug", help="Override the slug derived from the title")
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    slug = args.slug or slugify(args.title)
    existing = sorted(site.PAGE_DIRS["post"].glob(f"*-{slug}.md"))
    sources = photos.find(args.photos)

    if existing:
        if not sources:
            sys.exit(f"{existing[0].name} already exists; pass photos to add to it.")
        page = Page.load(existing[0])
        imported = photos.import_all(sources, page.photo_dir)
    else:
        imported = photos.import_all(sources, site.photo_dir("post", slug))
        dates = [p.taken for p in imported if p.taken]
        day = args.date or (min(dates) if dates else date.today())
        page = new_post(site.post_path(day, slug), args.title)
    page.add_photos(imported)
    page.save()

    print(json.dumps({
        "page": str(page.path.relative_to(site.ROOT)),
        "action": "added photos" if existing else "created",
        "photos_added": [f"{p.file} ({p.shape}) <- {p.source.name}" for p in imported],
    }, indent=2))


if __name__ == "__main__":
    main()
