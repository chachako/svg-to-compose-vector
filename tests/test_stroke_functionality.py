from src.parser.svg_parser import SvgParser
from src.generator.image_vector_generator import ImageVectorGenerator


class TestStrokeFunctionality:
  """Test stroke parsing and generation functionality."""

  def test_basic_stroke_parsing(self):
    """Test parsing basic stroke attributes."""
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
    <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path d="M 12 12 L 18 12" stroke="#FF0000" stroke-width="2" fill="none"/>
    </svg>"""

    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    assert len(ir.nodes) == 1
    path = ir.nodes[0]
    assert path.stroke is not None
    assert path.stroke.argb == 0xFFFF0000  # Red
    assert path.stroke_line_width == 2.0
    assert path.fill is None  # fill="none"

  def test_stroke_opacity_parsing(self):
    """Test parsing stroke and fill opacity."""
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
    <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path d="M 0 0 L 10 10" 
            stroke="blue" 
            stroke-opacity="0.5" 
            fill="red" 
            fill-opacity="0.8"/>
    </svg>"""

    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    path = ir.nodes[0]
    assert path.stroke_alpha == 0.5
    assert path.fill_alpha == 0.8

  def test_stroke_linecap_parsing(self):
    """Test parsing stroke-linecap attribute."""
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
    <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path d="M 0 0 L 10 10" stroke="black" stroke-linecap="round"/>
    </svg>"""

    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    path = ir.nodes[0]
    assert path.stroke_line_cap == "round"

  def test_stroke_linejoin_parsing(self):
    """Test parsing stroke-linejoin attribute."""
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
    <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path d="M 0 0 L 10 5 L 0 10" stroke="black" stroke-linejoin="bevel"/>
    </svg>"""

    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    path = ir.nodes[0]
    assert path.stroke_line_join == "bevel"

  def test_stroke_code_generation(self):
    """Test stroke code generation."""
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
    <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path d="M 0 0 L 10 10" 
            stroke="#00FF00" 
            stroke-width="3" 
            stroke-opacity="0.7"
            stroke-linecap="round"
            stroke-linejoin="round"
            fill="none"/>
    </svg>"""

    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    generator = ImageVectorGenerator()
    code = generator.generate(ir)

    # Check that stroke attributes are included in generated code
    assert "stroke = Color(0xFF00FF00)" in code
    assert "strokeLineWidth = 3.0f" in code
    assert "strokeAlpha = 0.7f" in code
    assert "strokeLineCap = StrokeCap.Round" in code
    assert "strokeLineJoin = StrokeJoin.Round" in code

    # Check that fill is not included when set to "none"
    assert "fill =" not in code

  def test_stroke_and_fill_combination(self):
    """Test stroke with fill combination."""
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
    <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path d="M 0 0 L 10 0 L 10 10 L 0 10 Z" 
            stroke="red" 
            stroke-width="1" 
            fill="blue"/>
    </svg>"""

    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    generator = ImageVectorGenerator()
    code = generator.generate(ir)

    # Both stroke and fill should be present
    assert "fill = Color(0xFF0000FF)" in code  # Blue
    assert "stroke = Color(0xFFFF0000)" in code  # Red
    assert "strokeLineWidth = 1.0f" in code

  def test_no_stroke_when_not_specified(self):
    """Test that stroke is not generated when not specified."""
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
    <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path d="M 0 0 L 10 10" fill="red"/>
    </svg>"""

    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    path = ir.nodes[0]
    assert path.stroke is None
    assert path.stroke_line_width == 0.0  # Default

    generator = ImageVectorGenerator()
    code = generator.generate(ir)

    # Stroke attributes should not be present
    assert "stroke =" not in code
    assert "strokeLineWidth" not in code

  def test_stroke_with_named_colors(self):
    """Test stroke with named colors."""
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
    <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path d="M 0 0 L 10 10" stroke="red" fill="blue"/>
    </svg>"""

    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    path = ir.nodes[0]
    assert path.stroke.argb == 0xFFFF0000  # Red
    assert path.fill.argb == 0xFF0000FF  # Blue


def test_stroke_integration_example():
  """Integration test with complex stroke example."""
  svg_content = """<?xml version="1.0" encoding="UTF-8"?>
  <svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
    <path d="M 10 10 L 90 10 L 90 90 L 10 90 Z" 
          stroke="#2196F3" 
          stroke-width="4" 
          stroke-opacity="0.8"
          stroke-linecap="round"
          stroke-linejoin="round"
          fill="#FFEB3B" 
          fill-opacity="0.6"/>
  </svg>"""

  parser = SvgParser()
  ir = parser.parse_svg(svg_content)

  generator = ImageVectorGenerator()
  code = generator.generate(ir)

  expected_elements = [
    "fill = Color(0xFFFFEB3B)",
    "stroke = Color(0xFF2196F3)",
    "fillAlpha = 0.6f",
    "strokeAlpha = 0.8f",
    "strokeLineWidth = 4.0f",
    "strokeLineCap = StrokeCap.Round",
    "strokeLineJoin = StrokeJoin.Round",
  ]

  for element in expected_elements:
    assert element in code, f"Missing expected element: {element}"
