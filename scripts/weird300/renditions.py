"""The two sizes every photo is published at, and the code that writes them.

    main   NN.jpg          long edge <= MAIN_EDGE   hero, portrait hero, lightbox
    thumb  thumbs/NN.jpg   long edge <= THUMB_EDGE  cards and the gallery grid

The budget exists because GitHub Pages caps a published site at 1 GB and git
keeps every photo ever committed. At these settings a photo costs roughly
340 KB + 70 KB, so 300 places with four photos each come to about 480 MB.
"""

from pathlib import Path

from PIL import Image

MAIN_EDGE, MAIN_QUALITY = 1600, 75
THUMB_EDGE, THUMB_QUALITY = 720, 72
THUMB_DIR = "thumbs"


def thumb_path(main: Path) -> Path:
    return main.parent / THUMB_DIR / main.name


def write(img: Image.Image, main: Path) -> None:
    """Save `img` (RGB, upright, sRGB, no metadata) as the main photo and its thumbnail."""
    for edge, quality, out in ((MAIN_EDGE, MAIN_QUALITY, main), (THUMB_EDGE, THUMB_QUALITY, thumb_path(main))):
        copy = img.copy()
        copy.thumbnail((edge, edge), Image.Resampling.LANCZOS)
        copy.info.clear()  # nothing from the source rides along into the save
        out.parent.mkdir(parents=True, exist_ok=True)
        copy.save(out, "JPEG", quality=quality, optimize=True, progressive=True)
