import re
from typing import List, Dict, Any
from dataclasses import dataclass
import math


@dataclass
class TransformMatrix:
  """Represents a 2D transformation matrix."""
  
  a: float = 1.0  # Scale X
  b: float = 0.0  # Skew Y
  c: float = 0.0  # Skew X
  d: float = 1.0  # Scale Y
  e: float = 0.0  # Translate X
  f: float = 0.0  # Translate Y


@dataclass
class DecomposedTransform:
  """Decomposed transformation parameters for Compose."""
  
  translation_x: float = 0.0
  translation_y: float = 0.0
  scale_x: float = 1.0
  scale_y: float = 1.0
  rotation: float = 0.0
  pivot_x: float = 0.0
  pivot_y: float = 0.0


class TransformParser:
  """Parses SVG transform attributes and converts to Compose parameters."""

  def __init__(self):
    # Regex for matching transform functions
    self.transform_regex = re.compile(
      r'(translate|scale|rotate|skewX|skewY|matrix)\s*\(\s*([^)]*)\s*\)',
      re.IGNORECASE
    )

  def parse_transform(self, transform_string: str) -> DecomposedTransform:
    """
    Parse SVG transform string and return decomposed transform.
    
    SVG transform functions are applied right-to-left (last function applied first),
    so we process them in reverse order.
    """
    if not transform_string:
      return DecomposedTransform()

    # Parse all transform functions
    functions = []
    for match in self.transform_regex.finditer(transform_string):
      func_name = match.group(1).lower()
      params_str = match.group(2).strip()
      
      # Parse parameters
      params = self._parse_parameters(params_str)
      functions.append((func_name, params))

    if not functions:
      return DecomposedTransform()

    # Build composite matrix by applying transforms in order
    matrix = TransformMatrix()
    for func_name, params in functions:
      func_matrix = self._create_function_matrix(func_name, params)
      matrix = self._multiply_matrices(matrix, func_matrix)

    # Decompose the final matrix into Compose-compatible parameters
    return self._decompose_matrix(matrix)

  def _parse_parameters(self, params_str: str) -> List[float]:
    """Parse parameter string into list of floats."""
    if not params_str:
      return []

    # Split on commas and/or whitespace
    param_parts = re.split(r'[,\s]+', params_str.strip())
    params = []
    
    for part in param_parts:
      part = part.strip()
      if part:
        try:
          params.append(float(part))
        except ValueError:
          continue
    
    return params

  def _create_function_matrix(self, func_name: str, params: List[float]) -> TransformMatrix:
    """Create transformation matrix for a specific function."""
    
    if func_name == "translate":
      tx = params[0] if len(params) > 0 else 0.0
      ty = params[1] if len(params) > 1 else 0.0
      return TransformMatrix(e=tx, f=ty)
    
    elif func_name == "scale":
      sx = params[0] if len(params) > 0 else 1.0
      sy = params[1] if len(params) > 1 else sx
      return TransformMatrix(a=sx, d=sy)
    
    elif func_name == "rotate":
      angle = params[0] if len(params) > 0 else 0.0
      cx = params[1] if len(params) > 1 else 0.0
      cy = params[2] if len(params) > 2 else 0.0
      
      # Convert degrees to radians
      angle_rad = math.radians(angle)
      cos_a = math.cos(angle_rad)
      sin_a = math.sin(angle_rad)
      
      if cx == 0.0 and cy == 0.0:
        # Simple rotation around origin
        return TransformMatrix(a=cos_a, b=sin_a, c=-sin_a, d=cos_a)
      else:
        # Rotation around point (cx, cy): translate(-cx,-cy) * rotate * translate(cx,cy)
        # Combined matrix calculation
        return TransformMatrix(
          a=cos_a,
          b=sin_a,
          c=-sin_a,
          d=cos_a,
          e=cx * (1 - cos_a) + cy * sin_a,
          f=cy * (1 - cos_a) - cx * sin_a
        )
    
    elif func_name == "skewx":
      angle = params[0] if len(params) > 0 else 0.0
      skew_x = math.tan(math.radians(angle))
      return TransformMatrix(c=skew_x)
    
    elif func_name == "skewy":
      angle = params[0] if len(params) > 0 else 0.0
      skew_y = math.tan(math.radians(angle))
      return TransformMatrix(b=skew_y)
    
    elif func_name == "matrix":
      # matrix(a b c d e f)
      if len(params) >= 6:
        return TransformMatrix(
          a=params[0], b=params[1], c=params[2],
          d=params[3], e=params[4], f=params[5]
        )
    
    # Return identity matrix for unrecognized functions
    return TransformMatrix()

  def _multiply_matrices(self, m1: TransformMatrix, m2: TransformMatrix) -> TransformMatrix:
    """Multiply two transformation matrices."""
    return TransformMatrix(
      a=m1.a * m2.a + m1.c * m2.b,
      b=m1.b * m2.a + m1.d * m2.b,
      c=m1.a * m2.c + m1.c * m2.d,
      d=m1.b * m2.c + m1.d * m2.d,
      e=m1.a * m2.e + m1.c * m2.f + m1.e,
      f=m1.b * m2.e + m1.d * m2.f + m1.f
    )

  def _decompose_matrix(self, matrix: TransformMatrix) -> DecomposedTransform:
    """
    Decompose transformation matrix into Compose-compatible parameters.
    
    This is a simplified decomposition that handles common cases.
    For complex transformations involving both rotation and scale,
    the decomposition may not be perfect.
    """
    
    # Extract translation (always straightforward)
    translation_x = matrix.e
    translation_y = matrix.f
    
    # Calculate scale factors
    scale_x = math.sqrt(matrix.a * matrix.a + matrix.b * matrix.b)
    scale_y = math.sqrt(matrix.c * matrix.c + matrix.d * matrix.d)
    
    # Handle negative scales (flips)
    if matrix.a < 0 or (matrix.a == 0 and matrix.b < 0):
      scale_x = -scale_x
    if matrix.d < 0 or (matrix.d == 0 and matrix.c > 0):
      scale_y = -scale_y
    
    # Calculate rotation (in degrees)
    rotation = 0.0
    if scale_x != 0:
      rotation = math.degrees(math.atan2(matrix.b, matrix.a))
    
    # Normalize rotation to [0, 360) and round to avoid floating point precision issues
    rotation = rotation % 360
    
    # Round to 5 decimal places to avoid precision issues like 44.99999999999999
    return DecomposedTransform(
      translation_x=round(translation_x, 5),
      translation_y=round(translation_y, 5),
      scale_x=round(scale_x, 5),
      scale_y=round(scale_y, 5),
      rotation=round(rotation, 5),
      pivot_x=0.0,  # SVG doesn't have explicit pivot, always 0
      pivot_y=0.0
    )

  def parse_transform_to_group_params(self, transform_string: str) -> Dict[str, Any]:
    """
    Parse transform string and return dictionary of group parameters.
    
    This is a convenience method that returns parameters directly
    usable in IrVectorGroup construction.
    """
    decomposed = self.parse_transform(transform_string)
    
    params = {}
    
    if decomposed.translation_x != 0.0:
      params['translation_x'] = decomposed.translation_x
    if decomposed.translation_y != 0.0:
      params['translation_y'] = decomposed.translation_y
    if decomposed.scale_x != 1.0:
      params['scale_x'] = decomposed.scale_x
    if decomposed.scale_y != 1.0:
      params['scale_y'] = decomposed.scale_y
    if decomposed.rotation != 0.0:
      params['rotation'] = decomposed.rotation
    if decomposed.pivot_x != 0.0:
      params['pivot_x'] = decomposed.pivot_x
    if decomposed.pivot_y != 0.0:
      params['pivot_y'] = decomposed.pivot_y
    
    return params