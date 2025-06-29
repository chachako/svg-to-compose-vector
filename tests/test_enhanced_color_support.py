"""Tests for enhanced color support with complete SVG keywords and smart naming."""

from src.generator.image_vector_generator import ImageVectorGenerator
from src.ir.color import IrColor, _get_svg_color, parse_color
from src.parser.svg_parser import SvgParser


class TestSvgColorKeywords:
  """Test complete SVG color keyword support."""

  def test_basic_svg_colors(self):
    """Test basic SVG color keywords."""
    basic_colors = {
      "red": "#ff0000",
      "green": "#008000",
      "blue": "#0000ff",
      "white": "#ffffff",
      "black": "#000000",
      "gray": "#808080",
      "lime": "#00ff00",
      "fuchsia": "#ff00ff",
      "transparent": "#00000000",
    }

    for name, expected_hex in basic_colors.items():
      color = parse_color(name)
      assert color is not None, f"Failed to parse color: {name}"

      if name == "transparent":
        assert color.alpha == 0
      else:
        # Convert back to hex for comparison
        actual_hex = f"#{color.red:02x}{color.green:02x}{color.blue:02x}"
        assert actual_hex == expected_hex, (
          f"Color {name}: expected {expected_hex}, got {actual_hex}"
        )

  def test_extended_svg_colors(self):
    """Test extended SVG color keywords."""
    extended_colors = [
      "cornflowerblue",
      "mediumseagreen",
      "darkslategray",
      "lightgoldenrodyellow",
      "palevioletred",
      "springgreen",
    ]

    for color_name in extended_colors:
      color = parse_color(color_name)
      assert color is not None, f"Failed to parse extended color: {color_name}"
      assert color.alpha == 255  # Should be opaque

  def test_color_name_variants(self):
    """Test color name variants (gray/grey)."""
    assert parse_color("gray").argb == parse_color("grey").argb
    assert parse_color("darkgray").argb == parse_color("darkgrey").argb
    assert parse_color("lightgray").argb == parse_color("lightgrey").argb

  def test_color_caching(self):
    """Test that color parsing uses caching effectively."""
    # Clear cache first (accessing private variable for testing)
    from src.ir.color import _svg_color_cache

    _svg_color_cache.clear()

    # First call should populate cache
    color1 = _get_svg_color("cornflowerblue")
    assert "cornflowerblue" in _svg_color_cache

    # Second call should use cache
    color2 = _get_svg_color("cornflowerblue")
    assert color1 is color2  # Should be same object from cache

  def test_invalid_color_names(self):
    """Test invalid color names return None."""
    invalid_names = ["notacolor", "invalidred", ""]
    for name in invalid_names:
      assert _get_svg_color(name) is None


class TestSmartColorNaming:
  """Test smart color naming features."""

  def test_to_name_exact_match(self):
    """Test exact color name matching for Compose built-in colors."""
    red = IrColor.from_rgb(255, 0, 0)
    assert red.to_compose_color_name() == "Red"

    blue = IrColor.from_rgb(0, 0, 255)
    assert blue.to_compose_color_name() == "Blue"

    # SVG lime maps to Compose Green
    lime = IrColor.from_hex("#00ff00")
    assert lime.to_compose_color_name() == "Green"

    # cornflowerblue is not a Compose built-in color
    cornflower = IrColor.from_hex("#6495ed")
    assert cornflower.to_compose_color_name() is None

  def test_to_name_with_alpha(self):
    """Test color name matching with alpha channel."""
    transparent_red = IrColor.from_rgb(255, 0, 0, 128)
    assert transparent_red.to_compose_color_name() == "Red"  # Should match RGB portion

    transparent_blue = IrColor.from_rgb(0, 0, 255, 64)
    assert transparent_blue.to_compose_color_name() == "Blue"

  def test_to_name_custom_colors(self):
    """Test that custom colors return None."""
    custom = IrColor.from_rgb(123, 45, 67)
    assert custom.to_compose_color_name() is None

  def test_solid_color_generation(self):
    """Test SolidColor generation with smart naming."""
    # Opaque named color
    red = IrColor.from_rgb(255, 0, 0)
    assert red.to_compose_solid_color() == "SolidColor(Color.Red)"

    # Transparent named color
    transparent_red = IrColor.from_rgb(255, 0, 0, 128)
    expected = "SolidColor(Color.Red.copy(alpha = 0.502f))"
    assert transparent_red.to_compose_solid_color() == expected

    # Custom color (no name)
    custom = IrColor.from_rgb(123, 45, 67)
    assert custom.to_compose_solid_color() == "SolidColor(Color(0xFF7B2D43))"

  def test_solid_color_without_naming(self):
    """Test SolidColor generation without smart naming."""
    red = IrColor.from_rgb(255, 0, 0)
    assert red.to_compose_solid_color(use_named_colors=False) == "SolidColor(Color(0xFFFF0000))"


class TestSvgIntegrationWithColors:
  """Test SVG parsing integration with enhanced color support."""

  def test_svg_with_advanced_colors(self):
    """Test SVG parsing with advanced color keywords."""
    svg_content = """<svg width="100" height="100" viewBox="0 0 100 100">
      <path d="M 10 10 L 50 10 L 50 50 L 10 50 Z" fill="cornflowerblue"/>
      <path d="M 60 10 L 90 10 L 90 50 L 60 50 Z" fill="mediumseagreen" stroke="darkslategray" stroke-width="2"/>
    </svg>"""

    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    # Check IR
    assert len(ir.nodes) == 2
    # Advanced colors like cornflowerblue are not Compose built-ins
    assert ir.nodes[0].fill.to_compose_color_name() is None
    assert ir.nodes[1].fill.to_compose_color_name() is None
    assert ir.nodes[1].stroke.to_compose_color_name() is None

  def test_code_generation_with_smart_colors(self):
    """Test code generation with Compose built-in colors."""
    svg_content = """<svg width="50" height="50" viewBox="0 0 50 50">
      <path d="M 5 5 L 45 5 L 45 45 L 5 45 Z" fill="red" stroke="blue" stroke-width="3"/>
    </svg>"""

    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    generator = ImageVectorGenerator()
    code = generator.generate(ir)

    # Check for smart color naming in output with Compose built-ins
    assert "fill = SolidColor(Color.Red)" in code
    assert "stroke = SolidColor(Color.Blue)" in code
    assert "strokeLineWidth = 3f" in code

  def test_transparent_colors_in_svg(self):
    """Test transparent color handling in SVG."""
    svg_content = """<svg width="50" height="50" viewBox="0 0 50 50">
      <path d="M 5 5 L 45 45" stroke="rgba(255, 0, 0, 0.5)" stroke-width="2"/>
    </svg>"""

    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    generator = ImageVectorGenerator()
    code = generator.generate(ir)

    # Should use smart naming with alpha
    assert "Color.Red.copy(alpha" in code
    assert "SolidColor(" in code

  def test_mixed_color_formats(self):
    """Test SVG with mixed color formats."""
    svg_content = """<svg width="100" height="100" viewBox="0 0 100 100">
      <path d="M 10 10 L 30 10 L 30 30 L 10 30 Z" fill="red"/>
      <path d="M 40 10 L 60 10 L 60 30 L 40 30 Z" fill="#00ff00"/>
      <path d="M 70 10 L 90 10 L 90 30 L 70 30 Z" fill="rgb(0, 0, 255)"/>
    </svg>"""

    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    generator = ImageVectorGenerator()
    code = generator.generate(ir)

    # Should use smart naming where possible
    assert "SolidColor(Color.Red)" in code  # Named color
    assert "SolidColor(Color.Green)" in code  # Hex #00ff00 matches Compose Green
    assert "SolidColor(Color.Blue)" in code  # RGB color that matches named


class TestColorApiCompliance:
  """Test compliance with Compose Color API requirements."""

  def test_brush_api_usage(self):
    """Test that colors are properly wrapped as Brush for path usage."""
    svg_content = """<svg width="50" height="50" viewBox="0 0 50 50">
      <path d="M 5 5 L 45 45" fill="red" stroke="blue"/>
    </svg>"""

    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    generator = ImageVectorGenerator()
    code = generator.generate(ir)

    # Should use SolidColor wrapper for Brush API
    assert "fill = SolidColor(" in code
    assert "stroke = SolidColor(" in code
    # Should NOT have direct Color usage in path
    assert "fill = Color(" not in code
    assert "stroke = Color(" not in code

  def test_required_imports(self):
    """Test that proper imports are generated."""
    svg_content = """<svg width="50" height="50" viewBox="0 0 50 50">
      <path d="M 5 5 L 45 45" fill="red"/>
    </svg>"""

    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    generator = ImageVectorGenerator()
    generator.generate(ir)  # Generate to populate imports
    imports = generator.get_required_imports()

    # Should include both Color and SolidColor imports
    assert "androidx.compose.ui.graphics.Color" in imports
    assert "androidx.compose.ui.graphics.SolidColor" in imports
