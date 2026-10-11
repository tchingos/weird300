# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11", "pyyaml>=6"]
# ///
"""Bring photos already on the site in line with the size budget in renditions.py.

    uv run scripts/rebuild_photos.py

Only touches what is out of budget: a main photo larger than MAIN_EDGE is
shrunk, and a missing thumbnail is made from the main photo. Running it again
does nothing, so photos are never re-compressed twice.
"""

from PIL import Image

from weird300 import renditions, site
from weird300.pages import Page


def main() -> None:
    pages = [Page.load(p) for d in site.PAGE_DIRS.values() for p in sorted(d.glob("*.md"))]
    for page in pages:
        for photo in page.photos:
            main_path = page.photo_dir / photo["file"]
            with Image.open(main_path) as img:
                img.load()
                too_big = max(img.size) > renditions.MAIN_EDGE
                missing_thumb = not renditions.thumb_path(main_path).exists()
                if too_big or missing_thumb:
                    before = main_path.stat().st_size
                    renditions.write(img.convert("RGB"), main_path)
                    after = main_path.stat().st_size
                    print(f"{main_path.relative_to(site.ROOT)}: {before // 1024} KB -> {after // 1024} KB, "
                          f"thumb {renditions.thumb_path(main_path).stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
