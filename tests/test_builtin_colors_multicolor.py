"""Tests for built-in color mapping in multicolor templates."""

import tempfile
from pathlib import Path
from textwrap import dedent

import pytest

from src.core.config import Config
from src.generator.image_vector_generator import ImageVectorGenerator
from src.generator.template_engine import TemplateEngine
from src.parser.svg_parser import SvgParser
from src.utils.naming import NameResolver


class TestBuiltinColorsMulticolor:
  """Test multicolor template support for Compose built-in colors."""

  def test_basic_builtin_colors_mapping(self):
    """Test that common built-in colors are properly mapped in multicolor templates."""

    # Create SVG with colors that map to Compose built-in colors
    svg_content = dedent("""
      <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <!-- Black circle -->
        <circle cx="6" cy="6" r="4" fill="#000000"/>

        <!-- Red rectangle -->
        <rect x="12" y="2" width="8" height="8" fill="#FF0000"/>

        <!-- White triangle -->
        <path d="M 2 14 L 10 14 L 6 22 Z" fill="#FFFFFF"/>

        <!-- Blue path -->
        <path d="M 14 14 Q 18 14 22 18 Q 18 22 14 22 Z" fill="#0000FF"/>

        <!-- Custom color - should NOT be mapped -->
        <circle cx="18" cy="18" r="2" fill="#9C27B0"/>
      </svg>
    """).strip()

    # Create multicolor template with built-in color mappings
    multicolor_template = dedent("""
      {{- imports }}

      {%- set color_mappings = {
          "#000000": {"semantic_name": "primaryColor", "default_value": "Color.Black"},
          "#FF0000": {"semantic_name": "dangerColor", "default_value": "Color.Red"},
          "#FFFFFF": {"semantic_name": "backgroundColor", "default_value": "Color.White"},
          "#0000FF": {"semantic_name": "accentColor", "default_value": "Color.Blue"}
      } -%}

      @Composable
      fun {{ name.name_part_pascal }}(
      {%- for color_hex, mapping in color_mappings.items() if color_hex in used_colors %}
        {{ mapping.semantic_name }}: Color = {{ mapping.default_value }}{{ "," if not loop.last }}
      {%- endfor %}
      ): ImageVector {
        return {{ build_code_with_color_params }}
      }
    """).strip()

    # Parse and generate
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    name_resolver = NameResolver()
    name_components = name_resolver.resolve_name_from_string("BuiltinColorsIcon")
    ir.name = name_components.name_part_pascal

    generator = ImageVectorGenerator()
    core_code, imports = generator.generate_core_code(ir)

    # Create temporary template file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".j2", delete=False) as f:
      f.write(multicolor_template)
      template_path = Path(f.name)

    try:
      config = Config()
      template_engine = TemplateEngine(config)

      result = template_engine.render_with_multicolor_support(
        template_name="default",
        build_code=core_code,
        imports=imports,
        ir=ir,
        multicolor_template_path=template_path,
        name_components=name_components,
      )

      # Verify multicolor template was used
      assert "@Composable" in result
      assert "fun BuiltinColorsIcon(" in result

      # Verify built-in color parameters are in function signature
      assert "primaryColor: Color = Color.Black" in result
      assert "dangerColor: Color = Color.Red" in result
      assert "backgroundColor: Color = Color.White" in result
      assert "accentColor: Color = Color.Blue" in result

      # Verify color substitution worked with built-in colors
      assert "fill = SolidColor(primaryColor)," in result
      assert "fill = SolidColor(dangerColor)," in result
      assert "fill = SolidColor(backgroundColor)," in result
      assert "fill = SolidColor(accentColor)," in result

      # Verify unmapped custom color remained unchanged
      assert "Color(0xFF9C27B0)" in result

      # Verify NO built-in color names are used in fill statements (only parameters)
      assert "fill = SolidColor(Color.Black)" not in result
      assert "fill = SolidColor(Color.Red)" not in result
      assert "fill = SolidColor(Color.White)" not in result
      assert "fill = SolidColor(Color.Blue)" not in result

    finally:
      template_path.unlink()  # Clean up

  def test_extended_builtin_colors_mapping(self):
    """Test extended set of built-in colors including grays and other colors."""

    # Create SVG with more built-in colors
    svg_content = dedent("""
      <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <rect x="0" y="0" width="4" height="4" fill="#808080"/>   <!-- Gray -->
        <rect x="4" y="0" width="4" height="4" fill="#CCCCCC"/>   <!-- LightGray -->
        <rect x="8" y="0" width="4" height="4" fill="#444444"/>   <!-- DarkGray -->
        <rect x="12" y="0" width="4" height="4" fill="#FFFF00"/>  <!-- Yellow -->
        <rect x="16" y="0" width="4" height="4" fill="#00FFFF"/>  <!-- Cyan -->
        <rect x="20" y="0" width="4" height="4" fill="#FF00FF"/>  <!-- Magenta -->
      </svg>
    """).strip()

    # Create multicolor template with extended built-in color mappings
    multicolor_template = dedent("""
      {{- imports }}

      {%- set color_mappings = {
          "#808080": {"semantic_name": "neutralColor", "default_value": "Color.Gray"},
          "#CCCCCC": {"semantic_name": "lightColor", "default_value": "Color.LightGray"},
          "#444444": {"semantic_name": "darkColor", "default_value": "Color.DarkGray"},
          "#FFFF00": {"semantic_name": "warningColor", "default_value": "Color.Yellow"},
          "#00FFFF": {"semantic_name": "infoColor", "default_value": "Color.Cyan"},
          "#FF00FF": {"semantic_name": "highlightColor", "default_value": "Color.Magenta"}
      } -%}

      @Composable
      fun {{ name.name_part_pascal }}(
      {%- for color_hex, mapping in color_mappings.items() if color_hex in used_colors %}
        {{ mapping.semantic_name }}: Color = {{ mapping.default_value }}{{ "," if not loop.last }}
      {%- endfor %}
      ): ImageVector {
        return {{ build_code_with_color_params }}
      }
    """).strip()

    # Parse and generate
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    name_resolver = NameResolver()
    name_components = name_resolver.resolve_name_from_string("ExtendedColorsIcon")
    ir.name = name_components.name_part_pascal

    generator = ImageVectorGenerator()
    core_code, imports = generator.generate_core_code(ir)

    # Create temporary template file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".j2", delete=False) as f:
      f.write(multicolor_template)
      template_path = Path(f.name)

    try:
      config = Config()
      template_engine = TemplateEngine(config)

      result = template_engine.render_with_multicolor_support(
        template_name="default",
        build_code=core_code,
        imports=imports,
        ir=ir,
        multicolor_template_path=template_path,
        name_components=name_components,
      )

      # Verify all extended built-in color parameters
      assert "neutralColor: Color = Color.Gray" in result
      assert "lightColor: Color = Color.LightGray" in result
      assert "darkColor: Color = Color.DarkGray" in result
      assert "warningColor: Color = Color.Yellow" in result
      assert "infoColor: Color = Color.Cyan" in result
      assert "highlightColor: Color = Color.Magenta" in result

      # Verify all substitutions worked
      assert "fill = SolidColor(neutralColor)," in result
      assert "fill = SolidColor(lightColor)," in result
      assert "fill = SolidColor(darkColor)," in result
      assert "fill = SolidColor(warningColor)," in result
      assert "fill = SolidColor(infoColor)," in result
      assert "fill = SolidColor(highlightColor)," in result

    finally:
      template_path.unlink()  # Clean up

  def test_mixed_builtin_and_hex_colors(self):
    """Test template with mix of built-in colors and custom hex colors."""

    svg_content = dedent("""
      <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <rect x="0" y="0" width="8" height="8" fill="#FF0000"/>   <!-- Red (built-in) -->
        <rect x="8" y="0" width="8" height="8" fill="#2196F3"/>   <!-- Custom blue -->
        <rect x="16" y="0" width="8" height="8" fill="#000000"/>  <!-- Black (built-in) -->
        <rect x="0" y="8" width="24" height="8" fill="#FF9800"/>  <!-- Custom orange -->
      </svg>
    """).strip()

    # Template mixing built-in and custom colors
    multicolor_template = dedent("""
      {{- imports }}

      {%- set color_mappings = {
          "#FF0000": {"semantic_name": "errorColor", "default_value": "Color.Red"},
          "#2196F3": {"semantic_name": "primaryColor", "default_value": "MaterialTheme.colorScheme.primary"},
          "#000000": {"semantic_name": "textColor", "default_value": "Color.Black"},
          "#FF9800": {"semantic_name": "accentColor", "default_value": "Color(0xFFFF9800)"}
      } -%}

      @Composable
      fun {{ name.name_part_pascal }}(
      {%- for color_hex, mapping in color_mappings.items() if color_hex in used_colors %}
        {{ mapping.semantic_name }}: Color = {{ mapping.default_value }}{{ "," if not loop.last }}
      {%- endfor %}
      ): ImageVector {
        return {{ build_code_with_color_params }}
      }
    """).strip()

    # Parse and generate
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    name_resolver = NameResolver()
    name_components = name_resolver.resolve_name_from_string("MixedColorsIcon")
    ir.name = name_components.name_part_pascal

    generator = ImageVectorGenerator()
    core_code, imports = generator.generate_core_code(ir)

    # Create temporary template file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".j2", delete=False) as f:
      f.write(multicolor_template)
      template_path = Path(f.name)

    try:
      config = Config()
      template_engine = TemplateEngine(config)

      result = template_engine.render_with_multicolor_support(
        template_name="default",
        build_code=core_code,
        imports=imports,
        ir=ir,
        multicolor_template_path=template_path,
        name_components=name_components,
      )

      # Verify mixed parameter types
      assert "errorColor: Color = Color.Red" in result  # Built-in
      assert "primaryColor: Color = MaterialTheme.colorScheme.primary" in result  # Material Theme
      assert "textColor: Color = Color.Black" in result  # Built-in
      assert "accentColor: Color = Color(0xFFFF9800)" in result  # Custom hex

      # Verify all substitutions worked
      assert "fill = SolidColor(errorColor)," in result
      assert "fill = SolidColor(primaryColor)," in result
      assert "fill = SolidColor(textColor)," in result
      assert "fill = SolidColor(accentColor)," in result

    finally:
      template_path.unlink()  # Clean up

  def test_gradient_with_builtin_colors(self):
    """Test multicolor template with gradients containing built-in colors."""

    svg_content = dedent("""
      <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="redToBlue">
            <stop offset="0%" stop-color="#FF0000"/>
            <stop offset="100%" stop-color="#0000FF"/>
          </linearGradient>
        </defs>
        <rect x="0" y="0" width="24" height="24" fill="url(#redToBlue)"/>
      </svg>
    """).strip()

    # Template mapping gradient colors to built-in colors
    multicolor_template = dedent("""
      {{- imports }}

      {%- set color_mappings = {
          "#FF0000": {"semantic_name": "startColor", "default_value": "Color.Red"},
          "#0000FF": {"semantic_name": "endColor", "default_value": "Color.Blue"}
      } -%}

      @Composable
      fun {{ name.name_part_pascal }}(
      {%- for color_hex, mapping in color_mappings.items() if color_hex in used_colors %}
        {{ mapping.semantic_name }}: Color = {{ mapping.default_value }}{{ "," if not loop.last }}
      {%- endfor %}
      ): ImageVector {
        return {{ build_code_with_color_params }}
      }
    """).strip()

    # Parse and generate
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    name_resolver = NameResolver()
    name_components = name_resolver.resolve_name_from_string("GradientIcon")
    ir.name = name_components.name_part_pascal

    generator = ImageVectorGenerator()
    core_code, imports = generator.generate_core_code(ir)

    # Create temporary template file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".j2", delete=False) as f:
      f.write(multicolor_template)
      template_path = Path(f.name)

    try:
      config = Config()
      template_engine = TemplateEngine(config)

      result = template_engine.render_with_multicolor_support(
        template_name="default",
        build_code=core_code,
        imports=imports,
        ir=ir,
        multicolor_template_path=template_path,
        name_components=name_components,
      )

      # Verify gradient color parameters
      assert "startColor: Color = Color.Red" in result
      assert "endColor: Color = Color.Blue" in result

      # Verify gradient substitutions worked
      assert "0f to startColor" in result
      assert "1f to endColor" in result

      # Verify NO built-in color names in gradient array
      assert "0f to Color.Red" not in result
      assert "1f to Color.Blue" not in result

    finally:
      template_path.unlink()  # Clean up


if __name__ == "__main__":
  pytest.main([__file__])
