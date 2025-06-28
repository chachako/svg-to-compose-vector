import xml.etree.ElementTree as ET
from typing import List, Optional, Dict, Any, Union
from pathlib import Path
from ..ir.image_vector import IrImageVector
from ..ir.vector_node import IrVectorNode, IrVectorPath
from ..ir.color import IrColor
from .path_parser import PathParser


class ParseContext:
  """Context for tracking parsing state."""
  
  def __init__(self):
    self.defs_cache: Dict[str, Any] = {}
    self.parent_styles: Dict[str, str] = {}
    self.transform_stack: List[str] = []


class SvgParser:
  """Parser for SVG XML documents."""
  
  def __init__(self):
    self.path_parser = PathParser()
    
  def parse_svg(self, input_source: Union[str, Path]) -> IrImageVector:
    """Parse SVG from file path (Path) or SVG content (str)."""
    if isinstance(input_source, Path):
      # It's a Path object - read file
      if not input_source.exists():
        raise FileNotFoundError(f"SVG file not found: {input_source}")
      svg_content = input_source.read_text(encoding='utf-8')
    else:
      # It's SVG content string
      svg_content = input_source
    
    # Parse XML
    try:
      root = ET.fromstring(svg_content)
    except ET.ParseError as e:
      raise ValueError(f"Invalid SVG XML: {e}")
    
    # Verify it's an SVG
    if not (root.tag == 'svg' or root.tag.endswith('}svg')):
      raise ValueError("Root element is not an SVG")
    
    return self._parse_svg_element(root)
  
  def _parse_svg_element(self, svg_element: ET.Element) -> IrImageVector:
    """Parse the root SVG element."""
    context = ParseContext()
    
    # Extract SVG attributes - use id from first path if available
    # Example: <svg><path id="star" d="..."/></svg> -> name becomes "star"
    name = svg_element.get('id')
    if not name:
      # Try to get name from first path element
      for child in svg_element:
        if (child.tag == 'path' or child.tag.endswith('}path')) and child.get('id'):
          name = child.get('id')
          break
      if not name:
        name = 'UnnamedIcon'
    
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
      nodes=nodes
    )
  
  def _parse_dimensions(self, svg_element: ET.Element) -> tuple[float, float]:
    """Parse width and height attributes."""
    width_str = svg_element.get('width', '24')
    height_str = svg_element.get('height', '24')
    
    # Simple parsing - strip units and convert to float
    width = self._parse_length(width_str)
    height = self._parse_length(height_str)
    
    return width, height
  
  def _parse_viewport(self, svg_element: ET.Element, default_width: float, default_height: float) -> tuple[float, float]:
    """Parse viewBox or use default dimensions."""
    viewbox = svg_element.get('viewBox')
    
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
    for unit in ['px', 'pt', 'pc', 'mm', 'cm', 'in', 'dp', 'dip', 'sp', 'em', 'rem']:
      if length_str.endswith(unit):
        length_str = length_str[:-len(unit)]
        break
    
    # Handle percentage (convert to default)
    if length_str.endswith('%'):
      return 24.0
    
    try:
      return float(length_str)
    except ValueError:
      return 24.0
  
  def _parse_element(self, element: ET.Element, context: ParseContext) -> List[IrVectorNode]:
    """Parse an SVG element and return vector nodes."""
    # Get tag name without namespace
    tag = element.tag.split('}')[-1] if '}' in element.tag else element.tag
    
    if tag == 'path':
      return self._parse_path_element(element, context)
    elif tag == 'g':
      return self._parse_group_element(element, context)
    elif tag in ['defs', 'style', 'title', 'desc', 'metadata']:
      # Skip these elements for now
      return []
    else:
      # For unsupported elements, try to recursively parse children
      nodes = []
      for child in element:
        child_nodes = self._parse_element(child, context)
        nodes.extend(child_nodes)
      return nodes
  
  def _parse_path_element(self, path_element: ET.Element, context: ParseContext) -> List[IrVectorNode]:
    """Parse a path element."""
    path_data = path_element.get('d')
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
    fill_color = self._parse_fill(path_element)
    name = path_element.get('id', 'path')
    
    vector_path = IrVectorPath(
      paths=path_nodes,
      name=name,
      fill=fill_color
    )
    
    return [vector_path]
  
  def _parse_group_element(self, group_element: ET.Element, context: ParseContext) -> List[IrVectorNode]:
    """Parse a group element."""
    # For now, just flatten groups and parse children
    nodes = []
    for child in group_element:
      child_nodes = self._parse_element(child, context)
      nodes.extend(child_nodes)
    return nodes
  
  def _parse_fill(self, element: ET.Element) -> Optional[IrColor]:
    """Parse fill attribute."""
    fill_str = element.get('fill')
    
    if fill_str == 'none':
      return None
    
    # Default to black when no fill attribute specified (SVG spec default)
    if not fill_str:
      fill_str = 'black'
    
    # Simple color parsing for now
    if fill_str.startswith('#'):
      try:
        return IrColor.from_hex(fill_str)
      except ValueError:
        pass
    
    # Named colors
    named_colors = {
      'black': '#000000',
      'white': '#ffffff', 
      'red': '#ff0000',
      'green': '#00ff00',
      'blue': '#0000ff',
      'currentColor': '#000000'
    }
    
    if fill_str in named_colors:
      return IrColor.from_hex(named_colors[fill_str])
    
    # Default to black if we can't parse
    return IrColor.from_hex('#000000')