import json
import tempfile
from pathlib import Path

import pytest

from src.core.config import Config


class TestConfig:
  """Test configuration system functionality."""

  def test_default_config(self):
    """Test default configuration values."""
    config = Config()

    assert config.template_path is None
    assert config.optimize_colors is True
    assert config.optimize_paths is True
    assert config.indent_size == 2
    assert config.use_trailing_comma is True
    assert config.max_line_length == 120
    assert config.imports_at_top is True
    assert config.group_imports is True

  def test_config_from_file_nonexistent(self):
    """Test loading config from non-existent file returns default."""
    with tempfile.TemporaryDirectory() as temp_dir:
      config_path = Path(temp_dir) / "nonexistent.json"
      config = Config.from_file(config_path)

      # Should return default config
      assert config.indent_size == 2

  def test_config_from_file_valid(self):
    """Test loading config from valid JSON file."""
    with tempfile.TemporaryDirectory() as temp_dir:
      config_path = Path(temp_dir) / "config.json"

      config_data = {"indent_size": 4, "optimize_colors": False, "max_line_length": 100}

      with open(config_path, "w") as f:
        json.dump(config_data, f)

      config = Config.from_file(config_path)

      assert config.indent_size == 4
      assert config.optimize_colors is False
      assert config.max_line_length == 100
      # Unspecified values should remain default
      assert config.use_trailing_comma is True

  def test_config_from_file_invalid_json(self):
    """Test loading config from invalid JSON file raises error."""
    with tempfile.TemporaryDirectory() as temp_dir:
      config_path = Path(temp_dir) / "invalid.json"

      with open(config_path, "w") as f:
        f.write("{ invalid json")

      with pytest.raises(ValueError, match="Invalid config file format"):
        Config.from_file(config_path)

  def test_config_to_file(self):
    """Test saving config to file."""
    with tempfile.TemporaryDirectory() as temp_dir:
      config_path = Path(temp_dir) / "output.json"

      config = Config(indent_size=4, optimize_colors=False)

      config.to_file(config_path)

      assert config_path.exists()

      with open(config_path) as f:
        data = json.load(f)

      assert data["indent_size"] == 4
      assert data["optimize_colors"] is False
      assert data["template_path"] is None

  def test_config_to_file_creates_directory(self):
    """Test saving config creates parent directories."""
    with tempfile.TemporaryDirectory() as temp_dir:
      config_path = Path(temp_dir) / "nested" / "config.json"

      config = Config()
      config.to_file(config_path)

      assert config_path.exists()
      assert config_path.parent.exists()

  def test_merge_with_options(self):
    """Test merging config with new options."""
    base_config = Config(indent_size=2, optimize_colors=True)

    merged_config = base_config.merge_with_options(indent_size=4, max_line_length=80)

    # Original config should be unchanged
    assert base_config.indent_size == 2
    assert base_config.max_line_length == 120

    # Merged config should have updated values
    assert merged_config.indent_size == 4  # updated
    assert merged_config.max_line_length == 80  # updated
    assert merged_config.optimize_colors is True  # unchanged

  def test_merge_with_empty_options(self):
    """Test merging with empty options returns identical config."""
    original_config = Config(indent_size=4)
    merged_config = original_config.merge_with_options()

    assert merged_config.indent_size == original_config.indent_size
    assert merged_config.optimize_colors == original_config.optimize_colors

  def test_template_path_handling(self):
    """Test template_path field with Path objects."""
    with tempfile.TemporaryDirectory() as temp_dir:
      template_path = Path(temp_dir) / "template.j2"
      template_path.write_text("test template")

      config = Config(template_path=template_path)

      # Save and reload
      config_file = Path(temp_dir) / "config.json"
      config.to_file(config_file)

      loaded_config = Config.from_file(config_file)

      # template_path should be loaded as string, not Path
      assert isinstance(loaded_config.template_path, str)
      assert loaded_config.template_path == str(template_path)
