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
    hex_string = hex_string.strip().lstrip('#')
    
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
    if self.alpha == 255:
      # Use hex notation for fully opaque colors as it's more compact
      return f"Color(0x{self.argb:08X})"
    else:
      # Use RGBA constructor for transparency to be more explicit
      return f"Color({self.red}, {self.green}, {self.blue}, {self.alpha})"

  def to_hex_string(self) -> str:
    """Convert to hex string format #RRGGBBAA."""
    return f"#{self.red:02X}{self.green:02X}{self.blue:02X}{self.alpha:02X}"

  def __str__(self) -> str:
    return self.to_hex_string()


# Named colors from CSS3 specification
NAMED_COLORS = {
  "black": IrColor.from_rgb(0, 0, 0),
  "white": IrColor.from_rgb(255, 255, 255),
  "red": IrColor.from_rgb(255, 0, 0),
  "green": IrColor.from_rgb(0, 128, 0),
  "blue": IrColor.from_rgb(0, 0, 255),
  "transparent": IrColor.from_rgb(0, 0, 0, 0),
}


def parse_color(color_string: str) -> Union[IrColor, None]:
  """Parse color from various string formats."""
  color_string = color_string.strip().lower()
  
  # SVG "none" means no fill/stroke should be applied
  if color_string == "none" or color_string == "transparent":
    return None
  
  if color_string in NAMED_COLORS:
    return NAMED_COLORS[color_string]
  
  if color_string.startswith('#'):
    return IrColor.from_hex(color_string)
  
  rgb_match = re.match(r'rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', color_string)
  if rgb_match:
    r, g, b = map(int, rgb_match.groups())
    return IrColor.from_rgb(r, g, b)
  
  rgba_match = re.match(r'rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([\d.]+)\s*\)', color_string)
  if rgba_match:
    r, g, b = map(int, rgba_match.groups()[:3])
    # Convert float alpha (0.0-1.0) to int (0-255)
    a = int(float(rgba_match.groups()[3]) * 255)
    return IrColor.from_rgb(r, g, b, a)
  
  raise ValueError(f"Unsupported color format: {color_string}")