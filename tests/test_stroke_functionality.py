from src.parser.svg_parser import SvgParser
from src.generator.image_vector_generator import ImageVectorGenerator
from src.ir.gradient import IrLinearGradient, IrRadialGradient


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
    assert "stroke = SolidColor(Color.Green)" in code
    assert "strokeLineWidth = 3f" in code
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
    assert "fill = SolidColor(Color.Blue)" in code  # Blue
    assert "stroke = SolidColor(Color.Red)" in code  # Red
    assert "strokeLineWidth = 1f" in code

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
    "fill = SolidColor(Color(0xFFFFEB3B))",
    "stroke = SolidColor(Color(0xFF2196F3))",
    "fillAlpha = 0.6f",
    "strokeAlpha = 0.8f",
    "strokeLineWidth = 4f",
    "strokeLineCap = StrokeCap.Round",
    "strokeLineJoin = StrokeJoin.Round",
  ]

  for element in expected_elements:
    assert element in code, f"Missing expected element: {element}"


class TestStrokeGradientSupport:
  """Test stroke gradient parsing and generation functionality."""

  def test_stroke_linear_gradient_parsing(self):
    """Test parsing stroke with linear gradient."""
    svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
    <svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="strokeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" style="stop-color:red;stop-opacity:1" />
          <stop offset="100%" style="stop-color:blue;stop-opacity:1" />
        </linearGradient>
      </defs>
      <path d="M10 10 L90 90" stroke="url(#strokeGrad)" stroke-width="3" fill="none"/>
    </svg>'''

    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    assert len(ir.nodes) == 1
    path = ir.nodes[0]
    
    # Check that stroke is a linear gradient
    assert isinstance(path.stroke, IrLinearGradient)
    assert path.stroke.start_x == 0.0
    assert path.stroke.start_y == 0.0
    assert path.stroke.end_x == 100.0
    assert path.stroke.end_y == 0.0
    
    # Check gradient stops
    assert len(path.stroke.color_stops) == 2
    assert path.stroke.color_stops[0].offset == 0.0
    assert path.stroke.color_stops[0].color.argb == 0xFFFF0000  # Red
    assert path.stroke.color_stops[1].offset == 1.0
    assert path.stroke.color_stops[1].color.argb == 0xFF0000FF  # Blue

  def test_stroke_radial_gradient_parsing(self):
    """Test parsing stroke with radial gradient."""
    svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
    <svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <radialGradient id="strokeRadial" cx="50%" cy="50%" r="50%">
          <stop offset="0%" style="stop-color:yellow;stop-opacity:1" />
          <stop offset="100%" style="stop-color:green;stop-opacity:1" />
        </radialGradient>
      </defs>
      <path d="M20 20 L80 80" stroke="url(#strokeRadial)" stroke-width="5" fill="none"/>
    </svg>'''

    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    assert len(ir.nodes) == 1
    path = ir.nodes[0]
    
    # Check that stroke is a radial gradient
    assert isinstance(path.stroke, IrRadialGradient)
    assert path.stroke.center_x == 50.0
    assert path.stroke.center_y == 50.0
    assert path.stroke.radius == 50.0
    
    # Check gradient stops
    assert len(path.stroke.color_stops) == 2
    assert path.stroke.color_stops[0].offset == 0.0
    assert path.stroke.color_stops[0].color.argb == 0xFFFFFF00  # Yellow
    assert path.stroke.color_stops[1].offset == 1.0
    assert path.stroke.color_stops[1].color.argb == 0xFF008000  # Green

  def test_stroke_linear_gradient_code_generation(self):
    """Test code generation for stroke with linear gradient."""
    svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
    <svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="myGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:red;stop-opacity:1" />
          <stop offset="100%" style="stop-color:blue;stop-opacity:1" />
        </linearGradient>
      </defs>
      <path d="M10 10 L90 90" stroke="url(#myGrad)" stroke-width="2" fill="none"/>
    </svg>'''

    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    generator = ImageVectorGenerator()
    code = generator.generate(ir)

    # Check that stroke uses Brush.linearGradient
    assert "stroke = Brush.linearGradient(" in code
    assert "start = Offset(" in code
    assert "end = Offset(" in code
    assert "colorStops = arrayOf(" in code
    assert "Color.Red" in code  # Red
    assert "Color.Blue" in code  # Blue
    assert "strokeLineWidth = 2f" in code

  def test_stroke_radial_gradient_code_generation(self):
    """Test code generation for stroke with radial gradient."""
    svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
    <svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <radialGradient id="radGrad" cx="50%" cy="50%" r="50%">
          <stop offset="0%" style="stop-color:yellow;stop-opacity:1" />
          <stop offset="100%" style="stop-color:green;stop-opacity:1" />
        </radialGradient>
      </defs>
      <path d="M20 20 L80 80" stroke="url(#radGrad)" stroke-width="3" fill="none"/>
    </svg>'''

    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    generator = ImageVectorGenerator()
    code = generator.generate(ir)

    # Check that stroke uses Brush.radialGradient
    assert "stroke = Brush.radialGradient(" in code
    assert "center = Offset(" in code
    assert "radius = " in code
    assert "colorStops = arrayOf(" in code
    assert "Color.Yellow" in code  # Yellow
    assert "Color(0xFF008000)" in code  # Green (SVG green is #008000, not Compose Green #00FF00)
    assert "strokeLineWidth = 3f" in code

  def test_stroke_and_fill_both_gradients(self):
    """Test path with both stroke and fill using gradients."""
    svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
    <svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="strokeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" style="stop-color:red;stop-opacity:1" />
          <stop offset="100%" style="stop-color:blue;stop-opacity:1" />
        </linearGradient>
        <radialGradient id="fillGrad" cx="50%" cy="50%" r="50%">
          <stop offset="0%" style="stop-color:white;stop-opacity:1" />
          <stop offset="100%" style="stop-color:black;stop-opacity:1" />
        </radialGradient>
      </defs>
      <path d="M10 10 L90 10 L90 90 L10 90 Z" 
            stroke="url(#strokeGrad)" 
            fill="url(#fillGrad)" 
            stroke-width="4"/>
    </svg>'''

    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    generator = ImageVectorGenerator()
    code = generator.generate(ir)

    # Check that both fill and stroke use gradients
    assert "fill = Brush.radialGradient(" in code
    assert "stroke = Brush.linearGradient(" in code
    assert "strokeLineWidth = 4f" in code
    
    # Check that proper imports are included
    imports = generator.get_required_imports()
    assert "androidx.compose.ui.graphics.Brush" in imports
    assert "androidx.compose.ui.geometry.Offset" in imports
