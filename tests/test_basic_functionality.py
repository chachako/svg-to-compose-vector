"""Basic functionality tests for SVG to Compose converter."""

from src.generator.image_vector_generator import ImageVectorGenerator
from src.ir.color import IrColor
from src.ir.image_vector import IrImageVector
from src.ir.path_node import IrClose, IrLineTo, IrMoveTo
from src.ir.vector_node import IrVectorPath
from src.parser.path_parser import PathParser


def test_ir_color_parsing():
  """Test IrColor hex parsing and Compose color generation."""
  red_color = IrColor.from_hex("#FF0000")
  assert red_color.red == 255
  assert red_color.green == 0
  assert red_color.blue == 0
  assert red_color.alpha == 255
  assert red_color.to_compose_color() == "Color.Red"


def test_path_parser_basic_commands():
  """Test PathParser with basic SVG commands."""
  parser = PathParser()
  path_data = parser.parse_path_data("M 0 0 L 24 0 L 24 24 L 0 24 Z")

  assert len(path_data) == 5
  assert isinstance(path_data[0], IrMoveTo)
  assert isinstance(path_data[1], IrLineTo)
  assert isinstance(path_data[4], IrClose)

  assert path_data[0].x == 0.0 and path_data[0].y == 0.0
  assert path_data[1].x == 24.0 and path_data[1].y == 0.0


def test_image_vector_generator():
  """Test ImageVectorGenerator with complete workflow."""
  # Parse path data
  parser = PathParser()
  path_data = parser.parse_path_data("M 0 0 L 24 0 L 24 24 L 0 24 Z")

  # Create IR structures
  red_color = IrColor.from_hex("#FF0000")
  path = IrVectorPath(paths=path_data, fill=red_color)

  image_vector = IrImageVector(
    name="TestIcon",
    default_width=24.0,
    default_height=24.0,
    viewport_width=24.0,
    viewport_height=24.0,
    nodes=[path],
  )

  # Generate Kotlin code
  generator = ImageVectorGenerator()
  kotlin_code = generator.generate(image_vector)

  # Verify output contains expected elements
  assert "ImageVector.Builder(" in kotlin_code
  assert 'name = "TestIcon"' in kotlin_code
  assert "defaultWidth = 24f.dp" in kotlin_code
  assert "viewportWidth = 24f" in kotlin_code
  assert "path(" in kotlin_code
  assert "fill = SolidColor(Color.Red)" in kotlin_code
  assert "moveTo(0f, 0f)" in kotlin_code
  assert "close()" in kotlin_code
  assert ".build()" in kotlin_code

  # Verify imports
  imports = generator.get_required_imports()
  assert "androidx.compose.ui.graphics.vector.ImageVector" in imports
  assert "androidx.compose.ui.graphics.Color" in imports
  assert "androidx.compose.ui.unit.dp" in imports


def test_end_to_end_integration():
  """Integration test demonstrating the complete pipeline."""
  # This test demonstrates the complete workflow
  parser = PathParser()
  path_data = parser.parse_path_data("M 0 0 L 24 0 L 24 24 L 0 24 Z")

  red_color = IrColor.from_hex("#FF0000")
  path = IrVectorPath(paths=path_data, fill=red_color)

  image_vector = IrImageVector(
    name="SquareIcon",
    default_width=24.0,
    default_height=24.0,
    viewport_width=24.0,
    viewport_height=24.0,
    nodes=[path],
  )

  generator = ImageVectorGenerator()
  kotlin_code = generator.generate(image_vector)

  # The generated code should be valid Kotlin that compiles
  assert kotlin_code.count("ImageVector.Builder(") == 1
  assert kotlin_code.count(".build()") == 1
  assert kotlin_code.count("path(") == 1

  print("\n=== Integration Test Output ===")
  print("Generated Kotlin code:")
  print(kotlin_code)
  print("\nRequired imports:")
  for import_line in generator.get_required_imports():
    print(f"import {import_line}")


if __name__ == "__main__":
  # Run tests individually for debugging
  test_ir_color_parsing()
  test_path_parser_basic_commands()
  test_image_vector_generator()
  test_end_to_end_integration()
  print("All tests passed!")
