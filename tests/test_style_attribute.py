from src.parser.svg_parser import SvgParser
from src.generator.image_vector_generator import ImageVectorGenerator


class TestStyleAttribute:
  """Test CSS style attribute parsing functionality."""

  def test_basic_style_parsing(self):
    """Test basic CSS style attribute parsing."""
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
    <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path d="M 0 0 L 10 10" style="fill: red; stroke: blue;"/>
    </svg>"""

    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    path = ir.nodes[0]
    assert path.fill.argb == 0xFFFF0000  # Red
    assert path.stroke.argb == 0xFF0000FF  # Blue

  def test_style_overrides_attributes(self):
    """Test that style attribute overrides direct attributes."""
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
    <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path d="M 0 0 L 10 10" 
            fill="green" 
            stroke="yellow"
            style="fill: red; stroke: blue;"/>
    </svg>"""

    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    path = ir.nodes[0]
    # Style should override attributes
    assert path.fill.argb == 0xFFFF0000  # Red (from style)
    assert path.stroke.argb == 0xFF0000FF  # Blue (from style)

  def test_rgb_color_in_style(self):
    """Test RGB color format in style."""
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
    <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path d="M 0 0 L 10 10" style="fill: rgb(255, 193, 7);"/>
    </svg>"""

    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    path = ir.nodes[0]
    assert path.fill.argb == 0xFFFFC107  # RGB(255, 193, 7)

  def test_hsl_color_in_style(self):
    """Test HSL color format in style."""
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
    <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path d="M 0 0 L 10 10" style="stroke: hsl(0, 100%, 50%);"/>
    </svg>"""

    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    path = ir.nodes[0]
    assert path.stroke.argb == 0xFFFF0000  # HSL(0, 100%, 50%) = Red

  def test_opacity_in_style(self):
    """Test opacity values in style."""
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
    <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path d="M 0 0 L 10 10" 
            style="fill: red; fill-opacity: 0.5; stroke: blue; stroke-opacity: 0.8;"/>
    </svg>"""

    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    path = ir.nodes[0]
    assert path.fill_alpha == 0.5
    assert path.stroke_alpha == 0.8

  def test_stroke_properties_in_style(self):
    """Test stroke properties in style."""
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
    <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path d="M 0 0 L 10 10" 
            style="stroke: red; stroke-width: 3; stroke-linecap: round; stroke-linejoin: bevel;"/>
    </svg>"""

    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    path = ir.nodes[0]
    assert path.stroke.argb == 0xFFFF0000  # Red
    assert path.stroke_line_width == 3.0
    assert path.stroke_line_cap == "round"
    assert path.stroke_line_join == "bevel"

  def test_mixed_style_and_attributes(self):
    """Test combination of style and individual attributes."""
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
    <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path d="M 0 0 L 10 10" 
            stroke-width="2"
            fill-opacity="0.3"
            style="fill: green; stroke: red;"/>
    </svg>"""

    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    path = ir.nodes[0]
    # Style values should be used
    assert path.fill.argb == 0xFF008000  # Green (CSS green)
    assert path.stroke.argb == 0xFFFF0000  # Red
    # Attribute values should be used where not overridden
    assert path.stroke_line_width == 2.0
    assert path.fill_alpha == 0.3

  def test_style_with_none_values(self):
    """Test style with 'none' values."""
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
    <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path d="M 0 0 L 10 10" style="fill: none; stroke: red;"/>
    </svg>"""

    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    path = ir.nodes[0]
    assert path.fill is None  # none
    assert path.stroke.argb == 0xFFFF0000  # Red

  def test_malformed_style_graceful_fallback(self):
    """Test graceful handling of malformed style attributes."""
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
    <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path d="M 0 0 L 10 10" 
            fill="blue"
            style="fill red; stroke: invalidcolor; valid-prop: value;"/>
    </svg>"""

    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    path = ir.nodes[0]
    # Should fall back to attribute for fill since style parsing fails
    assert path.fill.argb == 0xFF0000FF  # Blue (from attribute)
    # Stroke should be None since invalid color can't be parsed
    assert path.stroke is None


def test_style_attribute_integration():
  """Integration test with CSS style attributes."""
  svg_content = """<?xml version="1.0" encoding="UTF-8"?>
  <svg width="100" height="50" viewBox="0 0 100 50" xmlns="http://www.w3.org/2000/svg">
    <path d="M 10 10 L 40 10 L 40 30 L 10 30 Z" 
          style="fill: rgba(255, 0, 0, 0.8); stroke: hsl(240, 100%, 50%); stroke-width: 2;"/>
  </svg>"""

  parser = SvgParser()
  ir = parser.parse_svg(svg_content)

  generator = ImageVectorGenerator()
  code = generator.generate(ir)

  # Should include both RGB and HSL color conversions
  assert "fill = Color(0xCCFF0000)" in code  # RGBA(255,0,0,0.8) = alpha 0.8*255=204=0xCC
  assert "stroke = Color(0xFF0000FF)" in code  # HSL blue
  assert "strokeLineWidth = 2.0f" in code
