# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.0] - 2026-02-14

### Added

- Comprehensive type annotations across all modules (PEP 561 `py.typed` marker)
- Strict mypy configuration (`disallow_untyped_defs`, `check_untyped_defs`, `warn_return_any`)
- Python 3.13 support in CI test matrix and classifiers
- mypy type-checked badge to README
- "Statement of Need" section in README for JOSS pre-flight compliance

### Changed

- Upgraded GitHub Actions `actions/setup-python` from v4 to v5
- CI lint and security jobs now run on Python 3.13 (previously 3.11)
- Coverage upload now uses Python 3.13 matrix entry
- Stricter mypy settings enforced via `mypy.ini`

### Fixed

- Added missing type annotations for `pdf` parameters in all generator functions (now `canvas.Canvas`)
- Added return type to `timeout()` context manager (`Generator[None, None, None]`)
- Added type annotation on `timeout_handler` signal callback
- Added `-> None` return type to `ServiceContainer.__init__` and `ColorExtractor.__init__`

## [1.1.1] - 2026-02-10

### Fixed

- Fixed all mypy type errors (Optional types, incorrect function calls, return type annotations)
- Fixed isort/black formatting conflicts by adding `[tool.isort] profile = "black"` to pyproject.toml
- Fixed CI workflow: added `--profile black` to isort check, use `python -m pytest`
- Fixed missing `[project.optional-dependencies] dev` section in pyproject.toml
- Removed unused imports and ambiguous variable names across codebase
- Fixed `extract_colors_from_svg` reference to `extract_colors_from_svg_safe` in strategies and container

### Changed

- Dropped Python 3.8 support (EOL since October 2024, incompatible with ReportLab 4.x)
- Minimum Python version is now 3.9+
- Removed codecov badge and CI integration (not configured)
- Cleaned up README documentation links to reference only existing files

## [1.1.0] - 2026-02-10

### Added

- Dark mode compatibility checker with `check_dark_mode_compatibility()` function
- Palette generator with WCAG accessibility compliance:
  - `generate_accessibility_palette()` - Ensures text/background contrast
  - `generate_triadic_palette()` - Three colors 120° apart
  - `generate_split_complementary_palette()` - Base + two adjacent to complement
  - `generate_tetradic_palette()` - Four colors 90° apart
- Batch processing support via CLI:
  - `--batch` flag for processing multiple files
  - `--pattern` for glob patterns
  - JSON and CSV export formats
  - Optional individual PDF generation with `--pdfs`
- Comprehensive test suite:
  - 99+ tests across all modules
  - Property-based testing foundations
  - High code coverage (>90%)

### Changed

- Refactored monolithic script into modular package structure
- Improved logging with configurable levels
- Enhanced PDF generation with accessibility page
- Optimized image processing with intelligent resizing

### Fixed

- Memory optimization for large image processing
- Improved error handling and user feedback

## [1.0.0] - 2025-12-09

### Added

- Initial release
- SVG and image color extraction
- Color categorization (Red, Green, Blue)
- PDF report generation with color swatches
- HEX, RGB, CMYK, and HSL color conversions
- Color harmony calculations (complementary, analogous, triadic)
- WCAG 2.1 accessibility analysis
- Command-line interface
- Basic documentation

### Security

- Input validation for color formats
- File format verification
- SVG size limits

---

## Migration Guides

### Upgrading to 1.1.0

**New Features:**

- Try the new palette generator for WCAG-compliant color schemes
- Use batch processing for multiple files
- Check dark mode compatibility of your colors

**Breaking Changes:**
None - fully backward compatible

**Deprecations:**
None

### Upgrading to 2.0.0 (Planned)

**Planned Breaking Changes:**

- Configuration management: Environment variables will be required for some settings
- API changes: Some internal APIs may be refactored
- Python 3.8 support may be dropped (minimum 3.9)

**Migration Path:**
Detailed migration guide will be provided before 2.0.0 release.

---

## Release Process

1. Update version in `pyproject.toml` and `chromaspec/__init__.py`
2. Update this CHANGELOG.md with release date
3. Create git tag: `git tag -a v1.1.0 -m "Release v1.1.0"`
4. Push tag: `git push origin v1.1.0`
5. Build package: `python -m build`
6. Upload to PyPI: `twine upload dist/*`
7. Create GitHub release with changelog

---

## Version Numbering

We follow Semantic Versioning (SemVer):

- **MAJOR** version: Incompatible API changes
- **MINOR** version: New functionality in backward-compatible manner
- **PATCH** version: Backward-compatible bug fixes

Example: `1.2.3`

- 1 = Major version
- 2 = Minor version
- 3 = Patch version
