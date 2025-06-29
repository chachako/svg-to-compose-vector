from abc import ABC
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Union

from .color import IrColor
from .path_node import IrPathNode

if TYPE_CHECKING:
  from .gradient import IrFill


@dataclass
class IrVectorNode(ABC):
  """Base class for all vector nodes (paths and groups)."""

  name: str | None = field(default=None, kw_only=True)


@dataclass
class IrVectorPath(IrVectorNode):
  """Represents a path element with styling and path data."""

  paths: list[IrPathNode]
  fill: Union[IrColor, "IrFill"] | None = field(default=None, kw_only=True)
  stroke: Union[IrColor, "IrFill"] | None = field(default=None, kw_only=True)
  fill_alpha: float = field(default=1.0, kw_only=True)
  stroke_alpha: float = field(default=1.0, kw_only=True)
  stroke_line_width: float = field(default=0.0, kw_only=True)
  stroke_line_cap: str = field(default="butt", kw_only=True)
  stroke_line_join: str = field(default="miter", kw_only=True)
  stroke_line_miter: float = field(default=4.0, kw_only=True)
  path_fill_type: str = field(default="nonZero", kw_only=True)
  trim_path_start: float = field(default=0.0, kw_only=True)
  trim_path_end: float = field(default=1.0, kw_only=True)
  trim_path_offset: float = field(default=0.0, kw_only=True)

  def __post_init__(self):
    """Post-process the fill and stroke fields to ensure they're IrFill instances."""
    from .gradient import IrColorFill

    if self.fill is not None and isinstance(self.fill, IrColor):
      object.__setattr__(self, "fill", IrColorFill(color=self.fill))

    if self.stroke is not None and isinstance(self.stroke, IrColor):
      object.__setattr__(self, "stroke", IrColorFill(color=self.stroke))


@dataclass
class IrVectorGroup(IrVectorNode):
  """Represents a group element with transformation and child nodes."""

  children: list[IrVectorNode]
  rotation: float = field(default=0.0, kw_only=True)
  pivot_x: float = field(default=0.0, kw_only=True)
  pivot_y: float = field(default=0.0, kw_only=True)
  scale_x: float = field(default=1.0, kw_only=True)
  scale_y: float = field(default=1.0, kw_only=True)
  translation_x: float = field(default=0.0, kw_only=True)
  translation_y: float = field(default=0.0, kw_only=True)
  clip_path_data: list[IrPathNode] = field(default_factory=list, kw_only=True)
