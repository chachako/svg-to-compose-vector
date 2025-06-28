from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import json


@dataclass
class Config:
  """Configuration for SVG to Compose converter."""
  
  # Template settings
  template_path: Optional[Path] = None
  
  # Code generation settings
  optimize_colors: bool = True
  optimize_paths: bool = True
  indent_size: int = 2
  use_trailing_comma: bool = True
  
  # Output formatting
  max_line_length: int = 120
  imports_at_top: bool = True
  group_imports: bool = True
  
  @classmethod
  def from_file(cls, config_path: Path) -> "Config":
    """Load configuration from JSON file."""
    if not config_path.exists():
      return cls()
    
    try:
      with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
      return cls(**data)
    except (json.JSONDecodeError, TypeError) as e:
      raise ValueError(f"Invalid config file format: {e}")
  
  def to_file(self, config_path: Path) -> None:
    """Save configuration to JSON file."""
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    data = {
      "template_path": str(self.template_path) if self.template_path else None,
      "optimize_colors": self.optimize_colors,
      "optimize_paths": self.optimize_paths,
      "indent_size": self.indent_size,
      "use_trailing_comma": self.use_trailing_comma,
      "max_line_length": self.max_line_length,
      "imports_at_top": self.imports_at_top,
      "group_imports": self.group_imports,
    }
    
    with open(config_path, "w", encoding="utf-8") as f:
      json.dump(data, f, indent=2)
  
  def merge_with_options(self, **options) -> "Config":
    """Create new config with updated options."""
    data = {}
    for field_name in self.__dataclass_fields__:
      value = options.get(field_name, getattr(self, field_name))
      data[field_name] = value
    return Config(**data)