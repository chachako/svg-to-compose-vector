import pytest
import tempfile
import json
from pathlib import Path

from src.parser.svg_parser import SvgParser
from src.generator.image_vector_generator import ImageVectorGenerator
from src.generator.template_engine import TemplateEngine
from src.core.config import Config


class TestTemplateSystemIntegration:
  """Integration tests for the complete template system."""

  @pytest.fixture
  def simple_svg(self):
    """Simple SVG for testing."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 2L2 7v10l10 5 10-5V7l-10-5z" fill="#4285F4"/>
</svg>"""

  @pytest.fixture
  def complex_svg(self):
    """Complex SVG with groups and gradients."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="gradient1" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#FF6B35;stop-opacity:1" />
      <stop offset="50%" style="stop-color:#F7931E;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#FFCC02;stop-opacity:1" />
    </linearGradient>
  </defs>
  <g transform="translate(10, 10) scale(0.8)">
    <path d="M50 10 L90 50 L50 90 L10 50 Z" fill="url(#gradient1)" stroke="#333" stroke-width="2"/>
    <g transform="rotate(45 50 50)">
      <circle cx="50" cy="30" r="5" fill="#FF0000"/>
      <circle cx="50" cy="70" r="5" fill="#00FF00"/>
    </g>
  </g>
</svg>"""

  def test_end_to_end_simple_svg_default_template(self, simple_svg):
    """Test complete pipeline with simple SVG and default template."""
    # Parse SVG
    parser = SvgParser()
    ir = parser.parse_svg(simple_svg)
    
    # Generate code
    generator = ImageVectorGenerator()
    core_code, imports = generator.generate_core_code(ir)
    
    # Apply template
    config = Config()
    template_engine = TemplateEngine(config)
    result = template_engine.render(
      template_name="default",
      build_code=core_code,
      imports=imports,
      icon_name=ir.name
    )
    
    # Verify output
    assert "import androidx.compose.ui.graphics.vector.ImageVector" in result
    assert "import androidx.compose.ui.unit.dp" in result
    assert "ImageVector.Builder(" in result
    assert 'name = "UnnamedIcon"' in result
    assert "defaultWidth = 24f.dp" in result
    assert "defaultHeight = 24f.dp" in result
    assert "viewportWidth = 24f" in result
    assert "viewportHeight = 24f" in result
    assert "path(" in result
    assert "moveTo(12f, 2f)" in result
    assert ".build()" in result

  def test_end_to_end_composable_function_template(self, simple_svg):
    """Test complete pipeline with composable function template."""
    parser = SvgParser()
    ir = parser.parse_svg(simple_svg)
    ir.name = "HomeIcon"  # Set custom name
    
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
    
    # Verify composable function structure
    assert "import androidx.compose.runtime.Composable" in result
    assert "import androidx.compose.runtime.remember" in result
    assert "import androidx.compose.ui.Modifier" in result
    assert "@Composable" in result
    assert "fun HomeiconIcon(" in result  # PascalCase conversion behavior
    assert "modifier: Modifier = Modifier" in result
    assert "tint: Color = Color.Unspecified" in result
    assert "return remember {" in result
    assert "ImageVector.Builder(" in result

  def test_end_to_end_icon_object_template(self, simple_svg):
    """Test complete pipeline with icon object template."""
    parser = SvgParser()
    ir = parser.parse_svg(simple_svg)
    ir.name = "settings_icon"
    
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
    
    # Verify object structure
    assert "object SettingsIconIcon {" in result
    assert "val imageVector: ImageVector by lazy {" in result
    assert "ImageVector.Builder(" in result

  def test_end_to_end_with_val_declaration_template(self, simple_svg):
    """Test complete pipeline with val declaration template."""
    parser = SvgParser()
    ir = parser.parse_svg(simple_svg)
    
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
    
    # Verify val declaration is generated
    assert "val UnnamediconIcon: ImageVector = ImageVector.Builder(" in result

  def test_end_to_end_custom_template(self, simple_svg):
    """Test complete pipeline with custom template file."""
    with tempfile.TemporaryDirectory() as temp_dir:
      # Create custom template
      template_path = Path(temp_dir) / "custom.j2"
      template_content = """{{- imports }}

/**
 * Generated icon: {{ icon_name | pascal_case }}
 * Auto-generated from SVG
 */
@Suppress("UnusedReceiverParameter")
val Icons.Default.{{ icon_name | pascal_case }}: ImageVector
  get() {
    if (_{{ icon_name | camel_case }} != null) {
      return _{{ icon_name | camel_case }}!!
    }
    _{{ icon_name | camel_case }} = {{ build_code | indent(4, first=False) }}
    return _{{ icon_name | camel_case }}!!
  }

private var _{{ icon_name | camel_case }}: ImageVector? = null"""
      
      template_path.write_text(template_content)
      
      # Parse and generate
      parser = SvgParser()
      ir = parser.parse_svg(simple_svg)
      ir.name = "my_custom_icon"
      
      generator = ImageVectorGenerator()
      core_code, imports = generator.generate_core_code(ir)
      
      config = Config(template_path=template_path)
      template_engine = TemplateEngine(config)
      result = template_engine.render(
        template_name="default",  # Ignored when custom template is set
        build_code=core_code,
        imports=imports,
        icon_name=ir.name
      )
      
      # Verify custom template output (PascalCase conversion behavior)
      assert "Generated icon: Mycustomicon" in result
      assert "val Icons.Default.Mycustomicon: ImageVector" in result
      assert "private var _mycustomicon: ImageVector? = null" in result
      assert "ImageVector.Builder(" in result

  def test_end_to_end_complex_svg(self, complex_svg):
    """Test complete pipeline with complex SVG (groups, gradients)."""
    parser = SvgParser()
    ir = parser.parse_svg(complex_svg)
    
    generator = ImageVectorGenerator()
    core_code, imports = generator.generate_core_code(ir)
    
    config = Config()
    template_engine = TemplateEngine(config)
    result = template_engine.render(
      template_name="composable_function",
      build_code=core_code,
      imports=imports,
      icon_name="ComplexIcon"
    )
    
    # Verify complex features are handled
    assert "import androidx.compose.ui.graphics.Brush" in result
    assert "import androidx.compose.ui.geometry.Offset" in result
    assert "@Composable" in result
    assert "fun ComplexiconIcon(" in result  # PascalCase conversion behavior
    assert "group(" in result
    assert "Brush.linearGradient" in result
    assert "translationX = 10f" in result
    assert "scaleX = 0.8f" in result

  def test_config_file_integration(self, simple_svg):
    """Test integration with configuration file."""
    with tempfile.TemporaryDirectory() as temp_dir:
      # Create config file
      config_path = Path(temp_dir) / "config.json"
      config_data = {
        "indent_size": 4,
        "group_imports": False
      }
      
      with open(config_path, 'w') as f:
        json.dump(config_data, f)
      
      # Load config and process
      config = Config.from_file(config_path)
      
      parser = SvgParser()
      ir = parser.parse_svg(simple_svg)
      
      generator = ImageVectorGenerator()
      core_code, imports = generator.generate_core_code(ir)
      
      template_engine = TemplateEngine(config)
      result = template_engine.render(
        template_name="default",
        build_code=core_code,
        imports=imports,
        icon_name=ir.name
      )
      
      # Verify basic generation works
      assert "ImageVector.Builder(" in result
      
      # Verify imports are not grouped (group_imports: false)
      lines = result.split('\n')
      import_lines = [line for line in lines if line.startswith('import')]
      # Should not have empty lines between imports when grouping is disabled
      for i in range(len(import_lines) - 1):
        next_line_index = lines.index(import_lines[i]) + 1
        if next_line_index < len(lines):
          next_line = lines[next_line_index]
          if next_line.startswith('import'):
            # No empty line between consecutive imports
            assert True
          elif next_line == "":
            # If there's an empty line, next non-empty should not be import
            for j in range(next_line_index + 1, len(lines)):
              if lines[j] != "":
                assert not lines[j].startswith('import')
                break

  def test_name_conversion_filters(self, simple_svg):
    """Test name conversion filters in templates."""
    parser = SvgParser()
    ir = parser.parse_svg(simple_svg)
    
    # Test various name formats
    test_names = [
      "simple_name",
      "kebab-case-name", 
      "camelCaseName",
      "PascalCaseName",
      "mixed_Format-Name"
    ]
    
    generator = ImageVectorGenerator()
    core_code, imports = generator.generate_core_code(ir)
    
    config = Config()
    template_engine = TemplateEngine(config)
    
    for name in test_names:
      result = template_engine.render(
        template_name="composable_function",
        build_code=core_code,
        imports=imports,
        icon_name=name
      )
      
      # Should always generate valid Kotlin function names
      assert "fun " in result
      # Function name should be in PascalCase format
      if "simple_name" in name:
        assert "fun SimpleNameIcon(" in result
      elif "kebab-case-name" in name:
        assert "fun KebabCaseNameIcon(" in result

  def test_import_management_with_gradients(self, complex_svg):
    """Test that template engine correctly handles gradient imports."""
    parser = SvgParser()
    ir = parser.parse_svg(complex_svg)
    
    generator = ImageVectorGenerator()
    core_code, imports = generator.generate_core_code(ir)
    
    # Should include gradient-related imports
    assert "androidx.compose.ui.graphics.Brush" in imports
    assert "androidx.compose.ui.geometry.Offset" in imports
    
    config = Config(group_imports=True)
    template_engine = TemplateEngine(config)
    result = template_engine.render(
      template_name="default",
      build_code=core_code,
      imports=imports,
      icon_name="TestIcon"
    )
    
    # Verify imports are properly formatted and grouped
    assert "import androidx.compose.ui.graphics.Brush" in result
    assert "import androidx.compose.ui.geometry.Offset" in result
    
    # Imports should be at the top
    lines = result.split('\n')
    first_import_line = next(i for i, line in enumerate(lines) if line.startswith('import'))
    last_import_line = max(i for i, line in enumerate(lines) if line.startswith('import'))
    
    # All imports should be consecutive (with possible empty lines for grouping)
    for i in range(first_import_line, last_import_line + 1):
      line = lines[i]
      assert line.startswith('import') or line == ""