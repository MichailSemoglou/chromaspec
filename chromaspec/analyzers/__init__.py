"""
Color analysis modules for ChromaSpec.

This package provides functions for analyzing colors including classification,
harmony generation, and accessibility analysis.
"""

from chromaspec.analyzers.accessibility import (
    analyze_contrast_with_backgrounds,
    get_contrast_ratio,
    get_wcag_rating,
)
from chromaspec.analyzers.classification import (
    categorize_colors,
    is_blue_color,
    is_dominant_color,
    is_green_color,
    is_red_color,
)
from chromaspec.analyzers.dark_mode import (
    DarkModeResult,
    check_dark_mode_compatibility,
    generate_dark_mode_palette,
    get_compatible_text_color,
    suggest_dark_mode_adjustments,
)
from chromaspec.analyzers.harmonies import (
    get_analogous_colors,
    get_complementary_color,
    get_split_complementary,
    get_triadic_colors,
)

__all__ = [
    # Classification
    "is_dominant_color",
    "is_red_color",
    "is_green_color",
    "is_blue_color",
    "categorize_colors",
    # Harmonies
    "get_complementary_color",
    "get_analogous_colors",
    "get_split_complementary",
    "get_triadic_colors",
    # Accessibility
    "get_contrast_ratio",
    "get_wcag_rating",
    "analyze_contrast_with_backgrounds",
    # Dark Mode
    "check_dark_mode_compatibility",
    "DarkModeResult",
    "generate_dark_mode_palette",
    "get_compatible_text_color",
    "suggest_dark_mode_adjustments",
]
