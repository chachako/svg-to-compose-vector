from abc import ABC, abstractmethod
from dataclasses import dataclass

from .color import IrColor


@dataclass(frozen=True, kw_only=True)
class IrColorStop:
  offset: float
  color: IrColor
  opacity: float = 1.0


@dataclass(frozen=True, kw_only=True)
class IrFill(ABC):
  @abstractmethod
  def to_compose_code(self) -> str:
    pass


@dataclass(frozen=True, kw_only=True)
class IrColorFill(IrFill):
  color: IrColor

  def to_compose_code(self) -> str:
    return self.color.to_compose_color()

  # Backward compatibility properties
  @property
  def argb(self) -> int:
    """Backward compatibility: access the underlying color's ARGB value."""
    return self.color.argb

  def to_compose_color(self) -> str:
    """Backward compatibility: direct color generation."""
    return self.color.to_compose_color()

  def to_compose_color_name(self):
    """Backward compatibility: color name generation."""
    return (
      self.color.to_compose_color_name() if hasattr(self.color, "to_compose_color_name") else None
    )


@dataclass(frozen=True, kw_only=True)
class IrLinearGradient(IrFill):
  start_x: float
  start_y: float
  end_x: float
  end_y: float
  color_stops: list[IrColorStop]
  gradient_units: str = "objectBoundingBox"

  def to_compose_code(self, indent: str = "      ") -> str:
    from ..utils.formatting import format_float

    stops_code = []
    for stop in self.color_stops:
      stop_code = f"{format_float(stop.offset)} to {stop.color.to_compose_color()}"
      stops_code.append(stop_code)

    # Format colorStops array with proper indentation
    if len(stops_code) <= 2:
      # For 1-2 stops, keep on one line
      stops_str = ", ".join(stops_code)
      stops_array = f"arrayOf({stops_str})"
    else:
      # For 3+ stops, use multi-line format
      stops_lines = [f"{indent}  {stop}" for stop in stops_code]
      stops_str = ",\n".join(stops_lines)
      stops_array = f"arrayOf(\n{stops_str}\n{indent})"

    return (
      f"Brush.linearGradient(\n"
      f"{indent}colorStops = {stops_array},\n"
      f"{indent}start = Offset({format_float(self.start_x)}, {format_float(self.start_y)}),\n"
      f"{indent}end = Offset({format_float(self.end_x)}, {format_float(self.end_y)})\n"
      f"{indent[:-2]})"
    )


@dataclass(frozen=True, kw_only=True)
class IrRadialGradient(IrFill):
  center_x: float
  center_y: float
  radius: float
  focal_x: float | None = None
  focal_y: float | None = None
  color_stops: list[IrColorStop]
  gradient_units: str = "objectBoundingBox"

  def to_compose_code(self, indent: str = "      ") -> str:
    from ..utils.formatting import format_float

    stops_code = []
    for stop in self.color_stops:
      stop_code = f"{format_float(stop.offset)} to {stop.color.to_compose_color()}"
      stops_code.append(stop_code)

    # Format colorStops array with proper indentation
    if len(stops_code) <= 2:
      # For 1-2 stops, keep on one line
      stops_str = ", ".join(stops_code)
      stops_array = f"arrayOf({stops_str})"
    else:
      # For 3+ stops, use multi-line format
      stops_lines = [f"{indent}  {stop}" for stop in stops_code]
      stops_str = ",\n".join(stops_lines)
      stops_array = f"arrayOf(\n{stops_str}\n{indent})"

    return (
      f"Brush.radialGradient(\n"
      f"{indent}colorStops = {stops_array},\n"
      f"{indent}center = Offset({format_float(self.center_x)}, {format_float(self.center_y)}),\n"
      f"{indent}radius = {format_float(self.radius)}\n"
      f"{indent[:-2]})"
    )
