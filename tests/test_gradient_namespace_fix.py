"""Test gradient parsing with namespace support."""

from src.parser.svg_parser import SvgParser
from src.generator.image_vector_generator import ImageVectorGenerator
from src.ir.gradient import IrLinearGradient, IrRadialGradient


class TestGradientNamespaceFix:
  """Test that gradient parsing works correctly with XML namespaces."""

  def test_linear_gradient_with_namespace(self):
    """Test linear gradient parsing with SVG namespace."""
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="testGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#FF0000;stop-opacity:1" />
      <stop offset="50%" style="stop-color:#00FF00;stop-opacity:0.8" />
      <stop offset="100%" style="stop-color:#0000FF;stop-opacity:1" />
    </linearGradient>
  </defs>
  <path d="M0 0h24v24H0z" fill="url(#testGrad)"/>
</svg>"""
    
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)
    
    assert len(ir.nodes) == 1
    path_node = ir.nodes[0]
    
    # Verify the fill is a gradient
    assert path_node.fill is not None
    assert isinstance(path_node.fill, IrLinearGradient)
    
    # Verify gradient properties
    gradient = path_node.fill
    assert gradient.start_x == 0.0
    assert gradient.start_y == 0.0
    assert gradient.end_x == 100.0
    assert gradient.end_y == 0.0
    
    # Verify color stops are parsed correctly
    assert len(gradient.color_stops) == 3
    
    # Check first stop (red)
    stop0 = gradient.color_stops[0]
    assert stop0.offset == 0.0
    assert stop0.color.argb == 0xFFFF0000  # Red
    assert stop0.opacity == 1.0
    
    # Check second stop (green with opacity)
    stop1 = gradient.color_stops[1]
    assert stop1.offset == 0.5
    assert stop1.opacity == 0.8
    # Color should have opacity applied
    expected_alpha = int(255 * 0.8)  # 204
    assert (stop1.color.argb >> 24) & 0xFF == expected_alpha
    
    # Check third stop (blue)
    stop2 = gradient.color_stops[2]
    assert stop2.offset == 1.0
    assert stop2.color.argb == 0xFF0000FF  # Blue
    assert stop2.opacity == 1.0

  def test_radial_gradient_with_namespace(self):
    """Test radial gradient parsing with SVG namespace."""
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="radialGrad" cx="50%" cy="50%" r="50%">
      <stop offset="0%" style="stop-color:#FFFFFF;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#000000;stop-opacity:1" />
    </radialGradient>
  </defs>
  <path d="M10 10h80v80h-80z" fill="url(#radialGrad)"/>
</svg>"""
    
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)
    
    assert len(ir.nodes) == 1
    path_node = ir.nodes[0]
    
    # Verify the fill is a radial gradient
    assert path_node.fill is not None
    assert isinstance(path_node.fill, IrRadialGradient)
    
    # Note: Also check gradient storage in context
    # For now, let's check that gradients are being parsed and stored correctly
    # by checking the context instead
    
    # Create fresh parsing to check gradient storage
    import xml.etree.ElementTree as ET
    from src.parser.svg_parser import ParseContext
    
    root = ET.fromstring(svg_content)
    parser = SvgParser()
    context = ParseContext()
    
    # Parse the defs section
    for child in root:
      if child.tag.endswith('defs'):
        parser._parse_defs_element(child, context)
    
    # Verify gradient was stored
    assert "radialGrad" in context.gradients
    gradient = context.gradients["radialGrad"]
    assert isinstance(gradient, IrRadialGradient)
    
    # Verify radial gradient properties
    assert gradient.center_x == 50.0  # 50% of 100
    assert gradient.center_y == 50.0  # 50% of 100
    assert gradient.radius == 50.0    # 50% of min(100, 100)
    
    # Verify color stops
    assert len(gradient.color_stops) == 2
    assert gradient.color_stops[0].color.argb == 0xFFFFFFFF  # White
    assert gradient.color_stops[1].color.argb == 0xFF000000  # Black

  def test_gradient_without_namespace(self):
    """Test that gradients work without namespace too."""
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="24" height="24" viewBox="0 0 24 24">
  <defs>
    <linearGradient id="simpleGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#FF0000" />
      <stop offset="1" stop-color="#0000FF" />
    </linearGradient>
  </defs>
  <path d="M0 0h24v24H0z" fill="url(#simpleGrad)"/>
</svg>"""
    
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)
    
    assert len(ir.nodes) == 1
    path_node = ir.nodes[0]
    
    assert path_node.fill is not None
    assert isinstance(path_node.fill, IrLinearGradient)
    
    gradient = path_node.fill
    assert len(gradient.color_stops) == 2
    assert gradient.color_stops[0].color.argb == 0xFFFF0000  # Red
    assert gradient.color_stops[1].color.argb == 0xFF0000FF  # Blue

  def test_gradient_code_generation_with_multiple_stops(self):
    """Test code generation with multiple gradient stops."""
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="multiGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#FF6B35" />
      <stop offset="33%" style="stop-color:#F7931E" />
      <stop offset="66%" style="stop-color:#FFCC02" />
      <stop offset="100%" style="stop-color:#42A5F5" />
    </linearGradient>
  </defs>
  <path d="M0 0h24v24H0z" fill="url(#multiGrad)"/>
</svg>"""
    
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)
    
    generator = ImageVectorGenerator()
    code = generator.generate(ir)
    
    # Should generate multi-line colorStops array for readability
    assert "colorStops = arrayOf(" in code
    assert "0f to Color(0xFFFF6B35)" in code
    assert "0.33f to Color(0xFFF7931E)" in code
    assert "0.66f to Color(0xFFFFCC02)" in code
    assert "1f to Color(0xFF42A5F5)" in code
    
    # Check that it uses multi-line format for 3+ stops
    lines = code.split('\n')
    color_stop_lines = [line for line in lines if 'to Color(' in line]
    assert len(color_stop_lines) >= 4, "Should have separate lines for each color stop"

  def test_gradient_with_style_attributes_namespace(self):
    """Test gradient stop parsing with style attributes in namespaced SVG."""
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
  <defs>
    <linearGradient id="styledGrad">
      <stop offset="0%" style="stop-color:rgb(255,0,0);stop-opacity:0.5" />
      <stop offset="100%" style="stop-color:hsl(240,100%,50%);stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="24" height="24" fill="url(#styledGrad)"/>
</svg>"""
    
    parser = SvgParser()
    parser.parse_svg(svg_content)
    
    # The rect element won't be parsed as a path, but the gradient should be stored
    import xml.etree.ElementTree as ET
    from src.parser.svg_parser import ParseContext
    
    root = ET.fromstring(svg_content)
    context = ParseContext()
    
    # Parse defs
    for child in root:
      if child.tag.endswith('defs'):
        parser._parse_defs_element(child, context)
    
    assert "styledGrad" in context.gradients
    gradient = context.gradients["styledGrad"]
    assert len(gradient.color_stops) == 2
    
    # First stop: red with 50% opacity
    stop0 = gradient.color_stops[0]
    assert stop0.opacity == 0.5
    # Should have opacity applied to alpha channel
    expected_alpha = int(255 * 0.5)  # 127
    assert (stop0.color.argb >> 24) & 0xFF == expected_alpha
    
    # Second stop: blue with full opacity
    stop1 = gradient.color_stops[1]
    assert stop1.opacity == 1.0
    assert stop1.color.argb == 0xFF0000FF  # HSL(240,100%,50%) = blue