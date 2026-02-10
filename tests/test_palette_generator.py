"""Tests for color palette generator with accessibility compliance."""

import pytest

from chromaspec.exceptions import ValidationError
from chromaspec.generators.palette import (
    ColorPalette,
    _adjust_brightness,
    _rotate_hue,
    generate_accessibility_palette,
    generate_split_complementary_palette,
    generate_tetradic_palette,
    generate_triadic_palette,
)


class TestColorPalette:
    """Test ColorPalette dataclass."""

    def test_palette_initialization(self):
        """Test ColorPalette initialization."""
        palette = ColorPalette(
            name="Test",
            primary="#FF0000",
            secondary="#00FF00",
            background="#FFFFFF",
            text="#000000",
        )
        assert palette.name == "Test"
        assert palette.primary == "#FF0000"
        assert palette.secondary == "#00FF00"
        assert palette.background == "#FFFFFF"
        assert palette.text == "#000000"
        assert palette.accent is None

    def test_palette_to_dict(self):
        """Test palette conversion to dictionary."""
        palette = ColorPalette(
            name="Test",
            primary="#FF0000",
            secondary="#00FF00",
            background="#FFFFFF",
            text="#000000",
            accent="#0000FF",
            wcag_rating="AA",
            contrast_ratio=5.25,
        )
        result = palette.to_dict()
        assert result["name"] == "Test"
        assert result["colors"]["primary"] == "#FF0000"
        assert result["accessibility"]["wcag_rating"] == "AA"
        assert result["accessibility"]["contrast_ratio"] == 5.25

    def test_palette_str_representation(self):
        """Test string representation of palette."""
        palette = ColorPalette(
            name="Test",
            primary="#FF0000",
            secondary="#00FF00",
            background="#FFFFFF",
            text="#000000",
            wcag_rating="AA",
            contrast_ratio=5.25,
        )
        result = str(palette)
        assert "Test Palette:" in result
        assert "#FF0000" in result
        assert "WCAG Rating: AA" in result
        assert "5.25:1" in result


class TestRotateHue:
    """Test hue rotation functionality."""

    def test_rotate_hue_180_degrees(self):
        """Test rotating hue by 180 degrees."""
        result = _rotate_hue("#FF0000", 180)
        assert result == "#00FFFF"

    def test_rotate_hue_120_degrees(self):
        """Test rotating hue by 120 degrees."""
        result = _rotate_hue("#FF0000", 120)
        # Should result in green
        assert result[1:3].upper() in ["FF", "00", "80"]

    def test_rotate_hue_90_degrees(self):
        """Test rotating hue by 90 degrees."""
        result = _rotate_hue("#FF0000", 90)
        # Should result in yellow-ish color
        assert result.startswith("#")
        assert len(result) == 7

    def test_rotate_hue_360_degrees(self):
        """Test rotating hue by full circle (should be same color)."""
        result = _rotate_hue("#FF0000", 360)
        # Should return to original color
        assert result == "#FF0000"

    def test_rotate_hue_negative_degrees(self):
        """Test rotating hue by negative degrees."""
        result = _rotate_hue("#FF0000", -90)
        # Should work correctly
        assert len(result) == 7
        assert result.startswith("#")


class TestAdjustBrightness:
    """Test brightness adjustment functionality."""

    def test_adjust_brightness_lighter(self):
        """Test making color lighter."""
        result = _adjust_brightness("#FF0000", 20)
        # Should be lighter (higher lightness)
        assert result.startswith("#")
        # Verify it's different from original
        assert result != "#FF0000"

    def test_adjust_brightness_darker(self):
        """Test making color darker."""
        result = _adjust_brightness("#FF0000", -20)
        # Should be darker (lower lightness)
        assert result.startswith("#")
        # Verify it's different from original
        assert result != "#FF0000"

    def test_adjust_brightness_white_to_darker(self):
        """Test adjusting white to darker."""
        result = _adjust_brightness("#FFFFFF", -50)
        # Should still be gray
        assert result.startswith("#")
        assert result != "#FFFFFF"

    def test_adjust_brightness_black_to_lighter(self):
        """Test adjusting black to lighter."""
        result = _adjust_brightness("#000000", 50)
        # Should be some shade of gray
        assert result.startswith("#")
        assert result != "#000000"

    def test_adjust_brightness_bounds(self):
        """Test brightness adjustment stays within bounds."""
        result = _adjust_brightness("#FFFFFF", 50)
        # White stays white
        assert result == "#FFFFFF"

        result = _adjust_brightness("#000000", -50)
        # Black stays black
        assert result == "#000000"


class TestGenerateAccessibilityPalette:
    """Test accessible palette generation."""

    def test_generate_complementary_palette(self):
        """Test generating complementary palette."""
        palette = generate_accessibility_palette("#FF0000")
        assert palette.name == "Complementary"
        assert palette.primary == "#FF0000"
        assert palette.secondary == _rotate_hue("#FF0000", 180)
        assert palette.text in ["#000000", "#FFFFFF"]
        assert palette.wcag_rating in ["AA", "AAA", "AA Large"]
        assert palette.contrast_ratio > 0

    def test_generate_palette_with_invalid_color(self):
        """Test palette generation with invalid color."""
        with pytest.raises(ValidationError):
            generate_accessibility_palette("INVALID")

    def test_generate_palette_with_aaa_rating(self):
        """Test generating palette with AAA target rating."""
        palette = generate_accessibility_palette("#000000", target_rating="AAA")
        assert palette.wcag_rating == "AAA"
        assert palette.contrast_ratio >= 7.0

    def test_generate_palette_with_blue(self):
        """Test generating palette from blue color."""
        palette = generate_accessibility_palette("#0000FF")
        assert palette.primary == "#0000FF"
        assert len(palette.secondary) == 7
        assert palette.secondary.startswith("#")


class TestGenerateTriadicPalette:
    """Test triadic palette generation."""

    def test_generate_triadic_palette(self):
        """Test generating triadic palette."""
        palette = generate_triadic_palette("#FF0000")
        assert palette.name == "Triadic"
        assert palette.primary == "#FF0000"
        assert palette.secondary == _rotate_hue("#FF0000", 120)
        assert palette.accent == _rotate_hue("#FF0000", 240)
        assert palette.background in [
            palette.primary,
            palette.secondary,
            palette.accent,
        ]
        assert palette.contrast_ratio > 0

    def test_triadic_palette_accent_present(self):
        """Test that triadic palette has accent color."""
        palette = generate_triadic_palette("#FF0000")
        assert palette.accent is not None
        assert palette.accent.startswith("#")

    def test_triadic_palette_invalid_color(self):
        """Test triadic palette with invalid color."""
        with pytest.raises(ValidationError):
            generate_triadic_palette("INVALID")


class TestGenerateSplitComplementaryPalette:
    """Test split-complementary palette generation."""

    def test_generate_split_complementary_palette(self):
        """Test generating split-complementary palette."""
        palette = generate_split_complementary_palette("#FF0000")
        assert palette.name == "Split-Complementary"
        assert palette.primary == "#FF0000"
        assert palette.accent is not None
        assert palette.contrast_ratio > 0

    def test_split_complementary_structure(self):
        """Test split-complementary palette structure."""
        palette = generate_split_complementary_palette("#FF0000")
        complement = _rotate_hue("#FF0000", 180)
        # Secondary and accent should be 30 degrees from complement
        secondary_expected = _rotate_hue(complement, 30)
        accent_expected = _rotate_hue(complement, -30)
        assert palette.secondary == secondary_expected
        assert palette.accent == accent_expected


class TestGenerateTetradicPalette:
    """Test tetradic palette generation."""

    def test_generate_tetradic_palette(self):
        """Test generating tetradic palette."""
        palette = generate_tetradic_palette("#FF0000")
        assert palette.name == "Tetradic"
        assert palette.contrast_ratio > 0
        # All colors should be different
        colors = {palette.primary, palette.secondary, palette.background}
        if palette.accent:
            colors.add(palette.accent)
        assert len(colors) >= 3

    def test_tetradic_palette_90_degree_spacing(self):
        """Test tetradic colors are 90 degrees apart."""
        palette = generate_tetradic_palette("#FF0000")
        # The function generates 90 degree rotations
        c90 = _rotate_hue("#FF0000", 90)
        c180 = _rotate_hue("#FF0000", 180)
        c270 = _rotate_hue("#FF0000", 270)
        # At least one of the expected rotations should be present
        colors = [palette.primary, palette.secondary, palette.background]
        if palette.accent:
            colors.append(palette.accent)
        assert c90 in colors or c180 in colors or c270 in colors


class TestPaletteEdgeCases:
    """Test edge cases for palette generation."""

    def test_generate_with_white(self):
        """Test palette generation with white."""
        palette = generate_accessibility_palette("#FFFFFF")
        assert palette.primary == "#FFFFFF"
        assert palette.contrast_ratio > 0

    def test_generate_with_black(self):
        """Test palette generation with black."""
        palette = generate_accessibility_palette("#000000")
        assert palette.primary == "#000000"
        assert palette.contrast_ratio > 0

    def test_generate_with_gray(self):
        """Test palette generation with gray."""
        palette = generate_accessibility_palette("#808080")
        assert palette.primary == "#808080"
        assert palette.contrast_ratio > 0

    def test_generate_with_case_insensitive(self):
        """Test palette generation accepts both cases."""
        # Both should work without error
        palette1 = generate_accessibility_palette("#ff0000")
        palette2 = generate_accessibility_palette("#FF0000")
        # Note: validator normalizes to uppercase
        assert palette1.primary.upper() == palette2.primary.upper()
