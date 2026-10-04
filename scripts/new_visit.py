# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11", "pillow-heif>=0.20", "pyyaml>=6"]
# ///
"""Create a place page, or add photos to an existing one.

    uv run scripts/new_visit.py "Fingal's Cave" inbox/fingals-cave \
        --category "Rock Formations" --region "Staffa, Inner Hebrides"

Photos are cleaned by weird300.photos (upright, resized, metadata removed).
For a new page, the visit date and position are prefilled from the photos
unless given here. Unknown fields are left as TODO for check.py to flag.
Prints a JSON summary of what it did.
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from weird300 import photos, site
from weird300.pages import Page, new_page, slugify


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("title", help="Place name as it should appear on the site")
    ap.add_argument("photos", nargs="*", type=Path, help="Photo files and/or folders (can be added later)")
    ap.add_argument("--category", help="One of the names in _data/categories.yml")
    ap.add_argument("--region", help='e.g. "Staffa, Inner Hebrides"')
    ap.add_argument("--visited", type=date.fromisoformat, help="YYYY-MM-DD (default: earliest photo date)")
    ap.add_argument("--with", dest="companions", help="Who came along")
    ap.add_argument("--entry", type=int, help="Entry number in the book")
    ap.add_argument("--book-page", type=int, help="Page number in the book")
    ap.add_argument("--lat", type=float)
    ap.add_argument("--lng", type=float)
    ap.add_argument("--slug", help="Override the slug derived from the title")
    return ap.parse_args()


def centre(points: list[tuple[float, float]]) -> tuple[float, float] | tuple[None, None]:
    if not points:
        return None, None
    return (
        round(sum(p[0] for p in points) / len(points), 5),
        round(sum(p[1] for p in points) / len(points), 5),
    )


def main() -> None:
    args = parse_args()
    slug = args.slug or slugify(args.title)
    path = site.page_path(slug)
    is_new = not path.exists()

    if is_new and args.category not in site.categories():
        sys.exit(f"--category must be one of: {', '.join(site.categories())}")
    if not is_new and not args.photos:
        sys.exit(f"{path.name} already exists; pass photos to add to it.")

    imported = photos.import_all(photos.find(args.photos), site.photo_dir(slug))
    dates = [p.taken for p in imported if p.taken]
    points = [p.position for p in imported if p.position]

    if is_new:
        lat, lng = (args.lat, args.lng) if args.lat is not None else centre(points)
        page = new_page(
            path,
            title=args.title,
            category=args.category,
            region=args.region,
            visited=args.visited or (min(dates) if dates else None),
            companions=args.companions,
            entry=args.entry,
            book_page=args.book_page,
            lat=lat,
            lng=lng,
        )
    else:
        page = Page.load(path)
    page.add_photos([p.file for p in imported])
    page.save()

    summary = {
        "page": str(path.relative_to(site.ROOT)),
        "action": "created" if is_new else "added photos",
        "photos_added": [f"{p.file} <- {p.source.name}" for p in imported],
        "dates_in_photos": sorted({d.isoformat() for d in dates}),
        "gps_in_photos": len(points),
        "photos_without_gps": [p.source.name for p in imported if not p.position],
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
