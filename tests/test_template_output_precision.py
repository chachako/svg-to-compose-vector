from textwrap import dedent

from src.parser.svg_parser import SvgParser
from src.generator.image_vector_generator import ImageVectorGenerator
from src.generator.template_engine import TemplateEngine
from src.core.config import Config


class TestTemplateOutputPrecision:
  """Test precise output matching for templates with exact string comparison."""

  def test_minimal_svg_default_template_exact_output(self):
    """Test minimal SVG produces exact expected output with default template."""
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
  <path d="M0 0h24v24H0z" fill="#FF0000"/>
</svg>"""
    
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)
    
    generator = ImageVectorGenerator()
    core_code, imports = generator.generate_core_code(ir)
    
    config = Config()
    template_engine = TemplateEngine(config)
    result = template_engine.render(
      template_name="default",
      build_code=core_code,
      imports=imports,
      icon_name=ir.name
    )
    
    expected = dedent("""
      import androidx.compose.ui.graphics.Color
      import androidx.compose.ui.graphics.SolidColor
      import androidx.compose.ui.graphics.vector.ImageVector
      import androidx.compose.ui.unit.dp

      ImageVector.Builder(
        name = "UnnamedIcon",
        defaultWidth = 24f.dp,
        defaultHeight = 24f.dp,
        viewportWidth = 24f,
        viewportHeight = 24f,
      ).apply {
        path(
          fill = SolidColor(Color.Red),
        ) {
          moveTo(0f, 0f)
          horizontalLineToRelative(24f)
          verticalLineToRelative(24f)
          horizontalLineTo(0f)
          close()
        }
      }.build()
    """).strip()
    
    assert result.strip() == expected, f"Output mismatch:\n\nActual:\n{result}\n\nExpected:\n{expected}"

  def test_stroke_only_svg_exact_output(self):
    """Test SVG with only stroke produces exact expected output."""
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="48" height="48" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
  <path d="M10 10L38 38" fill="none" stroke="#0000FF" stroke-width="2"/>
</svg>"""
    
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)
    
    generator = ImageVectorGenerator()
    core_code, imports = generator.generate_core_code(ir)
    
    config = Config()
    template_engine = TemplateEngine(config)
    result = template_engine.render(
      template_name="default",
      build_code=core_code,
      imports=imports,
      icon_name=ir.name
    )
    
    expected = dedent("""
      import androidx.compose.ui.graphics.Color
      import androidx.compose.ui.graphics.SolidColor
      import androidx.compose.ui.graphics.vector.ImageVector
      import androidx.compose.ui.unit.dp

      ImageVector.Builder(
        name = "UnnamedIcon",
        defaultWidth = 48f.dp,
        defaultHeight = 48f.dp,
        viewportWidth = 48f,
        viewportHeight = 48f,
      ).apply {
        path(
          stroke = SolidColor(Color.Blue),
          strokeLineWidth = 2f,
        ) {
          moveTo(10f, 10f)
          lineTo(38f, 38f)
        }
      }.build()
    """).strip()
    
    assert result.strip() == expected, f"Output mismatch:\n\nActual:\n{result}\n\nExpected:\n{expected}"

  def test_composable_function_exact_indentation(self):
    """Test composable function template produces exact indentation."""
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="16" height="16" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg">
  <path d="M8 8m-8 0a8 8 0 1 0 16 0a8 8 0 1 0 -16 0" fill="#00FF00"/>
</svg>"""
    
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)
    ir.name = "CircleIcon"
    
    generator = ImageVectorGenerator()
    core_code, imports = generator.generate_core_code(ir)
    
    config = Config()
    template_engine = TemplateEngine(config)
    result = template_engine.render(
      template_name="composable_function",
      build_code=core_code,
      imports=imports,
      icon_name=ir.name
    )
    
    expected = dedent("""
      import androidx.compose.ui.graphics.Color
      import androidx.compose.ui.graphics.SolidColor
      import androidx.compose.ui.graphics.vector.ImageVector
      import androidx.compose.ui.unit.dp
      import androidx.compose.runtime.Composable
      import androidx.compose.runtime.remember
      import androidx.compose.ui.Modifier
      import androidx.compose.ui.graphics.Color

      @Composable
      fun CircleiconIcon(
        modifier: Modifier = Modifier,
        tint: Color = Color.Unspecified
      ): ImageVector {
        return remember {
          ImageVector.Builder(
            name = "CircleIcon",
            defaultWidth = 16f.dp,
            defaultHeight = 16f.dp,
            viewportWidth = 16f,
            viewportHeight = 16f,
          ).apply {
            path(
              fill = SolidColor(Color.Green),
            ) {
              moveTo(8f, 8f)
              moveToRelative(-8f, 0f)
              arcToRelative(8f, 8f, 0f, true, false, 16f, 0f)
              arcToRelative(8f, 8f, 0f, true, false, -16f, 0f)
            }
          }.build()
        }
      }
    """).strip()
    
    assert result.strip() == expected, f"Output mismatch:\n\nActual:\n{result}\n\nExpected:\n{expected}"

  def test_val_declaration_exact_output(self):
    """Test val declaration template produces exact expected output."""
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="32" height="32" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
  <path d="M16 4L28 16L16 28L4 16Z" fill="#FFFF00"/>
</svg>"""
    
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)
    ir.name = "DiamondIcon"
    
    generator = ImageVectorGenerator()
    core_code, imports = generator.generate_core_code(ir)
    
    config = Config()
    template_engine = TemplateEngine(config)
    result = template_engine.render(
      template_name="val_declaration",
      build_code=core_code,
      imports=imports,
      icon_name=ir.name
    )
    
    expected = dedent("""
      import androidx.compose.ui.graphics.Color
      import androidx.compose.ui.graphics.SolidColor
      import androidx.compose.ui.graphics.vector.ImageVector
      import androidx.compose.ui.unit.dp

      val DiamondiconIcon: ImageVector = ImageVector.Builder(
        name = "DiamondIcon",
        defaultWidth = 32f.dp,
        defaultHeight = 32f.dp,
        viewportWidth = 32f,
        viewportHeight = 32f,
      ).apply {
        path(
          fill = SolidColor(Color.Yellow),
        ) {
          moveTo(16f, 4f)
          lineTo(28f, 16f)
          lineTo(16f, 28f)
          lineTo(4f, 16f)
          close()
        }
      }.build()
    """).strip()
    
    assert result.strip() == expected, f"Output mismatch:\n\nActual:\n{result}\n\nExpected:\n{expected}"

  def test_icon_object_exact_output(self):
    """Test icon object template produces exact expected output."""
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="20" height="20" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
  <path d="M10 2L18 18L2 18Z" fill="#FF00FF"/>
</svg>"""
    
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)
    ir.name = "TriangleIcon"
    
    generator = ImageVectorGenerator()
    core_code, imports = generator.generate_core_code(ir)
    
    config = Config()
    template_engine = TemplateEngine(config)
    result = template_engine.render(
      template_name="icon_object",
      build_code=core_code,
      imports=imports,
      icon_name=ir.name
    )
    
    expected = dedent("""
      import androidx.compose.ui.graphics.Color
      import androidx.compose.ui.graphics.SolidColor
      import androidx.compose.ui.graphics.vector.ImageVector
      import androidx.compose.ui.unit.dp

      object TriangleiconIcon {
        val imageVector: ImageVector by lazy {
          ImageVector.Builder(
            name = "TriangleIcon",
            defaultWidth = 20f.dp,
            defaultHeight = 20f.dp,
            viewportWidth = 20f,
            viewportHeight = 20f,
          ).apply {
            path(
              fill = SolidColor(Color.Magenta),
            ) {
              moveTo(10f, 2f)
              lineTo(18f, 18f)
              lineTo(2f, 18f)
              close()
            }
          }.build()
        }
      }
    """).strip()
    
    assert result.strip() == expected, f"Output mismatch:\n\nActual:\n{result}\n\nExpected:\n{expected}"

  def test_complex_paths_formatting(self):
    """Test complex path commands produce properly formatted output."""
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" fill="#4CAF50"/>
</svg>"""
    
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)
    
    generator = ImageVectorGenerator()
    core_code, imports = generator.generate_core_code(ir)
    
    config = Config()
    template_engine = TemplateEngine(config)
    result = template_engine.render(
      template_name="default",
      build_code=core_code,
      imports=imports,
      icon_name=ir.name
    )
    
    lines = result.split('\n')
    
    # Find path content lines (should have 4 spaces indentation)
    path_content_lines = []
    in_path_block = False
    for line in lines:
      if 'path(' in line:
        in_path_block = True
      elif in_path_block and line.strip() == '}':
        in_path_block = False
      elif in_path_block and ('moveTo(' in line or 'lineTo(' in line or 'curveTo(' in line):
        path_content_lines.append(line)
    
    # Verify all path content lines have exactly 4 spaces
    for line in path_content_lines:
      assert line.startswith('    '), f"Path content line should have 4 spaces: '{line}'"
      assert not line.startswith('     '), f"Path content line should not have 5+ spaces: '{line}'"

  def test_gradient_formatting_exact_output(self):
    """Test gradient formatting produces exact expected output."""
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#FF0000;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#0000FF;stop-opacity:1" />
    </linearGradient>
  </defs>
  <path d="M0 0h24v24H0z" fill="url(#grad)"/>
</svg>"""
    
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)
    
    generator = ImageVectorGenerator()
    core_code, imports = generator.generate_core_code(ir)
    
    config = Config()
    template_engine = TemplateEngine(config)
    result = template_engine.render(
      template_name="default",
      build_code=core_code,
      imports=imports,
      icon_name=ir.name
    )
    
    # Check that gradient formatting is correct
    assert "import androidx.compose.ui.graphics.Brush" in result
    assert "import androidx.compose.ui.geometry.Offset" in result
    assert "fill = Brush.linearGradient(" in result
    assert "colorStops = arrayOf(" in result
    assert "0f to Color.Red" in result  # Red color stop
    assert "1f to Color.Blue" in result  # Blue color stop
    assert "start = Offset(0f, 0f)," in result
    assert "end = Offset(100f, 0f)" in result
    
    lines = result.split('\n')
    
    # Find gradient parameter lines and check indentation
    gradient_lines = [line for line in lines if 'colorStops' in line or 'start =' in line or 'end =' in line]
    for line in gradient_lines:
      # Gradient parameters should be indented properly within fill parameter
      assert line.startswith('      '), f"Gradient parameter should have 6 spaces: '{line}'"

  def test_empty_path_handling(self):
    """Test handling of SVG with empty or minimal path data."""
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 12" fill="#000000"/>
</svg>"""
    
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)
    
    generator = ImageVectorGenerator()
    core_code, imports = generator.generate_core_code(ir)
    
    config = Config()
    template_engine = TemplateEngine(config)
    result = template_engine.render(
      template_name="default",
      build_code=core_code,
      imports=imports,
      icon_name=ir.name
    )
    
    # Should still produce valid output structure
    assert "ImageVector.Builder(" in result
    assert "path(" in result
    assert "moveTo(12f, 12f)" in result
    assert "}.build()" in result
    
    lines = result.split('\n')
    
    # Check basic structure is maintained
    builder_line = next(line for line in lines if 'ImageVector.Builder(' in line)
    assert not builder_line.startswith(' '), "Builder line should not be indented"
    
    path_line = next(line for line in lines if 'path(' in line)
    assert path_line.startswith('  '), "Path line should have 2 spaces"

  def test_multiple_paths_formatting(self):
    """Test formatting with multiple path elements."""
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 2L2 7v10l10 5z" fill="#FF0000"/>
  <path d="M12 2L22 7v10l-10 5z" fill="#00FF00"/>
</svg>"""
    
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)
    
    generator = ImageVectorGenerator()
    core_code, imports = generator.generate_core_code(ir)
    
    config = Config()
    template_engine = TemplateEngine(config)
    result = template_engine.render(
      template_name="default",
      build_code=core_code,
      imports=imports,
      icon_name=ir.name
    )
    
    lines = result.split('\n')
    
    # Count path blocks
    path_blocks = [line for line in lines if line.strip().startswith('path(')]
    assert len(path_blocks) == 2, "Should have exactly 2 path blocks"
    
    # Check that all path blocks have same indentation
    for line in path_blocks:
      assert line.startswith('  '), f"Path block should have 2 spaces: '{line}'"
      assert not line.startswith('   '), f"Path block should not have 3+ spaces: '{line}'"
    
    # Check that both colors are included
    assert "Color.Red" in result
    assert "Color.Green" in result

  def test_whitespace_and_line_ending_consistency(self):
    """Test that all templates produce consistent whitespace and line endings."""
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 12L24 24" fill="#000000"/>
</svg>"""
    
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)
    
    generator = ImageVectorGenerator()
    core_code, imports = generator.generate_core_code(ir)
    
    config = Config()
    template_engine = TemplateEngine(config)
    
    templates = ["default", "composable_function", "icon_object", "val_declaration"]
    
    for template_name in templates:
      result = template_engine.render(
        template_name=template_name,
        build_code=core_code,
        imports=imports,
        icon_name=ir.name
      )
      
      lines = result.split('\n')
      
      # Check no trailing whitespace
      for i, line in enumerate(lines):
        assert not line.endswith(' '), f"Template {template_name} line {i+1} has trailing space: '{line}'"
        assert not line.endswith('\t'), f"Template {template_name} line {i+1} has trailing tab: '{line}'"
      
      # Check no leading/trailing empty lines
      assert lines[0].strip() != '', f"Template {template_name} should not start with empty line"
      assert lines[-1].strip() != '', f"Template {template_name} should not end with empty line"
      
      # Check proper line separation
      import_lines = [i for i, line in enumerate(lines) if line.startswith('import')]
      if import_lines:
        last_import_line = max(import_lines)
        # Should have exactly one empty line after imports
        assert lines[last_import_line + 1] == '', f"Template {template_name} should have empty line after imports"
        assert lines[last_import_line + 2] != '', f"Template {template_name} should not have multiple empty lines after imports"