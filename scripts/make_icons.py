# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11"]
# ///
"""Draw the site icon: a basalt-column hexagon with a googly eye.

    uv run scripts/make_icons.py

Writes assets/icons/favicon.svg (modern browsers) plus PNG and ICO versions
for iPhones and older browsers. Edit the shapes below and re-run to change it.
"""

import math
from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent.parent / "assets" / "icons"
GRID = 64  # every shape is defined on a 64x64 grid

TEAL, DARK, WHITE = "#0f766e", "#111418", "#ffffff"
HEX_RADIUS = 31
EYE = (32, 33, 15)  # centre x, centre y, radius
PUPIL = (37, 37, 7.5)  # off-centre, so the eye looks a bit sideways
GLINT = (39.5, 34, 2.2)


def hexagon(scale: float = 1.0) -> list[tuple[float, float]]:
    """Flat-topped hexagon, like the top of a basalt column."""
    return [
        (scale * (32 + HEX_RADIUS * math.cos(math.radians(a))), scale * (32 + HEX_RADIUS * math.sin(math.radians(a))))
        for a in range(0, 360, 60)
    ]


def svg() -> str:
    points = " ".join(f"{x:.2f},{y:.2f}" for x, y in hexagon())
    circle = lambda c, fill: f'<circle cx="{c[0]}" cy="{c[1]}" r="{c[2]}" fill="{fill}"/>'
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {GRID} {GRID}">'
        f'<polygon points="{points}" fill="{TEAL}"/>'
        f'<circle cx="{EYE[0]}" cy="{EYE[1]}" r="{EYE[2]}" fill="{WHITE}" stroke="{DARK}" stroke-width="2.5"/>'
        f"{circle(PUPIL, DARK)}{circle(GLINT, WHITE)}</svg>\n"
    )


def png(size: int) -> Image.Image:
    """Draw at 8x and downsample, which gives clean anti-aliased edges."""
    s = size * 8 / GRID
    img = Image.new("RGBA", (size * 8, size * 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.polygon(hexagon(s), fill=TEAL)
    dot = lambda c, **kw: d.ellipse([(c[0] - c[2]) * s, (c[1] - c[2]) * s, (c[0] + c[2]) * s, (c[1] + c[2]) * s], **kw)
    dot(EYE, fill=WHITE, outline=DARK, width=round(2.5 * s))
    dot(PUPIL, fill=DARK)
    dot(GLINT, fill=WHITE)
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
