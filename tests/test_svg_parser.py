"""Tests for SVG document parser using standard SVG examples."""

import pytest
from src.parser.svg_parser import SvgParser
from src.ir.image_vector import IrImageVector
from src.ir.vector_node import IrVectorPath


class TestSvgParser:
  """Test SVG parser with various SVG formats."""

  def test_simple_rectangle_svg(self):
    """Test parsing a simple rectangle SVG from W3Schools examples."""
    # Based on W3Schools basic rectangle example
    rectangle_svg = """<svg width="400" height="180" xmlns="http://www.w3.org/2000/svg">
      <rect width="300" height="100" style="fill:rgb(0,0,255);stroke-width:3;stroke:rgb(0,0,0)" />
    </svg>"""

    parser = SvgParser()
    # This should not crash even if rect is not fully supported yet
    ir = parser.parse_svg(rectangle_svg)

    assert isinstance(ir, IrImageVector)
    assert ir.default_width == 400.0
    assert ir.default_height == 180.0
    assert ir.viewport_width == 400.0
    assert ir.viewport_height == 180.0
    assert ir.name == "UnnamedIcon"  # Default name when no id

  def test_simple_path_svg(self):
    """Test parsing SVG with basic path element."""
    # Simple triangle path
    triangle_svg = """<svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
      <path d="M 50 10 L 10 90 L 90 90 Z" fill="red" id="triangle"/>
    </svg>"""

    parser = SvgParser()
    ir = parser.parse_svg(triangle_svg)

    assert ir.default_width == 100.0
    assert ir.default_height == 100.0
    assert ir.viewport_width == 100.0
    assert ir.viewport_height == 100.0
    assert ir.name == "triangle"

    # Should have one path node
    assert len(ir.nodes) == 1
    assert isinstance(ir.nodes[0], IrVectorPath)

    path_node = ir.nodes[0]
    assert path_node.name == "triangle"
    assert path_node.fill is not None
    assert path_node.fill.to_compose_color() == "Color(0xFFFF0000)"  # Red

    # Should have 4 path commands: MoveTo, LineTo, LineTo, Close
    assert len(path_node.paths) == 4

  def test_hexagon_path_svg(self):
    """Test parsing more complex path with multiple LineTo commands."""
    # Hexagon shape
    hexagon_svg = """<svg width="120" height="120" viewBox="0 0 120 120">
      <path d="M 60 10 L 100 35 L 100 85 L 60 110 L 20 85 L 20 35 Z" fill="#00ff00"/>
    </svg>"""

    parser = SvgParser()
    ir = parser.parse_svg(hexagon_svg)

    assert len(ir.nodes) == 1
    path_node = ir.nodes[0]
    assert path_node.fill.to_compose_color() == "Color(0xFF00FF00)"  # Green

    # Should have 7 path commands: MoveTo + 5 LineTo + Close
    assert len(path_node.paths) == 7

  def test_svg_with_viewbox_only(self):
    """Test SVG that only has viewBox without explicit width/height."""
    viewbox_svg = """<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path d="M12,2 C13.1,2 14,2.9 14,4 C14,5.1 13.1,6 12,6 C10.9,6 10,5.1 10,4 C10,2.9 10.9,2 12,2 Z" fill="black"/>
    </svg>"""

    parser = SvgParser()
    ir = parser.parse_svg(viewbox_svg)

    # Should use default dimensions when width/height not specified
    assert ir.default_width == 24.0
    assert ir.default_height == 24.0
    assert ir.viewport_width == 24.0
    assert ir.viewport_height == 24.0

  def test_svg_with_group_element(self):
    """Test SVG with group element (now preserves groups with IDs)."""
    group_svg = """<svg width="50" height="50" viewBox="0 0 50 50">
      <g id="shapes">
        <path d="M 10 10 L 40 10 L 40 40 L 10 40 Z" fill="blue"/>
        <path d="M 15 15 L 35 15 L 35 35 L 15 35 Z" fill="red"/>
      </g>
    </svg>"""

    parser = SvgParser()
    ir = parser.parse_svg(group_svg)

    # Should have 1 group with 2 paths inside (since group has ID, it's preserved)
    assert len(ir.nodes) == 1
    from src.ir.vector_node import IrVectorGroup
    assert isinstance(ir.nodes[0], IrVectorGroup)
    group = ir.nodes[0]
    assert group.name == "shapes"
    assert len(group.children) == 2
    assert all(isinstance(child, IrVectorPath) for child in group.children)

  def test_svg_with_named_colors(self):
    """Test SVG with named colors."""
    named_colors_svg = """<svg width="60" height="20" viewBox="0 0 60 20">
      <path d="M 0 0 L 20 0 L 20 20 L 0 20 Z" fill="red"/>
      <path d="M 20 0 L 40 0 L 40 20 L 20 20 Z" fill="green"/>
      <path d="M 40 0 L 60 0 L 60 20 L 40 20 Z" fill="blue"/>
    </svg>"""

    parser = SvgParser()
    ir = parser.parse_svg(named_colors_svg)

    assert len(ir.nodes) == 3

    # Check colors
    assert ir.nodes[0].fill.to_compose_color() == "Color(0xFFFF0000)"  # red
    assert ir.nodes[1].fill.to_compose_color() == "Color(0xFF008000)"  # green (CSS standard)
    assert ir.nodes[2].fill.to_compose_color() == "Color(0xFF0000FF)"  # blue

  def test_svg_with_no_fill(self):
    """Test SVG path with no fill attribute."""
    no_fill_svg = """<svg width="30" height="30" viewBox="0 0 30 30">
      <path d="M 5 5 L 25 5 L 25 25 L 5 25 Z"/>
    </svg>"""

    parser = SvgParser()
    ir = parser.parse_svg(no_fill_svg)

    assert len(ir.nodes) == 1
    # Should default to black when no fill specified
    assert ir.nodes[0].fill.to_compose_color() == "Color(0xFF000000)"

  def test_invalid_svg_content(self):
    """Test error handling for invalid SVG content."""
    invalid_svg = "This is not XML"

    parser = SvgParser()
    with pytest.raises(ValueError, match="Invalid SVG XML"):
      parser.parse_svg(invalid_svg)

  def test_non_svg_root_element(self):
    """Test error handling when root element is not SVG."""
    non_svg = """<html><body>Not an SVG</body></html>"""

    parser = SvgParser()
    with pytest.raises(ValueError, match="Root element is not an SVG"):
      parser.parse_svg(non_svg)

  def test_empty_path_data(self):
    """Test handling of path element with empty or missing d attribute."""
    empty_path_svg = """<svg width="10" height="10">
      <path d="" fill="red"/>
      <path fill="blue"/>
    </svg>"""

    parser = SvgParser()
    ir = parser.parse_svg(empty_path_svg)

    # Should skip empty paths
    assert len(ir.nodes) == 0


def test_svg_parser_integration():
  """Integration test demonstrating SVG parser with code generation."""
  from src.generator.image_vector_generator import ImageVectorGenerator

  # Use a standard SVG example similar to Material Design icons
  star_svg = """<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path d="M12 2 L15 9 L22 9 L16.5 14 L18.5 21 L12 17 L5.5 21 L7.5 14 L2 9 L9 9 Z" fill="#ffcc00" id="star"/>
  </svg>"""

  parser = SvgParser()
  ir = parser.parse_svg(star_svg)

  # Verify IR structure
  assert ir.name == "star"
  assert len(ir.nodes) == 1
  assert isinstance(ir.nodes[0], IrVectorPath)

  # Generate Kotlin code
  generator = ImageVectorGenerator()
  kotlin_code = generator.generate(ir)

  # Verify generated code contains expected elements
  assert "ImageVector.Builder(" in kotlin_code
  assert 'name = "star"' in kotlin_code
  assert "viewportWidth = 24f" in kotlin_code
  assert "path(" in kotlin_code
  assert "fill = SolidColor(Color(0xFFFFCC00))" in kotlin_code  # Gold color
  assert ".build()" in kotlin_code
