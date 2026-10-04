"""Turn camera photos into web-ready JPEGs with no metadata.

HEIC from an iPhone is supported. Each photo is rotated upright, resized so
its long edge is at most MAX_EDGE, and saved without EXIF, so GPS and camera
details are never published. Date and position are read first and returned.
"""

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from PIL import Image, ImageOps
from pillow_heif import register_heif_opener

from . import exif

register_heif_opener()

MAX_EDGE = 2000
JPEG_QUALITY = 82
SUFFIXES = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp", ".tif", ".tiff"}


@dataclass(frozen=True)
class ImportedPhoto:
    file: str
    source: Path
    taken: date | None
    position: tuple[float, float] | None


def find(inputs: list[Path]) -> list[Path]:
    """Expand files and folders into a sorted list of photo files."""
    found: list[Path] = []
    for path in inputs:
        if path.is_dir():
            found.extend(sorted(p for p in path.iterdir() if p.suffix.lower() in SUFFIXES))
        elif path.is_file():
            found.append(path)
        else:
            raise FileNotFoundError(path)
    if inputs and not found:
        raise FileNotFoundError(f"no photos in {', '.join(map(str, inputs))}")
    return found


def import_all(sources: list[Path], dest: Path) -> list[ImportedPhoto]:
    """Process sources into dest as 01.jpg, 02.jpg, ..., continuing any existing numbering."""
    dest.mkdir(parents=True, exist_ok=True)
    first = len(list(dest.glob("*.jpg"))) + 1
    return [_import_one(src, dest / f"{n:02d}.jpg") for n, src in enumerate(sources, start=first)]


def _import_one(src: Path, out: Path) -> ImportedPhoto:
    with Image.open(src) as img:
        taken, position = exif.capture_date(img), exif.gps_position(img)
        clean = ImageOps.exif_transpose(img).convert("RGB")
    clean.thumbnail((MAX_EDGE, MAX_EDGE), Image.Resampling.LANCZOS)
    clean.info.clear()  # nothing from the source rides along into the save
    clean.save(out, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
    return ImportedPhoto(file=out.name, source=src, taken=taken, position=position)
