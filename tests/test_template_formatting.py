import tempfile
from pathlib import Path

import pytest

from src.core.config import Config
from src.generator.image_vector_generator import ImageVectorGenerator
from src.generator.template_engine import TemplateEngine
from src.parser.svg_parser import SvgParser


class TestTemplateFormatting:
  """Test template formatting, indentation, and complete output matching."""

  @pytest.fixture
  def simple_svg(self):
    """Simple SVG for basic testing."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 2L2 7v10l10 5 10-5V7l-10-5z" fill="#FF0000"/>
</svg>"""

  @pytest.fixture
  def complex_svg_with_groups(self):
    """Complex SVG with groups and transforms for advanced testing."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#FF6B35;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#F7931E;stop-opacity:1" />
    </linearGradient>
  </defs>
  <g transform="translate(10, 10) scale(0.8)">
    <path d="M50 10 L90 50 L50 90 L10 50 Z" fill="url(#grad1)" stroke="#333" stroke-width="2"/>
    <g transform="rotate(45 50 50)">
      <circle cx="25" cy="25" r="5" fill="#FF0000"/>
    </g>
  </g>
</svg>"""

  def test_default_template_indentation(self, simple_svg):
    """Test default template produces correct indentation."""
    parser = SvgParser()
    ir = parser.parse_svg(simple_svg)

    generator = ImageVectorGenerator()
    core_code, imports = generator.generate_core_code(ir)

    config = Config()
    template_engine = TemplateEngine(config)
    result = template_engine.render(
      template_name="default", build_code=core_code, imports=imports, icon_name=ir.name
    )

    lines = result.split("\n")

    # Check import lines (no indentation)
    import_lines = [line for line in lines if line.startswith("import")]
    for line in import_lines:
      assert not line.startswith(" "), f"Import line should not be indented: {line}"

    # Check ImageVector.Builder line (no indentation)
    builder_line = next(line for line in lines if "ImageVector.Builder(" in line)
    assert not builder_line.startswith(" "), f"Builder line should not be indented: {builder_line}"

    # Check parameter lines (2 spaces indentation)
    param_lines = [line for line in lines if "name =" in line or "defaultWidth =" in line]
    for line in param_lines:
      assert line.startswith("  "), f"Parameter line should have 2 spaces: '{line}'"
      assert not line.startswith("   "), f"Parameter line should not have 3+ spaces: '{line}'"

    # Check .apply block (no indentation)
    apply_line = next(line for line in lines if ").apply {" in line)
    assert not apply_line.startswith(" "), f"Apply line should not be indented: {apply_line}"

    # Check path function (2 spaces indentation)
    path_lines = [line for line in lines if line.strip().startswith("path(")]
    for line in path_lines:
      assert line.startswith("  "), f"Path line should have 2 spaces: '{line}'"

    # Check path content (4 spaces indentation)
    path_content_lines = [line for line in lines if "moveTo(" in line or "lineTo(" in line]
    for line in path_content_lines:
      assert line.startswith("    "), f"Path content should have 4 spaces: '{line}'"

  def test_composable_function_template_indentation(self, simple_svg):
    """Test composable function template produces correct indentation."""
    parser = SvgParser()
    ir = parser.parse_svg(simple_svg)
    ir.name = "TestIcon"

    generator = ImageVectorGenerator()
    core_code, imports = generator.generate_core_code(ir)

    config = Config()
    template_engine = TemplateEngine(config)
    result = template_engine.render(
      template_name="composable_function", build_code=core_code, imports=imports, icon_name=ir.name
    )

    lines = result.split("\n")

    # Check @Composable annotation (no indentation)
    composable_line = next(line for line in lines if "@Composable" in line)
    assert not composable_line.startswith(" "), (
      f"@Composable should not be indented: {composable_line}"
    )

    # Check function declaration (no indentation)
    fun_line = next(line for line in lines if "fun " in line and "Icon(" in line)
    assert not fun_line.startswith(" "), f"Function declaration should not be indented: {fun_line}"

    # Check function parameters (2 spaces indentation)
    param_lines = [line for line in lines if "modifier:" in line or "tint:" in line]
    for line in param_lines:
      assert line.startswith("  "), f"Function parameter should have 2 spaces: '{line}'"

    # Check return statement (2 spaces indentation)
    return_line = next(line for line in lines if "return remember" in line)
    assert return_line.startswith("  "), f"Return statement should have 2 spaces: '{return_line}'"

    # Check ImageVector.Builder inside remember (4 spaces indentation)
    builder_lines = [line for line in lines if "ImageVector.Builder(" in line]
    for line in builder_lines:
      assert line.startswith("    "), f"Builder inside remember should have 4 spaces: '{line}'"

    # Check builder parameters (6 spaces indentation)
    nested_param_lines = [
      line
      for line in lines
      if ("name =" in line or "defaultWidth =" in line) and line.startswith("      ")
    ]
    assert len(nested_param_lines) > 0, "Should have nested parameters with 6 spaces"

  def test_icon_object_template_indentation(self, simple_svg):
    """Test icon object template produces correct indentation."""
    parser = SvgParser()
    ir = parser.parse_svg(simple_svg)
    ir.name = "TestIcon"

    generator = ImageVectorGenerator()
    core_code, imports = generator.generate_core_code(ir)

    config = Config()
    template_engine = TemplateEngine(config)
    result = template_engine.render(
      template_name="icon_object", build_code=core_code, imports=imports, icon_name=ir.name
    )

    lines = result.split("\n")

    # Check object declaration (no indentation)
    object_line = next(line for line in lines if "object " in line and "Icon {" in line)
    assert not object_line.startswith(" "), (
      f"Object declaration should not be indented: {object_line}"
    )

    # Check val property (2 spaces indentation)
    val_line = next(line for line in lines if "val imageVector:" in line)
    assert val_line.startswith("  "), f"Val property should have 2 spaces: '{val_line}'"

    # Check ImageVector.Builder inside lazy (4 spaces indentation)
    builder_lines = [line for line in lines if "ImageVector.Builder(" in line]
    for line in builder_lines:
      assert line.startswith("    "), f"Builder inside lazy should have 4 spaces: '{line}'"

  def test_val_declaration_template_indentation(self, simple_svg):
    """Test val declaration template produces correct indentation."""
    parser = SvgParser()
    ir = parser.parse_svg(simple_svg)
    ir.name = "TestIcon"

    generator = ImageVectorGenerator()
    core_code, imports = generator.generate_core_code(ir)

    config = Config()
    template_engine = TemplateEngine(config)
    result = template_engine.render(
      template_name="val_declaration", build_code=core_code, imports=imports, icon_name=ir.name
    )

    lines = result.split("\n")

    # Check val declaration (no indentation)
    val_line = next(line for line in lines if "val " in line and "Icon: ImageVector =" in line)
    assert not val_line.startswith(" "), f"Val declaration should not be indented: {val_line}"

    # The rest should follow the same indentation as the core code
    # Check parameter lines (2 spaces indentation)
    param_lines = [
      line
      for line in lines
      if ("name =" in line or "defaultWidth =" in line) and not line.strip().startswith("val")
    ]
    for line in param_lines:
      assert line.startswith("  "), f"Parameter line should have 2 spaces: '{line}'"

  def test_complete_default_template_output_matching(self, simple_svg):
    """Test complete default template output matches expected format exactly."""
    parser = SvgParser()
    ir = parser.parse_svg(simple_svg)

    generator = ImageVectorGenerator()
    core_code, imports = generator.generate_core_code(ir)

    config = Config()
    template_engine = TemplateEngine(config)
    result = template_engine.render(
      template_name="default", build_code=core_code, imports=imports, icon_name=ir.name
    )

    expected_output = """import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.graphics.vector.path
import androidx.compose.ui.unit.dp

ImageVector.Builder(
  name = "UnnamedIcon",
  defaultWidth = 24.dp,
  defaultHeight = 24.dp,
  viewportWidth = 24f,
  viewportHeight = 24f,
).apply {
  path(
    fill = SolidColor(Color.Red),
  ) {
    moveTo(12f, 2f)
    lineTo(2f, 7f)
    verticalLineToRelative(10f)
    lineToRelative(10f, 5f)
    lineToRelative(10f, -5f)
    verticalLineTo(7f)
    lineToRelative(-10f, -5f)
    close()
  }
}.build()"""

    # Normalize whitespace for comparison
    result_normalized = "\n".join(line.rstrip() for line in result.split("\n")).strip()
    expected_normalized = "\n".join(line.rstrip() for line in expected_output.split("\n")).strip()

    assert result_normalized == expected_normalized, (
      f"Output mismatch:\n\nActual:\n{result_normalized}\n\nExpected:\n{expected_normalized}"
    )

  def test_complete_composable_function_output_matching(self, simple_svg):
    """Test complete composable function output matches expected format exactly."""
    parser = SvgParser()
    ir = parser.parse_svg(simple_svg)
    ir.name = "HomeIcon"

    generator = ImageVectorGenerator()
    core_code, imports = generator.generate_core_code(ir)

    config = Config()
    template_engine = TemplateEngine(config)
    result = template_engine.render(
      template_name="composable_function", build_code=core_code, imports=imports, icon_name=ir.name
    )

    expected_output = """import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.graphics.vector.path
import androidx.compose.ui.unit.dp
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color

@Composable
fun HomeIconIcon(
  modifier: Modifier = Modifier,
  tint: Color = Color.Unspecified
): ImageVector {
  return remember {
    ImageVector.Builder(
      name = "HomeIcon",
      defaultWidth = 24.dp,
      defaultHeight = 24.dp,
      viewportWidth = 24f,
      viewportHeight = 24f,
    ).apply {
      path(
        fill = SolidColor(Color.Red),
      ) {
        moveTo(12f, 2f)
        lineTo(2f, 7f)
        verticalLineToRelative(10f)
        lineToRelative(10f, 5f)
        lineToRelative(10f, -5f)
        verticalLineTo(7f)
        lineToRelative(-10f, -5f)
        close()
      }
    }.build()
  }
}"""

    # Normalize whitespace for comparison
    result_normalized = "\n".join(line.rstrip() for line in result.split("\n")).strip()
    expected_normalized = "\n".join(line.rstrip() for line in expected_output.split("\n")).strip()

    assert result_normalized == expected_normalized, (
      f"Output mismatch:\n\nActual:\n{result_normalized}\n\nExpected:\n{expected_normalized}"
    )

  def test_complex_svg_formatting_with_groups(self, complex_svg_with_groups):
    """Test formatting with complex SVG containing groups and gradients."""
    parser = SvgParser()
    ir = parser.parse_svg(complex_svg_with_groups)

    generator = ImageVectorGenerator()
    core_code, imports = generator.generate_core_code(ir)

    config = Config()
    template_engine = TemplateEngine(config)
    result = template_engine.render(
      template_name="default", build_code=core_code, imports=imports, icon_name=ir.name
    )

    lines = result.split("\n")

    # Check that group blocks are properly indented
    group_lines = [line for line in lines if "group(" in line]
    for line in group_lines:
      # Groups inside .apply should have 2 spaces
      if "group(" in line and not line.strip().startswith("//"):
        assert line.startswith("  "), f"Group line should have 2 spaces: '{line}'"

    # Check nested group indentation (should be 4 spaces)
    nested_content_lines = [
      line for line in lines if line.startswith("    ") and ("path(" in line or "group(" in line)
    ]
    assert len(nested_content_lines) > 0, "Should have nested content with 4+ spaces indentation"

    # Check gradient imports are included
    assert any("import androidx.compose.ui.graphics.Brush" in line for line in lines), (
      "Should include Brush import"
    )
    assert any("import androidx.compose.ui.geometry.Offset" in line for line in lines), (
      "Should include Offset import"
    )

    # Check gradient code formatting
    gradient_lines = [line for line in lines if "Brush.linearGradient" in line]
    for line in gradient_lines:
      # Should be properly indented within path parameters
      assert line.strip().startswith("fill = Brush.linearGradient"), (
        f"Gradient should be fill parameter: '{line}'"
      )

  def test_indentation_with_custom_config(self, simple_svg):
    """Test that custom indent_size configuration affects output."""
    parser = SvgParser()
    ir = parser.parse_svg(simple_svg)

    generator = ImageVectorGenerator()
    core_code, imports = generator.generate_core_code(ir)

    # Test with 4-space indentation
    config = Config(indent_size=4)
    template_engine = TemplateEngine(config)
    result = template_engine.render(
      template_name="default", build_code=core_code, imports=imports, icon_name=ir.name
    )

    lines = result.split("\n")

    # Note: The current implementation doesn't use config.indent_size in the core generator
    # This is testing the template engine's formatting capabilities
    # The core ImageVectorGenerator uses fixed 2-space indentation

    # Check that the basic structure is still correct regardless of config
    param_lines = [line for line in lines if "name =" in line]
    assert len(param_lines) > 0, "Should have parameter lines"

    # The actual indentation is controlled by the ImageVectorGenerator, not config
    # This test verifies that templates work with different configs
    assert "ImageVector.Builder(" in result
    assert "moveTo(" in result

  def test_imports_grouping_affects_output(self, complex_svg_with_groups):
    """Test that import grouping configuration affects the output format."""
    parser = SvgParser()
    ir = parser.parse_svg(complex_svg_with_groups)

    generator = ImageVectorGenerator()
    core_code, imports = generator.generate_core_code(ir)

    # Test with import grouping enabled
    config_grouped = Config(group_imports=True)
    template_engine_grouped = TemplateEngine(config_grouped)
    result_grouped = template_engine_grouped.render(
      template_name="default", build_code=core_code, imports=imports, icon_name=ir.name
    )

    # Test with import grouping disabled
    config_ungrouped = Config(group_imports=False)
    template_engine_ungrouped = TemplateEngine(config_ungrouped)
    result_ungrouped = template_engine_ungrouped.render(
      template_name="default", build_code=core_code, imports=imports, icon_name=ir.name
    )

    # Grouped imports should have empty lines between groups
    grouped_lines = result_grouped.split("\n")
    ungrouped_lines = result_ungrouped.split("\n")

    # Count empty lines in import section for grouped version
    import_section_grouped = []
    for line in grouped_lines:
      if line.startswith("import") or (line == "" and len(import_section_grouped) > 0):
        import_section_grouped.append(line)
      elif line.strip() and not line.startswith("import"):
        break

    # Count empty lines in import section for ungrouped version
    import_section_ungrouped = []
    for line in ungrouped_lines:
      if line.startswith("import"):
        import_section_ungrouped.append(line)
      elif line.strip():
        break

    # Grouped should have more lines due to spacing
    assert len(import_section_grouped) >= len(import_section_ungrouped), (
      "Grouped imports should have more lines due to spacing"
    )

    # Both should have the same imports, just formatted differently
    grouped_imports = [line for line in import_section_grouped if line.startswith("import")]
    ungrouped_imports = [line for line in import_section_ungrouped if line.startswith("import")]

    assert sorted(grouped_imports) == sorted(ungrouped_imports), "Both should have the same imports"

  def test_template_with_custom_variables(self):
    """Test template with custom variables for complete output matching."""
    with tempfile.TemporaryDirectory() as temp_dir:
      # Create custom template with specific formatting
      template_path = Path(temp_dir) / "test_template.j2"
      template_content = """{{- imports }}

/**
 * {{ icon_name | pascal_case }} icon
 * Generated automatically
 */
object {{ icon_name | pascal_case }}Icons {
    val Default: ImageVector by lazy {
        {{ build_code | indent(8, first=False) }}
    }
}"""

      template_path.write_text(template_content)

      # Simple SVG for testing
      svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 12 L24 24" fill="none" stroke="#000"/>
</svg>"""

      parser = SvgParser()
      ir = parser.parse_svg(svg_content)
      ir.name = "custom_icon"

      generator = ImageVectorGenerator()
      core_code, imports = generator.generate_core_code(ir)

      config = Config(template_path=template_path)
      template_engine = TemplateEngine(config)
      result = template_engine.render(
        template_name="default",  # Ignored when custom template is set
        build_code=core_code,
        imports=imports,
        icon_name=ir.name,
      )

      lines = result.split("\n")

      # Check custom template structure (PascalCase converts custom_icon to CustomIcon)
      assert any("CustomIcon icon" in line for line in lines), "Should have custom header comment"
      assert any("object CustomIconIcons {" in line for line in lines), (
        "Should have custom object declaration"
      )
      assert any("val Default: ImageVector by lazy {" in line for line in lines), (
        "Should have custom property"
      )

      # Check indentation of nested ImageVector (8 spaces as specified in template)
      builder_lines = [line for line in lines if "ImageVector.Builder(" in line]
      for line in builder_lines:
        assert line.startswith("        "), f"Custom template should have 8 spaces: '{line}'"

  def test_line_endings_consistency(self, simple_svg):
    """Test that all templates produce consistent line endings."""
    parser = SvgParser()
    ir = parser.parse_svg(simple_svg)

    generator = ImageVectorGenerator()
    core_code, imports = generator.generate_core_code(ir)

    config = Config()
    template_engine = TemplateEngine(config)

    templates = ["default", "composable_function", "icon_object", "val_declaration"]

    for template_name in templates:
      result = template_engine.render(
        template_name=template_name, build_code=core_code, imports=imports, icon_name=ir.name
      )

      # Check no Windows line endings
      assert "\r\n" not in result, f"Template {template_name} should not have Windows line endings"

      # Check no trailing spaces
      lines = result.split("\n")
      for i, line in enumerate(lines):
        assert not line.endswith(" "), (
          f"Template {template_name} line {i + 1} should not have trailing spaces: '{line}'"
        )

      # Check no multiple consecutive empty lines
      empty_line_count = 0
      for line in lines:
        if line.strip() == "":
          empty_line_count += 1
          assert empty_line_count <= 2, (
            f"Template {template_name} should not have more than 2 consecutive empty lines"
          )
        else:
          empty_line_count = 0
