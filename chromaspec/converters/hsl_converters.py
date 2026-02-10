"""
HSL color conversion functions.

This module provides functions for converting between HSL and other color formats.
"""

import logging
from functools import lru_cache
from typing import Tuple

logger = logging.getLogger(__name__)


@lru_cache(maxsize=10000)
def rgb_to_hsl(rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
    """
    Convert RGB to HSL (Hue, Saturation, Lightness).

    Args:
        rgb: A tuple of (red, green, blue) values (0-255).

    Returns:
        A tuple of (hue 0-360, saturation 0-100, lightness 0-100).
    """
    r, g, b = rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0

    max_c = max(r, g, b)
    min_c = min(r, g, b)
    lightness = (max_c + min_c) / 2

    if max_c == min_c:
        h = s = 0.0
    else:
        d = max_c - min_c
        s = d / (2 - max_c - min_c) if lightness > 0.5 else d / (max_c + min_c)

        if max_c == r:
            h = (g - b) / d + (6 if g < b else 0)
        elif max_c == g:
            h = (b - r) / d + 2
        else:
            h = (r - g) / d + 4
        h /= 6

    return (round(h * 360, 1), round(s * 100, 1), round(lightness * 100, 1))


def hsl_to_rgb(h: float, s: float, lightness: float) -> Tuple[int, int, int]:
    """
    Convert HSL to RGB.

    Args:
        h: Hue (0-360)
        s: Saturation (0-100)
        lightness: Lightness (0-100)

    Returns:
        A tuple of (red, green, blue) values (0-255).
    """
    h = h / 360.0
    s = s / 100.0
    lightness = lightness / 100.0

    if s == 0:
        r = g = b = lightness
    else:

        def hue_to_rgb(p: float, q: float, t: float) -> float:
            if t < 0:
                t += 1
            if t > 1:
                t -= 1
            if t < 1 / 6:
                return p + (q - p) * 6 * t
            if t < 1 / 2:
                return q
            if t < 2 / 3:
                return p + (q - p) * (2 / 3 - t) * 6
            return p

        q = lightness * (1 + s) if lightness < 0.5 else lightness + s - lightness * s
        p = 2 * lightness - q
        r = hue_to_rgb(p, q, h + 1 / 3)
        g = hue_to_rgb(p, q, h)
        b = hue_to_rgb(p, q, h - 1 / 3)

    return (round(r * 255), round(g * 255), round(b * 255))
