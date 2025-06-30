"""Color parameter substitution for multi-color template support.

This module handles the replacement of hex color values with parameter references
in generated Kotlin code for multi-color icon templates.

Supports two color mapping formats:

1. Full format (with parameters):
   {%- set color_mappings = {
       "#FF0000": {"semantic_name": "errorColor", "replacement": "Color.Red"},
       "#0000FF": {"semantic_name": "primaryColor", "replacement": "MaterialTheme.colorScheme.primary"}
   } -%}

   Generated function will have corresponding color parameters:
   fun MyIcon(
     errorColor: Color = Color.Red,
     primaryColor: Color = MaterialTheme.colorScheme.primary
   ): ImageVector

2. Simplified format (direct replacement):
   {%- set color_mappings = {
       "#FF0000": "MaterialTheme.colorScheme.error",
       "#0000FF": "MaterialTheme.colorScheme.primary"
   } -%}

   Generated function will have no parameters, colors are directly replaced:
   fun MyIcon(): ImageVector

   Color(0xFFFF0000) in code becomes MaterialTheme.colorScheme.error

3. Mixed format:
   {%- set color_mappings = {
       "#FF0000": {"semantic_name": "errorColor", "replacement": "Color.Red"},
       "#0000FF": "MaterialTheme.colorScheme.primary"
   } -%}

   Generated function will only have semantic parameters:
   fun MyIcon(errorColor: Color = Color.Red): ImageVector
"""

import re
from pathlib import Path


class ColorParameterSubstitution:
  """Handles color parameter substitution in generated Kotlin code."""

  def __init__(self):
    # Regex patterns for color matching
    self.color_pattern = re.compile(r"Color\(0x([A-F0-9]{8})\)")
    self.solid_color_pattern = re.compile(r"SolidColor\(Color\(0x([A-F0-9]{8})\)\)")
    self.brush_color_pattern = re.compile(r"(\d+f\s+to\s+)Color\(0x([A-F0-9]{8})\)")

  def extract_color_mappings_from_template(
    self, template_content: str
  ) -> dict[str, dict[str, str]]:
    """Extract color mappings dictionary from template content.

    Args:
      template_content: The Jinja2 template content

    Returns:
      Dictionary mapping hex colors to their semantic info:
      {
        "#2196F3": {"semantic_name": "primaryColor", "replacement": "MaterialTheme.colorScheme.primary"},
        "#FF9800": {"semantic_name": "accentColor", "replacement": "Color(0xFFFF9800)"}
      }
    """
    mappings = {}

    try:
      # Look for color_mappings block in template
      # Handle Jinja2 set syntax with multi-line blocks
      # Support both {%- ... -%} and {%- ... %} formats
      mapping_pattern = r"\{%-\s*set\s+color_mappings\s*=\s*\{(.*?)\}\s*-?%\}"
      match = re.search(mapping_pattern, template_content, re.DOTALL)

      if match:
        mappings_block = match.group(1)

        # Extract individual color mappings with flexible patterns
        # Pattern handles both 6-digit (#RRGGBB) and 8-digit (#AARRGGBB) hex colors
        # Support both full format and simplified format

        # Full format: "#color": {"semantic_name": "name", "replacement": "value"}
        full_pattern = r'"(#[0-9A-Fa-f]{6,8})"\s*:\s*\{\s*"semantic_name"\s*:\s*"([^"]+)"\s*,\s*"replacement"\s*:\s*"([^"]+)"\s*\}'

        # Simplified format: "#color": "replacement_value"
        simple_pattern = r'"(#[0-9A-Fa-f]{6,8})"\s*:\s*"([^"]+)"'

        # First process full format entries
        for match in re.finditer(full_pattern, mappings_block, re.DOTALL):
          hex_color = match.group(1).upper()  # Normalize to uppercase
          semantic_name = match.group(2)
          replacement = match.group(3)

          mappings[hex_color] = {"semantic_name": semantic_name, "replacement": replacement}

        # Then process simplified format entries (only if not already processed)
        for match in re.finditer(simple_pattern, mappings_block, re.DOTALL):
          hex_color = match.group(1).upper()  # Normalize to uppercase
          replacement_value = match.group(2)

          # Only add if not already processed by full pattern
          if hex_color not in mappings:
            mappings[hex_color] = {"semantic_name": None, "replacement": replacement_value}

    except Exception as e:
      # Gracefully handle parsing errors
      print(f"Error parsing template mappings: {e}")
      pass

    return mappings

  def substitute_colors_in_code(
    self, kotlin_code: str, color_mappings: dict[str, dict[str, str]]
  ) -> str:
    """Replace hex color values with parameter references in Kotlin code.

    Args:
      kotlin_code: The generated Kotlin ImageVector code
      color_mappings: Color mapping dictionary from template

    Returns:
      Kotlin code with color parameters substituted
    """
    from ..ir.color import IrColor

    modified_code = kotlin_code

    # Create mapping from ARGB hex to parameter names
    argb_to_param = {}
    # Also create mapping from built-in color names to parameter names
    builtin_name_to_param = {}

    for hex_color, mapping in color_mappings.items():
      if hex_color.startswith("#"):
        # Determine the replacement value (semantic_name or replacement)
        replacement_value = mapping.get("semantic_name") or mapping["replacement"]

        if len(hex_color) == 7:
          # Convert #RRGGBB to 0xFFRRGGBB format (full opacity)
          argb_hex = f"FF{hex_color[1:].upper()}"
          argb_to_param[argb_hex] = replacement_value

          # Check if this hex color matches a built-in color
          color_obj = IrColor.from_hex(hex_color)
          builtin_name = color_obj.to_compose_color_name()
          if builtin_name:
            builtin_name_to_param[builtin_name] = replacement_value

        elif len(hex_color) == 9:
          # Convert #AARRGGBB to 0xAARRGGBB format (with alpha)
          argb_hex = hex_color[1:].upper()
          argb_to_param[argb_hex] = replacement_value

    # Replace SolidColor(Color.BuiltinName) patterns first
    builtin_solid_pattern = re.compile(r"SolidColor\(Color\.([A-Za-z]+)\)")

    def replace_builtin_solid_color(match):
      builtin_name = match.group(1)
      if builtin_name in builtin_name_to_param:
        return f"SolidColor({builtin_name_to_param[builtin_name]})"
      return match.group(0)  # No replacement

    modified_code = builtin_solid_pattern.sub(replace_builtin_solid_color, modified_code)

    # Replace standalone Color.BuiltinName patterns
    builtin_color_pattern = re.compile(r"Color\.([A-Za-z]+)")

    def replace_builtin_color(match):
      builtin_name = match.group(1)
      if builtin_name in builtin_name_to_param:
        return builtin_name_to_param[builtin_name]
      return match.group(0)  # No replacement

    modified_code = builtin_color_pattern.sub(replace_builtin_color, modified_code)

    # Replace gradient built-in color patterns: 0f to Color.BuiltinName
    builtin_brush_pattern = re.compile(r"(\d+f\s+to\s+)Color\.([A-Za-z]+)")

    def replace_builtin_brush_color(match):
      prefix = match.group(1)  # "0f to " part
      builtin_name = match.group(2)
      if builtin_name in builtin_name_to_param:
        return f"{prefix}{builtin_name_to_param[builtin_name]}"
      return match.group(0)  # No replacement

    modified_code = builtin_brush_pattern.sub(replace_builtin_brush_color, modified_code)

    # Replace SolidColor(Color(0xFFxxxxxx)) patterns
    def replace_solid_color(match):
      argb_value = match.group(1)
      if argb_value in argb_to_param:
        return f"SolidColor({argb_to_param[argb_value]})"
      return match.group(0)  # No replacement

    modified_code = self.solid_color_pattern.sub(replace_solid_color, modified_code)

    # Replace standalone Color(0xFFxxxxxx) patterns
    def replace_color(match):
      argb_value = match.group(1)
      if argb_value in argb_to_param:
        return argb_to_param[argb_value]
      return match.group(0)  # No replacement

    modified_code = self.color_pattern.sub(replace_color, modified_code)

    # Replace gradient color stop patterns: 0f to Color(0xFFxxxxxx)
    def replace_brush_color(match):
      prefix = match.group(1)  # "0f to " part
      argb_value = match.group(2)
      if argb_value in argb_to_param:
        return f"{prefix}{argb_to_param[argb_value]}"
      return match.group(0)  # No replacement

    modified_code = self.brush_color_pattern.sub(replace_brush_color, modified_code)

    return modified_code

  def generate_parameter_list(
    self, used_colors: set[str], color_mappings: dict[str, dict[str, str]]
  ) -> str:
    """Generate Kotlin function parameter list for colors.

    Args:
      used_colors: Set of hex colors used in the SVG
      color_mappings: Color mapping dictionary from template

    Returns:
      Kotlin parameter list string (without surrounding parentheses)
    """
    parameters = []

    for hex_color in sorted(used_colors):
      normalized_color = hex_color.upper()
      if normalized_color in color_mappings:
        mapping = color_mappings[normalized_color]
        # Only add parameters for mappings with semantic_name (not direct replacements)
        if mapping.get("semantic_name"):
          param_line = f"  {mapping['semantic_name']}: Color = {mapping['replacement']}"
          parameters.append(param_line)

    return ",\n".join(parameters)

  def load_and_parse_template(self, template_path: Path) -> dict[str, dict[str, str]]:
    """Load template file and extract color mappings.

    Args:
      template_path: Path to the template file

    Returns:
      Color mappings dictionary
    """
    if not template_path.exists():
      return {}

    try:
      template_content = template_path.read_text(encoding="utf-8")
      return self.extract_color_mappings_from_template(template_content)
    except Exception:
      return {}
