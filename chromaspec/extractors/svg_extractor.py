"""
SVG color extraction functions.

This module provides functions for extracting colors from SVG files
with protection against XXE (XML External Entity) attacks.
"""

import logging
import re
from collections import Counter
from pathlib import Path
from typing import Dict

try:
    import defusedxml.ElementTree as ET

    DEFUSEDXML_AVAILABLE = True
except ImportError:
    import xml.etree.ElementTree as ET  # nosec B405

    DEFUSEDXML_AVAILABLE = False

from chromaspec.exceptions import ValidationError
from chromaspec.utils.constants import ColorConstants, ImageProcessing
from chromaspec.utils.validators import validate_color_matches, validate_svg_size

logger = logging.getLogger(__name__)

if not DEFUSEDXML_AVAILABLE:
    logger.warning(
        "defusedxml not available. SVG parsing may be vulnerable to XXE attacks. "
        "Install with: pip install defusedxml"
    )

HEX_COLOR_PATTERN = re.compile(ColorConstants.HEX_PATTERN)
COLOR_ATTRIBUTES = ["fill", "stroke", "stop-color", "color"]


def extract_hex_colors_from_svg(svg_content: str) -> Dict[str, float]:
    """
    Extract all HEX color values from SVG content with their frequencies.

    Args:
        svg_content: The SVG file content as a string.

    Returns:
        A dictionary mapping HEX color strings to their frequency percentages.

    Raises:
        ValidationError: If SVG size or color match count exceeds limits.
    """
    # Validate SVG size to prevent DoS attacks
    validate_svg_size(svg_content)

    colors = HEX_COLOR_PATTERN.findall(svg_content)

    # Validate color match count to prevent ReDoS
    validate_color_matches(len(colors))

    if not colors:
        logger.warning("No colors found in SVG content")
        return {}

    total = len(colors)
    color_counts = Counter(colors)

    result = {color: (count / total) * 100 for color, count in color_counts.items()}

    logger.info(
        f"Extracted {len(result)} unique colors from SVG ({total} total occurrences)"
    )
    return result


def extract_colors_from_svg_safe(
    svg_path: Path, max_colors: int = None
) -> Dict[str, float]:
    """
    Extract colors from SVG file with XXE protection.

    This function uses XML parsing with defusedxml to prevent XXE attacks,
    while also extracting colors from fill/stroke attributes.

    Args:
        svg_path: Path to SVG file.
        max_colors: Maximum number of colors to extract.

    Returns:
        Dictionary mapping HEX colors to frequencies.

    Raises:
        ValidationError: If SVG contains malicious content or is invalid.
    """
    if max_colors is None:
        max_colors = ImageProcessing.MAX_COLORS

    # Validate file size first
    svg_content = svg_path.read_text(encoding="utf-8")
    validate_svg_size(svg_content)

    try:
        # Parse with defusedxml if available (prevents XXE attacks)
        if DEFUSEDXML_AVAILABLE:
            # defusedxml automatically forbids DTDs and entities
            tree = ET.parse(str(svg_path))  # nosec B314
        else:
            # Fallback to standard parser (less secure)
            tree = ET.parse(str(svg_path))  # nosec B314

        root = tree.getroot()

        # Extract colors from attributes
        colors = Counter()

        # Iterate through all elements
        for elem in root.iter():
            for attr in COLOR_ATTRIBUTES:
                if attr in elem.attrib:
                    color_value = elem.attrib[attr]
                    if color_value and color_value.lower() != "none":
                        # Extract HEX colors
                        hex_colors = HEX_COLOR_PATTERN.findall(color_value)
                        for hex_color in hex_colors:
                            colors[hex_color] += 1

        # Validate color match count
        validate_color_matches(sum(colors.values()))

        if not colors:
            # Fallback to regex extraction if no colors found via XML
            logger.debug("No colors found via XML parsing, falling back to regex")
            return extract_hex_colors_from_svg(svg_content)

        # Calculate frequencies
        total = sum(colors.values())
        color_freq = {
            color: (count / total) * 100
            for color, count in colors.most_common(max_colors)
        }

        logger.info(
            f"Extracted {len(color_freq)} unique colors from SVG via XML parsing "
            f"({total} total occurrences)"
        )
        return color_freq

    except ET.ParseError as e:
        logger.error(f"XML parsing failed for {svg_path}: {e}")
        raise ValidationError(
            f"Invalid or malicious SVG file. XML parsing failed: {e}"
        ) from e
    except Exception as e:
        logger.error(f"Failed to extract colors from {svg_path}: {e}")
        # Fallback to regex method for non-XML errors
        logger.debug("Falling back to regex extraction")
        return extract_hex_colors_from_svg(svg_content)
