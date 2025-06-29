import json
import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner

from src.cli import cli


class TestCLITemplateIntegration:
  """Test CLI integration with template system."""

  @pytest.fixture
  def runner(self):
    """Create click test runner."""
    return CliRunner()

  @pytest.fixture
  def sample_svg(self):
    """Create a simple SVG for testing."""
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 2L2 7v10l10 5 10-5V7l-10-5z" fill="#FF0000"/>
</svg>"""
    return svg_content

  @pytest.fixture
  def svg_file(self, sample_svg):
    """Create temporary SVG file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".svg", delete=False) as f:
      f.write(sample_svg)
      return Path(f.name)

  def test_convert_with_default_template(self, runner, svg_file):
    """Test convert command with default template."""
    result = runner.invoke(cli, ["convert", str(svg_file)])

    assert result.exit_code == 0
    assert "ImageVector.Builder(" in result.output
    assert "import androidx.compose.ui.graphics.vector.ImageVector" in result.output

  def test_convert_with_composable_function_template(self, runner, svg_file):
    """Test convert command with composable function template."""
    result = runner.invoke(cli, ["convert", str(svg_file), "-t", "composable_function"])

    assert result.exit_code == 0
    assert "@Composable" in result.output
    assert "fun " in result.output
    assert "return remember {" in result.output

  def test_convert_with_icon_object_template(self, runner, svg_file):
    """Test convert command with icon object template."""
    result = runner.invoke(cli, ["convert", str(svg_file), "-t", "icon_object"])

    assert result.exit_code == 0
    assert "object " in result.output
    assert "val imageVector: ImageVector by lazy {" in result.output

  def test_convert_with_custom_template_file(self, runner, svg_file):
    """Test convert command with custom template file."""
    with tempfile.TemporaryDirectory() as temp_dir:
      template_path = Path(temp_dir) / "custom.j2"
      template_content = """{{ imports }}

// Custom template test
val {{ icon_name | pascal_case }}CustomIcon = {{ build_code }}"""

      template_path.write_text(template_content)

      result = runner.invoke(cli, ["convert", str(svg_file), "-t", str(template_path)])

      assert result.exit_code == 0
      assert "// Custom template test" in result.output
      assert "CustomIcon = ImageVector.Builder(" in result.output

  def test_convert_with_output_file(self, runner, svg_file):
    """Test convert command with output file."""
    with tempfile.TemporaryDirectory() as temp_dir:
      output_path = Path(temp_dir) / "output.kt"

      result = runner.invoke(
        cli, ["convert", str(svg_file), "-o", str(output_path), "-t", "default"]
      )

      assert result.exit_code == 0
      assert f"Generated {output_path}" in result.output
      assert output_path.exists()

      content = output_path.read_text()
      assert "ImageVector.Builder(" in content

  def test_convert_with_config_file(self, runner, svg_file):
    """Test convert command with configuration file."""
    with tempfile.TemporaryDirectory() as temp_dir:
      config_path = Path(temp_dir) / "config.json"
      config_data = {"indent_size": 4, "group_imports": False}

      with open(config_path, "w") as f:
        json.dump(config_data, f)

      result = runner.invoke(cli, ["convert", str(svg_file), "-c", str(config_path)])

      assert result.exit_code == 0
      assert "ImageVector.Builder(" in result.output

  def test_convert_with_val_declaration_template(self, runner, svg_file):
    """Test convert command with val declaration template."""
    result = runner.invoke(cli, ["convert", str(svg_file), "-t", "val_declaration"])

    assert result.exit_code == 0
    assert "val " in result.output
    assert "Icon: ImageVector = ImageVector.Builder(" in result.output

  def test_convert_with_custom_name(self, runner, svg_file):
    """Test convert command with custom icon name."""
    result = runner.invoke(
      cli, ["convert", str(svg_file), "-n", "CustomName", "-t", "composable_function"]
    )

    assert result.exit_code == 0
    assert "fun CustomNameIcon(" in result.output  # PascalCase conversion

  def test_convert_config_overrides_defaults(self, runner, svg_file):
    """Test that config file options override defaults."""
    with tempfile.TemporaryDirectory() as temp_dir:
      config_path = Path(temp_dir) / "config.json"
      config_data = {"group_imports": False, "indent_size": 4}

      with open(config_path, "w") as f:
        json.dump(config_data, f)

      result = runner.invoke(cli, ["convert", str(svg_file), "-c", str(config_path)])

      assert result.exit_code == 0
      assert "ImageVector.Builder(" in result.output

  def test_templates_command(self, runner):
    """Test templates listing command."""
    result = runner.invoke(cli, ["templates"])

    assert result.exit_code == 0
    assert "Available built-in templates:" in result.output
    assert "- default" in result.output
    assert "- composable_function" in result.output
    assert "- icon_object" in result.output
    assert "- val_declaration" in result.output

  def test_convert_nonexistent_template(self, runner, svg_file):
    """Test convert with non-existent template."""
    result = runner.invoke(cli, ["convert", str(svg_file), "-t", "nonexistent_template"])

    assert result.exit_code == 1
    assert "Error:" in result.output

  def test_convert_nonexistent_svg_file(self, runner):
    """Test convert with non-existent SVG file."""
    result = runner.invoke(cli, ["convert", "/nonexistent/file.svg"])

    assert result.exit_code == 2  # Click exits with 2 for missing files

  def test_convert_nonexistent_config_file(self, runner, svg_file):
    """Test convert with non-existent config file."""
    result = runner.invoke(cli, ["convert", str(svg_file), "-c", "/nonexistent/config.json"])

    assert result.exit_code == 2  # Click exits with 2 for missing files

  def test_convert_invalid_config_file(self, runner, svg_file):
    """Test convert with invalid config file."""
    with tempfile.TemporaryDirectory() as temp_dir:
      config_path = Path(temp_dir) / "invalid.json"
      config_path.write_text("{ invalid json")

      result = runner.invoke(cli, ["convert", str(svg_file), "-c", str(config_path)])

      assert result.exit_code == 1
      assert "Error:" in result.output
      assert "Invalid config file format" in result.output

  def test_convert_with_complex_svg(self, runner):
    """Test convert with a more complex SVG (groups, gradients)."""
    complex_svg = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:rgb(255,255,0);stop-opacity:1" />
      <stop offset="100%" style="stop-color:rgb(255,0,0);stop-opacity:1" />
    </linearGradient>
  </defs>
  <g transform="translate(2, 2)">
    <path d="M10 0 L20 10 L10 20 L0 10 Z" fill="url(#grad1)"/>
  </g>
</svg>"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".svg", delete=False) as f:
      f.write(complex_svg)
      svg_path = Path(f.name)

    result = runner.invoke(cli, ["convert", str(svg_path), "-t", "composable_function"])

    assert result.exit_code == 0
    assert "@Composable" in result.output
    assert "group(" in result.output
    assert "Brush.linearGradient" in result.output

  def test_info_command_basic(self, runner, svg_file):
    """Test info command with basic SVG."""
    result = runner.invoke(cli, ["info", str(svg_file)])

    assert result.exit_code == 0
    assert "Dimensions:" in result.output
    assert "Viewport:" in result.output
    assert "Vector name:" in result.output
    assert "Nodes:" in result.output

  def test_cli_help(self, runner):
    """Test CLI help output."""
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "SVG to Compose ImageVector converter" in result.output
    assert "convert" in result.output
    assert "templates" in result.output
    assert "info" in result.output
    assert "version" in result.output

  def test_convert_help(self, runner):
    """Test convert command help."""
    result = runner.invoke(cli, ["convert", "--help"])

    assert result.exit_code == 0
    assert "--template" in result.output
    assert "--config" in result.output
