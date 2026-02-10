"""
ChromaSpec - Color Palette Analyzer

Extracts colors from SVG or image files (PNG, JPG, etc.) and generates a PDF
color swatch document organized by Red, Green, and Blue sections.

Also includes:
- Color palette generator with WCAG accessibility compliance
- Dark mode compatibility checker
- Batch processing support via CLI

Version: 1.1.1
"""

__version__ = "1.1.1"
__author__ = "Michail Semoglou"

from chromaspec.analyzers import categorize_colors
from chromaspec.extractors import extract_colors
from chromaspec.generators import generate_color_pdf

__all__ = [
    "extract_colors",
    "categorize_colors",
    "generate_color_pdf",
    "__version__",
]
