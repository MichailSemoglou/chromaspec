"""
Accessibility page generation for PDF reports.

This module provides functions for generating the accessibility and contrast
analysis page in PDF reports.
"""

import logging
from typing import Dict, List, Tuple

from chromaspec.analyzers import get_contrast_ratio, get_wcag_rating
from chromaspec.utils.constants import ColorConstants, PDFLayout

logger = logging.getLogger(__name__)


def draw_accessibility_page(
    pdf,
    color_categories: Dict[str, List[Tuple[str, float]]],
    width: float,
    height: float,
    page_number: int,
) -> None:
    """
    Draw a page with accessibility/contrast information.

    Args:
        pdf: The canvas object.
        color_categories: Dictionary with color categories.
        width: Page width.
        height: Page height.
        page_number: Current page number.
    """
    from chromaspec.generators.pdf_pages import draw_footer, draw_header

    draw_header(pdf, width, height)
    draw_footer(pdf, width, page_number)

    y = height - PDFLayout.MARGIN - PDFLayout.HEADER_HEIGHT - 0.3 * PDFLayout.MARGIN

    pdf.setFont(PDFLayout.PRIMARY_FONT_BOLD, 16)
    pdf.setFillColor("black")
    pdf.drawString(PDFLayout.MARGIN, y, "Accessibility & Contrast")
    y -= 0.4 * PDFLayout.MARGIN

    pdf.setFont(PDFLayout.PRIMARY_FONT, 10)
    pdf.setFillColor("gray")
    pdf.drawString(PDFLayout.MARGIN, y, "WCAG 2.1 contrast ratios for text readability")
    y -= 0.5 * PDFLayout.MARGIN

    all_colors = []
    for section_key in ["red", "green", "blue"]:
        all_colors.extend(color_categories[section_key])

    top_colors = sorted(all_colors, key=lambda x: x[1], reverse=True)[:8]

    pdf.setFont(PDFLayout.PRIMARY_FONT_BOLD, 10)
    pdf.setFillColor("black")
    col1 = PDFLayout.MARGIN
    col2 = PDFLayout.MARGIN + 1.5 * PDFLayout.MARGIN
    col3 = PDFLayout.MARGIN + 3.0 * PDFLayout.MARGIN
    col4 = PDFLayout.MARGIN + 4.5 * PDFLayout.MARGIN
    pdf.drawString(col1, y, "Color")
    pdf.drawString(col2, y, "vs White")
    pdf.drawString(col3, y, "vs Black")
    pdf.drawString(col4, y, "Best Use")
    y -= 0.35 * PDFLayout.MARGIN

    pdf.setStrokeColor("gray")
    pdf.line(
        PDFLayout.MARGIN,
        y + 0.1 * PDFLayout.MARGIN,
        width - PDFLayout.MARGIN,
        y + 0.1 * PDFLayout.MARGIN,
    )
    y -= 0.15 * PDFLayout.MARGIN

    for color, freq in top_colors:
        box_size = 0.25 * PDFLayout.MARGIN
        pdf.setFillColor(color)
        pdf.rect(PDFLayout.MARGIN, y - box_size, box_size, box_size, fill=1, stroke=0)

        pdf.setFont(PDFLayout.PRIMARY_FONT, 9)
        pdf.setFillColor("black")
        pdf.drawString(
            PDFLayout.MARGIN + box_size + 0.1 * PDFLayout.MARGIN,
            y - box_size / 2 - 3,
            color.upper(),
        )

        ratio_white = get_contrast_ratio(color, "#FFFFFF")
        ratio_black = get_contrast_ratio(color, "#000000")

        rating_white = get_wcag_rating(ratio_white)
        rating_black = get_wcag_rating(ratio_black)

        # Set color based on rating
        if rating_white in ["AAA", "AA"]:
            pdf.setFillColorRGB(*ColorConstants.RATING_GOOD)
        elif rating_white == "AA Large":
            pdf.setFillColorRGB(*ColorConstants.RATING_WARNING)
        else:
            pdf.setFillColorRGB(*ColorConstants.RATING_FAIL)
        pdf.drawString(
            col2, y - box_size / 2 - 3, f"{ratio_white:.1f}:1 ({rating_white})"
        )

        if rating_black in ["AAA", "AA"]:
            pdf.setFillColorRGB(*ColorConstants.RATING_GOOD)
        elif rating_black == "AA Large":
            pdf.setFillColorRGB(*ColorConstants.RATING_WARNING)
        else:
            pdf.setFillColorRGB(*ColorConstants.RATING_FAIL)
        pdf.drawString(
            col3, y - box_size / 2 - 3, f"{ratio_black:.1f}:1 ({rating_black})"
        )

        pdf.setFillColor("black")
        if ratio_white > ratio_black:
            best_use = "White text on color"
        else:
            best_use = "Black text on color"
        pdf.drawString(col4, y - box_size / 2 - 3, best_use)

        y -= box_size + 0.2 * PDFLayout.MARGIN

    y -= 0.3 * PDFLayout.MARGIN
    pdf.setFont(PDFLayout.PRIMARY_FONT_BOLD, 10)
    pdf.setFillColor("black")
    pdf.drawString(PDFLayout.MARGIN, y, "WCAG Rating Guide:")
    y -= 0.25 * PDFLayout.MARGIN
    pdf.setFont(PDFLayout.PRIMARY_FONT, 9)
    pdf.setFillColorRGB(*ColorConstants.RATING_GOOD)
    pdf.drawString(PDFLayout.MARGIN, y, "AAA (≥7:1) - Excellent for all text")
    y -= 0.2 * PDFLayout.MARGIN
    pdf.setFillColorRGB(*ColorConstants.RATING_GOOD)
    pdf.drawString(PDFLayout.MARGIN, y, "AA (≥4.5:1) - Good for normal text")
    y -= 0.2 * PDFLayout.MARGIN
    pdf.setFillColorRGB(*ColorConstants.RATING_WARNING)
    pdf.drawString(PDFLayout.MARGIN, y, "AA Large (≥3:1) - OK for large text only")
    y -= 0.2 * PDFLayout.MARGIN
    pdf.setFillColorRGB(*ColorConstants.RATING_FAIL)
    pdf.drawString(PDFLayout.MARGIN, y, "Fail (<3:1) - Not accessible")
