"""Color palette generator with accessibility compliance.

This module provides functions to generate harmonious color palettes
that meet WCAG accessibility standards for text and background colors.
"""

import logging
from dataclasses import dataclass
from typing import List, Optional, Tuple

from chromaspec.analyzers import get_contrast_ratio, get_wcag_rating
from chromaspec.converters import hex_to_rgb, hsl_to_rgb, rgb_to_hsl
from chromaspec.exceptions import ValidationError
from chromaspec.utils.validators import validate_hex_color

logger = logging.getLogger(__name__)


@dataclass
class ColorPalette:
    """Represents a color palette with accessibility information.

    Attributes:
        name: Name of the palette (e.g., "Complementary", "Triadic")
        primary: Primary HEX color
        secondary: Secondary HEX color
        background: Background HEX color
        text: Text HEX color for contrast
        accent: Optional accent HEX color
        wcag_rating: WCAG rating for text on background
        contrast_ratio: Contrast ratio between text and background
    """

    name: str
    primary: str
    secondary: str
    background: str
    text: str
    accent: Optional[str] = None
    wcag_rating: str = "Fail"
    contrast_ratio: float = 1.0

    def to_dict(self) -> dict:
        """Convert palette to dictionary representation.

        Returns:
            Dictionary containing palette information.
        """
        return {
            "name": self.name,
            "colors": {
                "primary": self.primary,
                "secondary": self.secondary,
                "background": self.background,
                "text": self.text,
                "accent": self.accent,
            },
            "accessibility": {
                "wcag_rating": self.wcag_rating,
                "contrast_ratio": round(self.contrast_ratio, 2),
            },
        }

    def __str__(self) -> str:
        """Return string representation of palette."""
        return (
            f"{self.name} Palette:\n"
            f"  Primary: {self.primary}\n"
            f"  Secondary: {self.secondary}\n"
            f"  Background: {self.background}\n"
            f"  Text: {self.text}\n"
            f"  Accent: {self.accent if self.accent else 'N/A'}\n"
            f"  WCAG Rating: {self.wcag_rating}\n"
            f"  Contrast Ratio: {self.contrast_ratio:.2f}:1"
        )


def _rotate_hue(hex_color: str, degrees: int) -> str:
    """Rotate hue of a HEX color by specified degrees.

    Args:
        hex_color: HEX color string (e.g., "#FF0000")
        degrees: Degrees to rotate hue (0-360)

    Returns:
        HEX color string with rotated hue.
    """
    rgb = hex_to_rgb(hex_color)
    h, s, l = rgb_to_hsl(rgb)
    new_h = (h + degrees) % 360
    new_rgb = hsl_to_rgb(new_h, s, l)
    return f"#{new_rgb[0]:02X}{new_rgb[1]:02X}{new_rgb[2]:02X}"


def _adjust_brightness(hex_color: str, amount: int) -> str:
    """Adjust brightness of a HEX color.

    Args:
        hex_color: HEX color string (e.g., "#FF0000")
        amount: Amount to adjust (-100 to 100, positive = lighter)

    Returns:
        HEX color string with adjusted brightness.
    """
    rgb = hex_to_rgb(hex_color)
    h, s, l = rgb_to_hsl(rgb)
    new_l = max(0, min(100, l + amount))
    new_rgb = hsl_to_rgb(h, s, new_l)
    return f"#{new_rgb[0]:02X}{new_rgb[1]:02X}{new_rgb[2]:02X}"


def _find_accessible_text(
    background: str,
    target_rating: str = "AA",
    max_iterations: int = 20,
) -> Tuple[str, float, str]:
    """Find a text color that meets WCAG rating against background.

    Args:
        background: Background HEX color.
        target_rating: Target WCAG rating ("AA", "AAA", or "AA Large").
        max_iterations: Maximum brightness adjustment iterations.

    Returns:
        Tuple of (text_color, contrast_ratio, wcag_rating).
    """
    # Try black and white first
    for color_name, hex_color in [("Black", "#000000"), ("White", "#FFFFFF")]:
        ratio = get_contrast_ratio(hex_color, background)
        wcag = get_wcag_rating(ratio)
        if wcag == target_rating or (
            target_rating == "AA" and wcag in ("AA", "AAA", "AA Large")
        ):
            return hex_color, ratio, wcag

    # If neither works, adjust brightness of background
    for i in range(1, max_iterations + 1):
        # Try darker version
        darker = _adjust_brightness(background, -i * 5)
        ratio = get_contrast_ratio(darker, background)
        wcag = get_wcag_rating(ratio)
        if wcag == target_rating or (
            target_rating == "AA" and wcag in ("AA", "AAA", "AA Large")
        ):
            return darker, ratio, wcag

        # Try lighter version
        lighter = _adjust_brightness(background, i * 5)
        ratio = get_contrast_ratio(lighter, background)
        wcag = get_wcag_rating(ratio)
        if wcag == target_rating or (
            target_rating == "AA" and wcag in ("AA", "AAA", "AA Large")
        ):
            return lighter, ratio, wcag

    # Fall back to best available
    white_ratio = get_contrast_ratio("#FFFFFF", background)
    black_ratio = get_contrast_ratio("#000000", background)
    if white_ratio >= black_ratio:
        return "#FFFFFF", white_ratio, get_wcag_rating(white_ratio)
    else:
        return "#000000", black_ratio, get_wcag_rating(black_ratio)


def generate_accessibility_palette(
    primary: str, target_rating: str = "AA"
) -> ColorPalette:
    """Generate a 2-color accessible palette (complementary colors).

    Args:
        primary: Primary HEX color.
        target_rating: Target WCAG rating ("AA", "AAA", or "AA Large").

    Returns:
        ColorPalette with complementary colors and accessible text.

    Raises:
        ValidationError: If primary color is invalid.
    """
    validate_hex_color(primary)
    logger.info(f"Generating accessible palette with primary: {primary}")

    # Generate complementary color
    secondary = _rotate_hue(primary, 180)

    # Choose background (lighter of the two for dark text)
    bg_brightness = rgb_to_hsl(hex_to_rgb(primary))[2]
    sec_brightness = rgb_to_hsl(hex_to_rgb(secondary))[2]
    background = primary if bg_brightness > sec_brightness else secondary

    # Find accessible text color
    text, contrast, rating = _find_accessible_text(background, target_rating)

    logger.info(f"Generated palette: contrast={contrast:.2f}, rating={rating}")

    return ColorPalette(
        name="Complementary",
        primary=primary,
        secondary=secondary,
        background=background,
        text=text,
        wcag_rating=rating,
        contrast_ratio=contrast,
    )


def generate_triadic_palette(primary: str, target_rating: str = "AA") -> ColorPalette:
    """Generate a 3-color triadic palette (120° apart).

    Args:
        primary: Primary HEX color.
        target_rating: Target WCAG rating ("AA", "AAA", or "AA Large").

    Returns:
        ColorPalette with triadic colors and accessible text.

    Raises:
        ValidationError: If primary color is invalid.
    """
    validate_hex_color(primary)
    logger.info(f"Generating triadic palette with primary: {primary}")

    # Generate triadic colors
    secondary = _rotate_hue(primary, 120)
    accent = _rotate_hue(primary, 240)

    # Choose background (lightest)
    colors = [primary, secondary, accent]
    brightnesses = [rgb_to_hsl(hex_to_rgb(c))[2] for c in colors]
    bg_idx = brightnesses.index(max(brightnesses))
    background = colors[bg_idx]

    # Find accessible text color
    text, contrast, rating = _find_accessible_text(background, target_rating)

    logger.info(f"Generated triadic palette: contrast={contrast:.2f}, rating={rating}")

    return ColorPalette(
        name="Triadic",
        primary=primary,
        secondary=secondary,
        background=background,
        text=text,
        accent=accent,
        wcag_rating=rating,
        contrast_ratio=contrast,
    )


def generate_split_complementary_palette(
    primary: str, target_rating: str = "AA"
) -> ColorPalette:
    """Generate a split-complementary palette (analogous + complementary).

    Args:
        primary: Primary HEX color.
        target_rating: Target WCAG rating ("AA", "AAA", or "AA Large").

    Returns:
        ColorPalette with split-complementary colors and accessible text.

    Raises:
        ValidationError: If primary color is invalid.
    """
    validate_hex_color(primary)
    logger.info(f"Generating split-complementary palette with primary: {primary}")

    # Generate split-complementary colors (primary + 2 colors adjacent to complement)
    complement = _rotate_hue(primary, 180)
    secondary = _rotate_hue(complement, 30)
    accent = _rotate_hue(complement, -30)

    # Choose background (lightest)
    colors = [primary, secondary, accent]
    brightnesses = [rgb_to_hsl(hex_to_rgb(c))[2] for c in colors]
    bg_idx = brightnesses.index(max(brightnesses))
    background = colors[bg_idx]

    # Find accessible text color
    text, contrast, rating = _find_accessible_text(background, target_rating)

    logger.info(
        f"Generated split-complementary palette: contrast={contrast:.2f}, rating={rating}"
    )

    return ColorPalette(
        name="Split-Complementary",
        primary=primary,
        secondary=secondary,
        background=background,
        text=text,
        accent=accent,
        wcag_rating=rating,
        contrast_ratio=contrast,
    )


def generate_tetradic_palette(primary: str, target_rating: str = "AA") -> ColorPalette:
    """Generate a tetradic palette (4 colors 90° apart).

    Args:
        primary: Primary HEX color.
        target_rating: Target WCAG rating ("AA", "AAA", or "AA Large").

    Returns:
        ColorPalette with tetradic colors and accessible text.

    Raises:
        ValidationError: If primary color is invalid.
    """
    validate_hex_color(primary)
    logger.info(f"Generating tetradic palette with primary: {primary}")

    # Generate tetradic colors (90° apart)
    secondary = _rotate_hue(primary, 90)
    accent = _rotate_hue(primary, 180)
    fourth = _rotate_hue(primary, 270)

    # Choose background (lightest)
    colors = [primary, secondary, accent, fourth]
    brightnesses = [rgb_to_hsl(hex_to_rgb(c))[2] for c in colors]
    bg_idx = brightnesses.index(max(brightnesses))
    background = colors[bg_idx]

    # Find accessible text color
    text, contrast, rating = _find_accessible_text(background, target_rating)

    # Use the two colors adjacent to background as primary/secondary
    colors.remove(background)
    primary = colors[0]
    secondary = colors[1]

    logger.info(f"Generated tetradic palette: contrast={contrast:.2f}, rating={rating}")

    return ColorPalette(
        name="Tetradic",
        primary=primary,
        secondary=secondary,
        background=background,
        text=text,
        accent=fourth if fourth != background else accent,
        wcag_rating=rating,
        contrast_ratio=contrast,
    )
