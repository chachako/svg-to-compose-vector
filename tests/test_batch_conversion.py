"""Tests for batch conversion functionality."""

import pytest
import tempfile
import json
from pathlib import Path
from click.testing import CliRunner

from src.cli import cli


class TestBatchConversion:
  """Test batch conversion of SVG files to ImageVector."""

  @pytest.fixture
  def runner(self):
    return CliRunner()

  @pytest.fixture
  def sample_svgs(self):
    """Create sample SVG files with different naming patterns."""
    svgs = {
      "media.play24.svg": """<?xml version="1.0" encoding="UTF-8"?>
<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
  <path d="M8 5v14l11-7z" fill="#000"/>
</svg>""",
      
      "media.pause16.svg": """<?xml version="1.0" encoding="UTF-8"?>
<svg width="16" height="16" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg">
  <path d="M6 4h4v8H6z" fill="#000"/>
</svg>""",
      
      "actions.download.svg": """<?xml version="1.0" encoding="UTF-8"?>
<svg width="20" height="20" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
  <path d="M10 12 L15 7 L5 7 Z" fill="#000"/>
</svg>""",
      
      "simple_icon.svg": """<?xml version="1.0" encoding="UTF-8"?>
<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
  <circle cx="12" cy="12" r="10" fill="#000"/>
</svg>""",
    }
    return svgs

  def test_batch_dry_run(self, runner, sample_svgs):
    """Test batch conversion with dry run option."""
    with tempfile.TemporaryDirectory() as temp_dir:
      input_dir = Path(temp_dir) / "input"
      input_dir.mkdir()
      
      # Create sample SVG files
      for filename, content in sample_svgs.items():
        (input_dir / filename).write_text(content)
      
      result = runner.invoke(cli, [
        'batch', str(input_dir), '--dry-run'
      ])
      
      assert result.exit_code == 0
      assert "DRY RUN" in result.output
      assert "Found 4 SVG files" in result.output
      assert "Successfully processed: 4" in result.output
      assert "Would create:" in result.output
      
      # Check expected file paths in output (lowercase directories)
      assert "media/Play24.kt" in result.output
      assert "media/Pause16.kt" in result.output  
      assert "actions/Download.kt" in result.output
      assert "SimpleIcon.kt" in result.output  # No namespace, root level

  def test_batch_basic_conversion(self, runner, sample_svgs):
    """Test basic batch conversion functionality."""
    with tempfile.TemporaryDirectory() as temp_dir:
      input_dir = Path(temp_dir) / "input" 
      output_dir = Path(temp_dir) / "output"
      input_dir.mkdir()
      
      # Create sample SVG files
      for filename, content in sample_svgs.items():
        (input_dir / filename).write_text(content)
      
      result = runner.invoke(cli, [
        'batch', str(input_dir), '-o', str(output_dir)
      ])
      
      assert result.exit_code == 0
      assert "Successfully processed: 4" in result.output
      
      # Check that files were created with correct structure (lowercase directories)
      assert (output_dir / "media" / "Play24.kt").exists()
      assert (output_dir / "media" / "Pause16.kt").exists()
      assert (output_dir / "actions" / "Download.kt").exists()
      assert (output_dir / "SimpleIcon.kt").exists()
      
      # Verify content of generated files
      play_content = (output_dir / "media" / "Play24.kt").read_text()
      assert "val Play24Icon: ImageVector" in play_content
      assert "ImageVector.Builder(" in play_content
      assert "moveTo(8f, 5f)" in play_content

  def test_batch_without_namespace_dirs(self, runner, sample_svgs):
    """Test batch conversion without creating namespace directories."""
    with tempfile.TemporaryDirectory() as temp_dir:
      input_dir = Path(temp_dir) / "input"
      output_dir = Path(temp_dir) / "output"
      input_dir.mkdir()
      
      # Create sample SVG files
      for filename, content in sample_svgs.items():
        (input_dir / filename).write_text(content)
      
      result = runner.invoke(cli, [
        'batch', str(input_dir), '-o', str(output_dir), '--no-namespace-dirs'
      ])
      
      assert result.exit_code == 0
      
      # All files should be in root output directory
      assert (output_dir / "Play24.kt").exists()
      assert (output_dir / "Pause16.kt").exists()
      assert (output_dir / "Download.kt").exists()
      assert (output_dir / "SimpleIcon.kt").exists()
      
      # Namespace directories should not exist
      assert not (output_dir / "media").exists()
      assert not (output_dir / "actions").exists()

  def test_batch_with_composable_template(self, runner, sample_svgs):
    """Test batch conversion with composable function template."""
    with tempfile.TemporaryDirectory() as temp_dir:
      input_dir = Path(temp_dir) / "input"
      output_dir = Path(temp_dir) / "output"
      input_dir.mkdir()
      
      # Create one sample SVG
      (input_dir / "media.play24.svg").write_text(sample_svgs["media.play24.svg"])
      
      result = runner.invoke(cli, [
        'batch', str(input_dir), '-o', str(output_dir), 
        '-t', 'composable_function'
      ])
      
      assert result.exit_code == 0
      
      play_content = (output_dir / "media" / "Play24.kt").read_text()
      assert "@Composable" in play_content
      assert "fun Play24Icon(" in play_content
      assert "modifier: Modifier = Modifier" in play_content

  def test_batch_overwrite_handling(self, runner, sample_svgs):
    """Test overwrite handling for existing files."""
    with tempfile.TemporaryDirectory() as temp_dir:
      input_dir = Path(temp_dir) / "input"
      output_dir = Path(temp_dir) / "output"
      input_dir.mkdir()
      output_dir.mkdir()
      
      # Create sample SVG
      (input_dir / "media.play24.svg").write_text(sample_svgs["media.play24.svg"])
      
      # Create existing output file
      existing_dir = output_dir / "media"
      existing_dir.mkdir()
      existing_file = existing_dir / "Play24.kt"
      existing_file.write_text("// Existing content")
      
      # Test without overwrite flag (should require confirmation)
      result = runner.invoke(cli, [
        'batch', str(input_dir), '-o', str(output_dir)
      ], input='n\n')  # Say no to overwrite
      
      assert result.exit_code == 0
      assert "Skipped: 1" in result.output
      assert existing_file.read_text() == "// Existing content"
      
      # Test with overwrite flag
      result = runner.invoke(cli, [
        'batch', str(input_dir), '-o', str(output_dir), '--overwrite'
      ])
      
      assert result.exit_code == 0
      assert "Successfully processed: 1" in result.output
      assert "ImageVector.Builder(" in existing_file.read_text()

  def test_batch_with_custom_template_file(self, runner, sample_svgs):
    """Test batch conversion with custom template file."""
    with tempfile.TemporaryDirectory() as temp_dir:
      input_dir = Path(temp_dir) / "input"
      output_dir = Path(temp_dir) / "output"
      input_dir.mkdir()
      
      # Create custom template
      template_path = Path(temp_dir) / "custom.j2"
      template_content = """{{ imports }}

// Custom template for {{ icon }}
object {{ icon }}Icon {
  val vector: ImageVector by lazy {
    {{ build_code | indent(4, first=False) }}
  }
}"""
      template_path.write_text(template_content)
      
      # Create sample SVG
      (input_dir / "simple_icon.svg").write_text(sample_svgs["simple_icon.svg"])
      
      result = runner.invoke(cli, [
        'batch', str(input_dir), '-o', str(output_dir),
        '-t', str(template_path)
      ])
      
      assert result.exit_code == 0
      
      content = (output_dir / "SimpleIcon.kt").read_text()
      assert "// Custom template for SimpleIcon" in content
      assert "object SimpleIconIcon {" in content
      assert "val vector: ImageVector by lazy {" in content

  def test_batch_with_config_file(self, runner, sample_svgs):
    """Test batch conversion with configuration file."""
    with tempfile.TemporaryDirectory() as temp_dir:
      input_dir = Path(temp_dir) / "input"
      output_dir = Path(temp_dir) / "output"
      input_dir.mkdir()
      
      # Create config file
      config_path = Path(temp_dir) / "config.json"
      config_data = {
        "group_imports": False,
        "indent_size": 4
      }
      with open(config_path, 'w') as f:
        json.dump(config_data, f)
      
      # Create sample SVG
      (input_dir / "media.play24.svg").write_text(sample_svgs["media.play24.svg"])
      
      result = runner.invoke(cli, [
        'batch', str(input_dir), '-o', str(output_dir),
        '-c', str(config_path)
      ])
      
      assert result.exit_code == 0
      
      content = (output_dir / "Media" / "Play24.kt").read_text()
      assert "ImageVector.Builder(" in content

  def test_batch_empty_directory(self, runner):
    """Test batch conversion with empty input directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
      input_dir = Path(temp_dir) / "input"
      input_dir.mkdir()
      
      result = runner.invoke(cli, [
        'batch', str(input_dir)
      ])
      
      assert result.exit_code == 0
      assert "No SVG files found" in result.output

  def test_batch_error_handling(self, runner):
    """Test batch conversion error handling for invalid SVG."""
    with tempfile.TemporaryDirectory() as temp_dir:
      input_dir = Path(temp_dir) / "input"
      output_dir = Path(temp_dir) / "output"
      input_dir.mkdir()
      
      # Create invalid SVG file
      (input_dir / "invalid.svg").write_text("This is not a valid SVG")
      
      result = runner.invoke(cli, [
        'batch', str(input_dir), '-o', str(output_dir)
      ])
      
      assert result.exit_code == 1
      assert "Errors: 1" in result.output
      assert "invalid.svg" in result.output

  def test_batch_help_output(self, runner):
    """Test batch command help output."""
    result = runner.invoke(cli, ['batch', '--help'])
    
    assert result.exit_code == 0
    assert "Convert all SVG files in a directory" in result.output
    assert "--namespace-dirs" in result.output
    assert "--dry-run" in result.output
    assert "--overwrite" in result.output
    assert "Examples:" in result.output

  def test_batch_multi_level_namespaces(self, runner):
    """Test batch conversion with multi-level nested namespaces."""
    with tempfile.TemporaryDirectory() as temp_dir:
      input_dir = Path(temp_dir) / "input"
      output_dir = Path(temp_dir) / "output"
      input_dir.mkdir()
      
      # Create multi-level namespace SVG files
      test_files = {
        "ui.button.primary.svg": """<?xml version="1.0" encoding="UTF-8"?>
<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
  <rect x="4" y="8" width="16" height="8" rx="4" fill="#000"/>
</svg>""",
        
        "system.dialog.modal.svg": """<?xml version="1.0" encoding="UTF-8"?>
<svg width="32" height="32" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
  <rect x="6" y="6" width="20" height="20" rx="2" fill="#000"/>
</svg>""",
        
        "icon.home.svg": """<?xml version="1.0" encoding="UTF-8"?>
<svg width="20" height="20" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
  <path d="M10 3l7 7v7H3v-7l7-7z" fill="#000"/>
</svg>""",
      }
      
      # Create sample SVG files
      for filename, content in test_files.items():
        (input_dir / filename).write_text(content)
      
      result = runner.invoke(cli, [
        'batch', str(input_dir), '-o', str(output_dir)
      ])
      
      assert result.exit_code == 0
      assert "Successfully processed: 3" in result.output
      
      # Check multi-level directory structure (lowercase directories)
      assert (output_dir / "ui" / "button" / "Primary.kt").exists()
      assert (output_dir / "system" / "dialog" / "Modal.kt").exists()
      assert (output_dir / "icon" / "Home.kt").exists()
      
      # Verify content contains correct names
      primary_content = (output_dir / "ui" / "button" / "Primary.kt").read_text()
      assert "val PrimaryIcon: ImageVector" in primary_content
      
      modal_content = (output_dir / "system" / "dialog" / "Modal.kt").read_text()
      assert "val ModalIcon: ImageVector" in modal_content
      
      home_content = (output_dir / "icon" / "Home.kt").read_text()
      assert "val HomeIcon: ImageVector" in home_content

  def test_batch_multi_level_without_namespace_dirs(self, runner):
    """Test multi-level namespaces without directory creation."""
    with tempfile.TemporaryDirectory() as temp_dir:
      input_dir = Path(temp_dir) / "input"
      output_dir = Path(temp_dir) / "output"
      input_dir.mkdir()
      
      # Create multi-level namespace SVG
      (input_dir / "ui.button.primary.svg").write_text("""<?xml version="1.0" encoding="UTF-8"?>
<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
  <rect x="4" y="8" width="16" height="8" rx="4" fill="#000"/>
</svg>""")
      
      result = runner.invoke(cli, [
        'batch', str(input_dir), '-o', str(output_dir), '--no-namespace-dirs'
      ])
      
      assert result.exit_code == 0
      
      # File should be in root directory, not nested
      assert (output_dir / "Primary.kt").exists()
      assert not (output_dir / "ui").exists()
      assert not (output_dir / "button").exists()
      
      # Content should still have correct name
      content = (output_dir / "Primary.kt").read_text()
      assert "val PrimaryIcon: ImageVector" in content

  def test_batch_underscore_naming(self, runner):
    """Test batch conversion with underscore naming patterns."""
    with tempfile.TemporaryDirectory() as temp_dir:
      input_dir = Path(temp_dir) / "input"
      output_dir = Path(temp_dir) / "output"
      input_dir.mkdir()
      
      # Create SVG files with underscore naming
      test_files = {
        "arrow_left.svg": """<?xml version="1.0" encoding="UTF-8"?>
<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
  <path d="M20 12H4m0 0l6-6m-6 6l6 6" stroke="#000" stroke-width="2" fill="none"/>
</svg>""",
        
        "icons.arrow_right.svg": """<?xml version="1.0" encoding="UTF-8"?>
<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
  <path d="M4 12h16m0 0l-6-6m6 6l-6 6" stroke="#000" stroke-width="2" fill="none"/>
</svg>""",
        
        "ui.button_primary.svg": """<?xml version="1.0" encoding="UTF-8"?>
<svg width="32" height="32" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
  <rect x="4" y="12" width="24" height="8" rx="4" fill="#000"/>
</svg>""",
      }
      
      # Create sample SVG files
      for filename, content in test_files.items():
        (input_dir / filename).write_text(content)
      
      result = runner.invoke(cli, [
        'batch', str(input_dir), '-o', str(output_dir)
      ])
      
      assert result.exit_code == 0
      assert "Successfully processed: 3" in result.output
      
      # Check file structure with underscore handling
      assert (output_dir / "ArrowLeft.kt").exists()  # No namespace
      assert (output_dir / "icons" / "ArrowRight.kt").exists()  # Single namespace
      assert (output_dir / "ui" / "ButtonPrimary.kt").exists()  # Multi-part name
      
      # Verify content contains correct PascalCase names
      arrow_left_content = (output_dir / "ArrowLeft.kt").read_text()
      assert "val ArrowLeftIcon: ImageVector" in arrow_left_content
      
      arrow_right_content = (output_dir / "icons" / "ArrowRight.kt").read_text()
      assert "val ArrowRightIcon: ImageVector" in arrow_right_content
      
      button_primary_content = (output_dir / "ui" / "ButtonPrimary.kt").read_text()
      assert "val ButtonPrimaryIcon: ImageVector" in button_primary_content

  def test_batch_mixed_naming_patterns(self, runner):
    """Test batch conversion with mixed naming patterns."""
    with tempfile.TemporaryDirectory() as temp_dir:
      input_dir = Path(temp_dir) / "input"
      output_dir = Path(temp_dir) / "output"
      input_dir.mkdir()
      
      # Create mix of naming patterns
      test_files = {
        "home.svg": """<svg width="24" height="24" viewBox="0 0 24 24"><path d="M10 3l7 7v7H3v-7l7-7z"/></svg>""",
        "arrow_left.svg": """<svg width="24" height="24" viewBox="0 0 24 24"><path d="M20 12H4l6-6m-6 6l6 6"/></svg>""",
        "ui.button.svg": """<svg width="24" height="24" viewBox="0 0 24 24"><rect x="4" y="10" width="16" height="4"/></svg>""",
        "icons.arrow_right.svg": """<svg width="24" height="24" viewBox="0 0 24 24"><path d="M4 12h16l-6-6m6 6l-6 6"/></svg>""",
        "system.dialog_modal.svg": """<svg width="24" height="24" viewBox="0 0 24 24"><rect x="4" y="4" width="16" height="16"/></svg>""",
      }
      
      for filename, content in test_files.items():
        (input_dir / filename).write_text(content)
      
      result = runner.invoke(cli, [
        'batch', str(input_dir), '-o', str(output_dir), '--dry-run'
      ])
      
      assert result.exit_code == 0
      assert "Successfully processed: 5" in result.output
      
      # Check expected output paths in dry run
      assert "Home.kt" in result.output  # Simple name
      assert "ArrowLeft.kt" in result.output  # Underscore converted
      assert "ui/Button.kt" in result.output  # Dot separator
      assert "icons/ArrowRight.kt" in result.output  # Namespace + underscore
      assert "system/DialogModal.kt" in result.output  # Namespace + underscore name

  def test_batch_space_naming(self, runner):
    """Test batch conversion with space naming patterns."""
    with tempfile.TemporaryDirectory() as temp_dir:
      input_dir = Path(temp_dir) / "input"
      output_dir = Path(temp_dir) / "output"
      input_dir.mkdir()
      
      # Create SVG files with space naming
      test_files = {
        "arrow left.svg": """<?xml version="1.0" encoding="UTF-8"?>
<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
  <path d="M20 12H4m0 0l6-6m-6 6l6 6" stroke="#000" stroke-width="2" fill="none"/>
</svg>""",
        
        "icons.arrow right.svg": """<?xml version="1.0" encoding="UTF-8"?>
<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
  <path d="M4 12h16m0 0l-6-6m6 6l-6 6" stroke="#000" stroke-width="2" fill="none"/>
</svg>""",
        
        "ui.button primary.svg": """<?xml version="1.0" encoding="UTF-8"?>
<svg width="32" height="32" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
  <rect x="4" y="12" width="24" height="8" rx="4" fill="#000"/>
</svg>""",
        
        "system.dialog modal.svg": """<?xml version="1.0" encoding="UTF-8"?>
<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
  <rect x="6" y="6" width="12" height="12" rx="2" fill="#000"/>
</svg>""",
      }
      
      # Create sample SVG files
      for filename, content in test_files.items():
        (input_dir / filename).write_text(content)
      
      result = runner.invoke(cli, [
        'batch', str(input_dir), '-o', str(output_dir)
      ])
      
      assert result.exit_code == 0
      assert "Successfully processed: 4" in result.output
      
      # Check file structure with space handling (converted to camelCase/PascalCase)
      assert (output_dir / "ArrowLeft.kt").exists()  # No namespace
      assert (output_dir / "icons" / "ArrowRight.kt").exists()  # Single namespace
      assert (output_dir / "ui" / "ButtonPrimary.kt").exists()  # Namespace + space name
      assert (output_dir / "system" / "DialogModal.kt").exists()  # Namespace + space name
      
      # Verify content contains correct PascalCase names
      arrow_left_content = (output_dir / "ArrowLeft.kt").read_text()
      assert "val ArrowLeftIcon: ImageVector" in arrow_left_content
      
      arrow_right_content = (output_dir / "icons" / "ArrowRight.kt").read_text()
      assert "val ArrowRightIcon: ImageVector" in arrow_right_content
      
      button_primary_content = (output_dir / "ui" / "ButtonPrimary.kt").read_text()
      assert "val ButtonPrimaryIcon: ImageVector" in button_primary_content
      
      dialog_modal_content = (output_dir / "system" / "DialogModal.kt").read_text()
      assert "val DialogModalIcon: ImageVector" in dialog_modal_content 