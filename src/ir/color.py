from dataclasses import dataclass
from typing import Union
import re


@dataclass(frozen=True)
class IrColor:
  """Immutable color representation using ARGB format."""

  argb: int

  @classmethod
  def from_hex(cls, hex_string: str) -> "IrColor":
    """Parse color from hex string (#RGB, #RRGGBB, #RRGGBBAA)."""
    hex_string = hex_string.strip().lstrip("#")

    if len(hex_string) == 3:
      # Expand short form: #RGB -> #RRGGBB (each digit doubled)
      r, g, b = hex_string
      hex_string = f"{r}{r}{g}{g}{b}{b}"
    elif len(hex_string) == 4:
      # Expand short form with alpha: #ARGB -> #AARRGGBB
      r, g, b, a = hex_string
      hex_string = f"{a}{a}{r}{r}{g}{g}{b}{b}"
    elif len(hex_string) == 6:
      # Add full opacity for RGB format: #RRGGBB -> #FFRRGGBB
      hex_string = f"ff{hex_string}"
    elif len(hex_string) == 8:
      # Convert #RRGGBBAA to ARGB format by moving alpha to front
      hex_string = f"{hex_string[6:8]}{hex_string[0:6]}"
    else:
      raise ValueError(f"Invalid hex color format: #{hex_string}")

    argb = int(hex_string, 16)
    return cls(argb)

  @classmethod
  def from_rgb(cls, red: int, green: int, blue: int, alpha: int = 255) -> "IrColor":
    """Create color from RGB(A) components (0-255)."""
    if not all(0 <= c <= 255 for c in [red, green, blue, alpha]):
      raise ValueError("Color components must be in range 0-255")

    # Pack components into ARGB format using bit shifting
    argb = (alpha << 24) | (red << 16) | (green << 8) | blue
    return cls(argb)

  @classmethod
  def from_argb(cls, argb: int) -> "IrColor":
    """Create color from ARGB integer."""
    if not 0 <= argb <= 0xFFFFFFFF:
      raise ValueError("ARGB value must be in range 0x00000000-0xFFFFFFFF")
    return cls(argb)

  @property
  def alpha(self) -> int:
    """Extract alpha component (0-255)."""
    return (self.argb >> 24) & 0xFF

  @property
  def red(self) -> int:
    """Extract red component (0-255)."""
    return (self.argb >> 16) & 0xFF

  @property
  def green(self) -> int:
    """Extract green component (0-255)."""
    return (self.argb >> 8) & 0xFF

  @property
  def blue(self) -> int:
    """Extract blue component (0-255)."""
    return self.argb & 0xFF

  def to_compose_color(self) -> str:
    """Generate Compose Color constructor call."""
    # Always use hex notation with ARGB format: Color(0xAARRGGBB)
    # This is the standard Compose format and handles both opaque and transparent colors
    return f"Color(0x{self.argb:08X})"

  def to_compose_solid_color(self, use_named_colors: bool = True) -> str:
    """Generate Compose SolidColor constructor call for use as Brush."""
    from ..utils.formatting import format_alpha
    
    # For use as fill/stroke in path()
    if use_named_colors:
      named = self.to_compose_color_name()
      if named and self.alpha == 255:
        # Use named color for full opacity colors like Color.Red
        return f"SolidColor(Color.{named})"
      elif named and self.alpha < 255:
        # Use named color with alpha like Color.Red.copy(alpha = 0.5f)
        alpha_value = self.alpha / 255.0
        return f"SolidColor(Color.{named}.copy(alpha = {format_alpha(alpha_value)}))"
    
    # Fallback to hex notation
    return f"SolidColor({self.to_compose_color()})"

  def to_compose_color_name(self) -> str | None:
    """Get Compose built-in color name if this color matches one."""
    # Check for exact matches with Compose built-in colors
    for name, color in COMPOSE_BUILTIN_COLORS.items():
      if self.argb == color.argb:
        return name.capitalize()
    
    # Check for RGB matches (ignoring alpha) for transparent versions
    for name, color in COMPOSE_BUILTIN_COLORS.items():
      if (self.red, self.green, self.blue) == (color.red, color.green, color.blue):
        return name.capitalize()
    
    return None

  def is_transparent(self) -> bool:
    """Check if this color is fully transparent."""
    return self.alpha == 0

  def __str__(self) -> str:
    return self.to_compose_color()


# Cached SVG color keywords (populated lazily)
_svg_color_cache: dict[str, IrColor] = {}

# Compose built-in colors that can be used as Color.Name
# Only these colors are available as named constants in Compose
COMPOSE_BUILTIN_COLORS = {
  "black": IrColor.from_rgb(0, 0, 0),
  "darkgray": IrColor.from_rgb(68, 68, 68),  
  "gray": IrColor.from_rgb(136, 136, 136),
  "lightgray": IrColor.from_rgb(204, 204, 204),
  "white": IrColor.from_rgb(255, 255, 255),
  "red": IrColor.from_rgb(255, 0, 0),
  "green": IrColor.from_rgb(0, 255, 0),  # Note: Compose Green is #00FF00, not #008000
  "blue": IrColor.from_rgb(0, 0, 255),
  "yellow": IrColor.from_rgb(255, 255, 0),
  "cyan": IrColor.from_rgb(0, 255, 255),
  "magenta": IrColor.from_rgb(255, 0, 255),
  "transparent": IrColor.from_rgb(0, 0, 0, 0),
}


def _get_svg_color(color_name: str) -> IrColor | None:
  """Get SVG color by name with lazy loading and caching."""
  if color_name not in _svg_color_cache:
    from .svg_colors import SVG_COLOR_HEX_MAP
    
    if color_name in SVG_COLOR_HEX_MAP:
      hex_value = SVG_COLOR_HEX_MAP[color_name]
      if hex_value.startswith("#") and len(hex_value) == 9:
        # Handle transparent colors with alpha
        _svg_color_cache[color_name] = IrColor.from_hex(hex_value)
      else:
        # Regular hex colors
        _svg_color_cache[color_name] = IrColor.from_hex(hex_value)
    else:
      return None
  
  return _svg_color_cache.get(color_name)


def parse_color(color_string: str) -> Union[IrColor, None]:
  """Parse color from various string formats."""
  color_string = color_string.strip().lower()

  # SVG "none" means no fill/stroke should be applied
  if color_string == "none":
    return None

  # Check for SVG color keywords with lazy loading
  svg_color = _get_svg_color(color_string)
  if svg_color is not None:
    return svg_color

  if color_string.startswith("#"):
    return IrColor.from_hex(color_string)

  rgb_match = re.match(r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", color_string)
  if rgb_match:
    r, g, b = map(int, rgb_match.groups())
    return IrColor.from_rgb(r, g, b)

  rgba_match = re.match(r"rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([\d.]+)\s*\)", color_string)
  if rgba_match:
    r, g, b = map(int, rgba_match.groups()[:3])
    # Convert float alpha (0.0-1.0) to int (0-255)
    a = int(float(rgba_match.groups()[3]) * 255)
    return IrColor.from_rgb(r, g, b, a)

  hsl_match = re.match(r"hsl\(\s*([\d.]+)\s*,\s*([\d.]+)%\s*,\s*([\d.]+)%\s*\)", color_string)
  if hsl_match:
    hue, saturation, lightness = map(float, hsl_match.groups())
    r, g, b = _hsl_to_rgb(hue / 360.0, saturation / 100.0, lightness / 100.0)
    return IrColor.from_rgb(r, g, b)

  hsla_match = re.match(
    r"hsla\(\s*([\d.]+)\s*,\s*([\d.]+)%\s*,\s*([\d.]+)%\s*,\s*([\d.]+)\s*\)", color_string
  )
  if hsla_match:
    hue, saturation, lightness, alpha_val = map(float, hsla_match.groups())
    r, g, b = _hsl_to_rgb(hue / 360.0, saturation / 100.0, lightness / 100.0)
    alpha = int(alpha_val * 255)
    return IrColor.from_rgb(r, g, b, alpha)

  raise ValueError(f"Unsupported color format: {color_string}")


def _hsl_to_rgb(hue: float, saturation: float, lightness: float) -> tuple[int, int, int]:
  """Convert HSL to RGB color values."""

  def _hue_to_rgb(p: float, q: float, t: float) -> float:
    if t < 0:
      t += 1
    if t > 1:
      t -= 1
    if t < 1 / 6:
      return p + (q - p) * 6 * t
    if t < 1 / 2:
      return q
    if t < 2 / 3:
      return p + (q - p) * (2 / 3 - t) * 6
    return p

  if saturation == 0:
    # Achromatic (gray)
    r = g = b = lightness
  else:
    q = (
      lightness * (1 + saturation)
      if lightness < 0.5
      else lightness + saturation - lightness * saturation
    )
    p = 2 * lightness - q
    r = _hue_to_rgb(p, q, hue + 1 / 3)
    g = _hue_to_rgb(p, q, hue)
    b = _hue_to_rgb(p, q, hue - 1 / 3)

  return int(r * 255), int(g * 255), int(b * 255)
