"""Utility functions for formatting Kotlin code output."""


def format_float(value: float, precision: int = 5) -> str:
  """Format float for Kotlin code generation.

  Args:
    value: The float value to format
    precision: Maximum decimal places (default 5)

  Returns:
    Formatted string with 'f' suffix, removing unnecessary trailing zeros.
    Whole numbers use compact format (e.g., 24f instead of 24.0f).
  """
  # Round to specified precision to avoid floating point artifacts
  rounded = round(value, precision)

  # Check if it's effectively a whole number
  if rounded == int(rounded):
    return f"{int(rounded)}f"

  # Format with the specified precision, then remove trailing zeros
  formatted = f"{rounded:.{precision}f}"
  # Remove trailing zeros after decimal point
  formatted = formatted.rstrip("0").rstrip(".")

  # Ensure it ends with 'f'
  return f"{formatted}f"


def format_alpha(alpha_value: float) -> str:
  """Format alpha value with 3 decimal places precision."""
  return format_float(alpha_value, precision=3)


def format_dp(value: float) -> str:
  """Format dimension value for dp units with float suffix (e.g., 24f, 2.5f)."""
  # Round to 5 decimal places maximum for dp values
  rounded = round(value, 5)

  # Check if it's effectively a whole number
  if rounded == int(rounded):
    return f"{int(rounded)}f"

  # Format with 5 decimal places max, then remove trailing zeros
  formatted = f"{rounded:.5f}"
  # Remove trailing zeros after decimal point
  formatted = formatted.rstrip("0").rstrip(".")

  # Ensure it ends with 'f'
  return f"{formatted}f"
