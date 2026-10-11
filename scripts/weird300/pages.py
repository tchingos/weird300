"""Read and write pages: YAML front matter followed by a Markdown write-up."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import yaml

from . import site
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .photos import ImportedPhoto

PLACEHOLDER = "TODO"
POST_NAME = re.compile(r"^(\d{4}-\d{2}-\d{2})-(.+)$")


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
    def kind(self) -> site.Kind:
        return "post" if self.path.parent == site.PAGE_DIRS["post"] else "place"

    @property
    def slug(self) -> str:
        """Matches Jekyll's slug: a post's filename minus its date prefix."""
        if self.kind == "post":
            match = POST_NAME.match(self.path.stem)
            if not match:
                raise ValueError(f"{self.path.name}: posts must be named YYYY-MM-DD-slug.md")
            return match.group(2)
        return self.path.stem

    @property
    def photo_dir(self) -> Path:
        return site.photo_dir(self.kind, self.slug)

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

    def add_photos(self, imported: list[ImportedPhoto]) -> None:
        self.photos.extend({"file": p.file, "shape": p.shape, "caption": ""} for p in imported)


def slugify(name: str) -> str:
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_name.replace("'", "").lower()).strip("-")


def new_place(path: Path, **meta) -> Page:
    """A fresh place with every field present, unknowns marked TODO for check.py to catch."""
    ordered = {
        "title": meta["title"],
        "category": meta["category"],
        "region": meta.get("region") or PLACEHOLDER,
        "visited": meta.get("visited") or PLACEHOLDER,
        "published": date.today(),  # when the page went up; fix it if publishing slips
        "with": meta.get("companions") or "",
        "entry": meta.get("entry"),
        "book_page": meta.get("book_page"),
        "lat": meta.get("lat") if meta.get("lat") is not None else PLACEHOLDER,
        "lng": meta.get("lng") if meta.get("lng") is not None else PLACEHOLDER,
        "summary": PLACEHOLDER,
        "photos": [],
    }
    return Page(path, ordered, f"{PLACEHOLDER}: write about the visit.")


def new_post(path: Path, title: str) -> Page:
    """A fresh journal post. Its date lives in the filename, as Jekyll expects."""
    meta = {"title": title, "summary": PLACEHOLDER, "location": "", "photos": []}
    return Page(path, meta, f"{PLACEHOLDER}: write the post.")


def post_date(page: Page) -> date:
    return date.fromisoformat(POST_NAME.match(page.path.stem).group(1))
