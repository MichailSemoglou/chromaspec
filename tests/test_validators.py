"""
Tests for validation functions.
"""

import pytest

from chromaspec.exceptions import ValidationError
from chromaspec.utils.validators import (
    validate_color_matches,
    validate_hex_color,
    validate_rgb_tuple,
    validate_svg_size,
)


class TestValidateHexColor:
    """Tests for validate_hex_color function."""

    @pytest.mark.parametrize(
        "hex_color",
        [
            "#FF0000",
            "#00FF00",
            "#0000FF",
            "#FFFFFF",
            "#000000",
            "#F00",  # Short form
            "#123456",
            "#ABCDEF",
            "#abc",  # Lowercase
        ],
    )
    def test_validate_hex_color_valid(self, hex_color):
        """Test valid HEX colors pass validation."""
        validate_hex_color(hex_color)

    @pytest.mark.parametrize(
        "hex_color",
        [
            "#GG0000",  # Invalid character
            "#FF",  # Too short
            "#FF00000",  # Odd length
            "",  # Empty string
            "not-a-color",  # Not a string with #
        ],
    )
    def test_validate_hex_color_invalid(self, hex_color):
        """Test invalid HEX colors raise ValidationError."""
        with pytest.raises(ValidationError):
            validate_hex_color(hex_color)


class TestValidateRgbTuple:
    """Tests for validate_rgb_tuple function."""

    @pytest.mark.parametrize(
        "rgb",
        [
            (255, 0, 0),
            (0, 255, 0),
            (0, 0, 255),
            (128, 128, 128),
            (0, 0, 0),
            (255, 255, 255),
        ],
    )
    def test_validate_rgb_tuple_valid(self, rgb):
        """Test valid RGB tuples pass validation."""
        validate_rgb_tuple(rgb)

    @pytest.mark.parametrize(
        "rgb",
        [
            (256, 0, 0),  # Value too high
            (-1, 0, 0),  # Negative value
            (0, 256, 0),
            (0, 0, 256),
            (255, 0),  # Too few elements
            (255, 0, 0, 0),  # Too many elements
        ],
    )
    def test_validate_rgb_tuple_invalid(self, rgb):
        """Test invalid RGB tuples raise ValidationError."""
        with pytest.raises(ValidationError):
            validate_rgb_tuple(rgb)


class TestValidateSvgSize:
    """Tests for validate_svg_size function."""

    def test_validate_svg_size_too_large(self):
        """Test SVG size limit prevents DoS."""
        # Create SVG larger than MAX_SVG_SIZE (10MB)
        # Each pattern is ~10 bytes, need ~1.2M repetitions for >12MB
        large_svg = "<svg>" + "#FFFFFF, " * 1200000 + "</svg>"
        with pytest.raises(ValidationError, match="too large"):
            validate_svg_size(large_svg)

    def test_validate_svg_size_valid(self):
        """Test valid SVG size passes validation."""
        svg = '<svg><rect fill="#FF0000"/></svg>'
        validate_svg_size(svg)  # Should not raise


class TestValidateColorMatches:
    """Tests for validate_color_matches function."""

    def test_validate_color_matches_too_many(self):
        """Test color match limit prevents ReDoS."""
        with pytest.raises(ValidationError, match="Too many"):
            validate_color_matches(10001)

    def test_validate_color_matches_valid(self):
        """Test valid color count passes validation."""
        validate_color_matches(100)  # Should not raise
