from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


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
    return f"moveTo({self.x}f, {self.y}f)"


@dataclass(frozen=True)
class IrLineTo(IrPathNode):
  """Absolute line to command (L)."""

  x: float
  y: float

  def to_compose_dsl(self) -> str:
    return f"lineTo({self.x}f, {self.y}f)"


@dataclass(frozen=True)
class IrHorizontalTo(IrPathNode):
  """Absolute horizontal line command (H)."""

  x: float

  def to_compose_dsl(self) -> str:
    return f"horizontalLineTo({self.x}f)"


@dataclass(frozen=True)
class IrVerticalTo(IrPathNode):
  """Absolute vertical line command (V)."""

  y: float

  def to_compose_dsl(self) -> str:
    return f"verticalLineTo({self.y}f)"


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
    return f"curveTo({self.x1}f, {self.y1}f, {self.x2}f, {self.y2}f, {self.x3}f, {self.y3}f)"


@dataclass(frozen=True)
class IrQuadTo(IrPathNode):
  """Absolute quadratic Bezier curve command (Q)."""

  x1: float
  y1: float
  x2: float
  y2: float

  def to_compose_dsl(self) -> str:
    return f"quadTo({self.x1}f, {self.y1}f, {self.x2}f, {self.y2}f)"


@dataclass(frozen=True)
class IrReflectiveCurveTo(IrPathNode):
  """Absolute reflective cubic Bezier curve command (S)."""

  x2: float
  y2: float
  x3: float
  y3: float

  def to_compose_dsl(self) -> str:
    return f"reflectiveCurveTo({self.x2}f, {self.y2}f, {self.x3}f, {self.y3}f)"


@dataclass(frozen=True)
class IrReflectiveQuadTo(IrPathNode):
  """Absolute reflective quadratic Bezier curve command (T)."""

  x: float
  y: float

  def to_compose_dsl(self) -> str:
    return f"reflectiveQuadTo({self.x}f, {self.y}f)"


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
      f"arcTo({self.horizontal_ellipse_radius}f, {self.vertical_ellipse_radius}f, "
      f"{self.theta}f, {str(self.is_more_than_half).lower()}, "
      f"{str(self.is_positive_arc).lower()}, {self.x1}f, {self.y1}f)"
    )


@dataclass(frozen=True)
class IrRelativeMoveTo(IrPathNode):
  """Relative move to command (m)."""

  dx: float
  dy: float

  def to_compose_dsl(self) -> str:
    return f"moveToRelative({self.dx}f, {self.dy}f)"


@dataclass(frozen=True)
class IrRelativeLineTo(IrPathNode):
  """Relative line to command (l)."""

  dx: float
  dy: float

  def to_compose_dsl(self) -> str:
    return f"lineToRelative({self.dx}f, {self.dy}f)"


@dataclass(frozen=True)
class IrRelativeHorizontalTo(IrPathNode):
  """Relative horizontal line command (h)."""

  dx: float

  def to_compose_dsl(self) -> str:
    return f"horizontalLineToRelative({self.dx}f)"


@dataclass(frozen=True)
class IrRelativeVerticalTo(IrPathNode):
  """Relative vertical line command (v)."""

  dy: float

  def to_compose_dsl(self) -> str:
    return f"verticalLineToRelative({self.dy}f)"


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
      f"curveToRelative({self.dx1}f, {self.dy1}f, {self.dx2}f, {self.dy2}f, "
      f"{self.dx3}f, {self.dy3}f)"
    )


@dataclass(frozen=True)
class IrRelativeQuadTo(IrPathNode):
  """Relative quadratic Bezier curve command (q)."""

  dx1: float
  dy1: float
  dx2: float
  dy2: float

  def to_compose_dsl(self) -> str:
    return f"quadToRelative({self.dx1}f, {self.dy1}f, {self.dx2}f, {self.dy2}f)"


@dataclass(frozen=True)
class IrRelativeReflectiveCurveTo(IrPathNode):
  """Relative reflective cubic Bezier curve command (s)."""

  dx2: float
  dy2: float
  dx3: float
  dy3: float

  def to_compose_dsl(self) -> str:
    return f"reflectiveCurveToRelative({self.dx2}f, {self.dy2}f, {self.dx3}f, {self.dy3}f)"


@dataclass(frozen=True)
class IrRelativeReflectiveQuadTo(IrPathNode):
  """Relative reflective quadratic Bezier curve command (t)."""

  dx: float
  dy: float

  def to_compose_dsl(self) -> str:
    return f"reflectiveQuadToRelative({self.dx}f, {self.dy}f)"


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
      f"arcToRelative({self.horizontal_ellipse_radius}f, {self.vertical_ellipse_radius}f, "
      f"{self.theta}f, {str(self.is_more_than_half).lower()}, "
      f"{str(self.is_positive_arc).lower()}, {self.dx1}f, {self.dy1}f)"
    )


def path_data_to_dsl(path_nodes: List[IrPathNode]) -> str:
  """Convert list of path nodes to Compose pathData DSL calls."""
  if not path_nodes:
    return ""

  lines = [node.to_compose_dsl() for node in path_nodes]
  return "\n".join(f"  {line}" for line in lines)
