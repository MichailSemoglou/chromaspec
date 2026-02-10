"""
Color extraction modules for ChromaSpec.

This package provides functions for extracting colors from SVG and image files
with security validations and XXE protection.
"""

import logging
from pathlib import Path
from typing import Dict

from chromaspec.exceptions import UnsupportedFormatError
from chromaspec.extractors.image_extractor import extract_colors_from_image
from chromaspec.extractors.svg_extractor import (
    extract_colors_from_svg_safe,
    extract_hex_colors_from_svg,
)
from chromaspec.utils.constants import (
    IMAGE_EXTENSIONS,
    SUPPORTED_EXTENSIONS,
    SVG_EXTENSIONS,
)
from chromaspec.utils.security import timeout, validate_file_size
from chromaspec.utils.validators import validate_file_exists, validate_file_format

logger = logging.getLogger(__name__)


def extract_colors(input_path: Path) -> Dict[str, float]:
    """
    Extract colors from an input file (SVG or image) with frequencies.

    This function automatically detects the file type and uses the appropriate
    extraction method with security protections including:
    - File size validation
    - XXE attack prevention for SVG files
    - Timeout protection (30 seconds max)

    Args:
        input_path: Path to the input file.

    Returns:
        A dictionary mapping HEX color strings to their frequency percentages.

    Raises:
        FileNotFoundError: If the input file doesn't exist.
        UnsupportedFormatError: If the file format is not supported.
        ValidationError: If file format validation fails or security checks fail.
        ImageProcessingError: If image processing fails.
        ImportError: If processing an image without Pillow installed.
        TimeoutError: If processing exceeds 30 seconds.
    """
    # Validate file exists and format is supported
    validate_file_exists(input_path)
    validate_file_format(input_path)

    # Validate file size (max 50MB for safety)
    validate_file_size(input_path, max_size_mb=50)

    extension = input_path.suffix.lower()

    try:
        # Apply timeout protection (30 seconds max)
        with timeout(30):
            if extension in SVG_EXTENSIONS:
                # Use safe XML parsing with XXE protection
                logger.info(f"Extracting colors from SVG: {input_path}")
                return extract_colors_from_svg_safe(input_path)
            elif extension in IMAGE_EXTENSIONS:
                logger.info(f"Extracting colors from image: {input_path}")
                return extract_colors_from_image(input_path)
            else:
                # This should not happen due to validation, but kept as a safeguard
                raise UnsupportedFormatError(
                    f"File format '{extension}' is not supported. "
                    f"Supported formats: {', '.join(SUPPORTED_EXTENSIONS)}"
                )
    except TimeoutError:
        logger.error(f"Timeout while processing {input_path}")
        raise TimeoutError(
            f"Processing {input_path.name} took too long (>30 seconds). "
            f"The file may be too large or complex."
        )


__all__ = [
    "extract_colors",
    "extract_hex_colors_from_svg",
    "extract_colors_from_image",
]
