from typing import List, Set
from ..ir.image_vector import IrImageVector
from ..ir.vector_node import IrVectorNode, IrVectorPath, IrVectorGroup
from ..ir.path_node import path_data_to_dsl


class ImageVectorGenerator:
  """Generates Kotlin ImageVector code from IR."""

  def __init__(self):
    self.imports: Set[str] = set()
    self.indent_level = 0

  def generate(self, ir: IrImageVector) -> str:
    """Generate complete ImageVector.Builder(...).build() code."""
    self.imports.clear()
    self.indent_level = 0

    self.imports.add("androidx.compose.ui.graphics.vector.ImageVector")
    self.imports.add("androidx.compose.ui.unit.dp")

    lines = []

    lines.append("ImageVector.Builder(")
    lines.append(f'  name = "{ir.name}",')
    lines.append(f"  defaultWidth = {ir.default_width}.dp,")
    lines.append(f"  defaultHeight = {ir.default_height}.dp,")
    lines.append(f"  viewportWidth = {ir.viewport_width}f,")
    lines.append(f"  viewportHeight = {ir.viewport_height}f,")

    if ir.auto_mirror:
      lines.append("  autoMirror = true,")

    lines.append(").apply {")

    self.indent_level = 1
    for node in ir.nodes:
      node_lines = self._generate_node(node)
      lines.extend(node_lines)

    lines.append("}.build()")

    return "\n".join(lines)

  def _generate_node(self, node: IrVectorNode) -> List[str]:
    """Generate code for a vector node (path or group)."""
    if isinstance(node, IrVectorPath):
      return self._generate_path(node)
    elif isinstance(node, IrVectorGroup):
      return self._generate_group(node)
    else:
      raise ValueError(f"Unknown node type: {type(node)}")

  def _generate_path(self, path: IrVectorPath) -> List[str]:
    """Generate path { } block."""
    lines = []
    indent = "  " * self.indent_level

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
        self.imports.add("androidx.compose.ui.graphics.Color")
        lines.append(f"{indent}  fill = {path.fill.to_compose_color()},")

      if path.stroke is not None:
        self.imports.add("androidx.compose.ui.graphics.Color")
        lines.append(f"{indent}  stroke = {path.stroke.to_compose_color()},")

      if path.fill_alpha != 1.0:
        lines.append(f"{indent}  fillAlpha = {path.fill_alpha}f,")

      if path.stroke_alpha != 1.0:
        lines.append(f"{indent}  strokeAlpha = {path.stroke_alpha}f,")

      if path.stroke_line_width != 0.0:
        lines.append(f"{indent}  strokeLineWidth = {path.stroke_line_width}f,")

      if path.stroke_line_cap != "butt":
        cap_value = self._get_stroke_cap_value(path.stroke_line_cap)
        lines.append(f"{indent}  strokeLineCap = {cap_value},")

      if path.stroke_line_join != "miter":
        join_value = self._get_stroke_join_value(path.stroke_line_join)
        lines.append(f"{indent}  strokeLineJoin = {join_value},")

      if path.stroke_line_miter != 4.0:
        lines.append(f"{indent}  strokeLineMiter = {path.stroke_line_miter}f,")

      if path.path_fill_type != "nonZero":
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

  def _generate_group(self, group: IrVectorGroup) -> List[str]:
    """Generate group { } block."""
    lines = []
    indent = "  " * self.indent_level

    # Check if any transform parameters differ from defaults
    # Compose group() without parameters is cleaner when no transforms are applied
    has_transform = (
      group.rotation != 0.0
      or group.pivot_x != 0.0
      or group.pivot_y != 0.0
      or group.scale_x != 1.0
      or group.scale_y != 1.0
      or group.translation_x != 0.0
      or group.translation_y != 0.0
    )

    if has_transform:
      lines.append(f"{indent}group(")

      if group.rotation != 0.0:
        lines.append(f"{indent}  rotate = {group.rotation}f,")

      if group.pivot_x != 0.0:
        lines.append(f"{indent}  pivotX = {group.pivot_x}f,")

      if group.pivot_y != 0.0:
        lines.append(f"{indent}  pivotY = {group.pivot_y}f,")

      if group.scale_x != 1.0:
        lines.append(f"{indent}  scaleX = {group.scale_x}f,")

      if group.scale_y != 1.0:
        lines.append(f"{indent}  scaleY = {group.scale_y}f,")

      if group.translation_x != 0.0:
        lines.append(f"{indent}  translationX = {group.translation_x}f,")

      if group.translation_y != 0.0:
        lines.append(f"{indent}  translationY = {group.translation_y}f,")

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
    fill_type_map = {"nonZero": "PathFillType.NonZero", "evenOdd": "PathFillType.EvenOdd"}

    if fill_type in fill_type_map:
      self.imports.add("androidx.compose.ui.graphics.PathFillType")
      return fill_type_map[fill_type]
    return "PathFillType.NonZero"

  def get_required_imports(self) -> List[str]:
    """Get list of required imports for generated code."""
    return sorted(list(self.imports))
