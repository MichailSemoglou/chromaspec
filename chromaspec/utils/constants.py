"""
Configuration constants for ChromaSpec.

This module centralizes all configuration values to avoid magic numbers
and make the codebase more maintainable.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm, inch

# File format constants
SVG_EXTENSIONS = {".svg"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp"}
SUPPORTED_EXTENSIONS = SVG_EXTENSIONS | IMAGE_EXTENSIONS


# Image processing constants
class ImageProcessing:
    """Constants for image processing operations."""

    MAX_DIMENSION = 200
    MAX_COLORS = 1000
    MAX_SVG_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_COLOR_MATCHES = 10000


# PDF layout constants - Swiss Systematic Clarity Design
class PDFLayout:
    """Constants for PDF layout and styling following Swiss typographic principles."""

    PAGE_SIZE = letter

    # Margins: 2cm all around (Swiss modularity)
    MARGIN = 2 * cm  # ~ 0.787 inches

    # Typographic scale (Helvetica/Arial)
    # Primary typeface: Helvetica (or Arial fallback)
    PRIMARY_FONT = "Helvetica"
    PRIMARY_FONT_BOLD = "Helvetica-Bold"

    # Body text: 11-12pt with 1.2 line spacing
    BODY_SIZE = 11
    BODY_LEADING = BODY_SIZE * 1.2  # 13.2pt leading

    # Hierarchy through scale, not drastic size changes
    TITLE_SIZE = 18  # Modest title size
    SECTION_SIZE = 12  # Section headers
    METADATA_SIZE = 9  # Small ALL-CAPS labels
    FOOTER_SIZE = 8

    # Vertical rhythm: predictable spacing on grid
    GRID_UNIT = BODY_LEADING  # Base grid unit
    SPACE_BEFORE_SECTION = GRID_UNIT * 3  # 3 grid units before sections
    SPACE_AFTER_SECTION = GRID_UNIT * 1  # 1 grid unit after section header
    SPACE_BETWEEN_ITEMS = GRID_UNIT * 1.5  # Between color items
    SPACE_BEFORE_TABLE = GRID_UNIT * 2
    SPACE_AFTER_TABLE = GRID_UNIT * 2
    SECTION_SPACING = GRID_UNIT * 3  # Spacing between major sections

    # Modular color swatch dimensions
    RECT_HEIGHT = 0.6 * cm
    RECT_WIDTH = 1.2 * cm
    LABEL_SPACING = 0.4 * cm

    # Header and footer: minimal
    HEADER_HEIGHT = GRID_UNIT * 2
    FOOTER_HEIGHT = GRID_UNIT * 2
    SECTION_HEADER_HEIGHT = GRID_UNIT * 2

    # Chart dimensions: modular
    PIE_RADIUS = 1.5 * cm
    BAR_HEIGHT = 0.4 * cm
    BAR_MAX_WIDTH = 10 * cm

    # Table styling: 0.5pt light gray borders, horizontal only
    TABLE_BORDER_WIDTH = 0.5
    TABLE_BORDER_COLOR = (0.7, 0.7, 0.7)  # Light gray
    TABLE_CELL_PADDING = 0.2 * cm
    TABLE_ROW_HEIGHT = GRID_UNIT * 1.8

    # Content limits
    COLORS_PER_SECTION = 30


# Color constants - Monochromatic logic (grayscale palette)
class ColorConstants:
    """Constants for color operations - Grayscale palette for systematic clarity."""

    HEX_PATTERN = r"#[0-9a-fA-F]{3,6}\b"

    # Grayscale chart representation
    GRAY_DARK = (0.2, 0.2, 0.2)  # Dark gray for primary
    GRAY_MEDIUM = (0.5, 0.5, 0.5)  # Medium gray for secondary
    GRAY_LIGHT = (0.7, 0.7, 0.7)  # Light gray for tertiary
    GRAY_VERY_LIGHT = (0.85, 0.85, 0.85)  # Very light gray for backgrounds

    # WCAG rating representation (grayscale)
    RATING_GOOD = (0.3, 0.3, 0.3)  # Dark gray
    RATING_WARNING = (0.5, 0.5, 0.5)  # Medium gray
    RATING_FAIL = (0.7, 0.7, 0.7)  # Light gray


# WCAG accessibility thresholds
class WCAGThresholds:
    """WCAG 2.1 contrast ratio thresholds."""

    AAA = 7.0
    AA = 4.5
    AA_LARGE = 3.0


# Logging configuration
class LoggingConfig:
    """Constants for logging configuration."""

    DEFAULT_LEVEL = "INFO"
    FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
