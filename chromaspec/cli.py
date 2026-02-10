"""
Command-line interface for ChromaSpec.

This module provides main CLI entry point for the application.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

from chromaspec.analyzers import categorize_colors
from chromaspec.exceptions import (
    ChromaSpecError,
)
from chromaspec.exceptions import FileNotFoundError as ChromaSpecFileNotFoundError
from chromaspec.exceptions import (
    ImageProcessingError,
    PDFGenerationError,
    UnsupportedFormatError,
    ValidationError,
)
from chromaspec.extractors import extract_colors
from chromaspec.generators import generate_color_pdf
from chromaspec.utils.constants import (
    IMAGE_EXTENSIONS,
    SUPPORTED_EXTENSIONS,
    LoggingConfig,
)
from chromaspec.utils.security import validate_safe_path
from chromaspec.utils.validators import validate_output_path

# Configure logging
logging.basicConfig(
    level=getattr(logging, LoggingConfig.DEFAULT_LEVEL),
    format=LoggingConfig.FORMAT,
    datefmt=LoggingConfig.DATE_FORMAT,
)
logger = logging.getLogger(__name__)


def process_file(
    input_path: Path, output_path: Path, quiet: bool = False
) -> Dict[str, Any]:
    """
    Process an input file to extract colors and optionally generate a PDF.

    Args:
        input_path: Path to input file (SVG or image).
        output_path: Path for the output (PDF or JSON).
        quiet: Whether to suppress console output.

    Returns:
        Dictionary containing extracted color data.

    Raises:
        ChromaSpecFileNotFoundError: If input file doesn't exist.
        ValidationError: If validation fails.
        UnsupportedFormatError: If file format is not supported.
        ImageProcessingError: If image processing fails.
        PDFGenerationError: If PDF generation fails.
    """
    logger.info(f"Starting processing: {input_path}")

    # Security: Validate paths to prevent path traversal attacks
    try:
        validate_safe_path(input_path)
        validate_safe_path(output_path)
    except ValidationError as e:
        logger.error(f"Path validation failed: {e}")
        raise

    # Extract colors with security protections (timeout, XXE prevention, etc.)
    hex_colors_with_freq = extract_colors(input_path)
    color_categories = categorize_colors(hex_colors_with_freq)

    total_colors = sum(len(colors) for colors in color_categories.values())
    if total_colors == 0 and not quiet:
        raise ValidationError(f"No red, green, or blue colors found in {input_path}")

    if not quiet:
        logger.info(
            f"Found colors - Red: {len(color_categories['red'])}, "
            f"Green: {len(color_categories['green'])}, "
            f"Blue: {len(color_categories['blue'])}"
        )
        print(
            f"Found colors - Red: {len(color_categories['red'])}, "
            f"Green: {len(color_categories['green'])}, "
            f"Blue: {len(color_categories['blue'])}"
        )

    # Prepare result dictionary
    result = {
        "file": str(input_path),
        "total_colors": total_colors,
        "colors_by_category": {
            "red": [{"color": c, "frequency": f} for c, f in color_categories["red"]],
            "green": [
                {"color": c, "frequency": f} for c, f in color_categories["green"]
            ],
            "blue": [{"color": c, "frequency": f} for c, f in color_categories["blue"]],
        },
    }

    # Generate PDF if output is PDF
    if output_path.suffix.lower() == ".pdf":
        generate_color_pdf(output_path, color_categories, input_path)
        logger.info(f"PDF generated: {output_path}")

    return result


def process_batch(
    input_files: List[Path],
    output_file: Path,
    format: str = "json",
    generate_pdfs: bool = False,
    quiet: bool = False,
) -> List[Dict[str, Any]]:
    """
    Process multiple files and generate a consolidated report.

    Args:
        input_files: List of paths to input files.
        output_file: Path for the consolidated output report.
        format: Output format ('json' or 'csv').
        generate_pdfs: Whether to generate individual PDFs.
        quiet: Whether to suppress console output.

    Returns:
        List of dictionaries containing color data for each file.

    Raises:
        ChromaSpecFileNotFoundError: If any input file doesn't exist.
        ValidationError: If validation fails.
    """
    logger.info(f"Starting batch processing of {len(input_files)} files")
    results = []

    for idx, input_path in enumerate(input_files, 1):
        if not quiet:
            print(f"\n[{idx}/{len(input_files)}] Processing: {input_path.name}")

        try:
            # Generate individual PDF if requested
            if generate_pdfs:
                pdf_path = input_path.with_name(f"{input_path.stem}_colors.pdf")
                process_file(input_path, pdf_path, quiet)
            else:
                # Just extract data without PDF
                hex_colors_with_freq = extract_colors(input_path)
                color_categories = categorize_colors(hex_colors_with_freq)

                total_colors = sum(len(colors) for colors in color_categories.values())

                result = {
                    "file": str(input_path),
                    "total_colors": total_colors,
                    "colors_by_category": {
                        "red": [
                            {"color": c, "frequency": f}
                            for c, f in color_categories["red"]
                        ],
                        "green": [
                            {"color": c, "frequency": f}
                            for c, f in color_categories["green"]
                        ],
                        "blue": [
                            {"color": c, "frequency": f}
                            for c, f in color_categories["blue"]
                        ],
                    },
                }
                results.append(result)

                if not quiet:
                    print(
                        f"  Colors - Red: {len(color_categories['red'])}, "
                        f"Green: {len(color_categories['green'])}, "
                        f"Blue: {len(color_categories['blue'])}"
                    )

        except Exception as e:
            logger.error(f"Error processing {input_path}: {e}")
            if not quiet:
                print(f"  Error: {e}")
            # Add error info to results
            results.append(
                {
                    "file": str(input_path),
                    "error": str(e),
                    "total_colors": 0,
                    "colors_by_category": {"red": [], "green": [], "blue": []},
                }
            )

    # Generate consolidated report
    _write_batch_report(results, output_file, format)
    logger.info(f"Batch processing complete: {output_file}")

    if not quiet:
        print(f"\n{'=' * 60}")
        print(f"Consolidated report generated: {output_file}")
        total_processed = len(results)
        total_errors = sum(1 for r in results if "error" in r)
        print(f"Files processed: {total_processed}")
        print(f"Successful: {total_processed - total_errors}")
        print(f"Errors: {total_errors}")

    return results


def _write_batch_report(
    results: List[Dict[str, Any]], output_file: Path, format: str
) -> None:
    """
    Write batch processing results to file.

    Args:
        results: List of processing results.
        output_file: Path for output file.
        format: Output format ('json' or 'csv').
    """
    if format.lower() == "json":
        with open(output_file, "w") as f:
            json.dump(
                {"files": results, "summary": _generate_summary(results)},
                f,
                indent=2,
            )
    elif format.lower() == "csv":
        import csv

        with open(output_file, "w", newline="") as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow(
                ["File", "Total Colors", "Red Count", "Green Count", "Blue Count"]
            )
            # Write data for each file
            for result in results:
                if "error" in result:
                    writer.writerow([result["file"], "ERROR", "-", "-", "-"])
                else:
                    red_count = len(result["colors_by_category"]["red"])
                    green_count = len(result["colors_by_category"]["green"])
                    blue_count = len(result["colors_by_category"]["blue"])
                    writer.writerow(
                        [
                            result["file"],
                            result["total_colors"],
                            red_count,
                            green_count,
                            blue_count,
                        ]
                    )


def _generate_summary(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate summary statistics from batch processing results.

    Args:
        results: List of processing results.

    Returns:
        Dictionary containing summary statistics.
    """
    total_files = len(results)
    successful_files = sum(1 for r in results if "error" not in r)
    failed_files = total_files - successful_files

    total_colors = sum(r.get("total_colors", 0) for r in results)
    avg_colors = total_colors / successful_files if successful_files > 0 else 0

    # Find file with most colors
    max_colors_file = None
    max_colors = 0
    for result in results:
        if result.get("total_colors", 0) > max_colors:
            max_colors = result.get("total_colors", 0)
            max_colors_file = result.get("file", "Unknown")

    return {
        "total_files": total_files,
        "successful_files": successful_files,
        "failed_files": failed_files,
        "total_colors_found": total_colors,
        "average_colors_per_file": round(avg_colors, 2),
        "file_with_most_colors": {
            "file": max_colors_file,
            "color_count": max_colors,
        },
    }


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments namespace.
    """
    supported_formats = ", ".join(sorted(SUPPORTED_EXTENSIONS))
    parser = argparse.ArgumentParser(
        description="Extract colors from SVG or image files and generate PDF color swatches.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Supported formats: {supported_formats}

Examples:
  Single file:
    %(prog)s image.svg
    %(prog)s photo.png
    %(prog)s image.jpg custom_output.pdf

  Batch processing:
    %(prog)s --batch *.svg report.json
    %(prog)s --batch images/* results.csv --format csv
    %(prog)s --batch --pattern "*.png" --output report.json --pdfs
        """,
    )

    # Single file mode (default)
    parser.add_argument(
        "input_file",
        type=Path,
        nargs="?",
        help=f"Path to input file ({supported_formats}) for single file mode",
    )
    parser.add_argument(
        "output_pdf",
        type=Path,
        nargs="?",
        default=None,
        help="Path for output PDF (default: <input_name>_colors.pdf)",
    )

    # Batch mode
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Enable batch processing mode",
    )
    parser.add_argument(
        "--pattern",
        type=str,
        help="File pattern to match for batch processing (e.g., '*.svg')",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output file for batch report (default: batch_report.json)",
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["json", "csv"],
        default="json",
        help="Output format for batch report (default: json)",
    )
    parser.add_argument(
        "--pdfs",
        action="store_true",
        help="Generate individual PDFs for each file in batch mode",
    )

    # Common options
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Suppress non-error output"
    )

    return parser.parse_args()


def main() -> int:
    """
    Main entry point for CLI.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    args = parse_arguments()

    # Adjust logging level based on arguments
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")
    elif args.quiet:
        logging.getLogger().setLevel(logging.ERROR)

    # Batch mode
    if args.batch:
        if not args.pattern and args.input_file and args.input_file.is_dir():
            # If directory provided, use it as base for pattern
            args.pattern = str(args.input_file / "*")
            args.input_file = None

        if not args.pattern:
            print(
                "Error: --pattern is required for batch mode unless a directory is provided",
                file=sys.stderr,
            )
            return 1

        # Find matching files
        pattern_path = Path(args.pattern)
        base_dir = pattern_path.parent if str(pattern_path.parent) != "." else Path(".")
        glob_pattern = pattern_path.name
        matching_files = sorted(base_dir.glob(glob_pattern))

        if not matching_files:
            print(
                f"Error: No files found matching pattern: {args.pattern}",
                file=sys.stderr,
            )
            return 1

        # Filter by supported extensions
        input_files = [
            f for f in matching_files if f.suffix.lower() in SUPPORTED_EXTENSIONS
        ]

        if not input_files:
            print(
                f"Error: No supported files found matching pattern: {args.pattern}",
                file=sys.stderr,
            )
            return 1

        # Determine output file
        output_file = args.output or Path(f"batch_report.{args.format}")

        # Process batch
        try:
            process_batch(input_files, output_file, args.format, args.pdfs, args.quiet)
            return 0
        except Exception as e:
            logger.exception(f"Batch processing error: {e}")
            print(f"Error: {e}", file=sys.stderr)
            return 1

    # Single file mode
    else:
        if not args.input_file:
            print("Error: input_file is required for single file mode", file=sys.stderr)
            return 1

        # Validate file extension
        extension = args.input_file.suffix.lower()
        if extension not in SUPPORTED_EXTENSIONS:
            logger.error(f"Unsupported file format: {extension}")
            print(
                f"Error: Unsupported file format '{extension}'. "
                f"Supported formats: {', '.join(sorted(SUPPORTED_EXTENSIONS))}",
                file=sys.stderr,
            )
            return 1

        # Check if Pillow is available for image files
        if extension in IMAGE_EXTENSIONS:
            try:
                from chromaspec.extractors.image_extractor import PIL_AVAILABLE

                if not PIL_AVAILABLE:
                    print(
                        "Error: Pillow is required for image processing. "
                        "Install it with: pip install Pillow",
                        file=sys.stderr,
                    )
                    return 1
            except ImportError:
                pass

        # Determine output path
        output_path = args.output_pdf or args.input_file.with_name(
            f"{args.input_file.stem}_colors.pdf"
        )

        # Validate output path
        try:
            output_path = validate_output_path(output_path)
        except ValidationError as e:
            logger.error(f"Output path validation failed: {e}")
            print(f"Error: {e}", file=sys.stderr)
            return 1

        # Process file
        try:
            process_file(args.input_file, output_path, args.quiet)
            return 0
        except ChromaSpecFileNotFoundError as e:
            logger.error(f"File not found: {e}")
            print(f"Error: {e}", file=sys.stderr)
            return 1
        except UnsupportedFormatError as e:
            logger.error(f"Unsupported format: {e}")
            print(f"Error: {e}", file=sys.stderr)
            return 1
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            print(f"Error: {e}", file=sys.stderr)
            return 1
        except ImageProcessingError as e:
            logger.error(f"Image processing error: {e}")
            print(f"Error: {e}", file=sys.stderr)
            return 1
        except PDFGenerationError as e:
            logger.error(f"PDF generation error: {e}")
            print(f"Error: {e}", file=sys.stderr)
            return 1
        except ChromaSpecError as e:
            logger.error(f"ChromaSpec error: {e}")
            print(f"Error: {e}", file=sys.stderr)
            return 1
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            print(f"Unexpected error: {e}", file=sys.stderr)
            return 1


if __name__ == "__main__":
    sys.exit(main())
