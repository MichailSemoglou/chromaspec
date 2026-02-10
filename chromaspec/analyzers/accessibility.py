"""
Accessibility and contrast analysis functions.

This module provides functions for calculating WCAG contrast ratios
and accessibility ratings for color pairs.
"""

import logging
from typing import Dict, List

from chromaspec.converters import calculate_luminance, hex_to_rgb
from chromaspec.utils.constants import WCAGThresholds

logger = logging.getLogger(__name__)


def get_contrast_ratio(color1: str, color2: str) -> float:
    """
    Calculate WCAG contrast ratio between two colors.

    Args:
        color1: First HEX color string.
        color2: Second HEX color string.

    Returns:
        Contrast ratio (1-21).
    """
    l1 = calculate_luminance(hex_to_rgb(color1))
    l2 = calculate_luminance(hex_to_rgb(color2))
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def get_wcag_rating(contrast_ratio: float) -> str:
    """
    Get WCAG accessibility rating based on contrast ratio.

    Args:
        contrast_ratio: The contrast ratio value.

    Returns:
        WCAG rating string (AAA, AA, AA Large, or Fail).
    """
    if contrast_ratio >= WCAGThresholds.AAA:
        return "AAA"
    elif contrast_ratio >= WCAGThresholds.AA:
        return "AA"
    elif contrast_ratio >= WCAGThresholds.AA_LARGE:
        return "AA Large"
    return "Fail"


def analyze_contrast_with_backgrounds(
    color: str, backgrounds: List[str] = None
) -> Dict[str, Dict]:
    """
    Analyze contrast of a color against multiple background colors.

    Args:
        color: The foreground HEX color string.
        backgrounds: List of background HEX color strings. Defaults to white and black.

    Returns:
        Dictionary mapping background colors to contrast info with keys:
        'contrast_ratio', 'rating', and 'recommendation'.
    """
    if backgrounds is None:
        backgrounds = ["#FFFFFF", "#000000"]

    results = {}

    for bg_color in backgrounds:
        ratio = get_contrast_ratio(color, bg_color)
        rating = get_wcag_rating(rating=ratio)

        # Determine best use
        if bg_color == "#FFFFFF":
            recommendation = (
                "White text on color"
                if ratio > get_contrast_ratio(color, "#000000")
                else None
            )
        elif bg_color == "#000000":
            recommendation = (
                "Black text on color"
                if ratio > get_contrast_ratio(color, "#FFFFFF")
                else None
            )
        else:
            recommendation = None

        results[bg_color] = {
            "contrast_ratio": round(ratio, 2),
            "rating": rating,
            "recommendation": recommendation,
        }

    logger.debug(
        f"Analyzed contrast for color {color} against {len(backgrounds)} backgrounds"
    )
    return results
