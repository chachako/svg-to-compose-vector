from abc import ABC, abstractmethod
from dataclasses import dataclass

from ..utils.formatting import format_float


@dataclass(frozen=True)
class IrPathNode(ABC):
  """Base class for all path commands."""

  @abstractmethod
  def to_compose_dsl(self) -> str:
    """Convert to Compose pathData DSL call."""
    pass


@dataclass(frozen=True)
class IrClose(IrPathNode):
  """Close path command (Z)."""

  def to_compose_dsl(self) -> str:
    return "close()"


@dataclass(frozen=True)
class IrMoveTo(IrPathNode):
  """Absolute move to command (M)."""

  x: float
  y: float

  def to_compose_dsl(self) -> str:
    return f"moveTo({format_float(self.x)}, {format_float(self.y)})"


@dataclass(frozen=True)
class IrLineTo(IrPathNode):
  """Absolute line to command (L)."""

  x: float
  y: float

  def to_compose_dsl(self) -> str:
    return f"lineTo({format_float(self.x)}, {format_float(self.y)})"


@dataclass(frozen=True)
class IrHorizontalTo(IrPathNode):
  """Absolute horizontal line command (H)."""

  x: float

  def to_compose_dsl(self) -> str:
    return f"horizontalLineTo({format_float(self.x)})"


@dataclass(frozen=True)
class IrVerticalTo(IrPathNode):
  """Absolute vertical line command (V)."""

  y: float

  def to_compose_dsl(self) -> str:
    return f"verticalLineTo({format_float(self.y)})"


@dataclass(frozen=True)
class IrCurveTo(IrPathNode):
  """Absolute cubic Bezier curve command (C)."""

  x1: float
  y1: float
  x2: float
  y2: float
  x3: float
  y3: float

  def to_compose_dsl(self) -> str:
    return f"curveTo({format_float(self.x1)}, {format_float(self.y1)}, {format_float(self.x2)}, {format_float(self.y2)}, {format_float(self.x3)}, {format_float(self.y3)})"


@dataclass(frozen=True)
class IrQuadTo(IrPathNode):
  """Absolute quadratic Bezier curve command (Q)."""

  x1: float
  y1: float
  x2: float
  y2: float

  def to_compose_dsl(self) -> str:
    return f"quadTo({format_float(self.x1)}, {format_float(self.y1)}, {format_float(self.x2)}, {format_float(self.y2)})"


@dataclass(frozen=True)
class IrReflectiveCurveTo(IrPathNode):
  """Absolute reflective cubic Bezier curve command (S)."""

  x2: float
  y2: float
  x3: float
  y3: float

  def to_compose_dsl(self) -> str:
    return f"reflectiveCurveTo({format_float(self.x2)}, {format_float(self.y2)}, {format_float(self.x3)}, {format_float(self.y3)})"


@dataclass(frozen=True)
class IrReflectiveQuadTo(IrPathNode):
  """Absolute reflective quadratic Bezier curve command (T)."""

  x: float
  y: float

  def to_compose_dsl(self) -> str:
    return f"reflectiveQuadTo({format_float(self.x)}, {format_float(self.y)})"


@dataclass(frozen=True)
class IrArcTo(IrPathNode):
  """Absolute arc command (A)."""

  horizontal_ellipse_radius: float
  vertical_ellipse_radius: float
  theta: float
  is_more_than_half: bool
  is_positive_arc: bool
  x1: float
  y1: float

  def to_compose_dsl(self) -> str:
    return (
      f"arcTo({format_float(self.horizontal_ellipse_radius)}, {format_float(self.vertical_ellipse_radius)}, "
      f"{format_float(self.theta)}, {str(self.is_more_than_half).lower()}, "
      f"{str(self.is_positive_arc).lower()}, {format_float(self.x1)}, {format_float(self.y1)})"
    )


@dataclass(frozen=True)
class IrRelativeMoveTo(IrPathNode):
  """Relative move to command (m)."""

  dx: float
  dy: float

  def to_compose_dsl(self) -> str:
    return f"moveToRelative({format_float(self.dx)}, {format_float(self.dy)})"


@dataclass(frozen=True)
class IrRelativeLineTo(IrPathNode):
  """Relative line to command (l)."""

  dx: float
  dy: float

  def to_compose_dsl(self) -> str:
    return f"lineToRelative({format_float(self.dx)}, {format_float(self.dy)})"


@dataclass(frozen=True)
class IrRelativeHorizontalTo(IrPathNode):
  """Relative horizontal line command (h)."""

  dx: float

  def to_compose_dsl(self) -> str:
    return f"horizontalLineToRelative({format_float(self.dx)})"


@dataclass(frozen=True)
class IrRelativeVerticalTo(IrPathNode):
  """Relative vertical line command (v)."""

  dy: float

  def to_compose_dsl(self) -> str:
    return f"verticalLineToRelative({format_float(self.dy)})"


@dataclass(frozen=True)
class IrRelativeCurveTo(IrPathNode):
  """Relative cubic Bezier curve command (c)."""

  dx1: float
  dy1: float
  dx2: float
  dy2: float
  dx3: float
  dy3: float

  def to_compose_dsl(self) -> str:
    return (
      f"curveToRelative({format_float(self.dx1)}, {format_float(self.dy1)}, {format_float(self.dx2)}, {format_float(self.dy2)}, "
      f"{format_float(self.dx3)}, {format_float(self.dy3)})"
    )


@dataclass(frozen=True)
class IrRelativeQuadTo(IrPathNode):
  """Relative quadratic Bezier curve command (q)."""

  dx1: float
  dy1: float
  dx2: float
  dy2: float

  def to_compose_dsl(self) -> str:
    return f"quadToRelative({format_float(self.dx1)}, {format_float(self.dy1)}, {format_float(self.dx2)}, {format_float(self.dy2)})"


@dataclass(frozen=True)
class IrRelativeReflectiveCurveTo(IrPathNode):
  """Relative reflective cubic Bezier curve command (s)."""

  dx2: float
  dy2: float
  dx3: float
  dy3: float

  def to_compose_dsl(self) -> str:
    return f"reflectiveCurveToRelative({format_float(self.dx2)}, {format_float(self.dy2)}, {format_float(self.dx3)}, {format_float(self.dy3)})"


@dataclass(frozen=True)
class IrRelativeReflectiveQuadTo(IrPathNode):
  """Relative reflective quadratic Bezier curve command (t)."""

  dx: float
  dy: float

  def to_compose_dsl(self) -> str:
    return f"reflectiveQuadToRelative({format_float(self.dx)}, {format_float(self.dy)})"


@dataclass(frozen=True)
class IrRelativeArcTo(IrPathNode):
  """Relative arc command (a)."""

  horizontal_ellipse_radius: float
  vertical_ellipse_radius: float
  theta: float
  is_more_than_half: bool
  is_positive_arc: bool
  dx1: float
  dy1: float

  def to_compose_dsl(self) -> str:
    return (
      f"arcToRelative({format_float(self.horizontal_ellipse_radius)}, {format_float(self.vertical_ellipse_radius)}, "
      f"{format_float(self.theta)}, {str(self.is_more_than_half).lower()}, "
      f"{str(self.is_positive_arc).lower()}, {format_float(self.dx1)}, {format_float(self.dy1)})"
    )


def path_data_to_dsl(path_nodes: list[IrPathNode]) -> str:
  """Convert list of path nodes to Compose pathData DSL calls."""
  if not path_nodes:
    return ""

  lines = [node.to_compose_dsl() for node in path_nodes]
  return "\n".join(f"  {line}" for line in lines)
