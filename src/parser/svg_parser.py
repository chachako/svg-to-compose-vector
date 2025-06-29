import xml.etree.ElementTree as ET
import re
from typing import List, Optional, Dict, Any, Union
from pathlib import Path
from ..ir.image_vector import IrImageVector
from ..ir.vector_node import IrVectorNode, IrVectorPath, IrVectorGroup
from ..ir.color import IrColor
from ..ir.gradient import IrFill, IrColorFill
from ..ir.path_node import IrPathNode
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
    self.clip_paths: Dict[str, List[IrPathNode]] = {}
    self.warnings: List[str] = []


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

    # Print warnings if any unsupported elements were encountered
    if context.warnings:
      print("⚠️  SVG Conversion Warnings:")
      for warning in context.warnings:
        print(f"   • {warning}")
      print()

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
    elif tag == "rect":
      return self._parse_rect_element(element, context)
    elif tag == "circle":
      return self._parse_circle_element(element, context)
    elif tag == "ellipse":
      return self._parse_ellipse_element(element, context)
    elif tag == "line":
      return self._parse_line_element(element, context)
    elif tag == "polygon":
      return self._parse_polygon_element(element, context)
    elif tag == "polyline":
      return self._parse_polyline_element(element, context)
    elif tag == "clipPath":
      return self._parse_clippath_element(element, context)
    elif tag in ["style", "title", "desc", "metadata"]:
      # Skip these elements for now
      return []
    elif tag in ["text", "tspan", "textPath"]:
      # Text elements are not supported by Compose ImageVector
      context.warnings.append(f"Text element '<{tag}>' is not supported by Compose ImageVector - text will be ignored")
      return []
    elif tag in ["marker", "use", "symbol", "switch"]:
      # Advanced SVG features not supported by Compose ImageVector
      context.warnings.append(f"Advanced SVG element '<{tag}>' is not supported by Compose ImageVector - element will be ignored")
      return []
    elif tag in ["filter", "feTurbulence", "feGaussianBlur", "feOffset", "feFlood", "feComposite"]:
      # Filter effects not supported by Compose ImageVector
      context.warnings.append(f"Filter element '<{tag}>' is not supported by Compose ImageVector - filters will be ignored")
      return []
    elif tag in ["animate", "animateTransform", "animateMotion", "set"]:
      # Animation elements not supported by Compose ImageVector
      context.warnings.append(f"Animation element '<{tag}>' is not supported by Compose ImageVector - animations will be ignored")
      return []
    elif tag in ["image", "foreignObject"]:
      # Embedded content not supported by Compose ImageVector
      context.warnings.append(f"Embedded content element '<{tag}>' is not supported by Compose ImageVector - content will be ignored")
      return []
    else:
      # For other unknown elements, check if they're unsupported first
      if tag not in ["svg", "g", "defs", "clipPath"]:  # Known container elements
        context.warnings.append(f"Unknown SVG element '<{tag}>' encountered - element will be ignored")
      
      # Try to recursively parse children
      nodes = []
      for child in element:
        child_nodes = self._parse_element(child, context)
        nodes.extend(child_nodes)
      return nodes

  def _parse_path_element(
    self, path_element: ET.Element, context: ParseContext
  ) -> List[IrVectorNode]:
    """Parse a path element."""
    # Check for unsupported child elements first
    self._check_unsupported_children(path_element, context)
    
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
    stroke_color = self._parse_stroke(path_element, context)
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
    """Parse a group element with support for transforms and clip paths."""
    # Parse group attributes
    group_name = group_element.get("id", "group")
    transform_str = group_element.get("transform", "")
    clip_path_str = self._get_attribute_or_style(group_element, "clip-path")
    
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
    
    # Parse clip path if present
    clip_path_data = []
    has_clip_path_attribute = clip_path_str and clip_path_str.startswith("url(#") and clip_path_str.endswith(")")
    if has_clip_path_attribute:
      clip_path_id = clip_path_str[5:-1]  # Remove "url(#" and ")"
      if clip_path_id in context.clip_paths:
        clip_path_data = context.clip_paths[clip_path_id]
    
    # If no transform, clip path attribute, and only one child, we can flatten to avoid unnecessary nesting
    # Note: we check has_clip_path_attribute rather than clip_path_data to preserve groups 
    # that reference clipPaths even if the clipPath is empty
    if not transform_params and not has_clip_path_attribute and len(children) == 1:
      return children
    
    # Create group node
    group = IrVectorGroup(
      children=children,
      name=group_name,
      clip_path_data=clip_path_data,
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

  def _parse_stroke(self, element: ET.Element, context: ParseContext) -> Optional[Union[IrColor, IrFill]]:
    """Parse stroke attribute, supporting colors and gradients."""
    stroke_str = self._get_attribute_or_style(element, "stroke")

    if not stroke_str or stroke_str == "none":
      return None

    # Check for gradient reference (url(#gradientId))
    if stroke_str.startswith("url(#") and stroke_str.endswith(")"):
      gradient_id = stroke_str[5:-1]  # Remove "url(#" and ")"
      if gradient_id in context.gradients:
        return context.gradients[gradient_id]
      else:
        # Gradient not found, fallback to black
        return IrColor(argb=0xFF000000)

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

  def _parse_rect_element(self, rect_element: ET.Element, context: ParseContext) -> List[IrVectorNode]:
    """Parse rect element and convert to path."""
    # Parse rect attributes
    x = float(rect_element.get("x", "0"))
    y = float(rect_element.get("y", "0"))
    width = float(rect_element.get("width", "0"))
    height = float(rect_element.get("height", "0"))
    rx = float(rect_element.get("rx", "0"))
    ry = float(rect_element.get("ry", "0"))

    # Handle invalid dimensions
    if width <= 0 or height <= 0:
      return []

    # Use symmetrical corner radius if only one is specified
    if rx > 0 and ry == 0:
      ry = rx
    elif ry > 0 and rx == 0:
      rx = ry

    # Clamp corner radius to half of smaller dimension
    max_radius = min(width, height) / 2
    rx = min(rx, max_radius)
    ry = min(ry, max_radius)

    # Generate path data for rectangle
    if rx == 0 and ry == 0:
      # Simple rectangle without rounded corners
      path_data = f"M{x},{y} L{x + width},{y} L{x + width},{y + height} L{x},{y + height} Z"
    else:
      # Rounded rectangle with arc commands
      path_data = (
        f"M{x + rx},{y} "
        f"L{x + width - rx},{y} "
        f"A{rx},{ry} 0 0 1 {x + width},{y + ry} "
        f"L{x + width},{y + height - ry} "
        f"A{rx},{ry} 0 0 1 {x + width - rx},{y + height} "
        f"L{x + rx},{y + height} "
        f"A{rx},{ry} 0 0 1 {x},{y + height - ry} "
        f"L{x},{y + ry} "
        f"A{rx},{ry} 0 0 1 {x + rx},{y} Z"
      )

    return self._convert_path_data_to_vector_path(path_data, rect_element, context)

  def _parse_circle_element(self, circle_element: ET.Element, context: ParseContext) -> List[IrVectorNode]:
    """Parse circle element and convert to path."""
    cx = float(circle_element.get("cx", "0"))
    cy = float(circle_element.get("cy", "0"))
    r = float(circle_element.get("r", "0"))

    if r <= 0:
      return []

    # Generate path data for circle using four arc commands
    path_data = (
      f"M{cx - r},{cy} "
      f"A{r},{r} 0 0 1 {cx},{cy - r} "
      f"A{r},{r} 0 0 1 {cx + r},{cy} "
      f"A{r},{r} 0 0 1 {cx},{cy + r} "
      f"A{r},{r} 0 0 1 {cx - r},{cy} Z"
    )

    return self._convert_path_data_to_vector_path(path_data, circle_element, context)

  def _parse_ellipse_element(self, ellipse_element: ET.Element, context: ParseContext) -> List[IrVectorNode]:
    """Parse ellipse element and convert to path."""
    cx = float(ellipse_element.get("cx", "0"))
    cy = float(ellipse_element.get("cy", "0"))
    rx = float(ellipse_element.get("rx", "0"))
    ry = float(ellipse_element.get("ry", "0"))

    if rx <= 0 or ry <= 0:
      return []

    # Generate path data for ellipse using four arc commands
    path_data = (
      f"M{cx - rx},{cy} "
      f"A{rx},{ry} 0 0 1 {cx},{cy - ry} "
      f"A{rx},{ry} 0 0 1 {cx + rx},{cy} "
      f"A{rx},{ry} 0 0 1 {cx},{cy + ry} "
      f"A{rx},{ry} 0 0 1 {cx - rx},{cy} Z"
    )

    return self._convert_path_data_to_vector_path(path_data, ellipse_element, context)

  def _parse_line_element(self, line_element: ET.Element, context: ParseContext) -> List[IrVectorNode]:
    """Parse line element and convert to path."""
    x1 = float(line_element.get("x1", "0"))
    y1 = float(line_element.get("y1", "0"))
    x2 = float(line_element.get("x2", "0"))
    y2 = float(line_element.get("y2", "0"))

    # Generate path data for line
    path_data = f"M{x1},{y1} L{x2},{y2}"

    return self._convert_path_data_to_vector_path(path_data, line_element, context)

  def _parse_polygon_element(self, polygon_element: ET.Element, context: ParseContext) -> List[IrVectorNode]:
    """Parse polygon element and convert to path."""
    points_str = polygon_element.get("points", "")
    if not points_str:
      return []

    points = self._parse_points_string(points_str)
    if len(points) < 3:  # Polygon needs at least 3 points
      return []

    # Generate path data for polygon
    path_data = f"M{points[0][0]},{points[0][1]}"
    for x, y in points[1:]:
      path_data += f" L{x},{y}"
    path_data += " Z"  # Close the polygon

    return self._convert_path_data_to_vector_path(path_data, polygon_element, context)

  def _parse_polyline_element(self, polyline_element: ET.Element, context: ParseContext) -> List[IrVectorNode]:
    """Parse polyline element and convert to path."""
    points_str = polyline_element.get("points", "")
    if not points_str:
      return []

    points = self._parse_points_string(points_str)
    if len(points) < 2:  # Polyline needs at least 2 points
      return []

    # Generate path data for polyline (no Z command - open path)
    path_data = f"M{points[0][0]},{points[0][1]}"
    for x, y in points[1:]:
      path_data += f" L{x},{y}"

    return self._convert_path_data_to_vector_path(path_data, polyline_element, context)

  def _parse_points_string(self, points_str: str) -> List[tuple[float, float]]:
    """Parse points string into list of coordinate pairs."""
    # Clean up the points string - handle various separators
    points_str = points_str.strip()
    
    # Replace commas and multiple spaces with single spaces
    points_str = re.sub(r'[,\s]+', ' ', points_str)
    
    # Split into individual numbers
    coords = points_str.split()
    
    # Group into coordinate pairs
    points = []
    for i in range(0, len(coords) - 1, 2):
      try:
        x = float(coords[i])
        y = float(coords[i + 1])
        points.append((x, y))
      except (ValueError, IndexError):
        # Skip invalid coordinate pairs
        continue
    
    return points

  def _convert_path_data_to_vector_path(self, path_data: str, element: ET.Element, context: ParseContext) -> List[IrVectorNode]:
    """Convert path data string to IrVectorPath using existing path parser."""
    # First check for any unsupported child elements
    self._check_unsupported_children(element, context)
    
    try:
      path_nodes = self.path_parser.parse_path_data(path_data)
    except Exception as e:
      print(f"Warning: Failed to parse generated path data '{path_data}': {e}")
      return []

    if not path_nodes:
      return []

    # Parse styles using existing methods
    fill_color = self._parse_fill(element, context)
    stroke_color = self._parse_stroke(element, context)
    stroke_width = self._parse_stroke_width(element)
    stroke_opacity = self._parse_stroke_opacity(element)
    fill_opacity = self._parse_fill_opacity(element)
    stroke_linecap = self._parse_stroke_linecap(element)
    stroke_linejoin = self._parse_stroke_linejoin(element)
    name = element.get("id", element.tag.split("}")[-1])

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

  def _check_unsupported_children(self, element: ET.Element, context: ParseContext) -> None:
    """Check for unsupported child elements and add warnings."""
    for child in element:
      tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
      
      if tag in ["text", "tspan", "textPath"]:
        context.warnings.append(f"Text element '<{tag}>' is not supported by Compose ImageVector - text will be ignored")
      elif tag in ["marker", "use", "symbol", "switch"]:
        context.warnings.append(f"Advanced SVG element '<{tag}>' is not supported by Compose ImageVector - element will be ignored")
      elif tag in ["filter", "feTurbulence", "feGaussianBlur", "feOffset", "feFlood", "feComposite"]:
        context.warnings.append(f"Filter element '<{tag}>' is not supported by Compose ImageVector - filters will be ignored")
      elif tag in ["animate", "animateTransform", "animateMotion", "set"]:
        context.warnings.append(f"Animation element '<{tag}>' is not supported by Compose ImageVector - animations will be ignored")
      elif tag in ["image", "foreignObject"]:
        context.warnings.append(f"Embedded content element '<{tag}>' is not supported by Compose ImageVector - content will be ignored")
      
      # Recursively check nested children
      self._check_unsupported_children(child, context)

  def _parse_clippath_element(self, clippath_element: ET.Element, context: ParseContext) -> List[IrVectorNode]:
    """Parse clipPath element and store path data in context."""
    clippath_id = clippath_element.get("id")
    if not clippath_id:
      return []

    # Collect all path data from children
    clip_path_nodes = []
    
    for child in clippath_element:
      # Parse child elements to get their path data
      child_nodes = self._parse_element(child, context)
      
      # Extract path data from IrVectorPath nodes
      for node in child_nodes:
        if isinstance(node, IrVectorPath):
          clip_path_nodes.extend(node.paths)
        elif isinstance(node, IrVectorGroup):
          # Recursively extract paths from groups
          self._extract_paths_from_group(node, clip_path_nodes)
    
    # Store the clip path data in context
    context.clip_paths[clippath_id] = clip_path_nodes
    
    # clipPath elements don't generate visible content themselves
    return []

  def _extract_paths_from_group(self, group: IrVectorGroup, path_list: List[IrPathNode]) -> None:
    """Recursively extract path nodes from a group and its children."""
    for child in group.children:
      if isinstance(child, IrVectorPath):
        path_list.extend(child.paths)
      elif isinstance(child, IrVectorGroup):
        self._extract_paths_from_group(child, path_list)
