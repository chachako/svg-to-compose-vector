from dataclasses import dataclass

from .color import IrColor
from .vector_node import IrVectorNode


@dataclass
class IrImageVector:
  """Root container for ImageVector data."""

  name: str
  default_width: float
  default_height: float
  viewport_width: float
  viewport_height: float
  nodes: list[IrVectorNode]
  auto_mirror: bool = False
  tint_color: IrColor | None = None

  def __post_init__(self):
    if self.viewport_width <= 0 or self.viewport_height <= 0:
      raise ValueError("Viewport dimensions must be positive")
    if self.default_width <= 0 or self.default_height <= 0:
      raise ValueError("Default dimensions must be positive")
