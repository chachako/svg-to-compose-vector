import xml.etree.ElementTree as ET
from typing import List, Optional, Dict, Any, Union
from pathlib import Path
from ..ir.image_vector import IrImageVector
from ..ir.vector_node import IrVectorNode, IrVectorPath, IrVectorGroup
from ..ir.color import IrColor
from ..ir.gradient import IrFill, IrColorFill
from .path_parser import PathParser
from .transform_parser import TransformParser
from .gradient_parser import GradientParser


class ParseContext:
  """Context for tracking parsing state."""

  def __init__(self):
    self.defs_cache: Dict[str, Any] = {}
    self.parent_styles: Dict[str, str] = {}
    self.transform_stack: List[str] = []
    self.gradients: Dict[str, IrFill] = {}


class SvgParser:
  """Parser for SVG XML documents."""

  def __init__(self):
    self.path_parser = PathParser()
    self.transform_parser = TransformParser()
    self.gradient_parser = GradientParser()

  def parse_svg(self, input_source: Union[str, Path]) -> IrImageVector:
    """Parse SVG from file path (Path) or SVG content (str)."""
    if isinstance(input_source, Path):
      # It's a Path object - read file
      if not input_source.exists():
        raise FileNotFoundError(f"SVG file not found: {input_source}")
      svg_content = input_source.read_text(encoding="utf-8")
    else:
      # It's SVG content string
      svg_content = input_source

    # Parse XML
    try:
      root = ET.fromstring(svg_content)
    except ET.ParseError as e:
      raise ValueError(f"Invalid SVG XML: {e}")

    # Verify it's an SVG
    if not (root.tag == "svg" or root.tag.endswith("}svg")):
      raise ValueError("Root element is not an SVG")

    return self._parse_svg_element(root)

  def _parse_svg_element(self, svg_element: ET.Element) -> IrImageVector:
    """Parse the root SVG element."""
    context = ParseContext()

    # Extract SVG attributes - use id from first path if available
    # Example: <svg><path id="star" d="..."/></svg> -> name becomes "star"
    name = svg_element.get("id")
    if not name:
      # Try to get name from first path element
      for child in svg_element:
        if (child.tag == "path" or child.tag.endswith("}path")) and child.get("id"):
          name = child.get("id")
          break
      if not name:
        name = "UnnamedIcon"

    # Parse dimensions and viewport
    width, height = self._parse_dimensions(svg_element)
    viewport_width, viewport_height = self._parse_viewport(svg_element, width, height)

    # Parse child elements
    nodes = []
    for child in svg_element:
      child_nodes = self._parse_element(child, context)
      nodes.extend(child_nodes)

    return IrImageVector(
      name=name,
      default_width=width,
      default_height=height,
      viewport_width=viewport_width,
      viewport_height=viewport_height,
      nodes=nodes,
    )

  def _parse_dimensions(self, svg_element: ET.Element) -> tuple[float, float]:
    """Parse width and height attributes."""
    width_str = svg_element.get("width", "24")
    height_str = svg_element.get("height", "24")

    # Simple parsing - strip units and convert to float
    width = self._parse_length(width_str)
    height = self._parse_length(height_str)

    return width, height

  def _parse_viewport(
    self, svg_element: ET.Element, default_width: float, default_height: float
  ) -> tuple[float, float]:
    """Parse viewBox or use default dimensions."""
    viewbox = svg_element.get("viewBox")

    if viewbox:
      # viewBox format: "min-x min-y width height"
      try:
        parts = viewbox.strip().split()
        if len(parts) == 4:
          # We only care about width and height (parts 2 and 3)
          viewport_width = float(parts[2])
          viewport_height = float(parts[3])
          return viewport_width, viewport_height
      except (ValueError, IndexError):
        pass

    # Fallback to default dimensions
    return default_width, default_height

  def _parse_length(self, length_str: str) -> float:
    """Parse length value, stripping common units."""
    if not length_str:
      return 24.0

    # Remove common units
    length_str = length_str.strip()
    for unit in ["px", "pt", "pc", "mm", "cm", "in", "dp", "dip", "sp", "em", "rem"]:
      if length_str.endswith(unit):
        length_str = length_str[: -len(unit)]
        break

    # Handle percentage (convert to default)
    if length_str.endswith("%"):
      return 24.0

    try:
      return float(length_str)
    except ValueError:
      return 24.0

  def _parse_element(self, element: ET.Element, context: ParseContext) -> List[IrVectorNode]:
    """Parse an SVG element and return vector nodes."""
    # Get tag name without namespace
    tag = element.tag.split("}")[-1] if "}" in element.tag else element.tag

    if tag == "path":
      return self._parse_path_element(element, context)
    elif tag == "g":
      return self._parse_group_element(element, context)
    elif tag == "defs":
      return self._parse_defs_element(element, context)
    elif tag == "linearGradient":
      self._parse_linear_gradient(element, context)
      return []
    elif tag == "radialGradient":
      self._parse_radial_gradient(element, context)
      return []
    elif tag in ["style", "title", "desc", "metadata"]:
      # Skip these elements for now
      return []
    else:
      # For unsupported elements, try to recursively parse children
      nodes = []
      for child in element:
        child_nodes = self._parse_element(child, context)
        nodes.extend(child_nodes)
      return nodes

  def _parse_path_element(
    self, path_element: ET.Element, context: ParseContext
  ) -> List[IrVectorNode]:
    """Parse a path element."""
    path_data = path_element.get("d")
    if not path_data:
      return []

    try:
      path_nodes = self.path_parser.parse_path_data(path_data)
    except Exception as e:
      # If path parsing fails, skip this path
      print(f"Warning: Failed to parse path data '{path_data}': {e}")
      return []

    if not path_nodes:
      return []

    # Parse styles
    fill_color = self._parse_fill(path_element, context)
    stroke_color = self._parse_stroke(path_element)
    stroke_width = self._parse_stroke_width(path_element)
    stroke_opacity = self._parse_stroke_opacity(path_element)
    fill_opacity = self._parse_fill_opacity(path_element)
    stroke_linecap = self._parse_stroke_linecap(path_element)
    stroke_linejoin = self._parse_stroke_linejoin(path_element)
    name = path_element.get("id", "path")

    vector_path = IrVectorPath(
      paths=path_nodes,
      name=name,
      fill=fill_color,
      stroke=stroke_color,
      stroke_line_width=stroke_width,
      stroke_alpha=stroke_opacity,
      fill_alpha=fill_opacity,
      stroke_line_cap=stroke_linecap,
      stroke_line_join=stroke_linejoin,
    )

    return [vector_path]

  def _parse_group_element(
    self, group_element: ET.Element, context: ParseContext
  ) -> List[IrVectorNode]:
    """Parse a group element with support for transforms."""
    # Parse group attributes
    group_name = group_element.get("id", "group")
    transform_str = group_element.get("transform", "")
    
    # Parse child elements
    children = []
    for child in group_element:
      child_nodes = self._parse_element(child, context)
      children.extend(child_nodes)
    
    # If no children, return empty list
    if not children:
      return []
    
    # Parse transform if present
    transform_params = {}
    if transform_str:
      transform_params = self.transform_parser.parse_transform_to_group_params(transform_str)
    
    # If no transform and only one child, we can flatten to avoid unnecessary nesting
    if not transform_params and len(children) == 1:
      return children
    
    # Create group node
    group = IrVectorGroup(
      children=children,
      name=group_name,
      **transform_params
    )
    
    return [group]

  def _parse_fill(self, element: ET.Element, context: ParseContext) -> Optional[IrFill]:
    """Parse fill attribute, supporting colors and gradients."""
    fill_str = self._get_attribute_or_style(element, "fill")

    if fill_str == "none":
      return None

    # Check for gradient reference (url(#gradientId))
    if fill_str.startswith("url(#") and fill_str.endswith(")"):
      gradient_id = fill_str[5:-1]  # Remove "url(#" and ")"
      if gradient_id in context.gradients:
        return context.gradients[gradient_id]
      else:
        # Gradient not found, fallback to black
        return IrColorFill(color=IrColor(argb=0xFF000000))

    # Default to black when no fill attribute specified (SVG spec default)
    if not fill_str:
      fill_str = "black"

    # Use the comprehensive color parser
    try:
      from ..ir.color import parse_color

      color = parse_color(fill_str)
      if color is not None:
        return IrColorFill(color=color)
    except (ValueError, ImportError):
      pass

    # Fallback to black if we can't parse
    return IrColorFill(color=IrColor.from_hex("#000000"))

  def _parse_stroke(self, element: ET.Element) -> Optional[IrColor]:
    """Parse stroke attribute."""
    stroke_str = self._get_attribute_or_style(element, "stroke")

    if not stroke_str or stroke_str == "none":
      return None

    # Use same color parsing logic as fill
    if stroke_str.startswith("#"):
      try:
        return IrColor.from_hex(stroke_str)
      except ValueError:
        pass

    # Named colors
    named_colors = {
      "black": "#000000",
      "white": "#ffffff",
      "red": "#ff0000",
      "green": "#00ff00",
      "blue": "#0000ff",
      "currentColor": "#000000",
    }

    if stroke_str in named_colors:
      return IrColor.from_hex(named_colors[stroke_str])

    # Try to parse using the centralized color parser
    try:
      from ..ir.color import parse_color

      return parse_color(stroke_str)
    except (ValueError, ImportError):
      return None

  def _parse_stroke_width(self, element: ET.Element) -> float:
    """Parse stroke-width attribute."""
    width_str = self._get_attribute_or_style(element, "stroke-width") or "0"

    try:
      # Remove units and parse as float
      width = self._parse_length(width_str)
      return max(0.0, width)  # Ensure non-negative
    except (ValueError, TypeError):
      return 0.0

  def _parse_stroke_opacity(self, element: ET.Element) -> float:
    """Parse stroke-opacity attribute."""
    opacity_str = self._get_attribute_or_style(element, "stroke-opacity") or "1.0"

    try:
      opacity = float(opacity_str)
      return max(0.0, min(1.0, opacity))  # Clamp to [0, 1]
    except (ValueError, TypeError):
      return 1.0

  def _parse_fill_opacity(self, element: ET.Element) -> float:
    """Parse fill-opacity attribute."""
    opacity_str = self._get_attribute_or_style(element, "fill-opacity") or "1.0"

    try:
      opacity = float(opacity_str)
      return max(0.0, min(1.0, opacity))  # Clamp to [0, 1]
    except (ValueError, TypeError):
      return 1.0

  def _parse_stroke_linecap(self, element: ET.Element) -> str:
    """Parse stroke-linecap attribute."""
    linecap = self._get_attribute_or_style(element, "stroke-linecap") or "butt"

    # Map SVG values to Compose values
    if linecap in ["butt", "round", "square"]:
      return linecap
    return "butt"  # Default

  def _parse_stroke_linejoin(self, element: ET.Element) -> str:
    """Parse stroke-linejoin attribute."""
    linejoin = self._get_attribute_or_style(element, "stroke-linejoin") or "miter"

    # Map SVG values to Compose values
    if linejoin in ["miter", "round", "bevel"]:
      return linejoin
    return "miter"  # Default

  def _parse_style_attribute(self, element: ET.Element) -> dict[str, str]:
    """Parse CSS style attribute into property dictionary."""
    style_str = element.get("style", "")
    if not style_str:
      return {}

    properties = {}
    # Split on semicolon, then split each property on colon
    for declaration in style_str.split(";"):
      declaration = declaration.strip()
      if ":" in declaration:
        property_name, property_value = declaration.split(":", 1)
        properties[property_name.strip()] = property_value.strip()

    return properties

  def _get_attribute_or_style(
    self, element: ET.Element, attr_name: str, style_name: str = None
  ) -> str:
    """Get value from attribute or style, with style taking precedence."""
    if style_name is None:
      style_name = attr_name

    # Check style attribute first (higher precedence)
    style_props = self._parse_style_attribute(element)
    if style_name in style_props:
      return style_props[style_name]

    # Fall back to direct attribute
    return element.get(attr_name, "")

  def _parse_defs_element(self, defs_element: ET.Element, context: ParseContext) -> List[IrVectorNode]:
    """Parse defs element, which contains reusable elements like gradients."""
    # Process all children and cache them
    for child in defs_element:
      self._parse_element(child, context)
    return []

  def _parse_linear_gradient(self, element: ET.Element, context: ParseContext) -> None:
    """Parse linearGradient element and store in context."""
    gradient_id = element.get("id")
    if not gradient_id:
      return

    # Use a reasonable viewport size for gradient calculations
    viewport_width = 100.0
    viewport_height = 100.0
    
    gradient = self.gradient_parser.parse_linear_gradient(element, viewport_width, viewport_height)
    context.gradients[gradient_id] = gradient

  def _parse_radial_gradient(self, element: ET.Element, context: ParseContext) -> None:
    """Parse radialGradient element and store in context."""
    gradient_id = element.get("id")
    if not gradient_id:
      return

    # Use a reasonable viewport size for gradient calculations
    viewport_width = 100.0
    viewport_height = 100.0
    
    gradient = self.gradient_parser.parse_radial_gradient(element, viewport_width, viewport_height)
    context.gradients[gradient_id] = gradient
