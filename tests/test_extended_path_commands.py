from src.parser.path_parser import PathParser
from src.ir.path_node import (
  IrQuadTo,
  IrRelativeQuadTo,
  IrReflectiveCurveTo,
  IrRelativeReflectiveCurveTo,
  IrReflectiveQuadTo,
  IrRelativeReflectiveQuadTo,
  IrArcTo,
  IrRelativeArcTo,
)


class TestExtendedPathCommands:
  """Test cases for extended SVG path commands (S, Q, T, A)."""

  def setup_method(self):
    self.parser = PathParser()

  def test_quadratic_bezier_absolute(self):
    """Test Q command (absolute quadratic Bezier curve)."""
    nodes = self.parser.parse_path_data("Q 10 15 20 25")

    assert len(nodes) == 1
    assert isinstance(nodes[0], IrQuadTo)
    assert nodes[0].x1 == 10.0
    assert nodes[0].y1 == 15.0
    assert nodes[0].x2 == 20.0
    assert nodes[0].y2 == 25.0
    assert nodes[0].to_compose_dsl() == "quadTo(10f, 15f, 20f, 25f)"

  def test_quadratic_bezier_relative(self):
    """Test q command (relative quadratic Bezier curve)."""
    nodes = self.parser.parse_path_data("q 5 10 15 20")

    assert len(nodes) == 1
    assert isinstance(nodes[0], IrRelativeQuadTo)
    assert nodes[0].dx1 == 5.0
    assert nodes[0].dy1 == 10.0
    assert nodes[0].dx2 == 15.0
    assert nodes[0].dy2 == 20.0
    assert nodes[0].to_compose_dsl() == "quadToRelative(5f, 10f, 15f, 20f)"

  def test_smooth_cubic_bezier_absolute(self):
    """Test S command (absolute smooth cubic Bezier curve)."""
    nodes = self.parser.parse_path_data("S 10 15 20 25")

    assert len(nodes) == 1
    assert isinstance(nodes[0], IrReflectiveCurveTo)
    assert nodes[0].x2 == 10.0
    assert nodes[0].y2 == 15.0
    assert nodes[0].x3 == 20.0
    assert nodes[0].y3 == 25.0
    assert nodes[0].to_compose_dsl() == "reflectiveCurveTo(10f, 15f, 20f, 25f)"

  def test_smooth_cubic_bezier_relative(self):
    """Test s command (relative smooth cubic Bezier curve)."""
    nodes = self.parser.parse_path_data("s 5 10 15 20")

    assert len(nodes) == 1
    assert isinstance(nodes[0], IrRelativeReflectiveCurveTo)
    assert nodes[0].dx2 == 5.0
    assert nodes[0].dy2 == 10.0
    assert nodes[0].dx3 == 15.0
    assert nodes[0].dy3 == 20.0
    assert nodes[0].to_compose_dsl() == "reflectiveCurveToRelative(5f, 10f, 15f, 20f)"

  def test_smooth_quadratic_bezier_absolute(self):
    """Test T command (absolute smooth quadratic Bezier curve)."""
    nodes = self.parser.parse_path_data("T 20 25")

    assert len(nodes) == 1
    assert isinstance(nodes[0], IrReflectiveQuadTo)
    assert nodes[0].x == 20.0
    assert nodes[0].y == 25.0
    assert nodes[0].to_compose_dsl() == "reflectiveQuadTo(20f, 25f)"

  def test_smooth_quadratic_bezier_relative(self):
    """Test t command (relative smooth quadratic Bezier curve)."""
    nodes = self.parser.parse_path_data("t 15 20")

    assert len(nodes) == 1
    assert isinstance(nodes[0], IrRelativeReflectiveQuadTo)
    assert nodes[0].dx == 15.0
    assert nodes[0].dy == 20.0
    assert nodes[0].to_compose_dsl() == "reflectiveQuadToRelative(15f, 20f)"

  def test_arc_absolute(self):
    """Test A command (absolute elliptical arc)."""
    nodes = self.parser.parse_path_data("A 25 50 -30 0 1 100 200")

    assert len(nodes) == 1
    assert isinstance(nodes[0], IrArcTo)
    assert nodes[0].horizontal_ellipse_radius == 25.0
    assert nodes[0].vertical_ellipse_radius == 50.0
    assert nodes[0].theta == -30.0
    assert not nodes[0].is_more_than_half
    assert nodes[0].is_positive_arc
    assert nodes[0].x1 == 100.0
    assert nodes[0].y1 == 200.0
    expected_dsl = "arcTo(25f, 50f, -30f, false, true, 100f, 200f)"
    assert nodes[0].to_compose_dsl() == expected_dsl

  def test_arc_relative(self):
    """Test a command (relative elliptical arc)."""
    nodes = self.parser.parse_path_data("a 10 20 45 1 0 50 75")

    assert len(nodes) == 1
    assert isinstance(nodes[0], IrRelativeArcTo)
    assert nodes[0].horizontal_ellipse_radius == 10.0
    assert nodes[0].vertical_ellipse_radius == 20.0
    assert nodes[0].theta == 45.0
    assert nodes[0].is_more_than_half
    assert not nodes[0].is_positive_arc
    assert nodes[0].dx1 == 50.0
    assert nodes[0].dy1 == 75.0
    expected_dsl = "arcToRelative(10f, 20f, 45f, true, false, 50f, 75f)"
    assert nodes[0].to_compose_dsl() == expected_dsl

  def test_multiple_commands_sequence(self):
    """Test sequence of different advanced commands."""
    path_data = "M 10 10 Q 20 5 30 10 T 50 10 S 70 5 80 10 A 5 5 0 0 1 90 10 z"
    nodes = self.parser.parse_path_data(path_data)

    # Should have: MoveTo, QuadTo, ReflectiveQuadTo, ReflectiveCurveTo, ArcTo, Close
    assert len(nodes) == 6

    # Verify specific node types
    from src.ir.path_node import IrMoveTo, IrClose

    assert isinstance(nodes[0], IrMoveTo)
    assert isinstance(nodes[1], IrQuadTo)
    assert isinstance(nodes[2], IrReflectiveQuadTo)
    assert isinstance(nodes[3], IrReflectiveCurveTo)
    assert isinstance(nodes[4], IrArcTo)
    assert isinstance(nodes[5], IrClose)

  def test_repeated_commands(self):
    """Test repeated commands without explicit command letters."""
    # Q command should support multiple coordinate sets
    nodes = self.parser.parse_path_data("Q 10 5 20 10 30 15 40 20")

    assert len(nodes) == 2
    assert all(isinstance(node, IrQuadTo) for node in nodes)

    # First quad curve
    assert nodes[0].x1 == 10.0 and nodes[0].y1 == 5.0
    assert nodes[0].x2 == 20.0 and nodes[0].y2 == 10.0

    # Second quad curve
    assert nodes[1].x1 == 30.0 and nodes[1].y1 == 15.0
    assert nodes[1].x2 == 40.0 and nodes[1].y2 == 20.0

  def test_scientific_notation_in_arc(self):
    """Test arc command with scientific notation."""
    nodes = self.parser.parse_path_data("A 1.5e2 2.0e1 -3.14e1 1 0 1e2 2e2")

    assert len(nodes) == 1
    assert isinstance(nodes[0], IrArcTo)
    assert nodes[0].horizontal_ellipse_radius == 150.0
    assert nodes[0].vertical_ellipse_radius == 20.0
    assert nodes[0].theta == -31.4
    assert nodes[0].x1 == 100.0
    assert nodes[0].y1 == 200.0


def test_end_to_end_advanced_path():
  """Test end-to-end conversion with advanced path commands."""
  from src.parser.svg_parser import SvgParser
  from src.generator.image_vector_generator import ImageVectorGenerator

  svg_content = """
  <svg width="100" height="100" viewBox="0 0 100 100">
    <path d="M 20 20 Q 50 10 80 20 T 80 50 S 70 80 50 80 A 10 10 0 0 1 20 70 Z" fill="blue"/>
  </svg>
  """

  parser = SvgParser()
  ir = parser.parse_svg(svg_content)

  generator = ImageVectorGenerator()
  kotlin_code = generator.generate(ir)

  # Verify the generated code contains the expected DSL calls
  assert "quadTo(50f, 10f, 80f, 20f)" in kotlin_code
  assert "reflectiveQuadTo(80f, 50f)" in kotlin_code
  assert "reflectiveCurveTo(70f, 80f, 50f, 80f)" in kotlin_code
  assert "arcTo(10f, 10f, 0f, false, true, 20f, 70f)" in kotlin_code
  assert "close()" in kotlin_code
