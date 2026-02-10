"""
Tests for color conversion functions.
"""

from functools import lru_cache

import pytest

from chromaspec.converters import (
    calculate_luminance,
    hex_to_rgb,
    hsl_to_rgb,
    rgb_to_cmyk,
    rgb_to_hsl,
)


class TestHexToRgb:
    """Tests for hex_to_rgb function."""

    @pytest.mark.parametrize(
        "hex_color, expected_rgb",
        [
            ("#FF0000", (255, 0, 0)),
            ("#00FF00", (0, 255, 0)),
            ("#0000FF", (0, 0, 255)),
            ("#FFFFFF", (255, 255, 255)),
            ("#000000", (0, 0, 0)),
            ("#F00", (255, 0, 0)),  # Short form
            ("#0F0", (0, 255, 0)),
            ("#00F", (0, 0, 255)),
            ("#123456", (18, 52, 86)),
            ("#ABC", (170, 187, 204)),
        ],
    )
    def test_hex_to_rgb_valid(self, hex_color, expected_rgb):
        """Test valid HEX to RGB conversions."""
        assert hex_to_rgb(hex_color) == expected_rgb

    def test_hex_to_rgb_case_insensitive(self):
        """Test that HEX to RGB is case insensitive."""
        assert hex_to_rgb("#ff0000") == hex_to_rgb("#FF0000")


class TestRgbToCmyk:
    """Tests for rgb_to_cmyk function."""

    @pytest.mark.parametrize(
        "rgb, expected_cmyk",
        [
            ((255, 0, 0), (0, 100, 100, 0)),
            ((0, 255, 0), (100, 0, 100, 0)),
            ((0, 0, 255), (100, 100, 0, 0)),
            ((255, 255, 255), (0, 0, 0, 0)),
            ((0, 0, 0), (0, 0, 0, 100)),
            ((128, 128, 128), (0, 0, 0, 50)),
        ],
    )
    def test_rgb_to_cmyk_valid(self, rgb, expected_cmyk):
        """Test valid RGB to CMYK conversions."""
        assert rgb_to_cmyk(rgb) == expected_cmyk


class TestCalculateLuminance:
    """Tests for calculate_luminance function."""

    def test_white_luminance(self):
        """Test that white has maximum luminance."""
        assert calculate_luminance((255, 255, 255)) == pytest.approx(1.0, rel=1e-10)

    def test_black_luminance(self):
        """Test that black has minimum luminance."""
        assert calculate_luminance((0, 0, 0)) == pytest.approx(0.0)

    def test_gray_luminance(self):
        """Test that middle gray has luminance ~0.215."""
        luminance = calculate_luminance((128, 128, 128))
        assert 0.2 < luminance < 0.23


class TestRgbToHsl:
    """Tests for rgb_to_hsl function."""

    @pytest.mark.parametrize(
        "rgb, expected_hsl",
        [
            ((255, 0, 0), (0.0, 100.0, 50.0)),
            ((0, 255, 0), (120.0, 100.0, 50.0)),
            ((0, 0, 255), (240.0, 100.0, 50.0)),
            ((255, 255, 255), (0.0, 0.0, 100.0)),
            ((0, 0, 0), (0.0, 0.0, 0.0)),
            ((128, 128, 128), (0.0, 0.0, 50.2)),
        ],
    )
    def test_rgb_to_hsl_valid(self, rgb, expected_hsl):
        """Test valid RGB to HSL conversions."""
        result = rgb_to_hsl(rgb)
        assert result[0] == expected_hsl[0]
        assert result[1] == expected_hsl[1]
        assert result[2] == expected_hsl[2]

    def test_rgb_to_hsl_caching(self):
        """Test that rgb_to_hsl uses LRU cache."""
        rgb = (255, 0, 0)
        # Clear any existing cache
        rgb_to_hsl.cache_clear()

        # First call
        result1 = rgb_to_hsl(rgb)
        assert rgb_to_hsl.cache_info().hits == 0
        assert rgb_to_hsl.cache_info().misses == 1

        # Second call (should hit cache)
        result2 = rgb_to_hsl(rgb)
        assert rgb_to_hsl.cache_info().hits == 1
        assert rgb_to_hsl.cache_info().misses == 1

        # Results should be identical
        assert result1 == result2


class TestHslToRgb:
    """Tests for hsl_to_rgb function."""

    @pytest.mark.parametrize(
        "h, s, l, expected_rgb",
        [
            (0, 100, 50, (255, 0, 0)),
            (120, 100, 50, (0, 255, 0)),
            (240, 100, 50, (0, 0, 255)),
            (0, 0, 100, (255, 255, 255)),
            (0, 0, 0, (0, 0, 0)),
            (0, 0, 50, (128, 128, 128)),
        ],
    )
    def test_hsl_to_rgb_valid(self, h, s, l, expected_rgb):
        """Test valid HSL to RGB conversions."""
        assert hsl_to_rgb(h, s, l) == expected_rgb


class TestRoundTripConversions:
    """Tests for round-trip color conversions."""

    def test_rgb_hsl_rgb_roundtrip(self):
        """Test RGB to HSL to RGB round-trip conversion."""
        test_rgb = (255, 128, 64)
        hsl = rgb_to_hsl(test_rgb)
        result_rgb = hsl_to_rgb(*hsl)
        assert result_rgb == test_rgb

    def test_hsl_rgb_hsl_roundtrip(self):
        """Test HSL to RGB to HSL round-trip conversion."""
        test_hsl = (180.0, 75.0, 50.0)
        rgb = hsl_to_rgb(*test_hsl)
        result_hsl = rgb_to_hsl(rgb)
        # Due to rounding, check approximate equality
        assert result_hsl[0] == pytest.approx(test_hsl[0], abs=0.1)
        assert result_hsl[1] == pytest.approx(test_hsl[1], abs=0.1)
        assert result_hsl[2] == pytest.approx(test_hsl[2], abs=0.1)
