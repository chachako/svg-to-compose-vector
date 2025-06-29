from ..ir.gradient import IrColorFill, IrFill, IrLinearGradient, IrRadialGradient
from ..ir.image_vector import IrImageVector
from ..ir.path_node import path_data_to_dsl
from ..ir.vector_node import IrVectorGroup, IrVectorNode, IrVectorPath
from ..utils.formatting import format_dp, format_float


class ImageVectorGenerator:
  """Generates Kotlin ImageVector code from IR."""

  def __init__(self):
    self.imports: set[str] = set()
    self.indent_level = 0

  def generate(self, ir: IrImageVector) -> str:
    """Generate complete ImageVector.Builder(...).build() code."""
    core_code, _ = self.generate_core_code(ir)
    return core_code

  def generate_core_code(self, ir: IrImageVector) -> tuple[str, set[str]]:
    """Generate ImageVector.Builder(...).build() code and return imports."""
    self.imports.clear()
    self.indent_level = 0

    self.imports.add("androidx.compose.ui.graphics.vector.ImageVector")
    self.imports.add("androidx.compose.ui.unit.dp")

    lines = []

    lines.append("ImageVector.Builder(")
    lines.append(f'  name = "{ir.name}",')
    lines.append(f"  defaultWidth = {format_dp(ir.default_width)}.dp,")
    lines.append(f"  defaultHeight = {format_dp(ir.default_height)}.dp,")
    lines.append(f"  viewportWidth = {format_float(ir.viewport_width)},")
    lines.append(f"  viewportHeight = {format_float(ir.viewport_height)},")

    if ir.auto_mirror:
      lines.append("  autoMirror = true,")

    lines.append(").apply {")

    self.indent_level = 1
    for node in ir.nodes:
      node_lines = self._generate_node(node)
      lines.extend(node_lines)

    lines.append("}.build()")

    return "\n".join(lines), self.imports.copy()

  def _generate_node(self, node: IrVectorNode) -> list[str]:
    """Generate code for a vector node (path or group)."""
    if isinstance(node, IrVectorPath):
      return self._generate_path(node)
    elif isinstance(node, IrVectorGroup):
      return self._generate_group(node)
    else:
      raise ValueError(f"Unknown node type: {type(node)}")

  def _generate_path(self, path: IrVectorPath) -> list[str]:
    """Generate path { } block."""
    lines = []
    indent = "  " * self.indent_level

    # Add import for path DSL function
    self.imports.add("androidx.compose.ui.graphics.vector.path")

    # Only generate parameter block if any non-default values are present
    # This keeps generated code clean by omitting default values
    has_parameters = (
      path.fill is not None
      or path.stroke is not None
      or path.fill_alpha != 1.0
      or path.stroke_alpha != 1.0
      or path.stroke_line_width != 0.0
      or path.stroke_line_cap != "butt"
      or path.stroke_line_join != "miter"
      or path.stroke_line_miter != 4.0
      or path.path_fill_type != "nonZero"
    )

    if has_parameters:
      lines.append(f"{indent}path(")

      if path.fill is not None:
        fill_code = self._generate_fill_code(path.fill, indent_level=2)
        lines.append(f"{indent}  fill = {fill_code},")

      if path.stroke is not None:
        stroke_code = self._generate_fill_code(path.stroke, indent_level=2)
        lines.append(f"{indent}  stroke = {stroke_code},")

      if path.fill_alpha != 1.0:
        lines.append(f"{indent}  fillAlpha = {format_float(path.fill_alpha)},")

      if path.stroke_alpha != 1.0:
        lines.append(f"{indent}  strokeAlpha = {format_float(path.stroke_alpha)},")

      if path.stroke_line_width != 0.0:
        lines.append(f"{indent}  strokeLineWidth = {format_float(path.stroke_line_width)},")

      if path.stroke_line_cap != "butt":
        cap_value = self._get_stroke_cap_value(path.stroke_line_cap)
        lines.append(f"{indent}  strokeLineCap = {cap_value},")

      if path.stroke_line_join != "miter":
        join_value = self._get_stroke_join_value(path.stroke_line_join)
        lines.append(f"{indent}  strokeLineJoin = {join_value},")

      if path.stroke_line_miter != 4.0:
        lines.append(f"{indent}  strokeLineMiter = {format_float(path.stroke_line_miter)},")

      if path.path_fill_type.lower() != "nonzero":
        fill_type_value = self._get_path_fill_type_value(path.path_fill_type)
        lines.append(f"{indent}  pathFillType = {fill_type_value},")

      lines.append(f"{indent}) {{")
    else:
      lines.append(f"{indent}path {{")

    path_data_lines = path_data_to_dsl(path.paths)
    if path_data_lines:
      for line in path_data_lines.split("\n"):
        lines.append(f"{indent}{line}")

    lines.append(f"{indent}}}")

    return lines

  def _generate_group(self, group: IrVectorGroup) -> list[str]:
    """Generate group { } block."""
    lines = []
    indent = "  " * self.indent_level

    # Add import for group DSL function
    self.imports.add("androidx.compose.ui.graphics.vector.group")

    # Check if any parameters differ from defaults (including name)
    # Compose group() without parameters is cleaner when no parameters are needed
    has_name = group.name and group.name.strip()
    has_transform = (
      group.rotation != 0.0
      or group.pivot_x != 0.0
      or group.pivot_y != 0.0
      or group.scale_x != 1.0
      or group.scale_y != 1.0
      or group.translation_x != 0.0
      or group.translation_y != 0.0
    )
    has_clip_path = bool(group.clip_path_data)

    if has_name or has_transform or has_clip_path:
      lines.append(f"{indent}group(")

      # Name parameter comes first (if present)
      if has_name:
        lines.append(f'{indent}  name = "{group.name}",')

      if group.rotation != 0.0:
        lines.append(f"{indent}  rotate = {format_float(group.rotation)},")

      if group.pivot_x != 0.0:
        lines.append(f"{indent}  pivotX = {format_float(group.pivot_x)},")

      if group.pivot_y != 0.0:
        lines.append(f"{indent}  pivotY = {format_float(group.pivot_y)},")

      if group.scale_x != 1.0:
        lines.append(f"{indent}  scaleX = {format_float(group.scale_x)},")

      if group.scale_y != 1.0:
        lines.append(f"{indent}  scaleY = {format_float(group.scale_y)},")

      if group.translation_x != 0.0:
        lines.append(f"{indent}  translationX = {format_float(group.translation_x)},")

      if group.translation_y != 0.0:
        lines.append(f"{indent}  translationY = {format_float(group.translation_y)},")

      if has_clip_path:
        self.imports.add("androidx.compose.ui.graphics.vector.PathNode")
        clip_path_code = self._generate_clip_path_data(
          group.clip_path_data, indent_level=self.indent_level + 1
        )
        lines.append(f"{indent}  clipPathData = {clip_path_code},")

      lines.append(f"{indent}) {{")
    else:
      lines.append(f"{indent}group {{")

    self.indent_level += 1
    for child in group.children:
      child_lines = self._generate_node(child)
      lines.extend(child_lines)
    self.indent_level -= 1

    lines.append(f"{indent}}}")

    return lines

  def _get_stroke_cap_value(self, cap: str) -> str:
    """Convert stroke cap to Compose enum value."""
    cap_map = {"butt": "StrokeCap.Butt", "round": "StrokeCap.Round", "square": "StrokeCap.Square"}

    if cap in cap_map:
      self.imports.add("androidx.compose.ui.graphics.StrokeCap")
      return cap_map[cap]
    # Fallback to default if unknown cap type
    return "StrokeCap.Butt"

  def _get_stroke_join_value(self, join: str) -> str:
    """Convert stroke join to Compose enum value."""
    join_map = {
      "miter": "StrokeJoin.Miter",
      "round": "StrokeJoin.Round",
      "bevel": "StrokeJoin.Bevel",
    }

    if join in join_map:
      self.imports.add("androidx.compose.ui.graphics.StrokeJoin")
      return join_map[join]
    return "StrokeJoin.Miter"

  def _get_path_fill_type_value(self, fill_type: str) -> str:
    """Convert path fill type to Compose enum value."""
    # Use case-insensitive comparison
    fill_type_lower = fill_type.lower()

    if fill_type_lower == "evenodd":
      self.imports.add("androidx.compose.ui.graphics.PathFillType")
      return "PathFillType.EvenOdd"
    else:  # Default to NonZero for any other value
      self.imports.add("androidx.compose.ui.graphics.PathFillType")
      return "PathFillType.NonZero"

  def get_required_imports(self) -> list[str]:
    """Get list of required imports for generated code."""
    return sorted(list(self.imports))

  def _generate_fill_code(self, fill: IrFill, indent_level: int = 2) -> str:
    """Generate Compose code for fill (color or gradient)."""
    if isinstance(fill, IrColorFill):
      self.imports.add("androidx.compose.ui.graphics.Color")
      self.imports.add("androidx.compose.ui.graphics.SolidColor")
      return self._generate_solid_color_code(fill.color)
    elif isinstance(fill, IrLinearGradient | IrRadialGradient):
      self.imports.add("androidx.compose.ui.graphics.Brush")
      self.imports.add("androidx.compose.ui.geometry.Offset")
      # Calculate proper indentation for gradient parameters
      gradient_indent = "  " * (indent_level + 1)
      return fill.to_compose_code(indent=gradient_indent)
    else:
      # Fallback to black solid color
      self.imports.add("androidx.compose.ui.graphics.Color")
      self.imports.add("androidx.compose.ui.graphics.SolidColor")
      return "SolidColor(Color.Black)"

  def _generate_solid_color_code(self, color) -> str:
    """Generate SolidColor code for color, preferring named constants."""
    self.imports.add("androidx.compose.ui.graphics.Color")

    # Try to use named color constants first
    named_color = color.to_compose_color_name()
    if named_color and color.alpha == 255:
      # Use named color for full opacity: SolidColor(Color.White), etc.
      return f"SolidColor(Color.{named_color})"
    elif named_color and color.alpha < 255:
      # Use named color with alpha: SolidColor(Color.White.copy(alpha = 0.5f))
      from ..utils.formatting import format_alpha

      alpha_value = color.alpha / 255.0
      return f"SolidColor(Color.{named_color}.copy(alpha = {format_alpha(alpha_value)}))"
    else:
      # Fallback to hex notation: SolidColor(Color(0xFFFFFFFF))
      return f"SolidColor({color.to_compose_color()})"

  def _generate_clip_path_data(self, clip_path_nodes, indent_level: int = 1) -> str:
    """Generate clipPathData list of PathNode elements."""
    if not clip_path_nodes:
      return "emptyList()"

    # For short clip paths, use single line format
    if len(clip_path_nodes) <= 3:
      path_dsl = path_data_to_dsl(clip_path_nodes)
      # Convert DSL to PathNode list format
      return self._convert_dsl_to_path_node_list(path_dsl)

    # For longer clip paths, use multiline format
    indent = "  " * indent_level
    lines = ["listOf("]

    path_dsl = path_data_to_dsl(clip_path_nodes)
    dsl_lines = path_dsl.split("\n")

    for i, line in enumerate(dsl_lines):
      line = line.strip()
      if line:
        # Convert DSL commands to PathNode calls
        path_node_call = self._convert_dsl_line_to_path_node(line)
        if i < len(dsl_lines) - 1:
          lines.append(f"{indent}  {path_node_call},")
        else:
          lines.append(f"{indent}  {path_node_call}")

    lines.append(f"{indent})")
    return "\n".join(lines)

  def _convert_dsl_to_path_node_list(self, dsl: str) -> str:
    """Convert path DSL to single-line PathNode list."""
    dsl_lines = [line.strip() for line in dsl.split("\n") if line.strip()]
    path_nodes = []

    for line in dsl_lines:
      path_node = self._convert_dsl_line_to_path_node(line)
      path_nodes.append(path_node)

    return f"listOf({', '.join(path_nodes)})"

  def _convert_dsl_line_to_path_node(self, dsl_line: str) -> str:
    """Convert a single DSL line to PathNode call."""
    dsl_line = dsl_line.strip()

    # Handle different DSL commands
    if dsl_line.startswith("moveTo("):
      return dsl_line.replace("moveTo(", "PathNode.MoveTo(")
    elif dsl_line.startswith("lineTo("):
      return dsl_line.replace("lineTo(", "PathNode.LineTo(")
    elif dsl_line.startswith("curveTo("):
      return dsl_line.replace("curveTo(", "PathNode.CurveTo(")
    elif dsl_line.startswith("quadTo("):
      return dsl_line.replace("quadTo(", "PathNode.QuadTo(")
    elif dsl_line.startswith("arcTo("):
      return dsl_line.replace("arcTo(", "PathNode.ArcTo(")
    elif dsl_line.startswith("close()"):
      return "PathNode.Close"
    else:
      # Fallback - assume it's already in PathNode format
      return dsl_line
