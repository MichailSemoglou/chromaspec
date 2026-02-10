"""
Main PDF generation module.

This module provides the main function for generating complete PDF reports
from color categories.
"""

import logging
from pathlib import Path
from typing import Dict, List, Tuple

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from chromaspec.converters import hex_to_rgb, rgb_to_cmyk
from chromaspec.exceptions import PDFGenerationError
from chromaspec.utils.constants import PDFLayout

logger = logging.getLogger(__name__)


def generate_color_pdf(
    output_path: Path,
    color_categories: Dict[str, List[Tuple[str, float]]],
    input_path: Path,
) -> None:
    """
    Generate a PDF document with color swatches organized by RGB sections.

    Args:
        output_path: The path for the output PDF file.
        color_categories: Dictionary with 'red', 'green', 'blue' keys containing (color, frequency) tuples.
        input_path: Path to the original input file (for cover page).

    Raises:
        PDFGenerationError: If PDF generation fails.
    """
    total_colors = sum(len(colors) for colors in color_categories.values())
    if total_colors == 0:
        logger.warning("No colors to write to PDF")
        print("No colors to write to PDF.")
        return

    try:
        from chromaspec.generators.accessibility_page import draw_accessibility_page
        from chromaspec.generators.charts import (
            draw_statistics_page,
            draw_top_colors_page,
        )
        from chromaspec.generators.pdf_pages import (
            draw_cover_page,
            draw_footer,
            draw_header,
        )

        pdf = canvas.Canvas(str(output_path), pagesize=letter)
        width, height = letter
        page_number = 1

        # Cover page
        draw_cover_page(pdf, input_path, color_categories, width, height)
        pdf.showPage()
        page_number += 1

        # Statistics page
        draw_statistics_page(pdf, color_categories, width, height, page_number)
        pdf.showPage()
        page_number += 1

        # Top colors & harmonies page
        draw_top_colors_page(pdf, color_categories, width, height, page_number)
        pdf.showPage()
        page_number += 1

        # Accessibility page
        draw_accessibility_page(pdf, color_categories, width, height, page_number)
        pdf.showPage()
        page_number += 1

        # Color swatch pages
        y_position = height - PDFLayout.MARGIN - PDFLayout.HEADER_HEIGHT

        section_titles = {
            "red": "Red Colors",
            "green": "Green Colors",
            "blue": "Blue Colors",
        }

        draw_header(pdf, width, height)
        draw_footer(pdf, width, page_number)

        for section_key in ["red", "green", "blue"]:
            colors = color_categories[section_key]
            if not colors:
                continue

            # Check if we need a new page
            if (
                y_position
                < PDFLayout.MARGIN
                + PDFLayout.FOOTER_HEIGHT
                + PDFLayout.SECTION_HEADER_HEIGHT
                + PDFLayout.RECT_HEIGHT
            ):
                pdf.showPage()
                page_number += 1
                draw_header(pdf, width, height)
                draw_footer(pdf, width, page_number)
                y_position = height - PDFLayout.MARGIN - PDFLayout.HEADER_HEIGHT

            # Draw section header
            pdf.setFont(PDFLayout.PRIMARY_FONT_BOLD, 14)
            pdf.setFillColor("black")
            pdf.drawString(
                PDFLayout.MARGIN,
                y_position - PDFLayout.HEADER_HEIGHT / 2,
                section_titles[section_key],
            )
            pdf.setFont(PDFLayout.PRIMARY_FONT, 10)
            y_position -= PDFLayout.SECTION_HEADER_HEIGHT

            # Draw color swatches
            for color, frequency in colors:
                # Check if we need a new page
                if (
                    y_position
                    < PDFLayout.MARGIN + PDFLayout.FOOTER_HEIGHT + PDFLayout.RECT_HEIGHT
                ):
                    pdf.showPage()
                    page_number += 1
                    draw_header(pdf, width, height)
                    draw_footer(pdf, width, page_number)
                    y_position = height - PDFLayout.MARGIN - PDFLayout.HEADER_HEIGHT

                # Draw color rectangle
                pdf.setFillColor(color)
                pdf.setStrokeColor(color)
                pdf.rect(
                    PDFLayout.MARGIN,
                    y_position - PDFLayout.RECT_HEIGHT,
                    PDFLayout.RECT_WIDTH,
                    PDFLayout.RECT_HEIGHT,
                    fill=1,
                    stroke=0,
                )

                # Draw color information
                rgb = hex_to_rgb(color)
                cmyk = rgb_to_cmyk(rgb)

                pdf.setFont(PDFLayout.PRIMARY_FONT, 10)
                pdf.setFillColor("black")
                label = (
                    f"{color.upper()}     RGB({rgb[0]:3}, {rgb[1]:3}, {rgb[2]:3})     "
                    f"CMYK({cmyk[0]:3}, {cmyk[1]:3}, {cmyk[2]:3}, {cmyk[3]:3})     {frequency:.3f}%"
                )
                text_y = y_position - PDFLayout.RECT_HEIGHT / 2 - 3.5
                pdf.drawString(
                    PDFLayout.MARGIN + PDFLayout.RECT_WIDTH + PDFLayout.LABEL_SPACING,
                    text_y,
                    label,
                )

                y_position -= PDFLayout.RECT_HEIGHT

            y_position -= PDFLayout.SECTION_SPACING

        pdf.showPage()
        pdf.save()

        logger.info(f"PDF saved to: {output_path}")
        print(f"PDF saved to: {output_path}")

    except Exception as e:
        logger.error(f"Failed to generate PDF: {e}")
        raise PDFGenerationError(f"Failed to generate PDF: {e}") from e
