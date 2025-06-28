import xml.etree.ElementTree as ET
from typing import Optional, List
from ..ir.gradient import IrLinearGradient, IrRadialGradient, IrColorStop, IrFill
from ..ir.color import IrColor


class GradientParser:
  """Parser for SVG gradient elements."""

  def parse_linear_gradient(self, element: ET.Element, viewport_width: float, viewport_height: float) -> IrLinearGradient:
    """Parse linearGradient element."""
    # Parse gradient attributes
    x1 = self._parse_coordinate(element.get("x1", "0%"), viewport_width)
    y1 = self._parse_coordinate(element.get("y1", "0%"), viewport_height)
    x2 = self._parse_coordinate(element.get("x2", "100%"), viewport_width)
    y2 = self._parse_coordinate(element.get("y2", "0%"), viewport_height)
    
    gradient_units = element.get("gradientUnits", "objectBoundingBox")

    # Parse color stops
    stops = self._parse_color_stops(element)

    return IrLinearGradient(
      start_x=x1,
      start_y=y1,
      end_x=x2,
      end_y=y2,
      color_stops=stops,
      gradient_units=gradient_units
    )

  def parse_radial_gradient(self, element: ET.Element, viewport_width: float, viewport_height: float) -> IrRadialGradient:
    """Parse radialGradient element."""
    # Parse gradient attributes
    cx = self._parse_coordinate(element.get("cx", "50%"), viewport_width)
    cy = self._parse_coordinate(element.get("cy", "50%"), viewport_height)
    r = self._parse_coordinate(element.get("r", "50%"), min(viewport_width, viewport_height))
    
    # Focal point (optional)
    fx = element.get("fx")
    fy = element.get("fy")
    focal_x = self._parse_coordinate(fx, viewport_width) if fx else None
    focal_y = self._parse_coordinate(fy, viewport_height) if fy else None
    
    gradient_units = element.get("gradientUnits", "objectBoundingBox")

    # Parse color stops
    stops = self._parse_color_stops(element)

    return IrRadialGradient(
      center_x=cx,
      center_y=cy,
      radius=r,
      focal_x=focal_x,
      focal_y=focal_y,
      color_stops=stops,
      gradient_units=gradient_units
    )

  def _parse_color_stops(self, gradient_element: ET.Element) -> List[IrColorStop]:
    """Parse stop elements from gradient."""
    stops = []
    
    for stop_element in gradient_element.findall(".//stop"):
      # Parse offset
      offset_str = stop_element.get("offset", "0")
      if offset_str.endswith("%"):
        offset = float(offset_str[:-1]) / 100.0
      else:
        offset = float(offset_str)
      
      # Parse stop-color and stop-opacity
      stop_color_str = stop_element.get("stop-color", "#000000")
      stop_opacity_str = stop_element.get("stop-opacity", "1.0")
      
      # Handle style attribute which may override stop-color and stop-opacity
      style = stop_element.get("style")
      if style:
        style_dict = self._parse_style_attribute(style)
        stop_color_str = style_dict.get("stop-color", stop_color_str)
        stop_opacity_str = style_dict.get("stop-opacity", stop_opacity_str)
      
      # Parse color
      from ..ir.color import parse_color
      color = parse_color(stop_color_str)
      if color is None:
        color = IrColor.from_hex("#000000")  # Fallback to black
      opacity = float(stop_opacity_str)
      
      # Apply opacity to color alpha channel
      if opacity < 1.0:
        alpha = int((color.argb >> 24) & 0xFF)
        alpha = int(alpha * opacity)
        color = IrColor(argb=(alpha << 24) | (color.argb & 0x00FFFFFF))
      
      stops.append(IrColorStop(offset=offset, color=color, opacity=opacity))
    
    # Sort stops by offset
    stops.sort(key=lambda stop: stop.offset)
    
    return stops

  def _parse_coordinate(self, value: str, reference_dimension: float) -> float:
    """Parse coordinate value, handling percentages and units."""
    if value.endswith("%"):
      percentage = float(value[:-1]) / 100.0
      return percentage * reference_dimension
    elif value.endswith("px"):
      return float(value[:-2])
    else:
      # Assume userSpaceOnUse units
      return float(value)

  def _parse_style_attribute(self, style: str) -> dict:
    """Parse CSS style attribute into property-value pairs."""
    result = {}
    
    # Split by semicolons and process each declaration
    for declaration in style.split(";"):
      declaration = declaration.strip()
      if ":" in declaration:
        property_name, property_value = declaration.split(":", 1)
        result[property_name.strip()] = property_value.strip()
    
    return result