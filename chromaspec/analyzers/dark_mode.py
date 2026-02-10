"""Dark mode compatibility checker for color schemes.

This module provides functions to verify that color schemes work well
in both light and dark themes by checking contrast ratios.
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Tuple

from chromaspec.analyzers import get_contrast_ratio, get_wcag_rating
from chromaspec.converters import hex_to_rgb, rgb_to_hsl
from chromaspec.exceptions import ValidationError
from chromaspec.utils.validators import validate_hex_color

logger = logging.getLogger(__name__)


@dataclass
class DarkModeResult:
    """Result of dark mode compatibility check.

    Attributes:
        light_background: Light mode background color.
        dark_background: Dark mode background color.
        text_color: Text color being tested.
        light_contrast: Contrast ratio in light mode.
        dark_contrast: Contrast ratio in dark mode.
        light_rating: WCAG rating in light mode.
        dark_rating: WCAG rating in dark mode.
        is_compatible: Whether both modes pass minimum requirements.
    """

    light_background: str
    dark_background: str
    text_color: str
    light_contrast: float
    dark_contrast: float
    light_rating: str
    dark_rating: str
    is_compatible: bool

    def to_dict(self) -> dict:
        """Convert result to dictionary.

        Returns:
            Dictionary containing dark mode compatibility information.
        """
        return {
            "text_color": self.text_color,
            "light_mode": {
                "background": self.light_background,
                "contrast_ratio": round(self.light_contrast, 2),
                "wcag_rating": self.light_rating,
            },
            "dark_mode": {
                "background": self.dark_background,
                "contrast_ratio": round(self.dark_contrast, 2),
                "wcag_rating": self.dark_rating,
            },
            "is_compatible": self.is_compatible,
        }

    def __str__(self) -> str:
        """Return string representation."""
        status = "✓ Compatible" if self.is_compatible else "✗ Not Compatible"
        return (
            f"Dark Mode Check: {self.text_color} - {status}\n"
            f"  Light:  {self.light_background} | Contrast: {self.light_contrast:.2f}:1 | {self.light_rating}\n"
            f"  Dark:   {self.dark_background} | Contrast: {self.dark_contrast:.2f}:1 | {self.dark_rating}"
        )


def check_dark_mode_compatibility(
    text_color: str,
    light_background: str = "#FFFFFF",
    dark_background: str = "#121212",
    min_rating: str = "AA",
) -> DarkModeResult:
    """Check if a text color works in both light and dark modes.

    Args:
        text_color: Text HEX color to test.
        light_background: Light mode background HEX color (default: #FFFFFF).
        dark_background: Dark mode background HEX color (default: #121212).
        min_rating: Minimum WCAG rating required ("AA", "AAA", or "AA Large").

    Returns:
        DarkModeResult with compatibility information.

    Raises:
        ValidationError: If any color is invalid.
    """
    validate_hex_color(text_color)
    validate_hex_color(light_background)
    validate_hex_color(dark_background)

    logger.info(
        f"Checking dark mode compatibility: {text_color} against "
        f"{light_background} (light) and {dark_background} (dark)"
    )

    # Calculate contrast ratios
    light_contrast = get_contrast_ratio(text_color, light_background)
    dark_contrast = get_contrast_ratio(text_color, dark_background)

    # Get WCAG ratings
    light_rating = get_wcag_rating(light_contrast)
    dark_rating = get_wcag_rating(dark_contrast)

    # Check compatibility based on minimum rating
    is_compatible = _check_rating_compatibility(light_rating, dark_rating, min_rating)

    logger.info(
        f"Result: Light={light_rating} ({light_contrast:.2f}), "
        f"Dark={dark_rating} ({dark_contrast:.2f}), Compatible={is_compatible}"
    )

    return DarkModeResult(
        light_background=light_background,
        dark_background=dark_background,
        text_color=text_color,
        light_contrast=light_contrast,
        dark_contrast=dark_contrast,
        light_rating=light_rating,
        dark_rating=dark_rating,
        is_compatible=is_compatible,
    )


def _check_rating_compatibility(
    light_rating: str, dark_rating: str, min_rating: str
) -> bool:
    """Check if both ratings meet minimum requirements.

    Args:
        light_rating: WCAG rating for light mode.
        dark_rating: WCAG rating for dark mode.
        min_rating: Minimum required rating.

    Returns:
        True if both modes meet requirements, False otherwise.
    """
    rating_priority = {"Fail": 0, "AA Large": 1, "AA": 2, "AAA": 3}
    min_priority = rating_priority.get(min_rating, 1)

    return (
        rating_priority.get(light_rating, 0) >= min_priority
        and rating_priority.get(dark_rating, 0) >= min_priority
    )


def generate_dark_mode_palette(
    primary: str,
    light_bg: str = "#FFFFFF",
    dark_bg: str = "#121212",
    target_rating: str = "AA",
) -> Dict[str, DarkModeResult]:
    """Generate a palette tested for dark mode compatibility.

    Args:
        primary: Primary HEX color.
        light_bg: Light mode background HEX color.
        dark_bg: Dark mode background HEX color.
        target_rating: Target WCAG rating.

    Returns:
        Dictionary mapping color names to DarkModeResult objects.

    Raises:
        ValidationError: If primary color is invalid.
    """
    from chromaspec.generators.palette import (
        generate_accessibility_palette,
        generate_triadic_palette,
    )

    validate_hex_color(primary)

    # Generate color palette
    palette = generate_triadic_palette(primary, target_rating)

    # Check each color in both light and dark modes
    colors = {
        "primary": palette.primary,
        "secondary": palette.secondary,
        "accent": palette.accent or palette.text,
    }

    results = {}
    for name, color in colors.items():
        results[name] = check_dark_mode_compatibility(
            color, light_bg, dark_bg, target_rating
        )

    # Also check the text color from palette
    results["text"] = check_dark_mode_compatibility(
        palette.text, light_bg, dark_bg, target_rating
    )

    return results


def suggest_dark_mode_adjustments(
    text_color: str,
    light_background: str = "#FFFFFF",
    dark_background: str = "#121212",
    target_rating: str = "AA",
    max_iterations: int = 10,
) -> List[Dict[str, str]]:
    """Suggest adjustments to make text color dark mode compatible.

    Args:
        text_color: Text HEX color to adjust.
        light_background: Light mode background HEX color.
        dark_background: Dark mode background HEX color.
        target_rating: Target WCAG rating.
        max_iterations: Maximum brightness adjustment iterations.

    Returns:
        List of suggested color adjustments with compatibility info.
    """
    validate_hex_color(text_color)
    validate_hex_color(light_background)
    validate_hex_color(dark_background)

    suggestions = []

    # Try adjusting brightness in both directions
    for i in range(-max_iterations, max_iterations + 1):
        if i == 0:
            continue  # Skip original color

        from chromaspec.generators.palette import _adjust_brightness

        adjusted = _adjust_brightness(text_color, i * 5)

        result = check_dark_mode_compatibility(
            adjusted, light_background, dark_background, target_rating
        )

        if result.is_compatible:
            suggestions.append(
                {
                    "color": adjusted,
                    "adjustment": f"{'+' if i > 0 else ''}{i * 5}%",
                    "light_contrast": round(result.light_contrast, 2),
                    "dark_contrast": round(result.dark_contrast, 2),
                }
            )

    return suggestions


def get_compatible_text_color(
    background_light: str = "#FFFFFF",
    background_dark: str = "#121212",
    target_rating: str = "AA",
) -> str:
    """Find a text color that works in both light and dark modes.

    Args:
        background_light: Light mode background HEX color.
        background_dark: Dark mode background HEX color.
        target_rating: Target WCAG rating.

    Returns:
        HEX color that works in both modes.

    Raises:
        ValidationError: If backgrounds are invalid.
    """
    validate_hex_color(background_light)
    validate_hex_color(background_dark)

    # Try common text colors
    test_colors = ["#000000", "#FFFFFF", "#333333", "#666666", "#999999"]

    for color in test_colors:
        result = check_dark_mode_compatibility(
            color, background_light, background_dark, target_rating
        )
        if result.is_compatible:
            logger.info(f"Found compatible text color: {color}")
            return color

    # If none found, try adjusting brightness
    from chromaspec.generators.palette import _adjust_brightness

    for i in range(5, 95, 5):
        # Try grays at different brightness levels
        gray = f"#{i:02X}{i:02X}{i:02X}"
        result = check_dark_mode_compatibility(
            gray, background_light, background_dark, target_rating
        )
        if result.is_compatible:
            logger.info(f"Found compatible gray: {gray}")
            return gray

    # Fall back to black (usually works on light, may fail on dark)
    logger.warning("No perfect match found, using fallback")
    return "#000000"
