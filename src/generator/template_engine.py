import re
from pathlib import Path

try:
  from jinja2 import Environment, FileSystemLoader

  HAS_JINJA2 = True
except ImportError:
  HAS_JINJA2 = False

from ..core.config import Config
from ..ir.image_vector import IrImageVector
from ..utils.color_analyzer import ColorAnalyzer
from ..utils.color_substitution import ColorParameterSubstitution
from ..utils.naming import NameComponents, NameResolver


class TemplateEngine:
  """Template engine for generating customized output."""

  def __init__(self, config: Config):
    self.config = config
    self._env: Environment | None = None
    self.color_analyzer = ColorAnalyzer()
    self.color_substitution = ColorParameterSubstitution()
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

  def render_with_multicolor_support(
    self,
    template_name: str,
    build_code: str,
    imports: set[str],
    ir: IrImageVector,
    multicolor_template_path: Path | None = None,
    name_components: NameComponents | None = None,
    icon_name: str | None = None,
    **template_vars,
  ) -> str:
    """Render template with multi-color support and intelligent template selection.

    Args:
      template_name: Default template name to use
      build_code: Generated ImageVector code
      imports: Required imports
      ir: ImageVector intermediate representation for color analysis
      multicolor_template_path: Path to multicolor template file (optional)
      name_components: Name components for template variables
      icon_name: Icon name for backward compatibility
      **template_vars: Additional template variables

    Returns:
      Rendered template output
    """
    # 1. Extract all colors used in SVG
    color_analysis = self.color_analyzer.analyze_colors(ir)
    used_colors = color_analysis.used_colors

    # 2. Check if multicolor template should be used
    should_use_multicolor = False
    color_mappings = {}

    if multicolor_template_path and multicolor_template_path.exists():
      # Parse color mappings from multicolor template
      template_colors = self.color_analyzer.load_template_mappings_from_file(
        multicolor_template_path
      )
      color_mappings = self.color_substitution.load_and_parse_template(multicolor_template_path)

      # 3. Check if intersection exists: (SVG colors ∩ template mappings) > 0
      should_use_multicolor = self.color_analyzer.should_use_multicolor_template(
        used_colors, template_colors
      )

    # 4. Choose template and generate appropriate code
    if should_use_multicolor and color_mappings:
      return self._render_multicolor_template(
        multicolor_template_path,
        build_code,
        imports,
        used_colors,
        color_mappings,
        name_components,
        icon_name,
        **template_vars,
      )
    else:
      # 5. Fallback to default template
      return self.render(
        template_name,
        build_code,
        imports,
        name_components,
        icon_name,
        **template_vars,
      )

  def _render_multicolor_template(
    self,
    template_path: Path,
    build_code: str,
    imports: set[str],
    used_colors: set[str],
    color_mappings: dict[str, dict[str, str]],
    name_components: NameComponents | None = None,
    icon_name: str | None = None,
    **template_vars,
  ) -> str:
    """Render multicolor template with color parameter substitution."""

    # Handle backward compatibility
    if name_components is None:
      if icon_name is None:
        raise ValueError("Either name_components or icon_name must be provided")

      name_resolver = NameResolver()
      name_components = name_resolver.resolve_name_from_string(icon_name)

    # Fallback if Jinja2 not available
    if not HAS_JINJA2 or not self._env:
      return self._simple_render(build_code, imports, **template_vars)

    # Generate code with color parameters substituted
    build_code_with_color_params = self.color_substitution.substitute_colors_in_code(
      build_code, color_mappings
    )

    # Format imports
    formatted_imports = self._format_imports(imports)

    # Prepare template variables for multicolor template
    variables = {
      "imports": formatted_imports,
      "build_code": build_code,  # Original code
      "build_code_with_color_params": build_code_with_color_params,  # Parameterized code
      "used_colors": used_colors,  # Set of hex colors used in SVG
      "color_mappings": color_mappings,  # Parsed color mappings
      "name": name_components,
      "namespace": name_components.namespace_part_pascal,
      "icon": name_components.name_part_pascal,
      "full_name": name_components.full_path_pascal,
      "icon_name": name_components.name,
      **template_vars,
    }

    # Load and render custom multicolor template
    template_content = template_path.read_text(encoding="utf-8")
    template = self._env.from_string(template_content)

    return template.render(**variables)
