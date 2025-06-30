"""Color analysis utilities for multi-color icon template support.

This module provides functionality to extract and analyze colors used in SVG icons,
enabling intelligent template selection for multi-color parameterization.
"""

import re
from dataclasses import dataclass
from pathlib import Path

from ..ir.gradient import IrColorFill, IrFill, IrLinearGradient, IrRadialGradient
from ..ir.image_vector import IrImageVector
from ..ir.vector_node import IrVectorGroup, IrVectorNode, IrVectorPath


@dataclass
class ColorAnalysisResult:
  """Result of color analysis on an SVG icon."""

  used_colors: set[str]
  is_multicolor: bool
  color_count: int


class ColorAnalyzer:
  """Analyzes colors used in SVG icons for template selection."""

  def extract_used_colors(self, ir: IrImageVector) -> set[str]:
    """Extract all colors used in the ImageVector IR.

    Args:
      ir: The ImageVector intermediate representation

    Returns:
      Set of hex color strings (e.g., {"#FF0000", "#00FF00"})
    """
    colors = set()

    for node in ir.nodes:
      colors.update(self._extract_colors_from_node(node))

    return colors

  def _extract_colors_from_node(self, node: IrVectorNode) -> set[str]:
    """Recursively extract colors from a vector node."""
    colors = set()

    if isinstance(node, IrVectorPath):
      # Extract colors from fill
      if node.fill:
        colors.update(self._extract_colors_from_fill(node.fill))

      # Extract colors from stroke
      if node.stroke:
        colors.update(self._extract_colors_from_fill(node.stroke))

    elif isinstance(node, IrVectorGroup):
      # Recursively process group children
      for child in node.children:
        colors.update(self._extract_colors_from_node(child))

    return colors

  def _extract_colors_from_fill(self, fill: IrFill) -> set[str]:
    """Extract colors from a fill object (color or gradient)."""
    colors = set()

    if isinstance(fill, IrColorFill):
      # Extract both base RGB color and full ARGB color for mapping flexibility
      colors.add(fill.color.to_hex())  # #RRGGBB
      if fill.color.alpha != 255:
        # Add full ARGB format for transparent colors: #AARRGGBB
        colors.add(f"#{fill.color.argb:08X}")

    elif isinstance(fill, IrLinearGradient | IrRadialGradient):
      for color_stop in fill.color_stops:
        colors.add(color_stop.color.to_hex())  # #RRGGBB
        if color_stop.color.alpha != 255:
          # Add full ARGB format for transparent colors: #AARRGGBB
          colors.add(f"#{color_stop.color.argb:08X}")

    return colors

  def analyze_colors(self, ir: IrImageVector) -> ColorAnalysisResult:
    """Perform comprehensive color analysis on an ImageVector.

    Args:
      ir: The ImageVector intermediate representation

    Returns:
      ColorAnalysisResult with analysis details
    """
    used_colors = self.extract_used_colors(ir)

    return ColorAnalysisResult(
      used_colors=used_colors, is_multicolor=len(used_colors) > 1, color_count=len(used_colors)
    )

  def parse_template_color_mappings(self, template_content: str) -> set[str]:
    """Parse color mappings from a Jinja2 template.

    Args:
      template_content: The template file content

    Returns:
      Set of hex color strings defined in template mappings
    """
    colors = set()

    try:
      # Look for color_mappings dictionary in template
      # Pattern matches both: "#RRGGBB": and "#AARRGGBB": formats
      color_mapping_pattern_6 = r'"(#[0-9A-Fa-f]{6})"\s*:\s*\{'
      color_mapping_pattern_8 = r'"(#[0-9A-Fa-f]{8})"\s*:\s*\{'

      # Find 6-digit hex colors (#RRGGBB)
      matches_6 = re.findall(color_mapping_pattern_6, template_content)
      colors.update(matches_6)

      # Find 8-digit hex colors (#AARRGGBB)
      matches_8 = re.findall(color_mapping_pattern_8, template_content)
      colors.update(matches_8)

    except Exception:
      # Gracefully handle template parsing errors
      pass

    return colors

  def should_use_multicolor_template(self, svg_colors: set[str], template_colors: set[str]) -> bool:
    """Determine if multicolor template should be used based on color intersection.

    Args:
      svg_colors: Colors used in the SVG
      template_colors: Colors defined in the template mappings

    Returns:
      True if intersection exists (template can handle SVG colors)
    """
    return len(svg_colors.intersection(template_colors)) > 0

  def load_template_mappings_from_file(self, template_path: Path) -> set[str]:
    """Load and parse color mappings from a template file.

    Args:
      template_path: Path to the template file

    Returns:
      Set of hex color strings from the template
    """
    if not template_path.exists():
      return set()

    try:
      template_content = template_path.read_text(encoding="utf-8")
      return self.parse_template_color_mappings(template_content)
    except Exception:
      return set()
