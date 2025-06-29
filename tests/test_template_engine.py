import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src.core.config import Config
from src.generator.template_engine import TemplateEngine


class TestTemplateEngine:
  """Test template engine functionality."""

  def test_init_with_default_config(self):
    """Test template engine initialization with default config."""
    config = Config()
    engine = TemplateEngine(config)

    assert engine.config == config

  def test_list_available_templates(self):
    """Test listing built-in templates."""
    config = Config()
    engine = TemplateEngine(config)

    templates = engine.list_available_templates()

    assert "default" in templates
    assert "composable_function" in templates
    assert "icon_object" in templates
    assert len(templates) >= 3

  def test_render_default_template(self):
    """Test rendering with default template."""
    config = Config()
    engine = TemplateEngine(config)

    build_code = "ImageVector.Builder().build()"
    imports = {"androidx.compose.ui.graphics.vector.ImageVector"}

    result = engine.render(
      template_name="default", build_code=build_code, imports=imports, icon_name="TestIcon"
    )

    assert "import androidx.compose.ui.graphics.vector.ImageVector" in result
    assert build_code in result
    assert result.strip().endswith(build_code)

  def test_render_composable_function_template(self):
    """Test rendering with composable function template."""
    config = Config()
    engine = TemplateEngine(config)

    build_code = "ImageVector.Builder().build()"
    imports = {"androidx.compose.ui.graphics.vector.ImageVector"}

    result = engine.render(
      template_name="composable_function",
      build_code=build_code,
      imports=imports,
      icon_name="test_icon",
    )

    assert "@Composable" in result
    assert "fun TestIconIcon(" in result
    assert "return remember {" in result
    assert "import androidx.compose.runtime.Composable" in result
    assert "import androidx.compose.runtime.remember" in result

  def test_render_icon_object_template(self):
    """Test rendering with icon object template."""
    config = Config()
    engine = TemplateEngine(config)

    build_code = "ImageVector.Builder().build()"
    imports = {"androidx.compose.ui.graphics.vector.ImageVector"}

    result = engine.render(
      template_name="icon_object", build_code=build_code, imports=imports, icon_name="home_icon"
    )

    assert "object HomeIconIcon {" in result
    assert "val imageVector: ImageVector by lazy {" in result

  def test_render_with_custom_template_file(self):
    """Test rendering with custom template file."""
    with tempfile.TemporaryDirectory() as temp_dir:
      template_path = Path(temp_dir) / "custom.j2"
      template_content = """{{ imports }}

// Custom template for {{ icon_name | pascal_case }}
val CustomIcon = {{ build_code }}"""

      template_path.write_text(template_content)

      config = Config(template_path=template_path)
      engine = TemplateEngine(config)

      result = engine.render(
        template_name="default",  # Ignored when custom template is set
        build_code="ImageVector.Builder().build()",
        imports={"androidx.compose.ui.graphics.vector.ImageVector"},
        icon_name="test_icon",
      )

      assert "// Custom template for TestIcon" in result
      assert "val CustomIcon = ImageVector.Builder().build()" in result

  def test_render_with_val_declaration_template(self):
    """Test rendering with val declaration template."""
    config = Config()
    engine = TemplateEngine(config)

    result = engine.render(
      template_name="val_declaration",
      build_code="ImageVector.Builder().build()",
      imports={"androidx.compose.ui.graphics.vector.ImageVector"},
      icon_name="TestIcon",
    )

    assert "val TestIconIcon: ImageVector = ImageVector.Builder().build()" in result

  def test_format_imports_grouped(self):
    """Test import formatting with grouping enabled."""
    config = Config(group_imports=True)
    engine = TemplateEngine(config)

    imports = {
      "androidx.compose.ui.graphics.Color",
      "androidx.compose.ui.graphics.vector.ImageVector",
      "androidx.compose.ui.unit.dp",
      "androidx.compose.runtime.Composable",
      "kotlin.collections.List",
    }

    formatted = engine._format_imports(imports)
    lines = formatted.split("\n")

    # Should have grouped imports
    assert "import androidx.compose.runtime.Composable" in formatted
    assert "import androidx.compose.ui.graphics.Color" in formatted
    assert "import androidx.compose.ui.graphics.vector.ImageVector" in formatted
    assert "import androidx.compose.ui.unit.dp" in formatted
    assert "import kotlin.collections.List" in formatted

    # Should have empty lines between groups
    assert "" in lines

  def test_format_imports_ungrouped(self):
    """Test import formatting with grouping disabled."""
    config = Config(group_imports=False)
    engine = TemplateEngine(config)

    imports = {
      "androidx.compose.ui.graphics.Color",
      "androidx.compose.ui.unit.dp",
      "androidx.compose.runtime.Composable",
    }

    formatted = engine._format_imports(imports)
    lines = formatted.split("\n")

    # Should be sorted alphabetically
    expected_lines = [
      "import androidx.compose.runtime.Composable",
      "import androidx.compose.ui.graphics.Color",
      "import androidx.compose.ui.unit.dp",
    ]

    assert lines == expected_lines

  def test_format_imports_empty(self):
    """Test formatting empty imports set."""
    config = Config()
    engine = TemplateEngine(config)

    formatted = engine._format_imports(set())
    assert formatted == ""

  def test_pascal_case_filter(self):
    """Test PascalCase conversion filter."""
    config = Config()
    engine = TemplateEngine(config)

    assert engine._to_pascal_case("test_icon") == "TestIcon"
    assert engine._to_pascal_case("home-icon") == "HomeIcon"
    assert engine._to_pascal_case("my icon name") == "MyIconName"
    assert engine._to_pascal_case("already_CamelCase") == "AlreadyCamelcase"
    assert (
      engine._to_pascal_case("123numeric") == "123numeric"
    )  # Numbers at start don't get capitalized
    assert engine._to_pascal_case("") == ""

  def test_camel_case_filter(self):
    """Test camelCase conversion filter."""
    config = Config()
    engine = TemplateEngine(config)

    assert engine._to_camel_case("test_icon") == "testIcon"
    assert engine._to_camel_case("home-icon") == "homeIcon"
    assert engine._to_camel_case("my icon name") == "myIconName"
    assert engine._to_camel_case("PascalCase") == "pascalcase"
    assert engine._to_camel_case("") == ""

  def test_snake_case_filter(self):
    """Test snake_case conversion filter."""
    config = Config()
    engine = TemplateEngine(config)

    assert engine._to_snake_case("TestIcon") == "test_icon"
    assert engine._to_snake_case("home-icon") == "home_icon"
    assert engine._to_snake_case("my icon name") == "my_icon_name"
    assert engine._to_snake_case("camelCaseString") == "camel_case_string"
    assert engine._to_snake_case("already_snake") == "already_snake"

  @patch("src.generator.template_engine.HAS_JINJA2", False)
  def test_fallback_without_jinja2(self):
    """Test fallback rendering when Jinja2 is not available."""
    config = Config()
    engine = TemplateEngine(config)

    result = engine.render(
      template_name="default",
      build_code="ImageVector.Builder().build()",
      imports={"androidx.compose.ui.graphics.vector.ImageVector"},
      icon_name="TestIcon",
    )

    assert "import androidx.compose.ui.graphics.vector.ImageVector" in result
    assert "ImageVector.Builder().build()" in result

  def test_render_with_extra_template_vars(self):
    """Test rendering with additional template variables."""
    with tempfile.TemporaryDirectory() as temp_dir:
      template_path = Path(temp_dir) / "custom.j2"
      template_content = """{{ imports }}

// Icon: {{ icon_name }}
// Author: {{ author }}
// Version: {{ version }}
val Icon = {{ build_code }}"""

      template_path.write_text(template_content)

      config = Config(template_path=template_path)
      engine = TemplateEngine(config)

      result = engine.render(
        template_name="default",
        build_code="ImageVector.Builder().build()",
        imports={"androidx.compose.ui.graphics.vector.ImageVector"},
        icon_name="test_icon",
        author="Test Author",
        version="1.0.0",
      )

      assert "// Author: Test Author" in result
      assert "// Version: 1.0.0" in result

  def test_template_not_found(self):
    """Test error handling for non-existent template."""
    config = Config()
    engine = TemplateEngine(config)

    with pytest.raises(Exception):  # Jinja2 will raise TemplateNotFound
      engine.render(
        template_name="nonexistent_template", build_code="test", imports=set(), icon_name="test"
      )
