"""
RGB color conversion functions.

This module provides functions for converting between RGB and other color formats.
"""

import logging
from functools import lru_cache
from typing import Tuple

logger = logging.getLogger(__name__)


@lru_cache(maxsize=10000)
def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """
    Convert a HEX color string to an RGB tuple.

    Args:
        hex_color: A HEX color string (e.g., '#FF0000' or '#F00').

    Returns:
        A tuple of (red, green, blue) values (0-255).

    Raises:
        ValueError: If the hex color is invalid.
    """
    hex_color = hex_color.lstrip("#")

    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)

    if len(hex_color) != 6:
        raise ValueError(f"Invalid HEX color: #{hex_color}")

    try:
        return (
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16),
        )
    except ValueError as e:
        logger.error(f"Failed to convert HEX to RGB: {hex_color}")
        raise ValueError(f"Invalid HEX color: #{hex_color}") from e


@lru_cache(maxsize=10000)
def rgb_to_cmyk(rgb: Tuple[int, int, int]) -> Tuple[int, int, int, int]:
    """
    Convert an RGB tuple to CMYK values.

    Args:
        rgb: A tuple of (red, green, blue) values (0-255).

    Returns:
        A tuple of (cyan, magenta, yellow, black) values (0-100).
    """
    r, g, b = rgb

    r_norm = r / 255.0
    g_norm = g / 255.0
    b_norm = b / 255.0

    k = 1 - max(r_norm, g_norm, b_norm)

    if k == 1:
        return (0, 0, 0, 100)

    c = (1 - r_norm - k) / (1 - k)
    m = (1 - g_norm - k) / (1 - k)
    y = (1 - b_norm - k) / (1 - k)

    return (
        round(c * 100),
        round(m * 100),
        round(y * 100),
        round(k * 100),
    )


def calculate_luminance(rgb: Tuple[int, int, int]) -> float:
    """
    Calculate relative luminance for WCAG contrast ratio.

    The luminance calculation follows the WCAG 2.1 specification.

    Args:
        rgb: A tuple of (red, green, blue) values (0-255).

    Returns:
        Relative luminance value (0-1).
    """

    def adjust(c: int) -> float:
        c_norm = c / 255.0
        return (
            c_norm / 12.92 if c_norm <= 0.03928 else ((c_norm + 0.055) / 1.055) ** 2.4
        )

    return 0.2126 * adjust(rgb[0]) + 0.7152 * adjust(rgb[1]) + 0.0722 * adjust(rgb[2])
