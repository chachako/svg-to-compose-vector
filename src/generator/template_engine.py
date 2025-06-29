import re
from pathlib import Path

try:
  from jinja2 import Environment, FileSystemLoader

  HAS_JINJA2 = True
except ImportError:
  HAS_JINJA2 = False

from ..core.config import Config
from ..utils.naming import NameComponents, NameResolver


class TemplateEngine:
  """Template engine for generating customized output."""

  def __init__(self, config: Config):
    self.config = config
    self._env: Environment | None = None
    self._setup_environment()

  def _setup_environment(self):
    """Set up Jinja2 environment with templates."""
    if not HAS_JINJA2:
      return

    templates_dir = Path(__file__).parent / "templates"
    self._env = Environment(
      loader=FileSystemLoader(templates_dir),
      trim_blocks=True,
      lstrip_blocks=True,
    )

    # Custom filters
    self._env.filters["pascal_case"] = self._to_pascal_case
    self._env.filters["camel_case"] = self._to_camel_case
    self._env.filters["snake_case"] = self._to_snake_case

  def render(
    self,
    template_name: str,
    build_code: str,
    imports: set[str],
    name_components: NameComponents | None = None,
    icon_name: str | None = None,
    **template_vars,
  ) -> str:
    """Render template with provided variables."""

    # Handle backward compatibility: create NameComponents from icon_name if needed
    if name_components is None:
      if icon_name is None:
        raise ValueError("Either name_components or icon_name must be provided")

      # Use NameResolver to properly parse the icon_name
      name_resolver = NameResolver()
      name_components = name_resolver.resolve_name_from_string(icon_name)

    # Fallback to simple string interpolation if Jinja2 not available
    if not HAS_JINJA2 or not self._env:
      return self._simple_render(build_code, imports, **template_vars)

    # Format imports
    formatted_imports = self._format_imports(imports)

    # Prepare template variables
    variables = {
      "imports": formatted_imports,
      "build_code": build_code,
      "name": name_components,  # Complete NameComponents object
      "namespace": name_components.namespace_part_pascal,
      "icon": name_components.name_part_pascal,
      "full_name": name_components.full_path_pascal,
      # Backward compatibility - pass raw name for filter processing
      "icon_name": name_components.name,  # Use raw name, not pascal case
      **template_vars,
    }

    # Use custom template file if specified
    if self.config.template_path:
      template_content = self.config.template_path.read_text(encoding="utf-8")
      template = self._env.from_string(template_content)
    else:
      # Use built-in template
      template = self._env.get_template(f"{template_name}.j2")

    return template.render(**variables)

  def _simple_render(self, build_code: str, imports: set[str], **template_vars) -> str:
    """Simple fallback rendering without Jinja2."""
    formatted_imports = self._format_imports(imports)

    return f"{formatted_imports}\n\n{build_code}"

  def _format_imports(self, imports: set[str]) -> str:
    """Format imports according to configuration."""
    if not imports:
      return ""

    sorted_imports = sorted(imports)

    if self.config.group_imports:
      # Group by package
      groups = {}
      for imp in sorted_imports:
        parts = imp.split(".")
        if len(parts) >= 3:
          group = f"{parts[0]}.{parts[1]}.{parts[2]}"
        else:
          group = imp
        if group not in groups:
          groups[group] = []
        groups[group].append(imp)

      lines = []
      for group_name in sorted(groups.keys()):
        for imp in sorted(groups[group_name]):
          lines.append(f"import {imp}")
        lines.append("")  # Empty line between groups

      # Remove trailing empty line
      if lines and lines[-1] == "":
        lines.pop()

      return "\n".join(lines)
    else:
      # Simple sorted list without grouping
      return "\n".join(f"import {imp}" for imp in sorted_imports)

  def _to_pascal_case(self, text: str) -> str:
    """Convert text to PascalCase."""
    # Remove non-alphanumeric characters and split
    words = re.sub(r"[^a-zA-Z0-9]", " ", text).split()
    return "".join(word.capitalize() for word in words if word)

  def _to_camel_case(self, text: str) -> str:
    """Convert text to camelCase."""
    pascal = self._to_pascal_case(text)
    return pascal[0].lower() + pascal[1:] if pascal else ""

  def _to_snake_case(self, text: str) -> str:
    """Convert text to snake_case."""
    # Replace non-alphanumeric with underscores
    text = re.sub(r"[^a-zA-Z0-9]", "_", text)
    # Handle camelCase
    text = re.sub(r"([a-z])([A-Z])", r"\1_\2", text)
    return text.lower()

  def list_available_templates(self) -> list[str]:
    """List available built-in templates."""
    templates_dir = Path(__file__).parent / "templates"
    if not templates_dir.exists():
      return []

    templates = []
    for template_file in templates_dir.glob("*.j2"):
      templates.append(template_file.stem)

    return sorted(templates)
