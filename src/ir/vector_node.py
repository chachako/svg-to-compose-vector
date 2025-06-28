from abc import ABC
from dataclasses import dataclass, field
from typing import List, Optional, Union
from .path_node import IrPathNode
from .color import IrColor


@dataclass
class IrVectorNode(ABC):
  """Base class for all vector nodes (paths and groups)."""

  name: Optional[str] = field(default=None, kw_only=True)


@dataclass
class IrVectorPath(IrVectorNode):
  """Represents a path element with styling and path data."""

  paths: List[IrPathNode]
  fill: Optional[Union[IrColor, "IrFill"]] = field(default=None, kw_only=True)
  stroke: Optional[IrColor] = field(default=None, kw_only=True)
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
    """Post-process the fill field to ensure it's an IrFill instance."""
    if self.fill is not None and isinstance(self.fill, IrColor):
      from .gradient import IrColorFill
      object.__setattr__(self, 'fill', IrColorFill(color=self.fill))


@dataclass
class IrVectorGroup(IrVectorNode):
  """Represents a group element with transformation and child nodes."""

  children: List[IrVectorNode]
  rotation: float = field(default=0.0, kw_only=True)
  pivot_x: float = field(default=0.0, kw_only=True)
  pivot_y: float = field(default=0.0, kw_only=True)
  scale_x: float = field(default=1.0, kw_only=True)
  scale_y: float = field(default=1.0, kw_only=True)
  translation_x: float = field(default=0.0, kw_only=True)
  translation_y: float = field(default=0.0, kw_only=True)
  clip_path_data: List[IrPathNode] = field(default_factory=list, kw_only=True)
