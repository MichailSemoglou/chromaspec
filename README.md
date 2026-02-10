# ChromaSpec

A professional Python package for color palette extraction, analysis, and visualization from SVG and image files.

[![PyPI version](https://badge.fury.io/py/chromaspec.svg)](https://badge.fury.io/py/chromaspec)
[![Tests](https://github.com/MichailSemoglou/chromaspec/actions/workflows/test.yml/badge.svg)](https://github.com/MichailSemoglou/chromaspec/actions/workflows/test.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17864788.svg)](https://doi.org/10.5281/zenodo.17864788)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Documentation

- **[Getting Started](#quick-start)** - Basic usage examples
- **[Features](#features)** - Complete feature list
- **[Python API](#python-api)** - Programmatic usage
- **[Module Documentation](#module-documentation)** - Detailed API reference
- **[Contributing](CONTRIBUTING.md)** - How to contribute to the project
- **[Changelog](CHANGELOG.md)** - Version history and release notes

## Features

- **Color Extraction**: Extract colors from SVG files and image formats (PNG, JPG, JPEG, GIF, BMP, TIFF, WEBP)
- **Color Analysis**:
  - Color categorization (Red, Green, Blue)
  - Color harmonies (Complementary, Analogous, Split-Complementary, Triadic)
  - WCAG 2.1 accessibility analysis and contrast ratios
  - **Dark mode compatibility** - Verify colors work in both light and dark themes
- **Color Palette Generator**: Generate harmonious palettes with WCAG accessibility compliance
  - Complementary palettes (2 colors)
  - Triadic palettes (3 colors, 120° apart)
  - Split-complementary palettes (3 colors)
  - Tetradic palettes (4 colors, 90° apart)
- **Color Conversions**: RGB, HSL, CMYK, and HEX formats
- **PDF Reports**: Generate comprehensive color swatch documents with visualizations
- **Batch Processing**: Process multiple files at once via CLI with consolidated reports
- **Security**: Input validation and protection against DoS/ReDoS attacks
- **Performance**: Optimized image processing with LRU caching

## Installation

```bash
pip install chromaspec
```

For image processing support:

```bash
pip install chromaspec[image]
# or
pip install Pillow
```

For development:

```bash
pip install chromaspec[dev]
```

## Quick Start

### Command Line

```bash
# Process an SVG file
chromaspec image.svg

# Process an image file
chromaspec photo.png

# Specify custom output
chromaspec image.jpg custom_report.pdf

# Batch process multiple files (generates consolidated JSON report)
chromaspec --batch --pattern "*.svg" --output report.json

# Batch process with individual PDFs
chromaspec --batch --pattern "images/*.png" --pdfs

# Batch process with CSV output
chromaspec --batch --pattern "*.jpg" --output results.csv --format csv

# Enable verbose logging
chromaspec image.svg -v

# Suppress output except errors
chromaspec image.png -q
```

### Python API

```python
from pathlib import Path
from chromaspec import ChromaSpec

# Initialize analyzer
analyzer = ChromaSpec()

# Extract colors from a file
colors = analyzer.extract_colors(Path("image.png"))

# Analyze colors
categories = analyzer.categorize_colors(colors)

# Generate color harmonies
from chromaspec.analyzers import get_complementary_color
comp = get_complementary_color("#FF0000")

# Check accessibility
from chromaspec.analyzers import get_contrast_ratio, get_wcag_rating
ratio = get_contrast_ratio("#FF0000", "#FFFFFF")
rating = get_wcag_rating(ratio)

# Generate color palettes with accessibility
from chromaspec.generators import (
    ColorPalette,
    generate_accessibility_palette,
    generate_triadic_palette,
)
palette = generate_triadic_palette("#FF0000", target_rating="AA")
print(f"Primary: {palette.primary}")
print(f"Secondary: {palette.secondary}")
print(f"Background: {palette.background}")
print(f"WCAG Rating: {palette.wcag_rating}")

# Check dark mode compatibility
from chromaspec.analyzers import check_dark_mode_compatibility
result = check_dark_mode_compatibility("#FF0000")
print(f"Compatible: {result.is_compatible}")
print(f"Light mode: {result.light_contrast:.2f}:1 ({result.light_rating})")
print(f"Dark mode: {result.dark_contrast:.2f}:1 ({result.dark_rating})")
```

## Supported File Formats

- **SVG**: `.svg`
- **Images**: `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.tiff`, `.webp`

## New Features Documentation

### Color Palette Generator

Generate harmonious color palettes that meet WCAG accessibility standards:

```python
from chromaspec.generators import (
    generate_accessibility_palette,
    generate_triadic_palette,
    generate_split_complementary_palette,
    generate_tetradic_palette,
)

# Generate complementary palette (2 colors)
palette = generate_accessibility_palette("#FF0000", target_rating="AA")
print(palette)

# Generate triadic palette (3 colors, 120° apart)
palette = generate_triadic_palette("#3B82F6", target_rating="AAA")

# Generate split-complementary palette
palette = generate_split_complementary_palette("#10B981")

# Generate tetradic palette (4 colors, 90° apart)
palette = generate_tetradic_palette("#8B5CF6")
```

### Dark Mode Compatibility Checker

Verify that colors work well in both light and dark themes:

```python
from chromaspec.analyzers import (
    check_dark_mode_compatibility,
    generate_dark_mode_palette,
    get_compatible_text_color,
    suggest_dark_mode_adjustments,
)

# Check a single color
result = check_dark_mode_compatibility("#333333")
if result.is_compatible:
    print("✓ Color works in both modes")
else:
    print("✗ Color needs adjustment")

# Generate a full palette tested for dark mode
results = generate_dark_mode_palette("#FF0000")
for color_name, result in results.items():
    print(f"{color_name}: {'✓' if result.is_compatible else '✗'}")

# Find a text color that works in both modes
text_color = get_compatible_text_color(
    background_light="#FFFFFF",
    background_dark="#121212",
    target_rating="AA"
)

# Get suggestions to fix incompatible colors
suggestions = suggest_dark_mode_adjustments("#FF0000")
for suggestion in suggestions:
    print(f"Try {suggestion['color']} ({suggestion['adjustment']})")
```

### Batch Processing CLI

Process multiple files at once with consolidated reports:

```bash
# Generate JSON report
chromaspec --batch --pattern "*.svg" --output report.json

# Generate CSV report
chromaspec --batch --pattern "images/*.png" --output results.csv --format csv

# Generate individual PDFs + consolidated report
chromaspec --batch --pattern "*.jpg" --pdfs --output summary.json

# Quiet mode (less output)
chromaspec --batch --pattern "*.svg" --output report.json -q

# Using a directory
chromaspec --batch ./my_images --output report.json
```

Report format includes:

- File-by-file color breakdown
- Red, Green, and Blue color counts
- Total colors per file
- Summary statistics (total files, colors found, average colors per file)
- Error tracking for failed files

## Module Documentation

### chromaspec.converters

Color conversion functions:

```python
from chromaspec.converters import hex_to_rgb, rgb_to_hsl, rgb_to_cmyk

# HEX to RGB
rgb = hex_to_rgb("#FF0000")  # (255, 0, 0)

# RGB to HSL
hsl = rgb_to_hsl((255, 0, 0))  # (0.0, 100.0, 50.0)

# RGB to CMYK
cmyk = rgb_to_cmyk((255, 0, 0))  # (0, 100, 100, 0)

# Calculate luminance (for contrast ratios)
from chromaspec.converters import calculate_luminance
lum = calculate_luminance((255, 0, 0))  # ~0.21
```

### chromaspec.analyzers

Color analysis and classification:

```python
from chromaspec.analyzers import (
    is_red_color, is_green_color, is_blue_color,
    categorize_colors,
    get_complementary_color, get_analogous_colors,
    get_contrast_ratio, get_wcag_rating
)

# Classify colors
is_red_color((255, 0, 0))  # True

# Get color harmonies
comp = get_complementary_color("#FF0000")  # "#00FFFF"
analogs = get_analogous_colors("#FF0000")  # ("#FF9900", "#FF0099")

# Accessibility analysis
ratio = get_contrast_ratio("#FF0000", "#FFFFFF")  # ~3.98
rating = get_wcag_rating(ratio)  # "AA Large"
```

### chromaspec.extractors

Color extraction from files:

```python
from pathlib import Path
from chromaspec.extractors import extract_colors

# Extract colors with frequencies
colors = extract_colors(Path("image.svg"))
# Returns: {"#FF0000": 25.5, "#00FF00": 30.2, ...}

# Extract specific formats
from chromaspec.extractors import extract_hex_colors_from_svg
svg_colors = extract_hex_colors_from_svg(svg_content)

from chromaspec.extractors import extract_colors_from_image
img_colors = extract_colors_from_image(Path("photo.png"))
```

### chromaspec.generators

PDF report generation:

```python
from pathlib import Path
from chromaspec.generators import generate_color_pdf
from chromaspec.analyzers import categorize_colors

# Generate PDF report
colors = extract_colors(Path("image.png"))
categories = categorize_colors(colors)
generate_color_pdf(
    Path("report.pdf"),
    categories,
    Path("image.png")
)
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Run tests with coverage
pytest --cov=chromaspec --cov-report=html

# Run specific test file
pytest tests/test_converters.py
```

### Code Quality

```bash
# Format code with Black
black chromaspec tests

# Sort imports with isort
isort chromaspec tests

# Lint with flake8
flake8 chromaspec tests

# Type check with mypy
mypy chromaspec
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run pre-commit manually
pre-commit run --all-files
```

## Project Structure

```
chromaspec/
├── __init__.py                # Package initialization
├── cli.py                     # Command-line interface with batch support
├── exceptions.py              # Custom exception hierarchy
├── analyzers/                 # Color analysis modules
│   ├── classification.py      # Color categorization
│   ├── harmonies.py           # Color harmony calculations
│   ├── accessibility.py       # WCAG contrast analysis
│   └── dark_mode.py           # Dark mode compatibility checker
├── converters/                # Color conversion modules
│   ├── rgb_converters.py      # RGB, CMYK, HEX conversions
│   └── hsl_converters.py      # HSL conversions
├── extractors/                # Color extraction modules
│   ├── svg_extractor.py       # SVG color extraction
│   └── image_extractor.py     # Image color extraction
├── generators/                # PDF generation modules
│   ├── pdf_pages.py           # PDF page layouts
│   ├── charts.py              # Chart generation
│   ├── accessibility_page.py
│   ├── palette.py             # Color palette generator
│   └── pdf_generator.py       # Main PDF generator
└── utils/                     # Utility modules
    ├── constants.py           # Configuration constants
    └── validators.py          # Input validation
```

## Performance Optimizations

- **LRU Caching**: RGB to HSL conversions are cached for repeated lookups
- **Image Resizing**: Large images are automatically resized for efficient processing
- **Memory Efficiency**: Color counting uses Counter directly on pixel data iterators
- **Input Validation**: Size limits prevent DoS attacks on SVG processing

## Security

- Input validation for all user-provided data
- Protection against ReDoS (Regex Denial of Service) attacks
- File format validation before processing
- Size limits for SVG content and color matches

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run the linters and tests
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Citation

If you use ChromaSpec in your research, please cite:

```bibtex
@software{chromaspec,
  author = {Semoglou, Michail},
  title = {ChromaSpec: Color Palette Analyzer},
  version = {1.1.0},
  year = {2026},
  url = {https://github.com/MichailSemoglou/chromaspec},
  doi = {10.5281/zenodo.17864788}
}
```

## Acknowledgments

- Color conversion algorithms based on standard color science
- WCAG accessibility calculations follow W3C specifications
- ReportLab for PDF generation
- Pillow for image processing
