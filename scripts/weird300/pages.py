"""Read and write place pages: YAML front matter followed by a Markdown write-up."""

import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import yaml

PLACEHOLDER = "TODO"


@dataclass
class Page:
    path: Path
    meta: dict
    body: str = ""
    photos: list[dict] = field(init=False)

    def __post_init__(self) -> None:
        self.photos = self.meta.setdefault("photos", []) or []
        self.meta["photos"] = self.photos

    @property
    def slug(self) -> str:
        return self.path.stem

    @classmethod
    def load(cls, path: Path) -> "Page":
        text = path.read_text()
        match = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
        if not match:
            raise ValueError(f"{path}: no front matter")
        return cls(path, yaml.safe_load(match.group(1)) or {}, match.group(2).strip())

    def save(self) -> None:
        front = yaml.safe_dump(self.meta, sort_keys=False, allow_unicode=True, width=1000)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(f"---\n{front}---\n\n{self.body.strip()}\n")

    def add_photos(self, files: list[str]) -> None:
        self.photos.extend({"file": f, "caption": ""} for f in files)


def slugify(name: str) -> str:
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_name.replace("'", "").lower()).strip("-")


def new_page(path: Path, **meta) -> Page:
    """A fresh page with every field present, unknowns marked TODO for check.py to catch."""
    ordered = {
        "title": meta["title"],
        "category": meta["category"],
        "region": meta.get("region") or PLACEHOLDER,
        "visited": meta.get("visited") or PLACEHOLDER,
        "with": meta.get("companions") or "",
        "entry": meta.get("entry"),
        "book_page": meta.get("book_page"),
        "lat": meta.get("lat") if meta.get("lat") is not None else PLACEHOLDER,
        "lng": meta.get("lng") if meta.get("lng") is not None else PLACEHOLDER,
        "summary": PLACEHOLDER,
        "photos": [],
    }
    return Page(path, ordered, f"{PLACEHOLDER}: write about the visit.")
