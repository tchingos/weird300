"""Classify a photo as landscape or portrait, which picks the page's hero layout."""

# A photo at least this much wider than tall gets the full-width banner hero.
# Anything squarer or taller gets the side-by-side portrait hero instead.
LANDSCAPE_MIN_RATIO = 1.2


def shape_of(size: tuple[int, int]) -> str:
    width, height = size
    return "landscape" if width >= LANDSCAPE_MIN_RATIO * height else "portrait"
