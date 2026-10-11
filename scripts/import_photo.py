# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11", "pillow-heif>=0.20", "pyyaml>=6"]
# ///
"""Import photos that belong to a page rather than a place or post.

    uv run scripts/import_photo.py assets/about inbox/me.jpg

Same cleanup as every other photo on the site (upright, sRGB, resized to the
budget in renditions.py, thumbnail, no metadata). Used for the About photo
and the optional home page hero. Prints each saved file and its shape.
"""

import sys
from pathlib import Path

from weird300 import photos, site


def main() -> None:
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    dest = site.ROOT / sys.argv[1]
    for p in photos.import_all(photos.find([Path(a) for a in sys.argv[2:]]), dest):
        print(f"{(dest / p.file).relative_to(site.ROOT)} ({p.shape}) <- {p.source.name}")


if __name__ == "__main__":
    main()
