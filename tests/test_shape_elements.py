"""Tests for SVG shape element parsing (rect, circle, ellipse, line, polygon, polyline)."""

from src.ir.gradient import IrColorFill
from src.ir.path_node import IrArcTo, IrClose, IrLineTo, IrMoveTo
from src.ir.vector_node import IrVectorPath
from src.parser.svg_parser import SvgParser


class TestRectElement:
  """Test rect element parsing."""

  def test_simple_rect(self):
    """Test simple rectangle without rounded corners."""
    svg_content = """<svg><rect x="10" y="20" width="30" height="40"/></svg>"""
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    assert len(ir.nodes) == 1
    assert isinstance(ir.nodes[0], IrVectorPath)
    path = ir.nodes[0]
    assert path.name == "rect"

    # Should generate: M10,20 L40,20 L40,60 L10,60 Z
    assert len(path.paths) == 5
    assert isinstance(path.paths[0], IrMoveTo)
    assert path.paths[0].x == 10.0 and path.paths[0].y == 20.0
    assert isinstance(path.paths[-1], IrClose)

  def test_rounded_rect(self):
    """Test rectangle with rounded corners."""
    svg_content = """<svg><rect x="0" y="0" width="100" height="50" rx="10" ry="5"/></svg>"""
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    assert len(ir.nodes) == 1
    path = ir.nodes[0]

    # Should contain arc commands for rounded corners
    arc_nodes = [node for node in path.paths if isinstance(node, IrArcTo)]
    assert len(arc_nodes) == 4  # Four corners

  def test_rect_with_styles(self):
    """Test rectangle with fill and stroke styles."""
    svg_content = """<svg><rect x="0" y="0" width="50" height="50" fill="red" stroke="blue" stroke-width="2"/></svg>"""
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    path = ir.nodes[0]
    assert isinstance(path.fill, IrColorFill)
    assert path.fill.color.argb == 0xFFFF0000  # Red
    assert isinstance(path.stroke, IrColorFill)
    assert path.stroke.color.argb == 0xFF0000FF  # Blue
    assert path.stroke_line_width == 2.0

  def test_invalid_rect_dimensions(self):
    """Test rectangle with invalid dimensions."""
    svg_content = """<svg><rect x="10" y="20" width="0" height="40"/></svg>"""
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    # Should return empty nodes for invalid rectangle
    assert len(ir.nodes) == 0


class TestCircleElement:
  """Test circle element parsing."""

  def test_simple_circle(self):
    """Test simple circle."""
    svg_content = """<svg><circle cx="50" cy="50" r="25"/></svg>"""
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    assert len(ir.nodes) == 1
    path = ir.nodes[0]
    assert path.name == "circle"

    # Circle should be generated with 4 arc commands
    arc_nodes = [node for node in path.paths if isinstance(node, IrArcTo)]
    assert len(arc_nodes) == 4

  def test_circle_with_styles(self):
    """Test circle with fill."""
    svg_content = """<svg><circle cx="0" cy="0" r="10" fill="green"/></svg>"""
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    path = ir.nodes[0]
    assert isinstance(path.fill, IrColorFill)
    assert path.fill.color.argb == 0xFF008000  # SVG green

  def test_invalid_circle_radius(self):
    """Test circle with invalid radius."""
    svg_content = """<svg><circle cx="50" cy="50" r="0"/></svg>"""
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    assert len(ir.nodes) == 0


class TestEllipseElement:
  """Test ellipse element parsing."""

  def test_simple_ellipse(self):
    """Test simple ellipse."""
    svg_content = """<svg><ellipse cx="50" cy="30" rx="40" ry="20"/></svg>"""
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    assert len(ir.nodes) == 1
    path = ir.nodes[0]
    assert path.name == "ellipse"

    # Ellipse should be generated with 4 arc commands
    arc_nodes = [node for node in path.paths if isinstance(node, IrArcTo)]
    assert len(arc_nodes) == 4

  def test_invalid_ellipse_radii(self):
    """Test ellipse with invalid radii."""
    svg_content = """<svg><ellipse cx="50" cy="30" rx="0" ry="20"/></svg>"""
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    assert len(ir.nodes) == 0


class TestLineElement:
  """Test line element parsing."""

  def test_simple_line(self):
    """Test simple line."""
    svg_content = """<svg><line x1="10" y1="20" x2="30" y2="40"/></svg>"""
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    assert len(ir.nodes) == 1
    path = ir.nodes[0]
    assert path.name == "line"

    # Line should generate: M10,20 L30,40
    assert len(path.paths) == 2
    assert isinstance(path.paths[0], IrMoveTo)
    assert path.paths[0].x == 10.0 and path.paths[0].y == 20.0
    assert isinstance(path.paths[1], IrLineTo)
    assert path.paths[1].x == 30.0 and path.paths[1].y == 40.0

  def test_line_with_stroke(self):
    """Test line with stroke properties."""
    svg_content = (
      """<svg><line x1="0" y1="0" x2="100" y2="0" stroke="red" stroke-width="5"/></svg>"""
    )
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    path = ir.nodes[0]
    assert isinstance(path.stroke, IrColorFill)
    assert path.stroke.color.argb == 0xFFFF0000  # Red
    assert path.stroke_line_width == 5.0


class TestPolygonElement:
  """Test polygon element parsing."""

  def test_simple_polygon(self):
    """Test simple triangle polygon."""
    svg_content = """<svg><polygon points="10,10 50,10 30,40"/></svg>"""
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    assert len(ir.nodes) == 1
    path = ir.nodes[0]
    assert path.name == "polygon"

    # Polygon should generate: M10,10 L50,10 L30,40 Z
    assert len(path.paths) == 4
    assert isinstance(path.paths[0], IrMoveTo)
    assert isinstance(path.paths[-1], IrClose)

  def test_polygon_with_commas(self):
    """Test polygon with comma-separated points."""
    svg_content = """<svg><polygon points="0,0, 10,0, 5,10"/></svg>"""
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    assert len(ir.nodes) == 1
    path = ir.nodes[0]
    assert len(path.paths) == 4  # M + 2L + Z

  def test_polygon_with_mixed_separators(self):
    """Test polygon with mixed space and comma separators."""
    svg_content = """<svg><polygon points="0 0,10,0 5 10"/></svg>"""
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    assert len(ir.nodes) == 1
    path = ir.nodes[0]
    assert len(path.paths) == 4

  def test_invalid_polygon_points(self):
    """Test polygon with insufficient points."""
    svg_content = """<svg><polygon points="10,10 50,10"/></svg>"""
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    # Polygon needs at least 3 points
    assert len(ir.nodes) == 0

  def test_empty_polygon_points(self):
    """Test polygon with empty points."""
    svg_content = """<svg><polygon points=""/></svg>"""
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    assert len(ir.nodes) == 0


class TestPolylineElement:
  """Test polyline element parsing."""

  def test_simple_polyline(self):
    """Test simple polyline."""
    svg_content = """<svg><polyline points="10,10 20,20 30,10"/></svg>"""
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    assert len(ir.nodes) == 1
    path = ir.nodes[0]
    assert path.name == "polyline"

    # Polyline should generate: M10,10 L20,20 L30,10 (no Z)
    assert len(path.paths) == 3
    assert isinstance(path.paths[0], IrMoveTo)
    assert isinstance(path.paths[1], IrLineTo)
    assert isinstance(path.paths[2], IrLineTo)
    # Should NOT have IrClose

  def test_polyline_vs_polygon(self):
    """Test difference between polyline and polygon (open vs closed)."""
    polyline_svg = """<svg><polyline points="0,0 10,0 5,10"/></svg>"""
    polygon_svg = """<svg><polygon points="0,0 10,0 5,10"/></svg>"""

    parser = SvgParser()
    polyline_ir = parser.parse_svg(polyline_svg)
    polygon_ir = parser.parse_svg(polygon_svg)

    polyline_path = polyline_ir.nodes[0]
    polygon_path = polygon_ir.nodes[0]

    # Polyline should NOT have close command
    close_in_polyline = any(isinstance(node, IrClose) for node in polyline_path.paths)
    assert not close_in_polyline

    # Polygon should have close command
    close_in_polygon = any(isinstance(node, IrClose) for node in polygon_path.paths)
    assert close_in_polygon

  def test_invalid_polyline_points(self):
    """Test polyline with insufficient points."""
    svg_content = """<svg><polyline points="10,10"/></svg>"""
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    # Polyline needs at least 2 points
    assert len(ir.nodes) == 0


class TestShapeIntegration:
  """Test integration of shapes with other SVG features."""

  def test_shapes_in_groups(self):
    """Test shapes inside groups with transforms."""
    svg_content = """
    <svg>
      <g transform="translate(10,10)">
        <rect x="0" y="0" width="20" height="20"/>
        <circle cx="30" cy="10" r="5"/>
      </g>
    </svg>
    """
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    # Should have one group containing two shapes
    assert len(ir.nodes) == 1
    from src.ir.vector_node import IrVectorGroup

    assert isinstance(ir.nodes[0], IrVectorGroup)
    group = ir.nodes[0]
    assert len(group.children) == 2

  def test_mixed_shapes_and_paths(self):
    """Test document with both shapes and path elements."""
    svg_content = """
    <svg>
      <rect x="0" y="0" width="50" height="25"/>
      <path d="M10,10 L40,10 L25,35 Z"/>
      <circle cx="75" cy="25" r="10"/>
    </svg>
    """
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    assert len(ir.nodes) == 3
    # All should be IrVectorPath (shapes converted to paths)
    for node in ir.nodes:
      assert isinstance(node, IrVectorPath)

  def test_shapes_with_gradients(self):
    """Test shapes with gradient fills."""
    svg_content = """
    <svg>
      <defs>
        <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" style="stop-color:rgb(255,255,0);stop-opacity:1" />
          <stop offset="100%" style="stop-color:rgb(255,0,0);stop-opacity:1" />
        </linearGradient>
      </defs>
      <rect x="10" y="10" width="80" height="40" fill="url(#grad1)"/>
    </svg>
    """
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    assert len(ir.nodes) == 1
    path = ir.nodes[0]
    from src.ir.gradient import IrLinearGradient

    assert isinstance(path.fill, IrLinearGradient)
