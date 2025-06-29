import re

from ..ir.path_node import (
  IrArcTo,
  IrClose,
  IrCurveTo,
  IrHorizontalTo,
  IrLineTo,
  IrMoveTo,
  IrPathNode,
  IrQuadTo,
  IrReflectiveCurveTo,
  IrReflectiveQuadTo,
  IrRelativeArcTo,
  IrRelativeCurveTo,
  IrRelativeHorizontalTo,
  IrRelativeLineTo,
  IrRelativeMoveTo,
  IrRelativeQuadTo,
  IrRelativeReflectiveCurveTo,
  IrRelativeReflectiveQuadTo,
  IrRelativeVerticalTo,
  IrVerticalTo,
)


class PathParser:
  """Parser for SVG path data strings."""

  def __init__(self):
    self.position = 0
    self.path_string = ""

  def parse_path_data(self, path_string: str) -> list[IrPathNode]:
    """Parse SVG path data string into IrPathNode list."""
    self.path_string = path_string.strip()
    self.position = 0

    nodes = []

    while self.position < len(self.path_string):
      self._skip_whitespace()
      if self.position >= len(self.path_string):
        break

      command = self._read_command()
      if not command:
        break

      command_nodes = self._parse_command(command)
      nodes.extend(command_nodes)

    return nodes

  def _skip_whitespace(self):
    """Skip whitespace and commas."""
    while self.position < len(self.path_string) and self.path_string[self.position] in " \t\n\r,":
      self.position += 1

  def _read_command(self) -> str:
    """Read the next command character."""
    self._skip_whitespace()
    if self.position >= len(self.path_string):
      return ""

    char = self.path_string[self.position]
    if char in "MmLlHhVvCcSsQqTtAaZz":
      self.position += 1
      return char
    return ""

  def _read_number(self) -> float:
    """Read a floating point number."""
    self._skip_whitespace()

    number_pattern = r"[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?"
    match = re.match(number_pattern, self.path_string[self.position :])

    if not match:
      raise ValueError(f"Expected number at position {self.position}")

    number_str = match.group(0)
    self.position += len(number_str)
    return float(number_str)

  def _read_coordinate_pair(self) -> tuple[float, float]:
    """Read x,y coordinate pair."""
    x = self._read_number()
    y = self._read_number()
    return (x, y)

  def _parse_command(self, command: str) -> list[IrPathNode]:
    """Parse specific command with its parameters."""
    nodes = []

    if command in "Zz":
      nodes.append(IrClose())

    elif command == "M":
      x, y = self._read_coordinate_pair()
      nodes.append(IrMoveTo(x, y))
      # SVG spec: additional coordinate pairs after MoveTo are treated as LineTo
      while self._has_more_coordinates():
        x, y = self._read_coordinate_pair()
        nodes.append(IrLineTo(x, y))

    elif command == "m":
      dx, dy = self._read_coordinate_pair()
      nodes.append(IrRelativeMoveTo(dx, dy))
      # SVG spec: additional coordinate pairs after relative MoveTo are treated as relative LineTo
      while self._has_more_coordinates():
        dx, dy = self._read_coordinate_pair()
        nodes.append(IrRelativeLineTo(dx, dy))

    elif command == "L":
      while self._has_more_coordinates():
        x, y = self._read_coordinate_pair()
        nodes.append(IrLineTo(x, y))

    elif command == "l":
      while self._has_more_coordinates():
        dx, dy = self._read_coordinate_pair()
        nodes.append(IrRelativeLineTo(dx, dy))

    elif command == "H":
      while self._has_more_coordinates():
        x = self._read_number()
        nodes.append(IrHorizontalTo(x))

    elif command == "h":
      while self._has_more_coordinates():
        dx = self._read_number()
        nodes.append(IrRelativeHorizontalTo(dx))

    elif command == "V":
      while self._has_more_coordinates():
        y = self._read_number()
        nodes.append(IrVerticalTo(y))

    elif command == "v":
      while self._has_more_coordinates():
        dy = self._read_number()
        nodes.append(IrRelativeVerticalTo(dy))

    elif command == "C":
      while self._has_more_coordinates():
        x1 = self._read_number()
        y1 = self._read_number()
        x2 = self._read_number()
        y2 = self._read_number()
        x3 = self._read_number()
        y3 = self._read_number()
        nodes.append(IrCurveTo(x1, y1, x2, y2, x3, y3))

    elif command == "c":
      while self._has_more_coordinates():
        dx1 = self._read_number()
        dy1 = self._read_number()
        dx2 = self._read_number()
        dy2 = self._read_number()
        dx3 = self._read_number()
        dy3 = self._read_number()
        nodes.append(IrRelativeCurveTo(dx1, dy1, dx2, dy2, dx3, dy3))

    elif command == "S":
      while self._has_more_coordinates():
        x2 = self._read_number()
        y2 = self._read_number()
        x3 = self._read_number()
        y3 = self._read_number()
        nodes.append(IrReflectiveCurveTo(x2, y2, x3, y3))

    elif command == "s":
      while self._has_more_coordinates():
        dx2 = self._read_number()
        dy2 = self._read_number()
        dx3 = self._read_number()
        dy3 = self._read_number()
        nodes.append(IrRelativeReflectiveCurveTo(dx2, dy2, dx3, dy3))

    elif command == "Q":
      while self._has_more_coordinates():
        x1 = self._read_number()
        y1 = self._read_number()
        x2 = self._read_number()
        y2 = self._read_number()
        nodes.append(IrQuadTo(x1, y1, x2, y2))

    elif command == "q":
      while self._has_more_coordinates():
        dx1 = self._read_number()
        dy1 = self._read_number()
        dx2 = self._read_number()
        dy2 = self._read_number()
        nodes.append(IrRelativeQuadTo(dx1, dy1, dx2, dy2))

    elif command == "T":
      while self._has_more_coordinates():
        x = self._read_number()
        y = self._read_number()
        nodes.append(IrReflectiveQuadTo(x, y))

    elif command == "t":
      while self._has_more_coordinates():
        dx = self._read_number()
        dy = self._read_number()
        nodes.append(IrRelativeReflectiveQuadTo(dx, dy))

    elif command == "A":
      while self._has_more_coordinates():
        rx = self._read_number()
        ry = self._read_number()
        x_axis_rotation = self._read_number()
        large_arc_flag = self._read_number()
        sweep_flag = self._read_number()
        x = self._read_number()
        y = self._read_number()
        nodes.append(IrArcTo(rx, ry, x_axis_rotation, large_arc_flag != 0, sweep_flag != 0, x, y))

    elif command == "a":
      while self._has_more_coordinates():
        rx = self._read_number()
        ry = self._read_number()
        x_axis_rotation = self._read_number()
        large_arc_flag = self._read_number()
        sweep_flag = self._read_number()
        dx = self._read_number()
        dy = self._read_number()
        nodes.append(
          IrRelativeArcTo(rx, ry, x_axis_rotation, large_arc_flag != 0, sweep_flag != 0, dx, dy)
        )

    else:
      raise ValueError(f"Unsupported path command: {command}")

    return nodes

  def _has_more_coordinates(self) -> bool:
    """Check if there are more coordinate values to read."""
    saved_position = self.position
    self._skip_whitespace()

    if self.position >= len(self.path_string):
      return False

    next_char = self.path_string[self.position]
    # Coordinate starts with digit, +, -, or decimal point
    is_coordinate = next_char.isdigit() or next_char in "+-."

    # Restore position to avoid consuming characters during peek
    self.position = saved_position
    return is_coordinate
