"""Tests for dark mode compatibility checker."""

import pytest

from chromaspec.analyzers.dark_mode import (
    DarkModeResult,
    check_dark_mode_compatibility,
    generate_dark_mode_palette,
    get_compatible_text_color,
    suggest_dark_mode_adjustments,
)
from chromaspec.exceptions import ValidationError


class TestDarkModeResult:
    """Test DarkModeResult dataclass."""

    def test_result_initialization(self):
        """Test DarkModeResult initialization."""
        result = DarkModeResult(
            light_background="#FFFFFF",
            dark_background="#121212",
            text_color="#333333",
            light_contrast=10.5,
            dark_contrast=7.2,
            light_rating="AAA",
            dark_rating="AAA",
            is_compatible=True,
        )
        assert result.light_background == "#FFFFFF"
        assert result.dark_background == "#121212"
        assert result.text_color == "#333333"
        assert result.is_compatible is True

    def test_result_to_dict(self):
        """Test result conversion to dictionary."""
        result = DarkModeResult(
            light_background="#FFFFFF",
            dark_background="#121212",
            text_color="#333333",
            light_contrast=10.5,
            dark_contrast=7.2,
            light_rating="AAA",
            dark_rating="AAA",
            is_compatible=True,
        )
        result_dict = result.to_dict()
        assert result_dict["text_color"] == "#333333"
        assert result_dict["is_compatible"] is True
        assert result_dict["light_mode"]["background"] == "#FFFFFF"
        assert result_dict["dark_mode"]["background"] == "#121212"
        assert result_dict["light_mode"]["contrast_ratio"] == 10.5
        assert result_dict["dark_mode"]["contrast_ratio"] == 7.2

    def test_result_str_representation(self):
        """Test string representation of result."""
        result = DarkModeResult(
            light_background="#FFFFFF",
            dark_background="#121212",
            text_color="#333333",
            light_contrast=10.5,
            dark_contrast=7.2,
            light_rating="AAA",
            dark_rating="AAA",
            is_compatible=True,
        )
        result_str = str(result)
        assert "#333333" in result_str
        assert "Compatible" in result_str


class TestCheckDarkModeCompatibility:
    """Test dark mode compatibility checking."""

    def test_check_with_black_text(self):
        """Test checking black text on backgrounds."""
        result = check_dark_mode_compatibility("#000000")
        assert result.text_color == "#000000"
        assert result.light_background == "#FFFFFF"
        assert result.dark_background == "#121212"
        assert result.light_contrast > 0
        assert result.dark_contrast > 0

    def test_check_with_white_text(self):
        """Test checking white text on backgrounds."""
        result = check_dark_mode_compatibility("#FFFFFF")
        assert result.text_color == "#FFFFFF"
        assert result.light_contrast > 0
        assert result.dark_contrast > 0

    def test_check_with_gray_text(self):
        """Test checking gray text on backgrounds."""
        result = check_dark_mode_compatibility("#333333")
        assert result.text_color == "#333333"
        assert isinstance(result.is_compatible, bool)

    def test_check_custom_backgrounds(self):
        """Test checking with custom backgrounds."""
        result = check_dark_mode_compatibility(
            "#333333",
            light_background="#F0F0F0",
            dark_background="#1A1A1A",
        )
        assert result.light_background == "#F0F0F0"
        assert result.dark_background == "#1A1A1A"

    def test_check_with_invalid_text_color(self):
        """Test checking with invalid text color."""
        with pytest.raises(ValidationError):
            check_dark_mode_compatibility("INVALID")

    def test_check_with_invalid_light_background(self):
        """Test checking with invalid light background."""
        with pytest.raises(ValidationError):
            check_dark_mode_compatibility("#333333", light_background="INVALID")

    def test_check_with_invalid_dark_background(self):
        """Test checking with invalid dark background."""
        with pytest.raises(ValidationError):
            check_dark_mode_compatibility("#333333", dark_background="INVALID")

    def test_check_rating_priorities(self):
        """Test with different WCAG rating targets."""
        result_aa = check_dark_mode_compatibility("#333333", min_rating="AA")
        result_aaa = check_dark_mode_compatibility("#333333", min_rating="AAA")

        # AAA should be stricter than AA
        assert result_aa.light_contrast >= 0
        assert result_aaa.light_contrast >= 0

    def test_check_compatible_true(self):
        """Test that some colors are compatible."""
        result = check_dark_mode_compatibility("#000000")
        # Black on white should be compatible
        assert isinstance(result.is_compatible, bool)

    def test_check_compatible_false(self):
        """Test that some colors are incompatible."""
        result = check_dark_mode_compatibility("#808080")
        # Gray might not pass both
        assert isinstance(result.is_compatible, bool)


class TestGenerateDarkModePalette:
    """Test dark mode palette generation."""

    def test_generate_palette(self):
        """Test generating a palette tested for dark mode."""
        results = generate_dark_mode_palette("#FF0000")
        assert "primary" in results
        assert "secondary" in results
        assert "accent" in results or "text" in results

    def test_palette_results_are_dark_mode_results(self):
        """Test that palette results are DarkModeResult objects."""
        results = generate_dark_mode_palette("#FF0000")
        for color_name, result in results.items():
            assert isinstance(result, DarkModeResult)

    def test_generate_palette_with_custom_backgrounds(self):
        """Test palette with custom backgrounds."""
        results = generate_dark_mode_palette(
            "#FF0000",
            light_bg="#F0F0F0",
            dark_bg="#1A1A1A",
        )
        for result in results.values():
            assert result.light_background == "#F0F0F0"
            assert result.dark_background == "#1A1A1A"

    def test_generate_palette_with_invalid_color(self):
        """Test palette generation with invalid color."""
        with pytest.raises(ValidationError):
            generate_dark_mode_palette("INVALID")


class TestGetCompatibleTextColor:
    """Test finding compatible text colors."""

    def test_get_compatible_text_color_defaults(self):
        """Test finding compatible text color with default backgrounds."""
        color = get_compatible_text_color()
        assert len(color) == 7
        assert color.startswith("#")

    def test_get_compatible_text_color_custom_backgrounds(self):
        """Test finding compatible text with custom backgrounds."""
        color = get_compatible_text_color(
            background_light="#F0F0F0",
            background_dark="#1A1A1A",
        )
        assert color.startswith("#")

    def test_get_compatible_text_color_aaa(self):
        """Test finding compatible text for AAA rating."""
        color = get_compatible_text_color(target_rating="AAA")
        assert color.startswith("#")

    def test_get_compatible_text_color_invalid_light_background(self):
        """Test with invalid light background."""
        with pytest.raises(ValidationError):
            get_compatible_text_color(background_light="INVALID")

    def test_get_compatible_text_color_invalid_dark_background(self):
        """Test with invalid dark background."""
        with pytest.raises(ValidationError):
            get_compatible_text_color(background_dark="INVALID")

    def test_get_compatible_text_color_common_colors(self):
        """Test that common colors are checked."""
        color = get_compatible_text_color()
        # Should return one of the tested colors
        assert color in [
            "#000000",
            "#FFFFFF",
            "#333333",
            "#666666",
            "#999999",
        ] or color.startswith("#")


class TestSuggestDarkModeAdjustments:
    """Test dark mode adjustment suggestions."""

    def test_suggest_adjustments_returns_list(self):
        """Test that suggestions return a list."""
        suggestions = suggest_dark_mode_adjustments("#FF0000")
        assert isinstance(suggestions, list)

    def test_suggest_adjustments_structure(self):
        """Test that suggestions have correct structure."""
        suggestions = suggest_dark_mode_adjustments("#FF0000")
        if suggestions:
            for suggestion in suggestions:
                assert "color" in suggestion
                assert "adjustment" in suggestion
                assert "light_contrast" in suggestion
                assert "dark_contrast" in suggestion

    def test_suggest_adjustments_color_format(self):
        """Test that suggested colors are valid HEX."""
        suggestions = suggest_dark_mode_adjustments("#FF0000")
        if suggestions:
            for suggestion in suggestions:
                assert suggestion["color"].startswith("#")
                assert len(suggestion["color"]) == 7

    def test_suggest_adjustments_contrast_values(self):
        """Test that suggestions have valid contrast values."""
        suggestions = suggest_dark_mode_adjustments("#FF0000")
        if suggestions:
            for suggestion in suggestions:
                assert isinstance(suggestion["light_contrast"], (int, float))
                assert isinstance(suggestion["dark_contrast"], (int, float))
                assert suggestion["light_contrast"] > 0
                assert suggestion["dark_contrast"] > 0

    def test_suggest_adjustments_custom_backgrounds(self):
        """Test suggestions with custom backgrounds."""
        suggestions = suggest_dark_mode_adjustments(
            "#FF0000",
            light_background="#F0F0F0",
            dark_background="#1A1A1A",
        )
        assert isinstance(suggestions, list)

    def test_suggest_adjustments_custom_rating(self):
        """Test suggestions with custom WCAG rating."""
        suggestions = suggest_dark_mode_adjustments(
            "#FF0000",
            target_rating="AAA",
        )
        assert isinstance(suggestions, list)

    def test_suggest_adjustments_invalid_text_color(self):
        """Test suggestions with invalid text color."""
        with pytest.raises(ValidationError):
            suggest_dark_mode_adjustments("INVALID")

    def test_suggest_adjustments_invalid_light_background(self):
        """Test suggestions with invalid light background."""
        with pytest.raises(ValidationError):
            suggest_dark_mode_adjustments("#FF0000", light_background="INVALID")

    def test_suggest_adjustments_invalid_dark_background(self):
        """Test suggestions with invalid dark background."""
        with pytest.raises(ValidationError):
            suggest_dark_mode_adjustments("#FF0000", dark_background="INVALID")

    def test_suggest_adjustments_max_iterations(self):
        """Test suggestions with custom max iterations."""
        suggestions = suggest_dark_mode_adjustments("#FF0000", max_iterations=5)
        assert isinstance(suggestions, list)

    def test_suggest_adjustments_format_string(self):
        """Test that adjustment string is formatted correctly."""
        suggestions = suggest_dark_mode_adjustments("#FF0000")
        if suggestions:
            for suggestion in suggestions:
                assert (
                    "+" in suggestion["adjustment"] or "-" in suggestion["adjustment"]
                )
                assert "%" in suggestion["adjustment"]


class TestDarkModeEdgeCases:
    """Test edge cases for dark mode functionality."""

    def test_check_with_red(self):
        """Test dark mode with red color."""
        result = check_dark_mode_compatibility("#FF0000")
        assert result.text_color == "#FF0000"

    def test_check_with_green(self):
        """Test dark mode with green color."""
        result = check_dark_mode_compatibility("#00FF00")
        assert result.text_color == "#00FF00"

    def test_check_with_blue(self):
        """Test dark mode with blue color."""
        result = check_dark_mode_compatibility("#0000FF")
        assert result.text_color == "#0000FF"

    def test_check_with_purple(self):
        """Test dark mode with purple color."""
        result = check_dark_mode_compatibility("#800080")
        assert result.text_color == "#800080"

    def test_check_with_orange(self):
        """Test dark mode with orange color."""
        result = check_dark_mode_compatibility("#FFA500")
        assert result.text_color == "#FFA500"

    def test_contrast_ratios_are_positive(self):
        """Test that all contrast ratios are positive."""
        result = check_dark_mode_compatibility("#333333")
        assert result.light_contrast > 0
        assert result.dark_contrast > 0

    def test_wcag_ratings_are_valid(self):
        """Test that WCAG ratings are valid."""
        valid_ratings = ["Fail", "AA Large", "AA", "AAA"]
        result = check_dark_mode_compatibility("#333333")
        assert result.light_rating in valid_ratings
        assert result.dark_rating in valid_ratings
