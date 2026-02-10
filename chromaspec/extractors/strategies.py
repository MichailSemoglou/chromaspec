"""
Strategy pattern for color extraction.

This module defines an abstract base class for color extraction strategies,
making it easier to add new file formats or extraction methods.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional


class ColorExtractionStrategy(ABC):
    """Abstract base class for color extraction strategies."""

    @abstractmethod
    def can_handle(self, file_path: Path) -> bool:
        """
        Determine if this strategy can handle the given file.

        Args:
            file_path: Path to the file to check.

        Returns:
            True if this strategy can handle the file, False otherwise.
        """
        pass

    @abstractmethod
    def extract(
        self, file_path: Path, max_colors: Optional[int] = None
    ) -> Dict[str, float]:
        """
        Extract colors from the file.

        Args:
            file_path: Path to the file.
            max_colors: Maximum number of colors to extract.

        Returns:
            Dictionary mapping HEX color strings to frequencies.
        """
        pass


class ImageExtractionStrategy(ColorExtractionStrategy):
    """Strategy for extracting colors from image files."""

    def can_handle(self, file_path: Path) -> bool:
        """Check if file is an image."""
        from chromaspec.utils.constants import IMAGE_EXTENSIONS

        return file_path.suffix.lower() in IMAGE_EXTENSIONS

    def extract(
        self, file_path: Path, max_colors: Optional[int] = None
    ) -> Dict[str, float]:
        """Extract colors from image."""
        from chromaspec.extractors.image_extractor import extract_colors_from_image

        return extract_colors_from_image(file_path, max_colors)


class SVGExtractionStrategy(ColorExtractionStrategy):
    """Strategy for extracting colors from SVG files."""

    def can_handle(self, file_path: Path) -> bool:
        """Check if file is SVG."""
        from chromaspec.utils.constants import SVG_EXTENSIONS

        return file_path.suffix.lower() in SVG_EXTENSIONS

    def extract(
        self, file_path: Path, max_colors: Optional[int] = None
    ) -> Dict[str, float]:
        """Extract colors from SVG."""
        from chromaspec.extractors.svg_extractor import extract_colors_from_svg_safe

        return extract_colors_from_svg_safe(file_path, max_colors)


class ColorExtractor:
    """Context class that uses extraction strategies."""

    def __init__(self):
        self._strategies = [
            ImageExtractionStrategy(),
            SVGExtractionStrategy(),
        ]

    def add_strategy(self, strategy: ColorExtractionStrategy) -> None:
        """Add a new extraction strategy."""
        self._strategies.append(strategy)

    def extract_colors(
        self, file_path: Path, max_colors: Optional[int] = None
    ) -> Dict[str, float]:
        """
        Extract colors using the appropriate strategy.

        Args:
            file_path: Path to the file.
            max_colors: Maximum number of colors to extract.

        Returns:
            Dictionary mapping HEX color strings to frequencies.

        Raises:
            UnsupportedFormatError: If no strategy can handle the file.
        """
        from chromaspec.exceptions import UnsupportedFormatError

        for strategy in self._strategies:
            if strategy.can_handle(file_path):
                return strategy.extract(file_path, max_colors)

        raise UnsupportedFormatError(
            f"No extraction strategy available for {file_path.suffix}"
        )
