# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.40"]
# ///
"""Render pages at phone and desktop width and save screenshots to look at.

    uv run scripts/check_mobile.py /places/pixel-wall/ /places/fata-morgana-teahouse/
    uv run scripts/check_mobile.py --base https://tchingos.github.io/weird300 /about/

Headless Chrome on its own ignores the viewport meta tag, so a plain
`--window-size=412` screenshot renders a desktop layout squeezed into a narrow
window and tells you nothing. This drives real device emulation instead, which
is the only way the phone breakpoints actually apply.

It also fails on horizontal overflow, which is the usual cause of a page that
will not sit still under a thumb.
"""

import argparse
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

PHONE = {"width": 412, "height": 915}
DESKTOP = {"width": 1280, "height": 900}


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+", help="Site paths, e.g. /places/pixel-wall/")
    ap.add_argument("--base", default="http://localhost:8799", help="Base URL (default: a server this script starts)")
    ap.add_argument("--site", default="_site", help="Built site to serve when --base is not given")
    ap.add_argument("--out", default="/tmp/weird300-shots", help="Where to write the PNGs")
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    server = None
    if args.base == "http://localhost:8799":
        root = Path(args.site)
        if not root.exists():
            sys.exit(f"{root} does not exist; build the site first or pass --base")
        server = subprocess.Popen([sys.executable, "-m", "http.server", "8799", "--directory", str(root)],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    problems = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="chrome")
            for path in args.paths:
                slug = path.strip("/").replace("/", "-") or "home"
                for label, size, mobile in (("phone", PHONE, True), ("desktop", DESKTOP, False)):
                    ctx = browser.new_context(viewport=size, device_scale_factor=2,
                                              is_mobile=mobile, has_touch=mobile)
                    page = ctx.new_page()
                    page.goto(args.base.rstrip("/") + path, wait_until="networkidle")
                    inner = page.evaluate("window.innerWidth")
                    scroll = page.evaluate("document.documentElement.scrollWidth")
                    shot = out / f"{slug}-{label}.png"
                    page.screenshot(path=str(shot), full_page=False)
                    flag = ""
                    if scroll > inner + 1:
                        flag = f"  OVERFLOW by {scroll - inner}px"
                        problems.append(f"{path} ({label})")
                    print(f"{path:44} {label:8} {inner}px  -> {shot}{flag}")
                    ctx.close()
            browser.close()
    finally:
        if server:
            server.terminate()

    if problems:
        sys.exit("horizontal overflow on: " + ", ".join(problems))
    print("\nNo horizontal overflow. Open the PNGs and check the photo crops.")


if __name__ == "__main__":
    main()
