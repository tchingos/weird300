# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11"]
# ///
"""Draw the site icon: a map pin.

    uv run scripts/make_icons.py

Writes assets/icons/favicon.svg (modern browsers) plus PNG and ICO versions
for iPhones and older browsers. Edit the shapes below and re-run to change it.
"""

import math
from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent.parent / "assets" / "icons"
GRID = 64  # every shape is defined on a 64x64 grid

TEAL, WHITE = "#0f766e", "#ffffff"
HEAD = (32, 24, 20)  # the pin's round head: centre x, centre y, radius
TIP = (32, 61)  # the point of the pin
DOT = (32, 24, 8)  # the white hole in the head


def tangents() -> tuple[tuple[float, float], tuple[float, float]]:
    """Where straight lines from the tip touch the head, so the pin's sides are smooth."""
    cx, cy, r = HEAD
    d = TIP[1] - cy
    a = math.acos(r / d)  # angle at the head's centre between the tip and a tangent point
    left = (cx - r * math.sin(a), cy + r * math.cos(a))
    right = (cx + r * math.sin(a), cy + r * math.cos(a))
    return left, right


def svg() -> str:
    (lx, ly), (rx, ry) = tangents()
    r = HEAD[2]
    pin = f"M{lx:.2f},{ly:.2f} A{r},{r} 0 1 1 {rx:.2f},{ry:.2f} L{TIP[0]},{TIP[1]} Z"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {GRID} {GRID}">'
        f'<path d="{pin}" fill="{TEAL}"/>'
        f'<circle cx="{DOT[0]}" cy="{DOT[1]}" r="{DOT[2]}" fill="{WHITE}"/></svg>\n'
    )


def png(size: int) -> Image.Image:
    """Draw at 8x and downsample, which gives clean anti-aliased edges."""
    s = size * 8 / GRID
    img = Image.new("RGBA", (size * 8, size * 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    dot = lambda c, **kw: d.ellipse([(c[0] - c[2]) * s, (c[1] - c[2]) * s, (c[0] + c[2]) * s, (c[1] + c[2]) * s], **kw)
    left, right = tangents()
    d.polygon([(x * s, y * s) for x, y in (left, right, TIP)], fill=TEAL)
    dot(HEAD, fill=TEAL)
    dot(DOT, fill=WHITE)
    return img.resize((size, size), Image.Resampling.LANCZOS)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "favicon.svg").write_text(svg())
    png(32).save(OUT / "favicon-32.png")
    # iOS fills transparency with black, so the home-screen icon gets a white ground.
    touch = Image.new("RGBA", (180, 180), WHITE)
    touch.alpha_composite(png(180))
    touch.convert("RGB").save(OUT / "apple-touch-icon.png")
    png(48).save(OUT.parent.parent / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    print(f"Wrote icons to {OUT.relative_to(OUT.parent.parent)}/ and favicon.ico")


if __name__ == "__main__":
    main()
