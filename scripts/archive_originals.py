# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11", "pillow-heif>=0.20", "pyyaml>=6"]
# ///
"""Archive a visit's original photos to Google Drive, before new_visit.py shrinks them.

    uv run scripts/archive_originals.py "London Wall" inbox
    uv run scripts/archive_originals.py "London Wall" inbox --visited 2026-10-14 --dry-run

Uploads through the `weird300` rclone remote as `YYYY-MM-DD-<slug>-NN.jpg`,
checks every file against its checksum on the far side, then writes
originals/<slug>.yml. Only once that manifest exists should the inbox be
cleared. Prints a JSON summary of what it did.
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from weird300 import archive, photos, site
from weird300.pages import slugify


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("title", help="Place name; its slug names the archived files")
    ap.add_argument("photos", nargs="+", type=Path, help="Photo files and/or folders")
    ap.add_argument("--visited", type=date.fromisoformat, help="YYYY-MM-DD (default: earliest photo date)")
    ap.add_argument("--slug", help="Override the slug derived from the title")
    ap.add_argument("--dry-run", action="store_true", help="Show the plan without uploading")
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    sources = photos.find(args.photos)
    slug = args.slug or slugify(args.title)

    visited = args.visited or archive.visit_date(sources)
    if not visited:
        sys.exit("no capture date in these photos; pass --visited YYYY-MM-DD")

    planned = archive.plan(sources, visited, slug)

    if args.dry_run:
        print(json.dumps({
            "dry_run": True,
            "slug": slug,
            "visited": visited.isoformat(),
            "uploads": [f"{o.source} -> {o.archived} (becomes {o.site_file})" for o in planned],
        }, indent=2))
        return

    if not archive.remote_configured():
        sys.exit(f"rclone remote {archive.REMOTE!r} is not set up yet; see CLAUDE.md")

    archive.upload(sources, planned)
    problems = archive.verify(planned)
    if problems:
        sys.exit("archive failed, so the inbox must not be cleared:\n  " + "\n  ".join(problems))

    manifest = archive.write_manifest(slug, visited, args.title, planned)
    print(json.dumps({
        "slug": slug,
        "visited": visited.isoformat(),
        "archived": [o.archived for o in planned],
        "verified": True,
        "manifest": str(manifest.relative_to(site.ROOT)),
    }, indent=2))


if __name__ == "__main__":
    main()
