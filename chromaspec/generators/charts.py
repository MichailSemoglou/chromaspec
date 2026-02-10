"""
PDF chart generation functions.

This module provides functions for generating pie charts and bar charts in PDF reports.
"""

import logging
from typing import Dict, List, Tuple

from chromaspec.analyzers.harmonies import get_analogous_colors, get_complementary_color
from chromaspec.converters import hex_to_rgb, rgb_to_hsl
from chromaspec.utils.constants import ColorConstants, PDFLayout

logger = logging.getLogger(__name__)


def draw_pie_chart(
    pdf,
    color_categories: Dict[str, List[Tuple[str, float]]],
    center_x: float,
    center_y: float,
    radius: float,
) -> None:
    """
    Draw a pie chart showing RGB distribution.

    Args:
        pdf: The canvas object.
        color_categories: Dictionary with color categories.
        center_x: X coordinate of pie center.
        center_y: Y coordinate of pie center.
        radius: Radius of the pie chart.
    """
    total_red = len(color_categories["red"])
    total_green = len(color_categories["green"])
    total_blue = len(color_categories["blue"])
    total = total_red + total_green + total_blue

    if total == 0:
        logger.warning("No colors to display in pie chart")
        return

    colors_data = [
        (ColorConstants.GRAY_DARK, total_red / total * 360, "Red"),
        (ColorConstants.GRAY_MEDIUM, total_green / total * 360, "Green"),
        (ColorConstants.GRAY_LIGHT, total_blue / total * 360, "Blue"),
    ]

    start_angle = 90
    for color, angle, _ in colors_data:
        if angle > 0:
            pdf.setFillColorRGB(*color)
            pdf.setStrokeColorRGB(*color)
            pdf.wedge(
                center_x - radius,
                center_y - radius,
                center_x + radius,
                center_y + radius,
                start_angle,
                angle,
                fill=1,
                stroke=0,
            )
            start_angle += angle


def draw_bar_chart(
    pdf,
    color_categories: Dict[str, List[Tuple[str, float]]],
    x: float,
    y: float,
    max_width: float,
) -> float:
    """
    Draw horizontal bar chart showing color distribution.

    Args:
        pdf: The canvas object.
        color_categories: Dictionary with color categories.
        x: Starting X position.
        y: Starting Y position.
        max_width: Maximum bar width.

    Returns:
        Updated Y position after the chart.
    """
    total_red = len(color_categories["red"])
    total_green = len(color_categories["green"])
    total_blue = len(color_categories["blue"])
    total = max(total_red, total_green, total_blue, 1)

    bars = [
        (ColorConstants.GRAY_DARK, total_red, "Red"),
        (ColorConstants.GRAY_MEDIUM, total_green, "Green"),
        (ColorConstants.GRAY_LIGHT, total_blue, "Blue"),
    ]

    pdf.setFont(PDFLayout.PRIMARY_FONT, 10)
    for color, count, label in bars:
        bar_width = (count / total) * max_width if total > 0 else 0

        pdf.setFillColor("black")
        pdf.drawString(x, y - PDFLayout.BAR_HEIGHT / 2 - 3, f"{label}:")

        if bar_width > 0:
            pdf.setFillColorRGB(*color)
            pdf.rect(
                x + 0.6 * PDFLayout.MARGIN,
                y - PDFLayout.BAR_HEIGHT,
                bar_width,
                PDFLayout.BAR_HEIGHT,
                fill=1,
                stroke=0,
            )

        pdf.setFillColor("black")
        pdf.drawString(
            x + 0.6 * PDFLayout.MARGIN + bar_width + 0.1 * PDFLayout.MARGIN,
            y - PDFLayout.BAR_HEIGHT / 2 - 3,
            str(count),
        )

        y -= PDFLayout.BAR_HEIGHT + 0.15 * PDFLayout.MARGIN

    return y


def draw_statistics_page(
    pdf,
    color_categories: Dict[str, List[Tuple[str, float]]],
    width: float,
    height: float,
    page_number: int,
) -> None:
    """
    Draw a statistics and visualization page.

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
    pdf.drawString(PDFLayout.MARGIN, y, "Color Distribution")
    y -= 0.5 * PDFLayout.MARGIN

    pie_center_x = PDFLayout.MARGIN + PDFLayout.PIE_RADIUS + 0.3 * PDFLayout.MARGIN
    pie_center_y = y - PDFLayout.PIE_RADIUS
    draw_pie_chart(
        pdf, color_categories, pie_center_x, pie_center_y, PDFLayout.PIE_RADIUS
    )

    legend_x = pie_center_x + PDFLayout.PIE_RADIUS + 0.5 * PDFLayout.MARGIN
    legend_y = y - 0.3 * PDFLayout.MARGIN

    total_red = len(color_categories["red"])
    total_green = len(color_categories["green"])
    total_blue = len(color_categories["blue"])
    total = total_red + total_green + total_blue

    legend_items = [
        (
            ColorConstants.GRAY_DARK,
            "Red",
            total_red,
            total_red / total * 100 if total > 0 else 0,
        ),
        (
            ColorConstants.GRAY_MEDIUM,
            "Green",
            total_green,
            total_green / total * 100 if total > 0 else 0,
        ),
        (
            ColorConstants.GRAY_LIGHT,
            "Blue",
            total_blue,
            total_blue / total * 100 if total > 0 else 0,
        ),
    ]

    pdf.setFont(PDFLayout.PRIMARY_FONT, 10)
    for color, label, count, pct in legend_items:
        pdf.setFillColorRGB(*color)
        pdf.rect(
            legend_x,
            legend_y - 0.12 * PDFLayout.MARGIN,
            0.15 * PDFLayout.MARGIN,
            0.15 * PDFLayout.MARGIN,
            fill=1,
            stroke=0,
        )
        pdf.setFillColor("black")
        pdf.drawString(
            legend_x + 0.25 * PDFLayout.MARGIN,
            legend_y - 0.12 * PDFLayout.MARGIN,
            f"{label}: {count} ({pct:.1f}%)",
        )
        legend_y -= 0.35 * PDFLayout.MARGIN

    y = pie_center_y - PDFLayout.PIE_RADIUS - 0.6 * PDFLayout.MARGIN

    pdf.setFont(PDFLayout.PRIMARY_FONT_BOLD, 14)
    pdf.drawString(PDFLayout.MARGIN, y, "Color Count Comparison")
    y -= 0.4 * PDFLayout.MARGIN

    y = draw_bar_chart(
        pdf, color_categories, PDFLayout.MARGIN, y, PDFLayout.BAR_MAX_WIDTH
    )


def draw_top_colors_page(
    pdf,
    color_categories: Dict[str, List[Tuple[str, float]]],
    width: float,
    height: float,
    page_number: int,
) -> None:
    """
    Draw a page with top colors and their harmonies.

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
    pdf.drawString(PDFLayout.MARGIN, y, "Top Colors & Harmonies")
    y -= 0.5 * PDFLayout.MARGIN

    all_colors = []
    for section_key in ["red", "green", "blue"]:
        all_colors.extend(color_categories[section_key])

    top_colors = sorted(all_colors, key=lambda x: x[1], reverse=True)[:5]

    for i, (color, freq) in enumerate(top_colors, 1):
        pdf.setFont(PDFLayout.PRIMARY_FONT_BOLD, 12)
        pdf.setFillColor("black")
        pdf.drawString(PDFLayout.MARGIN, y, f"#{i} Most Used Color ({freq:.2f}%)")
        y -= 0.35 * PDFLayout.MARGIN

        # Two stacked rectangles (no gap)
        box_width = 0.4 * PDFLayout.MARGIN
        rect_height = 0.2 * PDFLayout.MARGIN

        # Top rectangle - aligned with HEX
        pdf.setFillColor(color)
        pdf.rect(
            PDFLayout.MARGIN, y - rect_height, box_width, rect_height, fill=1, stroke=0
        )

        # Bottom rectangle - aligned with HSL (no gap)
        pdf.setFillColor(color)
        pdf.rect(
            PDFLayout.MARGIN,
            y - 2 * rect_height,
            box_width,
            rect_height,
            fill=1,
            stroke=0,
        )

        rgb = hex_to_rgb(color)
        hsl = rgb_to_hsl(rgb)

        pdf.setFont(PDFLayout.PRIMARY_FONT, 9)
        pdf.setFillColor("black")
        info_x = PDFLayout.MARGIN + box_width + 0.15 * PDFLayout.MARGIN

        # Top row: HEX and Complementary
        hex_y = y - rect_height / 2 - 3
        pdf.drawString(info_x, hex_y, f"HEX: {color.upper()}")

        comp_color = get_complementary_color(color)
        pdf.drawString(info_x + 2.6 * PDFLayout.MARGIN, hex_y, "Complementary:")
        pdf.setFillColor(comp_color)
        pdf.rect(
            info_x + 3.9 * PDFLayout.MARGIN,
            y - rect_height,
            0.25 * PDFLayout.MARGIN,
            rect_height,
            fill=1,
            stroke=0,
        )

        # Bottom row: HSL and Analogous
        hsl_y = y - rect_height - rect_height / 2 - 3
        pdf.setFillColor("black")
        pdf.drawString(info_x, hsl_y, f"HSL: {hsl[0]}°, {hsl[1]}%, {hsl[2]}%")

        analog1, analog2 = get_analogous_colors(color)
        pdf.drawString(info_x + 2.6 * PDFLayout.MARGIN, hsl_y, "Analogous:")
        pdf.setFillColor(analog1)
        pdf.rect(
            info_x + 3.9 * PDFLayout.MARGIN,
            y - 2 * rect_height,
            0.25 * PDFLayout.MARGIN,
            rect_height,
            fill=1,
            stroke=0,
        )
        pdf.setFillColor(analog2)
        pdf.rect(
            info_x + 4.15 * PDFLayout.MARGIN,
            y - 2 * rect_height,
            0.25 * PDFLayout.MARGIN,
            rect_height,
            fill=1,
            stroke=0,
        )

        y -= 2 * rect_height + 0.6 * PDFLayout.MARGIN
