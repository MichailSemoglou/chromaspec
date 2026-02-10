"""
Input validation utilities for ChromaSpec.

This module provides validation functions for file paths, file formats,
and other input data to ensure security and prevent injection attacks.
"""

import logging
from pathlib import Path
from typing import Optional

from chromaspec.exceptions import ValidationError
from chromaspec.utils.constants import SUPPORTED_EXTENSIONS, ImageProcessing

logger = logging.getLogger(__name__)


def validate_file_exists(file_path: Path) -> None:
    """
    Validate that a file exists and is accessible.

    Args:
        file_path: Path to the file to validate.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        ValidationError: If the file is not a regular file.
    """
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        raise FileNotFoundError(f"Input file not found: {file_path}")

    if not file_path.is_file():
        logger.error(f"Path is not a file: {file_path}")
        raise ValidationError(f"Path is not a regular file: {file_path}")

    logger.debug(f"File validation passed: {file_path}")


def validate_file_format(file_path: Path) -> None:
    """
    Validate that the file has a supported format.

    Args:
        file_path: Path to the file to validate.

    Raises:
        ValidationError: If the file format is not supported.
    """
    extension = file_path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        logger.error(f"Unsupported file format: {extension}")
        raise ValidationError(
            f"Unsupported file format: {extension}. "
            f"Supported formats: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    logger.debug(f"File format validation passed: {extension}")


def validate_svg_size(
    svg_content: str, max_size: int = ImageProcessing.MAX_SVG_SIZE
) -> None:
    """
    Validate that SVG content is within size limits.

    Args:
        svg_content: The SVG file content as a string.
        max_size: Maximum allowed size in bytes.

    Raises:
        ValidationError: If the SVG content is too large.
    """
    content_size = len(svg_content.encode("utf-8"))

    if content_size > max_size:
        logger.error(f"SVG file too large: {content_size} bytes")
        raise ValidationError(
            f"SVG file too large ({content_size:,} bytes). "
            f"Maximum allowed: {max_size:,} bytes."
        )

    logger.debug(f"SVG size validation passed: {content_size:,} bytes")


def validate_color_matches(
    color_count: int, max_matches: int = ImageProcessing.MAX_COLOR_MATCHES
) -> None:
    """
    Validate that the number of color matches is reasonable.

    Args:
        color_count: Number of colors found.
        max_matches: Maximum allowed color matches.

    Raises:
        ValidationError: If too many color matches found (possible ReDoS).
    """
    if color_count > max_matches:
        logger.error(f"Too many color matches: {color_count}")
        raise ValidationError(
            f"Too many color matches detected ({color_count}). "
            f"This may indicate a malformed SVG file. Maximum allowed: {max_matches}."
        )

    logger.debug(f"Color matches validation passed: {color_count}")


def validate_output_path(output_path: Path, base_dir: Optional[Path] = None) -> Path:
    """
    Validate that the output path is safe and within allowed directory.

    Args:
        output_path: Path to validate.
        base_dir: Base directory that output must be within. If None, uses current directory.

    Returns:
        The validated, resolved path.

    Raises:
        ValidationError: If the output path is outside allowed directory.
    """
    if base_dir is None:
        base_dir = Path.cwd()

    try:
        resolved = output_path.resolve().absolute()
        base = base_dir.resolve().absolute()
        resolved.relative_to(base)  # Raises ValueError if outside base

        # Check if parent directory exists or can be created
        parent_dir = resolved.parent
        if parent_dir != Path.cwd() and not parent_dir.exists():
            parent_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created output directory: {parent_dir}")

        logger.debug(f"Output path validation passed: {resolved}")
        return resolved

    except ValueError:
        logger.error(f"Invalid output path (outside allowed directory): {output_path}")
        raise ValidationError(
            f"Invalid output path: {output_path}. "
            f"Output must be within the current working directory or its subdirectories."
        )


def validate_hex_color(hex_color: str) -> None:
    """
    Validate that a string is a valid HEX color.

    Args:
        hex_color: String to validate.

    Raises:
        ValidationError: If HEX color is invalid.
    """
    import re

    pattern = re.compile(r"^#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?$")

    if not isinstance(hex_color, str):
        logger.error(f"HEX color must be string: {type(hex_color)}")
        raise ValidationError("HEX color must be a string")

    if not pattern.match(hex_color):
        logger.error(f"Invalid HEX color format: {hex_color}")
        raise ValidationError(
            f"Invalid HEX color: '{hex_color}'. " "Expected format: #RGB or #RRGGBB"
        )

    logger.debug(f"HEX color validation passed: {hex_color}")


def validate_rgb_tuple(rgb: tuple) -> None:
    """
    Validate that a tuple is a valid RGB color.

    Args:
        rgb: Tuple to validate.

    Raises:
        ValidationError: If RGB tuple is invalid.
    """
    if not isinstance(rgb, tuple):
        logger.error(f"RGB must be tuple: {type(rgb)}")
        raise ValidationError("RGB value must be a tuple")

    if len(rgb) != 3:
        logger.error(f"RGB tuple must have 3 elements: {len(rgb)}")
        raise ValidationError("RGB tuple must have exactly 3 elements")

    for i, value in enumerate(rgb):
        if not isinstance(value, int):
            logger.error(f"RGB value must be int: {type(value)}")
            raise ValidationError("RGB value must be an integer")

        if not (0 <= value <= 255):
            logger.error(f"RGB value out of range: {value}")
            raise ValidationError(f"RGB value must be between 0 and 255. Got: {value}")

    logger.debug(f"RGB tuple validation passed: {rgb}")
