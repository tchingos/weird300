# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11", "pyyaml>=6"]
# ///
"""Validate every place page. Exits non-zero if anything needs fixing.

    uv run scripts/check.py

Runs locally before publishing and in CI on every push.
"""

import sys

from weird300 import checks, site
from weird300.pages import Page


def main() -> int:
    pages = [Page.load(p) for p in sorted(site.PLACES_DIR.glob("*.md"))]
    failed = False
    for page in pages:
        problems = checks.check_page(page)
        status = "ok" if not problems else "FAIL"
        print(f"{status:4}  {page.path.relative_to(site.ROOT)}")
        for problem in problems:
            print(f"      - {problem}")
        failed |= bool(problems)
    for folder in checks.orphan_photo_dirs({p.slug for p in pages}):
        print(f"FAIL  {folder.relative_to(site.ROOT)} has no matching page")
        failed = True
    print(f"\n{len(pages)} page(s) checked.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
