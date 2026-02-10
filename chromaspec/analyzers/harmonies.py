"""
Color harmony analysis functions.

This module provides functions for calculating color harmonies including
complementary and analogous colors.
"""

import logging
from typing import Tuple

from chromaspec.converters import hex_to_rgb, hsl_to_rgb, rgb_to_hsl

logger = logging.getLogger(__name__)


def get_complementary_color(hex_color: str) -> str:
    """
    Get the complementary color (opposite on color wheel).

    Args:
        hex_color: A HEX color string.

    Returns:
        The complementary color as a HEX string.
    """
    rgb = hex_to_rgb(hex_color)
    comp = (255 - rgb[0], 255 - rgb[1], 255 - rgb[2])
    return f"#{comp[0]:02X}{comp[1]:02X}{comp[2]:02X}"


def get_analogous_colors(hex_color: str) -> Tuple[str, str]:
    """
    Get analogous colors (adjacent on color wheel, ±30°).

    Args:
        hex_color: A HEX color string.

    Returns:
        A tuple of two analogous colors as HEX strings.
    """
    rgb = hex_to_rgb(hex_color)
    hsl = rgb_to_hsl(rgb)

    h1 = (hsl[0] + 30) % 360
    h2 = (hsl[0] - 30) % 360

    rgb1 = hsl_to_rgb(h1, hsl[1], hsl[2])
    rgb2 = hsl_to_rgb(h2, hsl[1], hsl[2])

    return (
        f"#{rgb1[0]:02X}{rgb1[1]:02X}{rgb1[2]:02X}",
        f"#{rgb2[0]:02X}{rgb2[1]:02X}{rgb2[2]:02X}",
    )


def get_split_complementary(hex_color: str) -> Tuple[str, str]:
    """
    Get split-complementary colors (150° from base).

    Args:
        hex_color: A HEX color string.

    Returns:
        A tuple of two split-complementary colors as HEX strings.
    """
    rgb = hex_to_rgb(hex_color)
    hsl = rgb_to_hsl(rgb)

    h1 = (hsl[0] + 150) % 360
    h2 = (hsl[0] + 210) % 360

    rgb1 = hsl_to_rgb(h1, hsl[1], hsl[2])
    rgb2 = hsl_to_rgb(h2, hsl[1], hsl[2])

    return (
        f"#{rgb1[0]:02X}{rgb1[1]:02X}{rgb1[2]:02X}",
        f"#{rgb2[0]:02X}{rgb2[1]:02X}{rgb2[2]:02X}",
    )


def get_triadic_colors(hex_color: str) -> Tuple[str, str]:
    """
    Get triadic colors (120° and 240° from base).

    Args:
        hex_color: A HEX color string.

    Returns:
        A tuple of two triadic colors as HEX strings.
    """
    rgb = hex_to_rgb(hex_color)
    hsl = rgb_to_hsl(rgb)

    h1 = (hsl[0] + 120) % 360
    h2 = (hsl[0] + 240) % 360

    rgb1 = hsl_to_rgb(h1, hsl[1], hsl[2])
    rgb2 = hsl_to_rgb(h2, hsl[1], hsl[2])

    return (
        f"#{rgb1[0]:02X}{rgb1[1]:02X}{rgb1[2]:02X}",
        f"#{rgb2[0]:02X}{rgb2[1]:02X}{rgb2[2]:02X}",
    )
