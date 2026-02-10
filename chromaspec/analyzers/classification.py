"""
Color classification functions.

This module provides functions for classifying colors into color families
(Red, Green, Blue) based on their dominant RGB component.
"""

import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


def is_dominant_color(rgb: Tuple[int, int, int], component: str) -> bool:
    """
    Check if the specified RGB component is dominant.

    Args:
        rgb: A tuple of (red, green, blue) values (0-255).
        component: One of 'red', 'green', or 'blue'.

    Returns:
        True if the specified component is dominant, False otherwise.

    Raises:
        ValueError: If component is not 'red', 'green', or 'blue'.
    """
    components = {"red": 0, "green": 1, "blue": 2}

    if component not in components:
        raise ValueError(
            f"Invalid component: {component}. Must be 'red', 'green', or 'blue'."
        )

    idx = components[component]
    other_indices = [i for i in range(3) if i != idx]

    return rgb[idx] > max(rgb[other_indices[0]], rgb[other_indices[1]])


def is_red_color(rgb: Tuple[int, int, int]) -> bool:
    """
    Determine if an RGB color is a shade of red.

    A color is considered red if the red component is greater than
    both the green and blue components.

    Args:
        rgb: A tuple of (red, green, blue) values.

    Returns:
        True if the color is a shade of red, False otherwise.
    """
    return is_dominant_color(rgb, "red")


def is_green_color(rgb: Tuple[int, int, int]) -> bool:
    """
    Determine if an RGB color is a shade of green.

    A color is considered green if the green component is greater than
    both the red and blue components.

    Args:
        rgb: A tuple of (red, green, blue) values.

    Returns:
        True if the color is a shade of green, False otherwise.
    """
    return is_dominant_color(rgb, "green")


def is_blue_color(rgb: Tuple[int, int, int]) -> bool:
    """
    Determine if an RGB color is a shade of blue.

    A color is considered blue if the blue component is greater than
    both the red and green components.

    Args:
        rgb: A tuple of (red, green, blue) values.

    Returns:
        True if the color is a shade of blue, False otherwise.
    """
    return is_dominant_color(rgb, "blue")


def categorize_colors(
    hex_colors_with_freq: Dict[str, float]
) -> Dict[str, List[Tuple[str, float]]]:
    """
    Categorize colors into Red, Green, and Blue groups with frequencies.

    Args:
        hex_colors_with_freq: A dictionary mapping HEX colors to frequency percentages.

    Returns:
        A dictionary with 'red', 'green', 'blue' keys containing lists of (color, frequency) tuples.
    """
    categories: Dict[str, List[Tuple[str, float]]] = {
        "red": [],
        "green": [],
        "blue": [],
    }

    from chromaspec.converters import hex_to_rgb

    for color, freq in hex_colors_with_freq.items():
        rgb = hex_to_rgb(color)
        if is_red_color(rgb):
            categories["red"].append((color, freq))
        elif is_green_color(rgb):
            categories["green"].append((color, freq))
        elif is_blue_color(rgb):
            categories["blue"].append((color, freq))

    # Sort each category by frequency (descending)
    for key in categories:
        categories[key] = sorted(categories[key], key=lambda x: x[1], reverse=True)

    logger.info(
        f"Categorized colors - Red: {len(categories['red'])}, "
        f"Green: {len(categories['green'])}, "
        f"Blue: {len(categories['blue'])}"
    )

    return categories
