from src.parser.svg_parser import SvgParser
from src.parser.gradient_parser import GradientParser
from src.generator.image_vector_generator import ImageVectorGenerator
from src.ir.gradient import IrLinearGradient, IrRadialGradient, IrColorStop, IrColorFill
from src.ir.color import IrColor


class TestGradientParser:
  """Test gradient parsing functionality."""

  def test_linear_gradient_parsing(self):
    """Test parsing of linear gradient elements."""
    gradient_xml = '''
    <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#ff0000" />
      <stop offset="100%" stop-color="#0000ff" />
    </linearGradient>
    '''
    
    import xml.etree.ElementTree as ET
    element = ET.fromstring(gradient_xml)
    
    parser = GradientParser()
    gradient = parser.parse_linear_gradient(element, 100.0, 100.0)
    
    assert isinstance(gradient, IrLinearGradient)
    assert gradient.start_x == 0.0
    assert gradient.start_y == 0.0
    assert gradient.end_x == 100.0
    assert gradient.end_y == 0.0
    assert len(gradient.color_stops) == 2
    assert gradient.color_stops[0].offset == 0.0
    assert gradient.color_stops[0].color.argb == 0xFFFF0000  # Red
    assert gradient.color_stops[1].offset == 1.0
    assert gradient.color_stops[1].color.argb == 0xFF0000FF  # Blue

  def test_radial_gradient_parsing(self):
    """Test parsing of radial gradient elements."""
    gradient_xml = '''
    <radialGradient id="grad2" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#ffffff" />
      <stop offset="100%" stop-color="#000000" />
    </radialGradient>
    '''
    
    import xml.etree.ElementTree as ET
    element = ET.fromstring(gradient_xml)
    
    parser = GradientParser()
    gradient = parser.parse_radial_gradient(element, 100.0, 100.0)
    
    assert isinstance(gradient, IrRadialGradient)
    assert gradient.center_x == 50.0
    assert gradient.center_y == 50.0
    assert gradient.radius == 50.0
    assert gradient.focal_x is None
    assert gradient.focal_y is None
    assert len(gradient.color_stops) == 2
    assert gradient.color_stops[0].color.argb == 0xFFFFFFFF  # White
    assert gradient.color_stops[1].color.argb == 0xFF000000  # Black

  def test_gradient_with_style_attribute(self):
    """Test gradient stop with style attribute."""
    gradient_xml = '''
    <linearGradient id="grad3">
      <stop offset="0%" style="stop-color:#ff0000; stop-opacity:0.5" />
      <stop offset="100%" stop-color="#0000ff" stop-opacity="0.8" />
    </linearGradient>
    '''
    
    import xml.etree.ElementTree as ET
    element = ET.fromstring(gradient_xml)
    
    parser = GradientParser()
    gradient = parser.parse_linear_gradient(element, 100.0, 100.0)
    
    assert len(gradient.color_stops) == 2
    # First stop should have alpha from style opacity
    first_stop = gradient.color_stops[0]
    assert (first_stop.color.argb >> 24) & 0xFF == int(255 * 0.5)  # Alpha channel
    
    # Second stop should have alpha from stop-opacity attribute
    second_stop = gradient.color_stops[1]
    assert (second_stop.color.argb >> 24) & 0xFF == int(255 * 0.8)  # Alpha channel


class TestSvgGradientIntegration:
  """Test SVG gradient parsing integration."""

  def test_svg_with_linear_gradient(self):
    """Test SVG containing linear gradient."""
    svg_content = '''<svg width="100" height="100" viewBox="0 0 100 100">
      <defs>
        <linearGradient id="myGradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#ff0000" />
          <stop offset="100%" stop-color="#0000ff" />
        </linearGradient>
      </defs>
      <path d="M 10,10 L 90,10 L 90,90 L 10,90 Z" fill="url(#myGradient)" />
    </svg>'''
    
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)
    
    assert len(ir.nodes) == 1
    path_node = ir.nodes[0]
    assert path_node.fill is not None
    assert isinstance(path_node.fill, IrLinearGradient)
    assert path_node.fill.start_x == 0.0
    assert path_node.fill.end_x == 100.0

  def test_svg_with_radial_gradient(self):
    """Test SVG containing radial gradient."""
    svg_content = '''<svg width="100" height="100" viewBox="0 0 100 100">
      <defs>
        <radialGradient id="radialGrad" cx="50%" cy="50%" r="40%">
          <stop offset="0%" stop-color="#ffffff" />
          <stop offset="100%" stop-color="#000000" />
        </radialGradient>
      </defs>
      <path d="M 50,10 A 40,40 0 1,1 49.9,10 Z" fill="url(#radialGrad)" />
    </svg>'''
    
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)
    
    assert len(ir.nodes) == 1
    path_node = ir.nodes[0]
    assert path_node.fill is not None
    assert isinstance(path_node.fill, IrRadialGradient)
    assert path_node.fill.center_x == 50.0
    assert path_node.fill.center_y == 50.0

  def test_svg_with_missing_gradient_reference(self):
    """Test SVG with missing gradient reference falls back to black."""
    svg_content = '''<svg width="100" height="100" viewBox="0 0 100 100">
      <path d="M 10,10 L 90,10 L 90,90 L 10,90 Z" fill="url(#missingGradient)" />
    </svg>'''
    
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)
    
    assert len(ir.nodes) == 1
    path_node = ir.nodes[0]
    assert path_node.fill is not None
    assert isinstance(path_node.fill, IrColorFill)
    assert path_node.fill.color.argb == 0xFF000000  # Black fallback


class TestGradientCodeGeneration:
  """Test gradient code generation."""

  def test_linear_gradient_code_generation(self):
    """Test Kotlin code generation for linear gradients."""
    red = IrColor.from_hex("#FF0000")
    blue = IrColor.from_hex("#0000FF")
    
    gradient = IrLinearGradient(
      start_x=0.0,
      start_y=0.0,
      end_x=100.0,
      end_y=0.0,
      color_stops=[
        IrColorStop(offset=0.0, color=red),
        IrColorStop(offset=1.0, color=blue)
      ]
    )
    
    code = gradient.to_compose_code()
    
    assert "Brush.linearGradient(" in code
    assert "colorStops = arrayOf(" in code
    assert "0f to Color(0xFFFF0000)" in code
    assert "1f to Color(0xFF0000FF)" in code
    assert "start = Offset(0f, 0f)" in code
    assert "end = Offset(100f, 0f)" in code

  def test_radial_gradient_code_generation(self):
    """Test Kotlin code generation for radial gradients."""
    white = IrColor.from_hex("#FFFFFF")
    black = IrColor.from_hex("#000000")
    
    gradient = IrRadialGradient(
      center_x=50.0,
      center_y=50.0,
      radius=40.0,
      color_stops=[
        IrColorStop(offset=0.0, color=white),
        IrColorStop(offset=1.0, color=black)
      ]
    )
    
    code = gradient.to_compose_code()
    
    assert "Brush.radialGradient(" in code
    assert "colorStops = arrayOf(" in code
    assert "0f to Color(0xFFFFFFFF)" in code
    assert "1f to Color(0xFF000000)" in code
    assert "center = Offset(50f, 50f)" in code
    assert "radius = 40f" in code


class TestEndToEndGradients:
  """Test complete gradient workflow from SVG to Kotlin code."""

  def test_complete_linear_gradient_workflow(self):
    """Test complete workflow with linear gradient."""
    svg_content = '''<svg width="200" height="100" viewBox="0 0 200 100">
      <defs>
        <linearGradient id="sunset" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#ff6b35" />
          <stop offset="50%" stop-color="#f7931e" />
          <stop offset="100%" stop-color="#ffcc02" />
        </linearGradient>
      </defs>
      <path d="M 20,20 L 180,20 L 180,80 L 20,80 Z" fill="url(#sunset)" />
    </svg>'''
    
    # Parse SVG
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)
    
    # Generate Kotlin code
    generator = ImageVectorGenerator()
    kotlin_code = generator.generate(ir)
    
    # Verify gradient is properly generated
    assert "Brush.linearGradient(" in kotlin_code
    assert "colorStops = arrayOf(" in kotlin_code
    assert "start = Offset(" in kotlin_code
    assert "end = Offset(" in kotlin_code
    assert "0f to Color(" in kotlin_code
    assert "0.5f to Color(" in kotlin_code
    assert "1f to Color(" in kotlin_code
    
    # Verify required imports are present
    imports = generator.get_required_imports()
    assert "androidx.compose.ui.graphics.Brush" in imports
    assert "androidx.compose.ui.geometry.Offset" in imports

  def test_complete_radial_gradient_workflow(self):
    """Test complete workflow with radial gradient."""
    svg_content = '''<svg width="100" height="100" viewBox="0 0 100 100">
      <defs>
        <radialGradient id="spotlight" cx="50%" cy="30%" r="60%">
          <stop offset="0%" stop-color="#ffffff" stop-opacity="1" />
          <stop offset="100%" stop-color="#000000" stop-opacity="0.8" />
        </radialGradient>
      </defs>
      <path d="M 50,10 A 40,40 0 1,1 49.9,10 Z" fill="url(#spotlight)" />
    </svg>'''
    
    # Parse SVG
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)
    
    # Generate Kotlin code
    generator = ImageVectorGenerator()
    kotlin_code = generator.generate(ir)
    
    # Verify gradient is properly generated
    assert "Brush.radialGradient(" in kotlin_code
    assert "center = Offset(" in kotlin_code
    assert "radius = " in kotlin_code
    
    # Check that opacity is properly handled in color stops
    assert "Color(0xFFFFFFFF)" in kotlin_code  # White with full opacity
    assert "Color(0xCC000000)" in kotlin_code  # Black with 0.8 opacity