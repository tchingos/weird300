"""Turn camera photos into web-ready JPEGs with no metadata.

HEIC from an iPhone is supported. Each photo is rotated upright, converted
from its embedded colour profile (Display P3, or HDR curves like PQ) into
plain sRGB, resized so its long edge is at most MAX_EDGE, and saved without
any metadata, so GPS and camera details are never published. Date and
position are read first and returned.

The colour conversion matters: dropping a profile without converting makes
wide-gamut photos look dull and HDR photos look flat and grey.
"""

from dataclasses import dataclass
from datetime import date
from pathlib import Path

import io

from PIL import Image, ImageCms, ImageOps
from pillow_heif import register_heif_opener

from . import exif
from .shapes import shape_of

register_heif_opener()

MAX_EDGE = 2000
JPEG_QUALITY = 82
SUFFIXES = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp", ".tif", ".tiff"}


@dataclass(frozen=True)
class ImportedPhoto:
    file: str
    source: Path
    shape: str
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


SRGB = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB"))


def _to_srgb(img: Image.Image) -> Image.Image:
    rgb = img.convert("RGB")
    icc = img.info.get("icc_profile")
    if not icc:
        return rgb  # untagged photos are assumed to be sRGB already
    source = ImageCms.ImageCmsProfile(io.BytesIO(icc))
    return ImageCms.profileToProfile(rgb, source, SRGB, renderingIntent=ImageCms.Intent.PERCEPTUAL, outputMode="RGB")


def _import_one(src: Path, out: Path) -> ImportedPhoto:
    with Image.open(src) as img:
        taken, position = exif.capture_date(img), exif.gps_position(img)
        clean = _to_srgb(ImageOps.exif_transpose(img))
    clean.thumbnail((MAX_EDGE, MAX_EDGE), Image.Resampling.LANCZOS)
    clean.info.clear()  # nothing from the source rides along into the save
    clean.save(out, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
    return ImportedPhoto(file=out.name, source=src, shape=shape_of(clean.size), taken=taken, position=position)
