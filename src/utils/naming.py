import re
from dataclasses import dataclass
from typing import Optional, List
from pathlib import Path


@dataclass
class NameComponents:
  """Parsed name components providing flexible access to naming parts."""
  
  raw_name: str
  file_stem: str
  categories: List[str]
  name: str

  @property
  def namespace_part(self) -> str:
    """Content before the last dot.
    
    Example: 'navigation.home' -> 'Navigation'
    Example: 'button' -> '' (empty)
    """
    return ".".join(self.categories[:-1]) if len(self.categories) > 1 else ""

  @property
  def name_part(self) -> str:
    """Content after the last dot.
    
    Example: 'navigation.home' -> 'Home'
    Example: 'button' -> 'Button'
    """
    return self.name

  @property
  def full_path(self) -> str:
    """Complete path with all components.
    
    Example: 'navigation.home' -> 'Navigation.Home'
    Example: 'button' -> 'Button'
    """
    return ".".join(self.categories)

  @property
  def namespace_part_pascal(self) -> str:
    """Namespace in PascalCase format.
    
    Example: 'navigation.settings' -> 'Navigation'
    Example: 'icon_button' -> '' (empty for single component)
    """
    return self._to_pascal_case(self.namespace_part)

  @property
  def namespace_part_camel(self) -> str:
    """Namespace in camelCase format.
    
    Example: 'navigation.settings' -> 'navigation'
    Example: 'icon_button' -> '' (empty for single component)
    """
    return self._to_camel_case(self.namespace_part)

  @property
  def name_part_pascal(self) -> str:
    """Name in PascalCase format.
    
    Example: 'navigation.home_icon' -> 'HomeIcon'
    Example: 'close-button' -> 'CloseButton'
    """
    return self._to_pascal_case(self.name_part)

  @property
  def name_part_camel(self) -> str:
    """Name in camelCase format.
    
    Example: 'navigation.home_icon' -> 'homeIcon'
    Example: 'close-button' -> 'closeButton'
    """
    return self._to_camel_case(self.name_part)

  @property
  def full_path_pascal(self) -> str:
    """Full path in PascalCase.
    
    Example: 'ui.button' -> 'Ui.Button'
    Example: 'system.dialog.modal' -> 'System.Dialog.Modal'
    """
    return ".".join(self._pascalize_word(cat) for cat in self.categories)

  @property
  def full_path_camel(self) -> str:
    """Full path in camelCase format.
    
    Example: 'ui.buttons.primary' -> 'ui.buttons.primary'
    Example: 'arrow_left' -> 'arrowLeft'
    """
    return self._to_camel_case(self.full_path)

  @property
  def namespace_path_components(self) -> List[str]:
    """Namespace path components for creating nested directories.
    
    Example: 'ui.button' -> ['Ui']
    Example: 'system.dialog.modal' -> ['System', 'Dialog']
    Example: 'icon' -> [] (empty)
    """
    if len(self.categories) > 1:
      return [self._pascalize_word(cat) for cat in self.categories[:-1]]
    return []

  @property
  def namespace_path_components_lowercase(self) -> List[str]:
    """Namespace path components in lowercase for directory creation.
    
    Example: 'ui.button' -> ['ui']
    Example: 'system.dialog.modal' -> ['system', 'dialog']
    Example: 'icon' -> [] (empty)
    """
    if len(self.categories) > 1:
      return [cat.lower() for cat in self.categories[:-1]]
    return []

  @property
  def namespace_nested_path(self) -> Path:
    """Namespace as nested Path object for directory creation.
    
    Example: 'ui.button' -> Path('Ui')
    Example: 'system.dialog.modal' -> Path('System/Dialog')
    Example: 'icon' -> Path('.') (current dir)
    """
    if self.namespace_path_components:
      return Path(*self.namespace_path_components)
    return Path(".")

  @property
  def namespace_nested_path_lowercase(self) -> Path:
    """Namespace as nested Path object with lowercase directories.
    
    Example: 'ui.button' -> Path('ui')
    Example: 'system.dialog.modal' -> Path('system/dialog')
    Example: 'icon' -> Path('.') (current dir)
    """
    if self.namespace_path_components_lowercase:
      return Path(*self.namespace_path_components_lowercase)
    return Path(".")

  def _to_pascal_case(self, text: str) -> str:
    """Convert text to PascalCase, preserving dot separators."""
    if not text:
      return ""
    parts = text.split(".")
    return ".".join(self._capitalize_word(part) for part in parts)

  def _to_camel_case(self, text: str) -> str:
    """Convert text to camelCase, preserving dot separators."""
    if not text:
      return ""
    parts = text.split(".")
    result = []
    for i, part in enumerate(parts):
      if i == 0:
        result.append(self._lowercase_word(part))
      else:
        result.append(self._capitalize_word(part))
    return ".".join(result)

  def _capitalize_word(self, word: str) -> str:
    """Convert single word to PascalCase."""
    if not word:
      return ""
    
    # Split by word boundaries (underscores, hyphens, spaces, and camelCase boundaries)
    # This regex splits on non-alphanumeric characters and camelCase boundaries
    parts = re.split(r'[^a-zA-Z0-9]+|(?<=[a-z])(?=[A-Z])', word)
    
    # Filter out empty parts and capitalize each part
    result_parts = []
    for part in parts:
      if part:  # Only process non-empty parts
        result_parts.append(part.capitalize())
    
    return "".join(result_parts)

  def _lowercase_word(self, word: str) -> str:
    """Convert single word to camelCase."""
    capitalized = self._capitalize_word(word)
    return capitalized[0].lower() + capitalized[1:] if capitalized else ""

  def _pascalize_word(self, word: str) -> str:
    """Convert a word to PascalCase."""
    return self._capitalize_word(word)


class NameResolver:
  """Resolves hierarchical naming structure from file paths."""

  def __init__(self, separator: str = "."):
    self.separator = separator

  def resolve_name(self, file_path: Path, user_name: Optional[str] = None) -> NameComponents:
    """Parse name components from file path or user-specified name.
    
    Examples:
      'navigation.home.svg' -> NameComponents with namespace='Navigation', name='Home'
      'arrow-left.svg' -> NameComponents with namespace='', name='ArrowLeft'
      user_name='ui.buttons.primary' -> NameComponents with namespace='Ui.Buttons', name='Primary'
    """
    if user_name:
      return self._parse_name(user_name)
    else:
      # Clean filename by replacing problematic characters
      clean_name = file_path.stem.replace("-", "_").replace(" ", "_")
      return self._parse_name(clean_name)

  def _parse_name(self, name: str) -> NameComponents:
    """Parse name string into hierarchical components."""
    parts = name.split(self.separator)

    # Store original parts without case conversion for later processing
    categories = []
    for part in parts:
      clean_part = self._clean_identifier(part)
      if clean_part:  # Only add non-empty parts
        categories.append(clean_part)

    return NameComponents(
      raw_name=name,
      file_stem=name,
      categories=categories,
      name=categories[-1] if categories else "UnnamedIcon"
    )

  def _clean_identifier(self, text: str) -> str:
    """Clean text but preserve word boundaries for proper case conversion."""
    # Replace invalid characters with underscores to preserve word boundaries
    clean_text = re.sub(r"[^a-zA-Z0-9]", "_", text)
    # Remove leading/trailing underscores and collapse multiple underscores
    clean_text = re.sub(r"^_+|_+$", "", clean_text)
    clean_text = re.sub(r"_+", "_", clean_text)
    return clean_text

  def resolve_name_from_string(self, name: str) -> NameComponents:
    """Parse name components directly from a string.
    
    This is a convenience method that doesn't require a file path.
    
    Examples:
      'navigation.home' -> NameComponents with namespace='Navigation', name='Home'
      'arrow_left' -> NameComponents with namespace='', name='ArrowLeft'
    """
    return self._parse_name(name) 