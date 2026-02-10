"""
Image color extraction functions.

This module provides functions for extracting colors from image files
with optimized memory usage.
"""

import logging
from collections import Counter
from pathlib import Path
from typing import Dict, Optional

try:
    from PIL import Image

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from chromaspec.exceptions import ImageProcessingError
from chromaspec.utils.constants import ImageProcessing

logger = logging.getLogger(__name__)


def extract_colors_from_image(
    image_path: Path, max_colors: Optional[int] = None
) -> Dict[str, float]:
    """
    Extract dominant colors from an image file with their frequencies.

    This function uses optimized processing that doesn't load the entire
    image into memory at once. It resizes large images first to improve
    performance.

    Args:
        image_path: Path to the image file.
        max_colors: Maximum number of colors to extract. Defaults to ImageProcessing.MAX_COLORS.

    Returns:
        A dictionary mapping HEX color strings to their frequency percentages.

    Raises:
        ImportError: If Pillow is not installed.
        ImageProcessingError: If image processing fails.
    """
    if not PIL_AVAILABLE:
        raise ImportError(
            "Pillow is required for image processing. "
            "Install it with: pip install Pillow"
        )

    if max_colors is None:
        max_colors = ImageProcessing.MAX_COLORS

    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode != "RGB":
                img = img.convert("RGB")

            # Resize large images for performance (this is the key optimization)
            max_dimension = ImageProcessing.MAX_DIMENSION
            if max(img.size) > max_dimension:
                img.thumbnail((max_dimension, max_dimension))
                logger.debug(f"Resized image to: {img.size}")

            # Use getdata() directly with Counter - more memory efficient than list()
            # Counter can iterate over the getdata() iterator without creating a list
            color_counts = Counter(img.getdata())
            total_pixels = sum(color_counts.values())

            if total_pixels == 0:
                logger.warning("No pixels found in image")
                return {}

            # Get most common colors up to max_colors
            common_colors = color_counts.most_common(max_colors)

            hex_colors_with_freq = {
                f"#{r:02X}{g:02X}{b:02X}": (count / total_pixels) * 100
                for (r, g, b), count in common_colors
            }

            logger.info(
                f"Extracted {len(hex_colors_with_freq)} colors from image "
                f"({total_pixels:,} total pixels, resized to {img.size})"
            )
            return hex_colors_with_freq

    except Exception as e:
        logger.error(f"Failed to process image {image_path}: {e}")
        raise ImageProcessingError(f"Failed to process image: {e}") from e
