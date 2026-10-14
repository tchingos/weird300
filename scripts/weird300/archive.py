"""Put the untouched originals somewhere safe before the import shrinks them.

The site publishes a 1600px copy of every photo with its metadata stripped,
which is right for the web and useless for print. The originals are what a
photo book needs, so they go to Google Drive through rclone first, and a
manifest of what went up is kept in the repo. The manifest is text, so it
belongs in git. The photos never do.

Archived names are `YYYY-MM-DD-<slug>-NN.jpg`, flat in one Drive folder, so
the whole archive sorts by visit date and no name carries a space. The slug is
the site's own, so the archive, `_places/<slug>.md` and
`assets/photos/<slug>/` all agree. NN matches the site's own NN.jpg, because
both number the photos in the order photos.find returns.

The rclone remote holds the Drive folder id. Nothing here records it, because
this repo is public.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

import yaml
from PIL import Image

from . import exif, site

REMOTE = "weird300"
MANIFEST_DIR = site.ROOT / "originals"
BLOCK = 1 << 20


@dataclass(frozen=True)
class Original:
    site_file: str
    archived: str
    source: str
    bytes: int
    md5: str
    width: int
    height: int


def remote_configured() -> bool:
    listed = subprocess.run(["rclone", "listremotes"], capture_output=True, text=True, check=True)
    return f"{REMOTE}:" in listed.stdout.split()


def md5(path: Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(BLOCK), b""):
            digest.update(block)
    return digest.hexdigest()


def visit_date(sources: list[Path]) -> date | None:
    """The earliest capture date across the photos, as new_visit.py would use."""
    dates = []
    for path in sources:
        with Image.open(path) as img:
            taken = exif.capture_date(img)
        if taken:
            dates.append(taken)
    return min(dates) if dates else None


def prefix(visited: date, slug: str) -> str:
    return f"{visited.isoformat()}-{slug}"


def plan(sources: list[Path], visited: date, slug: str) -> list[Original]:
    """What each original will be called on the remote, and what it will become on the site."""
    planned = []
    for number, path in enumerate(sources, start=1):
        with Image.open(path) as img:
            width, height = img.size
        planned.append(
            Original(
                site_file=f"{number:02d}.jpg",
                archived=f"{prefix(visited, slug)}-{number:02d}{path.suffix.lower()}",
                source=path.name,
                bytes=path.stat().st_size,
                md5=md5(path),
                width=width,
                height=height,
            )
        )
    return planned


def upload(sources: list[Path], planned: list[Original]) -> None:
    """One rclone call per photo, so a failure names the photo that failed."""
    for path, original in zip(sources, planned, strict=True):
        subprocess.run(["rclone", "copyto", str(path), f"{REMOTE}:{original.archived}"], check=True)


def on_remote() -> dict[str, str]:
    """Everything in the archive folder, as {filename: md5}."""
    listed = subprocess.run(
        ["rclone", "lsjson", "--hash", f"{REMOTE}:"], capture_output=True, text=True, check=True
    )
    return {item["Name"]: item.get("Hashes", {}).get("md5", "") for item in json.loads(listed.stdout)}


def verify(planned: list[Original]) -> list[str]:
    """Every original must be on the remote under its archived name, byte for byte."""
    there = on_remote()
    problems = []
    for original in planned:
        if original.archived not in there:
            problems.append(f"{original.archived} is not on the remote")
        elif there[original.archived] != original.md5:
            problems.append(f"{original.archived} is on the remote with a different checksum")
    return problems


def manifest_path(slug: str) -> Path:
    return MANIFEST_DIR / f"{slug}.yml"


def write_manifest(slug: str, visited: date, title: str, planned: list[Original]) -> Path:
    path = manifest_path(slug)
    path.parent.mkdir(parents=True, exist_ok=True)
    body = {
        "slug": slug,
        "title": title,
        "visited": visited,
        "remote": f"{REMOTE}:",
        "archived_on": date.today(),
        "files": [asdict(o) for o in planned],
    }
    path.write_text(yaml.safe_dump(body, sort_keys=False, allow_unicode=True))
    return path


def manifest_matches(slug: str, planned: list[Original]) -> bool:
    """True when a manifest exists and records exactly these photos, so a re-run is a no-op."""
    path = manifest_path(slug)
    if not path.exists():
        return False
    recorded = yaml.safe_load(path.read_text()).get("files", [])
    return [f["md5"] for f in recorded] == [o.md5 for o in planned]


def archived(slug: str) -> bool:
    """True once the originals for this slug are safely up. The gate on clearing the inbox."""
    return manifest_path(slug).exists()
