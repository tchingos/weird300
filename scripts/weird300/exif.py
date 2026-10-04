"""Read the capture date and GPS position from a photo's EXIF data."""

from datetime import date, datetime

from PIL import ExifTags, Image

GPS_LAT_REF, GPS_LAT, GPS_LNG_REF, GPS_LNG = 1, 2, 3, 4


def capture_date(img: Image.Image) -> date | None:
    exif = img.getexif()
    raw = exif.get_ifd(ExifTags.IFD.Exif).get(ExifTags.Base.DateTimeOriginal) or exif.get(
        ExifTags.Base.DateTime
    )
    if not raw:
        return None
    return datetime.strptime(str(raw).strip("\x00")[:19], "%Y:%m:%d %H:%M:%S").date()


def gps_position(img: Image.Image) -> tuple[float, float] | None:
    gps = img.getexif().get_ifd(ExifTags.IFD.GPSInfo)
    if GPS_LAT not in gps or GPS_LNG not in gps:
        return None
    return (
        _to_decimal(gps[GPS_LAT], gps.get(GPS_LAT_REF, "N")),
        _to_decimal(gps[GPS_LNG], gps.get(GPS_LNG_REF, "E")),
    )


def has_metadata(img: Image.Image) -> bool:
    """True if the image still carries EXIF or XMP that would be published."""
    return bool(img.getexif()) or "xmp" in img.info or "XML:com.adobe.xmp" in img.info


def _to_decimal(dms: tuple, ref: str) -> float:
    d, m, s = (float(v) for v in dms)
    sign = -1 if ref in ("S", "W") else 1
    return round(sign * (d + m / 60 + s / 3600), 5)
