"""Tests for multi-color template system with intelligent color mapping."""

from pathlib import Path
from textwrap import dedent

import pytest

from src.core.config import Config
from src.generator.image_vector_generator import ImageVectorGenerator
from src.generator.template_engine import TemplateEngine
from src.parser.svg_parser import SvgParser
from src.utils.color_analyzer import ColorAnalyzer
from src.utils.color_substitution import ColorParameterSubstitution
from src.utils.naming import NameResolver


class TestColorAnalyzer:
  """Test color analysis functionality."""

  def test_extract_colors_from_simple_svg(self):
    """Test color extraction from simple multi-color SVG."""
    svg_content = dedent("""
      <svg width="24" height="24" viewBox="0 0 24 24">
        <circle fill="#2196F3" cx="6" cy="6" r="4"/>
        <rect fill="#FF9800" x="10" y="2" width="8" height="8"/>
      </svg>
    """).strip()

    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    analyzer = ColorAnalyzer()
    analysis = analyzer.analyze_colors(ir)

    expected_colors = {"#2196F3", "#FF9800"}
    assert analysis.used_colors == expected_colors
    assert analysis.is_multicolor is True
    assert analysis.color_count == 2

  def test_extract_colors_with_gradients(self):
    """Test color extraction from SVG with gradients."""
    svg_content = dedent("""
      <svg width="24" height="24" viewBox="0 0 24 24">
        <defs>
          <linearGradient id="grad1">
            <stop offset="0%" stop-color="#FF0000"/>
            <stop offset="100%" stop-color="#00FF00"/>
          </linearGradient>
        </defs>
        <rect fill="url(#grad1)" x="0" y="0" width="24" height="24"/>
        <circle fill="#0000FF" cx="12" cy="12" r="4"/>
      </svg>
    """).strip()

    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    analyzer = ColorAnalyzer()
    analysis = analyzer.analyze_colors(ir)

    expected_colors = {"#FF0000", "#00FF00", "#0000FF"}
    assert analysis.used_colors == expected_colors
    assert analysis.color_count == 3

  def test_single_color_analysis(self):
    """Test analysis of single-color SVG."""
    svg_content = dedent("""
      <svg width="24" height="24" viewBox="0 0 24 24">
        <path fill="#000000" d="M 0 0 L 24 0 L 24 24 L 0 24 Z"/>
      </svg>
    """).strip()

    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    analyzer = ColorAnalyzer()
    analysis = analyzer.analyze_colors(ir)

    assert analysis.used_colors == {"#000000"}
    assert analysis.is_multicolor is False
    assert analysis.color_count == 1

  def test_extract_colors_with_transparency(self):
    """Test color extraction from SVG with transparent colors."""
    svg_content = dedent("""
      <svg width="24" height="24" viewBox="0 0 24 24">
        <circle fill="#2196F3" fill-opacity="0.5" cx="6" cy="6" r="4"/>
        <rect fill="rgba(255, 152, 0, 0.8)" x="10" y="2" width="8" height="8"/>
        <path fill="#4CAF50" opacity="0.3" d="M 0 12 L 12 12 L 6 24 Z"/>
      </svg>
    """).strip()

    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    analyzer = ColorAnalyzer()
    analysis = analyzer.analyze_colors(ir)

    # Colors should be extracted in both base RGB and full ARGB formats for transparency
    expected_colors = {"#2196F3", "#FF9800", "#4CAF50", "#CCFF9800"}
    assert analysis.used_colors == expected_colors
    assert analysis.is_multicolor is True
    assert analysis.color_count == 4  # Includes ARGB format for transparent color


class TestColorParameterSubstitution:
  """Test color parameter substitution functionality."""

  def test_extract_color_mappings_from_template(self):
    """Test extraction of color mappings from Jinja2 template."""
    template_content = dedent("""
      {{- imports }}

      {%- set color_mappings = {
          "#2196F3": {"semantic_name": "primaryColor", "replacement": "MaterialTheme.colorScheme.primary"},
          "#FF9800": {"semantic_name": "accentColor", "replacement": "Color(0xFFFF9800)"}
      } -%}

      @Composable
      fun {{ name.name_part_pascal }}(): ImageVector {
        return {{ build_code_with_color_params }}
      }
    """).strip()

    substitution = ColorParameterSubstitution()
    mappings = substitution.extract_color_mappings_from_template(template_content)

    expected_mappings = {
      "#2196F3": {
        "semantic_name": "primaryColor",
        "replacement": "MaterialTheme.colorScheme.primary",
      },
      "#FF9800": {"semantic_name": "accentColor", "replacement": "Color(0xFFFF9800)"},
    }

    assert mappings == expected_mappings

  def test_substitute_solid_colors(self):
    """Test substitution of solid colors in generated code."""
    kotlin_code = dedent("""
      path(
        fill = SolidColor(Color(0xFF2196F3)),
      ) {
        moveTo(0f, 0f)
      }
      path(
        fill = SolidColor(Color(0xFF00FF00)),
      ) {
        lineTo(10f, 10f)
      }
    """).strip()

    color_mappings = {
      "#2196F3": {
        "semantic_name": "primaryColor",
        "replacement": "MaterialTheme.colorScheme.primary",
      },
      "#00FF00": {"semantic_name": "successColor", "replacement": "Color.Green"},
    }

    substitution = ColorParameterSubstitution()
    result = substitution.substitute_colors_in_code(kotlin_code, color_mappings)

    assert "SolidColor(primaryColor)" in result
    assert "SolidColor(successColor)" in result
    assert "Color(0xFF2196F3)" not in result
    assert "Color(0xFF00FF00)" not in result

  def test_substitute_gradient_colors(self):
    """Test substitution of colors in gradients."""
    kotlin_code = dedent("""
      fill = Brush.linearGradient(
        colorStops = arrayOf(
          0f to Color(0xFF2196F3),
          1f to Color(0xFFFF9800)
        )
      )
    """).strip()

    color_mappings = {
      "#2196F3": {
        "semantic_name": "primaryColor",
        "replacement": "MaterialTheme.colorScheme.primary",
      },
      "#FF9800": {"semantic_name": "accentColor", "replacement": "Color(0xFFFF9800)"},
    }

    substitution = ColorParameterSubstitution()
    result = substitution.substitute_colors_in_code(kotlin_code, color_mappings)

    assert "0f to primaryColor" in result
    assert "1f to accentColor" in result

  def test_partial_color_mapping(self):
    """Test that unmapped colors remain unchanged."""
    kotlin_code = dedent("""
      path(fill = SolidColor(Color(0xFF2196F3))) { }
      path(fill = SolidColor(Color(0xFF9C27B0))) { }
    """).strip()

    color_mappings = {
      "#2196F3": {
        "semantic_name": "primaryColor",
        "replacement": "MaterialTheme.colorScheme.primary",
      }
      # #9C27B0 is intentionally not mapped
    }

    substitution = ColorParameterSubstitution()
    result = substitution.substitute_colors_in_code(kotlin_code, color_mappings)

    assert "SolidColor(primaryColor)" in result
    assert "Color(0xFF9C27B0)" in result  # Should remain unchanged

  def test_substitute_colors_with_transparency(self):
    """Test substitution of colors with alpha/transparency handling."""
    kotlin_code = dedent("""
      path(
        fill = SolidColor(Color(0x802196F3)),  // Semi-transparent blue
      ) {
        moveTo(0f, 0f)
      }
      path(
        fill = SolidColor(Color(0xCCFF9800)),  // Semi-transparent orange
      ) {
        lineTo(10f, 10f)
      }
    """).strip()

    color_mappings = {
      "#2196F3": {
        "semantic_name": "primaryColor",
        "replacement": "MaterialTheme.colorScheme.primary",
      },
      "#FF9800": {"semantic_name": "accentColor", "replacement": "Color(0xFFFF9800)"},
    }

    substitution = ColorParameterSubstitution()
    result = substitution.substitute_colors_in_code(kotlin_code, color_mappings)

    # Transparent colors should NOT be substituted (different ARGB values)
    assert "Color(0x802196F3)" in result  # Should remain unchanged
    assert "Color(0xCCFF9800)" in result  # Should remain unchanged
    assert "primaryColor" not in result
    assert "accentColor" not in result

  def test_template_with_transparency_mapping(self):
    """Test template that specifically maps transparent colors."""
    template_content = dedent("""
      {{- imports }}

      {%- set color_mappings = {
          "#2196F3": {"semantic_name": "primaryColor", "replacement": "MaterialTheme.colorScheme.primary.copy(alpha = 0.5f)"},
          "#FF9800": {"semantic_name": "accentColor", "replacement": "MaterialTheme.colorScheme.secondary.copy(alpha = 0.8f)"}
      } -%}

      @Composable
      fun {{ name.name_part_pascal }}(): ImageVector {
        return {{ build_code_with_color_params }}
      }
    """).strip()

    substitution = ColorParameterSubstitution()
    mappings = substitution.extract_color_mappings_from_template(template_content)

    expected_mappings = {
      "#2196F3": {
        "semantic_name": "primaryColor",
        "replacement": "MaterialTheme.colorScheme.primary.copy(alpha = 0.5f)",
      },
      "#FF9800": {
        "semantic_name": "accentColor",
        "replacement": "MaterialTheme.colorScheme.secondary.copy(alpha = 0.8f)",
      },
    }

    assert mappings == expected_mappings


class TestMultiColorTemplateIntegration:
  """Integration tests for complete multi-color template system."""

  def test_multicolor_template_selection_with_intersection(self):
    """Test that multicolor template is used when colors intersect with mappings."""
    # Create test SVG with colors that match template mappings
    svg_content = dedent("""
      <svg width="24" height="24" viewBox="0 0 24 24">
        <circle fill="#2196F3" cx="6" cy="6" r="4"/>
        <rect fill="#FF9800" x="10" y="2" width="8" height="8"/>
        <path fill="#9C27B0" d="M 0 12 L 12 12 L 6 24 Z"/>
      </svg>
    """).strip()

    # Create multicolor template
    multicolor_template = dedent("""
      {{- imports }}

      {%- set color_mappings = {
          "#2196F3": {"semantic_name": "primaryColor", "replacement": "MaterialTheme.colorScheme.primary"},
          "#FF9800": {"semantic_name": "accentColor", "replacement": "Color(0xFFFF9800)"}
      } -%}

      @Composable
      fun {{ name.name_part_pascal }}(
      {%- for color_hex, mapping in color_mappings.items() if color_hex in used_colors %}
        {{ mapping.semantic_name }}: Color = {{ mapping.replacement }}{{ "," if not loop.last }}
      {%- endfor %}
      ): ImageVector {
        return {{ build_code_with_color_params }}
      }
    """).strip()

    # Parse and generate
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    name_resolver = NameResolver()
    name_components = name_resolver.resolve_name_from_string("TestIcon")
    ir.name = name_components.name_part_pascal

    generator = ImageVectorGenerator()
    core_code, imports = generator.generate_core_code(ir)

    # Create temporary template file
    import tempfile

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
      assert "fun TestIcon(" in result
      assert "primaryColor: Color = MaterialTheme.colorScheme.primary" in result
      assert "accentColor: Color = Color(0xFFFF9800)" in result

      # Verify color substitution worked
      assert "SolidColor(primaryColor)" in result
      assert "SolidColor(accentColor)" in result

      # Verify unmapped color remained unchanged
      assert "Color(0xFF9C27B0)" in result

    finally:
      template_path.unlink()  # Clean up

  def test_fallback_to_default_template_no_intersection(self):
    """Test fallback to default template when no color intersection exists."""
    # Create test SVG with colors that DON'T match template mappings
    svg_content = dedent("""
      <svg width="24" height="24" viewBox="0 0 24 24">
        <circle fill="#9C27B0" cx="12" cy="12" r="8"/>
        <rect fill="#009688" x="0" y="0" width="8" height="8"/>
      </svg>
    """).strip()

    # Create multicolor template with different colors
    multicolor_template = dedent("""
      {{- imports }}

      {%- set color_mappings = {
          "#2196F3": {"semantic_name": "primaryColor", "replacement": "MaterialTheme.colorScheme.primary"},
          "#FF9800": {"semantic_name": "accentColor", "replacement": "Color(0xFFFF9800)"}
      } -%}

      @Composable
      fun {{ name.name_part_pascal }}(): ImageVector {
        return {{ build_code_with_color_params }}
      }
    """).strip()

    # Parse and generate
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    name_resolver = NameResolver()
    name_components = name_resolver.resolve_name_from_string("TestIcon")
    ir.name = name_components.name_part_pascal

    generator = ImageVectorGenerator()
    core_code, imports = generator.generate_core_code(ir)

    # Create temporary template file
    import tempfile

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

      # Verify default template was used (should not contain @Composable function)
      assert "@Composable" not in result
      assert "fun TestIcon(" not in result

      # Should contain the basic ImageVector.Builder code
      assert "ImageVector.Builder(" in result
      assert ".build()" in result

    finally:
      template_path.unlink()  # Clean up

  def test_template_selection_logic(self):
    """Test the core template selection decision logic."""
    analyzer = ColorAnalyzer()

    # Test case 1: Intersection exists -> use multicolor template
    svg_colors = {"#2196F3", "#FF9800", "#9C27B0"}
    template_colors = {"#2196F3", "#4CAF50"}

    should_use = analyzer.should_use_multicolor_template(svg_colors, template_colors)
    assert should_use is True

    # Test case 2: No intersection -> use default template
    svg_colors = {"#9C27B0", "#009688"}
    template_colors = {"#2196F3", "#FF9800"}

    should_use = analyzer.should_use_multicolor_template(svg_colors, template_colors)
    assert should_use is False

    # Test case 3: Empty template colors -> use default template
    svg_colors = {"#2196F3"}
    template_colors = set()

    should_use = analyzer.should_use_multicolor_template(svg_colors, template_colors)
    assert should_use is False

  def test_end_to_end_transparent_colors_mapping(self):
    """Test mapping of SVG colors that include transparency (RGBA) to template parameters."""
    # Create SVG with RGBA colors (semi-transparent colors)
    svg_content = dedent("""
      <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <circle cx="6" cy="6" r="4" fill="rgba(33, 150, 243, 0.8)"/>
        <rect x="10" y="2" width="8" height="8" fill="rgba(255, 152, 0, 0.6)"/>
        <path d="M 0 12 L 12 12 L 6 24 Z" fill="#4CAF50"/>
      </svg>
    """).strip()

    # Create multicolor template that maps colors with their exact ARGB values
    multicolor_template = dedent("""
      {{- imports }}

      {%- set color_mappings = {
          "#CC2196F3": {"semantic_name": "primaryColor", "replacement": "MaterialTheme.colorScheme.primary"},
          "#99FF9800": {"semantic_name": "accentColor", "replacement": "MaterialTheme.colorScheme.secondary"},
          "#4CAF50": {"semantic_name": "successColor", "replacement": "Color.Green"}
      } -%}

      @Composable
      fun {{ name.name_part_pascal }}(
      {%- for color_hex, mapping in color_mappings.items() if color_hex in used_colors %}
        {{ mapping.semantic_name }}: Color = {{ mapping.replacement }}{{ "," if not loop.last }}
      {%- endfor %}
      ): ImageVector {
        return {{ build_code_with_color_params }}
      }
    """).strip()

    # Parse and generate
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    name_resolver = NameResolver()
    name_components = name_resolver.resolve_name_from_string("TransparentColorsIcon")
    ir.name = name_components.name_part_pascal

    generator = ImageVectorGenerator()
    core_code, imports = generator.generate_core_code(ir)

    # Create temporary template file
    import tempfile

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
      assert "fun TransparentColorsIcon(" in result

      # Verify parameters are present (should include all colors that have mappings)
      assert "primaryColor: Color = MaterialTheme.colorScheme.primary" in result
      assert "accentColor: Color = MaterialTheme.colorScheme.secondary" in result
      assert "successColor: Color = Color.Green" in result

      # Verify color substitution worked for mapped colors
      assert "fill = SolidColor(primaryColor)," in result
      assert "fill = SolidColor(accentColor)," in result
      assert "fill = SolidColor(successColor)," in result

      # Verify that original transparent hex colors with alpha are NOT present as hex values
      # (The system should extract base colors for mapping, regardless of alpha)
      assert "Color(0xCC2196F3)" not in result  # 0.8 alpha version
      assert "Color(0x992196F3)" not in result  # 0.6 alpha version

      # Verify proper structure
      assert "return ImageVector.Builder(" in result
      assert "}.build()" in result

    finally:
      template_path.unlink()  # Clean up


class TestMultiColorOutputPrecision:
  """Test output precision and formatting for multi-color templates."""

  def test_complete_output_with_whitespace_preservation(self):
    """Test complete multicolor template output including blank line preservation."""
    
    svg_content = dedent("""
      <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <circle cx="6" cy="6" r="4" fill="#2196F3"/>
        <rect x="12" y="2" width="8" height="8" fill="#FF9800"/>
      </svg>
    """).strip()

    # Template with strategic blank lines that should be preserved
    multicolor_template = dedent("""
      {{ imports }}

      {%- set color_mappings = {
          "#2196F3": {"semantic_name": "primaryColor", "replacement": "MaterialTheme.colorScheme.primary"},
          "#FF9800": {"semantic_name": "accentColor", "replacement": "Color(0xFFFF9800)"}
      } %}

      @Composable
      fun {{ name.name_part_pascal }}(
      {%- for color_hex, mapping in color_mappings.items() if color_hex in used_colors %}
        {{ mapping.semantic_name }}: Color = {{ mapping.replacement }}{{ "," if not loop.last }}
      {%- endfor %}
      ): ImageVector {
        return {{ build_code_with_color_params }}
      }
    """).strip()

    # Parse and generate
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    name_resolver = NameResolver()
    name_components = name_resolver.resolve_name_from_string("WhitespaceTestIcon")
    ir.name = name_components.name_part_pascal

    generator = ImageVectorGenerator()
    core_code, imports = generator.generate_core_code(ir)

    # Create temporary template file
    import tempfile

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

      # Test the specific structure we expect from color mapping section
      lines = result.split("\n")
      
      # Find the blank line after imports
      blank_line_found = False
      composable_line_idx = -1
      for i, line in enumerate(lines):
        if line.startswith("import "):
          continue
        elif line.strip() == "":
          # This should be the blank line after imports
          if i > 0 and lines[i-1].startswith("import "):
            blank_line_found = True
            composable_line_idx = i + 1
            assert lines[i+1].strip() == "@Composable", f"Expected @Composable after blank line, got: '{lines[i+1]}'"
            break
      
      assert blank_line_found, "No blank line found after imports"
      
      # Verify function structure
      assert lines[composable_line_idx] == "@Composable"
      assert "fun WhitespaceTestIcon(" in lines[composable_line_idx + 1]
      
      # Verify parameters are properly formatted (they are on separate lines)
      # The parameters should be on lines 8 and 9 based on debug output
      param_lines = [lines[8], lines[9]]
      param_content = " ".join(line.strip() for line in param_lines)
      assert "primaryColor: Color = MaterialTheme.colorScheme.primary" in param_content
      assert "accentColor: Color = Color(0xFFFF9800)" in param_content

      # Verify color substitution worked
      assert "fill = SolidColor(primaryColor)," in result
      assert "fill = SolidColor(accentColor)," in result

      # Verify complete structure
      assert "return ImageVector.Builder(" in result
      assert "}.build()" in result

      # Test the complete expected structure
      expected_structure_checks = [
        # Should have imports
        "import androidx.compose.ui.graphics.Color",
        "import androidx.compose.ui.graphics.SolidColor", 
        "import androidx.compose.ui.graphics.vector.ImageVector",
        # Should have blank line, then @Composable
        # Should have proper function structure
        "@Composable",
        "fun WhitespaceTestIcon(",
        "primaryColor: Color = MaterialTheme.colorScheme.primary",
        "accentColor: Color = Color(0xFFFF9800)",
        "): ImageVector {",
        # Should have ImageVector structure
        "return ImageVector.Builder(",
        'name = "WhitespaceTestIcon",',
        "defaultWidth = 24.dp,",
        "defaultHeight = 24.dp,",
        "viewportWidth = 24f,",
        "viewportHeight = 24f,",
        # Should have color-substituted paths
        "fill = SolidColor(primaryColor),",
        "fill = SolidColor(accentColor),",
        # Should end properly
        "}.build()",
        "}"
      ]
      
      for expected in expected_structure_checks:
        assert expected in result, f"Expected structure element missing: '{expected}'"

    finally:
      template_path.unlink()  # Clean up

  def test_complete_multicolor_output_format(self):
    """Test complete output format matches expected structure exactly."""
    # Create test SVG with specific colors
    svg_content = dedent("""
      <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <circle cx="6" cy="6" r="4" fill="#2196F3"/>
        <rect x="12" y="2" width="8" height="8" fill="#FF9800"/>
      </svg>
    """).strip()

    # Create multicolor template
    multicolor_template = dedent("""
      {{- imports }}

      {%- set color_mappings = {
          "#2196F3": {"semantic_name": "primaryColor", "replacement": "MaterialTheme.colorScheme.primary"},
          "#FF9800": {"semantic_name": "accentColor", "replacement": "Color(0xFFFF9800)"}
      } -%}

      @Composable
      fun {{ name.name_part_pascal }}(
      {%- for color_hex, mapping in color_mappings.items() if color_hex in used_colors %}
        {{ mapping.semantic_name }}: Color = {{ mapping.replacement }}{{ "," if not loop.last }}
      {%- endfor %}
      ): ImageVector {
        return {{ build_code_with_color_params }}
      }
    """).strip()

    # Parse and generate
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    name_resolver = NameResolver()
    name_components = name_resolver.resolve_name_from_string("MultiColorIcon")
    ir.name = name_components.name_part_pascal

    generator = ImageVectorGenerator()
    core_code, imports = generator.generate_core_code(ir)

    # Create temporary template file
    import tempfile

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

      # Verify essential components of the output
      lines = result.split("\n")

      # Check imports exist
      assert any("import androidx.compose.ui.graphics.Color" in line for line in lines)
      assert any("import androidx.compose.ui.graphics.SolidColor" in line for line in lines)
      assert any("import androidx.compose.ui.graphics.vector.ImageVector" in line for line in lines)

      # Check function signature
      assert "@Composable" in result
      assert "fun MultiColorIcon(" in result
      assert "primaryColor: Color = MaterialTheme.colorScheme.primary" in result
      assert "accentColor: Color = Color(0xFFFF9800)" in result
      assert "): ImageVector {" in result

      # Check ImageVector.Builder structure
      assert "return ImageVector.Builder(" in result
      assert 'name = "MultiColorIcon",' in result
      assert "defaultWidth = 24.dp," in result
      assert "defaultHeight = 24.dp," in result
      assert "viewportWidth = 24f," in result
      assert "viewportHeight = 24f," in result

      # Check color substitution worked
      assert "fill = SolidColor(primaryColor)," in result
      assert "fill = SolidColor(accentColor)," in result

      # Ensure original hex colors are NOT present in fill statements (only in parameter defaults)
      assert "fill = SolidColor(Color(0xFF2196F3))" not in result
      assert "fill = SolidColor(Color(0xFFFF9800))" not in result

      # But Color(0xFFFF9800) should appear in parameter default value
      assert "accentColor: Color = Color(0xFFFF9800)" in result

      # Check path operations
      assert "moveTo(" in result
      assert "arcTo(" in result
      assert "lineTo(" in result
      assert "close()" in result

      # Check proper closing
      assert "}.build()" in result
      assert result.strip().endswith("}")

      # Check the function signature format
      # Parameters are now on separate lines
      function_start_line = None
      for i, line in enumerate(lines):
        if "fun MultiColorIcon(" in line:
          function_start_line = i
          break

      assert function_start_line is not None, "Function declaration not found"

      # Verify that both parameters are present in the following lines
      # (parameters are now on separate lines)
      function_section = "\n".join(lines[function_start_line:function_start_line+5])
      assert "primaryColor: Color = MaterialTheme.colorScheme.primary" in function_section
      assert "accentColor: Color = Color(0xFFFF9800)" in function_section

      # Check that imports and @Composable are properly separated
      # Find line with @Composable
      composable_line_index = None
      for i, line in enumerate(lines):
        if "@Composable" in line:
          composable_line_index = i
          break

      assert composable_line_index is not None, "@Composable annotation not found"

      # The line before @Composable should be imports only
      if composable_line_index > 0:
        prev_line = lines[composable_line_index - 1]
        # Should be an import line or empty
        assert prev_line.startswith("import ") or prev_line.strip() == "", (
          f"Unexpected line before @Composable: {prev_line}"
        )

    finally:
      template_path.unlink()  # Clean up

  def test_direct_color_replacement_without_parameters(self):
    """Test that colors can be directly replaced without creating function parameters."""

    # Create SVG with colors that should be directly replaced
    svg_content = dedent("""
      <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <rect x="0" y="0" width="12" height="12" fill="#FF0000"/>   <!-- Red -> Direct replacement -->
        <rect x="12" y="0" width="12" height="12" fill="#0000FF"/>  <!-- Blue -> Direct replacement -->
        <rect x="0" y="12" width="24" height="12" fill="#00FF00"/>  <!-- Green -> Direct replacement -->
      </svg>
    """).strip()

    # Create multicolor template with simplified color mappings (no semantic_name)
    multicolor_template = dedent("""
      {{- imports }}

      {%- set color_mappings = {
          "#FF0000": "MaterialTheme.colorScheme.error",
          "#0000FF": "MaterialTheme.colorScheme.primary",
          "#00FF00": "MaterialTheme.colorScheme.secondary"
      } -%}

      @Composable
      fun {{ name.name_part_pascal }}(): ImageVector {
        return {{ build_code_with_color_params }}
      }
    """).strip()

    # Parse and generate
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    name_resolver = NameResolver()
    name_components = name_resolver.resolve_name_from_string("DirectReplacementIcon")
    ir.name = name_components.name_part_pascal

    generator = ImageVectorGenerator()
    core_code, imports = generator.generate_core_code(ir)

    # Create temporary template file
    import tempfile

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
      assert "fun DirectReplacementIcon(): ImageVector" in result

      # Verify NO function parameters (since we're using direct replacement)
      assert "fun DirectReplacementIcon():" in result  # No parameters
      assert "primaryColor:" not in result
      assert "errorColor:" not in result
      assert "secondaryColor:" not in result

      # Verify direct color replacements worked
      assert "fill = SolidColor(MaterialTheme.colorScheme.error)," in result
      assert "fill = SolidColor(MaterialTheme.colorScheme.primary)," in result
      assert "fill = SolidColor(MaterialTheme.colorScheme.secondary)," in result

      # Verify NO hex colors remain
      assert "Color(0xFFFF0000)" not in result
      assert "Color(0xFF0000FF)" not in result
      assert "Color(0xFF00FF00)" not in result

    finally:
      template_path.unlink()  # Clean up

  def test_mixed_semantic_and_direct_replacement(self):
    """Test template with both semantic parameters and direct replacements."""

    svg_content = dedent("""
      <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <rect x="0" y="0" width="8" height="8" fill="#FF0000"/>   <!-- Red -> Parameter -->
        <rect x="8" y="0" width="8" height="8" fill="#0000FF"/>  <!-- Blue -> Direct replacement -->
        <rect x="16" y="0" width="8" height="8" fill="#00FF00"/> <!-- Green -> Direct replacement -->
        <rect x="0" y="8" width="24" height="8" fill="#FFFF00"/> <!-- Yellow -> Parameter -->
      </svg>
    """).strip()

    # Template mixing semantic parameters and direct replacements
    multicolor_template = dedent("""
      {{- imports }}

      {%- set color_mappings = {
          "#FF0000": {"semantic_name": "errorColor", "replacement": "Color.Red"},
          "#0000FF": "MaterialTheme.colorScheme.primary",
          "#00FF00": "MaterialTheme.colorScheme.secondary",
          "#FFFF00": {"semantic_name": "warningColor", "replacement": "Color.Yellow"}
      } -%}

      @Composable
      fun {{ name.name_part_pascal }}(
      {%- for color_hex, mapping in color_mappings.items() if color_hex in used_colors %}
        {%- if mapping is mapping and mapping.semantic_name is defined %}
        {{ mapping.semantic_name }}: Color = {{ mapping.replacement }}{{ "," if not loop.last }}
        {%- endif %}
      {%- endfor %}
      ): ImageVector {
        return {{ build_code_with_color_params }}
      }
    """).strip()

    # Parse and generate
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    name_resolver = NameResolver()
    name_components = name_resolver.resolve_name_from_string("MixedMappingIcon")
    ir.name = name_components.name_part_pascal

    generator = ImageVectorGenerator()
    core_code, imports = generator.generate_core_code(ir)

    # Create temporary template file
    import tempfile

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

      # Verify function has only semantic parameters (not direct replacements)
      assert "errorColor: Color = Color.Red" in result
      assert "warningColor: Color = Color.Yellow" in result

      # Verify semantic parameter substitutions
      assert "fill = SolidColor(errorColor)," in result
      assert "fill = SolidColor(warningColor)," in result

      # Verify direct replacements
      assert "fill = SolidColor(MaterialTheme.colorScheme.primary)," in result
      assert "fill = SolidColor(MaterialTheme.colorScheme.secondary)," in result

      # Verify no direct replacement values appear as parameters
      assert "MaterialTheme.colorScheme.primary:" not in result
      assert "MaterialTheme.colorScheme.secondary:" not in result

    finally:
      template_path.unlink()  # Clean up


if __name__ == "__main__":
  pytest.main([__file__])
