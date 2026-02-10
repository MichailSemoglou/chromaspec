"""
Tests for color extraction functions.
"""

import pytest

from chromaspec.extractors import extract_hex_colors_from_svg


class TestExtractHexColorsFromSvg:
    """Tests for extract_hex_colors_from_svg function."""

    def test_extract_basic_colors(self):
        """Test extracting basic HEX colors from SVG."""
        svg = """
        <svg>
            <rect fill="#FF0000"/>
            <circle fill="#00FF00"/>
            <line stroke="#0000FF"/>
        </svg>
        """
        colors = extract_hex_colors_from_svg(svg)
        assert "#FF0000" in colors
        assert "#00FF00" in colors
        assert "#0000FF" in colors

    def test_extract_colors_with_hashtag_only(self):
        """Test extracting colors that use standard HEX format."""
        svg = """
        <svg>
            <rect fill="#FF0000"/>
            <circle fill="#00FF00"/>
        </svg>
        """
        colors = extract_hex_colors_from_svg(svg)
        assert "#FF0000" in colors
        assert "#00FF00" in colors

    def test_extract_case_preserved(self):
        """Test that HEX color case is preserved as-is."""
        svg = """
        <svg>
            <rect fill="#ff0000"/>
            <circle fill="#ABCDEF"/>
        </svg>
        """
        colors = extract_hex_colors_from_svg(svg)
        assert "#ff0000" in colors  # lowercase preserved
        assert "#ABCDEF" in colors  # uppercase preserved

    def test_extract_no_colors(self):
        """Test SVG with no colors returns empty dict."""
        svg = "<svg><rect/></svg>"
        colors = extract_hex_colors_from_svg(svg)
        assert colors == {}

    def test_extract_short_hex_format(self):
        """Test extracting short HEX format (#RGB)."""
        svg = """
        <svg>
            <rect fill="#F00"/>
            <circle fill="#0F0"/>
        </svg>
        """
        colors = extract_hex_colors_from_svg(svg)
        assert "#F00" in colors
        assert "#0F0" in colors

    def test_extract_colors_from_style(self):
        """Test extracting colors from style attributes."""
        svg = """
        <svg>
            <rect style="fill: #FF0000;"/>
            <circle style="stroke: #00FF00;"/>
        </svg>
        """
        colors = extract_hex_colors_from_svg(svg)
        assert "#FF0000" in colors
        assert "#00FF00" in colors

    def test_count_color_occurrences(self):
        """Test that color occurrences are counted."""
        svg = """
        <svg>
            <rect fill="#FF0000"/>
            <circle fill="#FF0000"/>
            <line fill="#00FF00"/>
        </svg>
        """
        colors = extract_hex_colors_from_svg(svg)
        assert colors["#FF0000"] > colors["#00FF00"]

    def test_calculate_frequency_percentages(self):
        """Test that frequencies are calculated as percentages."""
        svg = """
        <svg>
            <rect fill="#FF0000"/>
            <circle fill="#FF0000"/>
            <line fill="#00FF00"/>
        </svg>
        """
        colors = extract_hex_colors_from_svg(svg)
        total = sum(colors.values())
        assert total == pytest.approx(100.0, rel=0.1)
