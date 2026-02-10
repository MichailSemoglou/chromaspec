"""
Tests for color analysis functions.
"""

import pytest

from chromaspec.analyzers import (
    categorize_colors,
    get_analogous_colors,
    get_complementary_color,
    get_contrast_ratio,
    get_wcag_rating,
    is_blue_color,
    is_dominant_color,
    is_green_color,
    is_red_color,
)
from chromaspec.exceptions import ValidationError


class TestColorClassification:
    """Tests for color classification functions."""

    def test_is_red_color_true(self):
        """Test that red colors are identified correctly."""
        assert is_red_color((255, 0, 0))
        assert is_red_color((255, 50, 50))
        assert is_red_color((200, 100, 90))

    def test_is_red_color_false(self):
        """Test that non-red colors are not identified as red."""
        assert not is_red_color((0, 255, 0))
        assert not is_red_color((0, 0, 255))
        assert not is_red_color((100, 100, 100))

    def test_is_green_color_true(self):
        """Test that green colors are identified correctly."""
        assert is_green_color((0, 255, 0))
        assert is_green_color((50, 255, 50))
        assert is_green_color((90, 200, 100))

    def test_is_green_color_false(self):
        """Test that non-green colors are not identified as green."""
        assert not is_green_color((255, 0, 0))
        assert not is_green_color((0, 0, 255))
        assert not is_green_color((100, 100, 100))

    def test_is_blue_color_true(self):
        """Test that blue colors are identified correctly."""
        assert is_blue_color((0, 0, 255))
        assert is_blue_color((50, 50, 255))
        assert is_blue_color((90, 100, 200))

    def test_is_blue_color_false(self):
        """Test that non-blue colors are not identified as blue."""
        assert not is_blue_color((255, 0, 0))
        assert not is_blue_color((0, 255, 0))
        assert not is_blue_color((100, 100, 100))

    def test_is_dominant_color_valid(self):
        """Test dominant color detection with valid inputs."""
        assert is_dominant_color((255, 0, 0), "red")
        assert is_dominant_color((0, 255, 0), "green")
        assert is_dominant_color((0, 0, 255), "blue")

    def test_is_dominant_color_invalid_component(self):
        """Test that invalid component raises ValueError."""
        with pytest.raises(ValueError, match="Invalid component"):
            is_dominant_color((255, 0, 0), "yellow")


class TestCategorizeColors:
    """Tests for categorize_colors function."""

    def test_categorize_colors_basic(self):
        """Test basic color categorization."""
        colors = {
            "#FF0000": 50.0,
            "#00FF00": 30.0,
            "#0000FF": 20.0,
        }
        result = categorize_colors(colors)

        assert len(result["red"]) == 1
        assert len(result["green"]) == 1
        assert len(result["blue"]) == 1
        assert result["red"][0][0] == "#FF0000"
        assert result["green"][0][0] == "#00FF00"
        assert result["blue"][0][0] == "#0000FF"

    def test_categorize_colors_sorting(self):
        """Test that colors are sorted by frequency."""
        colors = {
            "#FF0000": 10.0,
            "#AA0000": 30.0,
            "#00FF00": 20.0,
        }
        result = categorize_colors(colors)

        # Red colors should be sorted by frequency descending
        assert result["red"][0][1] > result["red"][1][1]

    def test_categorize_colors_empty(self):
        """Test categorization with empty input."""
        result = categorize_colors({})
        assert len(result["red"]) == 0
        assert len(result["green"]) == 0
        assert len(result["blue"]) == 0


class TestColorHarmonies:
    """Tests for color harmony functions."""

    def test_get_complementary_color(self):
        """Test complementary color calculation."""
        # Red's complementary is cyan
        comp = get_complementary_color("#FF0000")
        assert comp == "#00FFFF"

        # Black's complementary is white
        comp = get_complementary_color("#000000")
        assert comp == "#FFFFFF"

    def test_get_analogous_colors(self):
        """Test analogous color calculation."""
        analog1, analog2 = get_analogous_colors("#FF0000")

        # Both should be valid HEX colors
        assert len(analog1) == 7
        assert len(analog2) == 7
        assert analog1.startswith("#")
        assert analog2.startswith("#")

        # Analogous colors should be different from original
        assert analog1 != "#FF0000"
        assert analog2 != "#FF0000"


class TestAccessibility:
    """Tests for accessibility and contrast functions."""

    def test_get_contrast_ratio_black_white(self):
        """Test contrast ratio between black and white."""
        ratio = get_contrast_ratio("#000000", "#FFFFFF")
        assert ratio == pytest.approx(21.0, rel=0.01)

    def test_get_contrast_ratio_same_color(self):
        """Test contrast ratio of same color."""
        ratio = get_contrast_ratio("#FF0000", "#FF0000")
        assert ratio == pytest.approx(1.0, rel=0.01)

    def test_get_wcag_rating_aaa(self):
        """Test AAA rating."""
        assert get_wcag_rating(7.0) == "AAA"
        assert get_wcag_rating(21.0) == "AAA"

    def test_get_wcag_rating_aa(self):
        """Test AA rating."""
        assert get_wcag_rating(4.5) == "AA"
        assert get_wcag_rating(5.0) == "AA"

    def test_get_wcag_rating_aa_large(self):
        """Test AA Large rating."""
        assert get_wcag_rating(3.0) == "AA Large"
        assert get_wcag_rating(4.0) == "AA Large"

    def test_get_wcag_rating_fail(self):
        """Test Fail rating."""
        assert get_wcag_rating(1.0) == "Fail"
        assert get_wcag_rating(2.9) == "Fail"

    def test_get_wcag_rating_with_hex_colors(self):
        """Test WCAG rating calculation from HEX colors."""
        # Get contrast ratio first, then rate it
        ratio_aaa = get_contrast_ratio("#000000", "#FFFFFF")
        result_aaa = get_wcag_rating(ratio_aaa)
        assert result_aaa == "AAA"

        ratio_aa = get_contrast_ratio("#777777", "#FFFFFF")
        result_aa = get_wcag_rating(ratio_aa)
        assert result_aa == "AA Large"  # #777777 on white gives ~5.5 contrast

        ratio_fail = get_contrast_ratio("#FF0000", "#FF0000")
        result_fail = get_wcag_rating(ratio_fail)
        assert result_fail == "Fail"

    @pytest.mark.parametrize(
        "text_color,background_color,expected_range",
        [
            ("#000000", "#FFFFFF", (21.0, 21.1)),  # Max contrast
            ("#FFFFFF", "#000000", (21.0, 21.1)),  # Reversed
            ("#FF0000", "#FFFFFF", (3.9, 4.0)),  # Red on white
            ("#0000FF", "#FFFFFF", (8.5, 8.6)),  # Blue on white
            ("#808080", "#FFFFFF", (3.9, 4.0)),  # Gray on white
        ],
    )
    def test_contrast_ratio_various_colors(
        self, text_color, background_color, expected_range
    ):
        """Test contrast ratio calculation for various color combinations."""
        ratio = get_contrast_ratio(text_color, background_color)
        assert expected_range[0] <= ratio <= expected_range[1]

    def test_get_contrast_ratio_edge_cases(self):
        """Test contrast ratio with edge case colors."""
        # Same color should have ratio of 1
        assert get_contrast_ratio("#FF0000", "#FF0000") == pytest.approx(1.0, rel=0.01)

        # Black on white should be maximum (~21)
        assert get_contrast_ratio("#000000", "#FFFFFF") > 20.0

        # White on black should also be maximum
        assert get_contrast_ratio("#FFFFFF", "#000000") > 20.0
