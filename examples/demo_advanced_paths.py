#!/usr/bin/env python3

import sys
from pathlib import Path

# Add src to path and import modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.generator.image_vector_generator import ImageVectorGenerator
from src.parser.svg_parser import SvgParser


def demo_advanced_paths():
  """Demonstrate the new advanced path command support."""

  print("🎉 SVG to Compose Vector - Advanced Path Commands Demo")
  print("=" * 60)

  # SVG with advanced path commands
  svg_content = """
  <svg width="200" height="200" viewBox="0 0 200 200">
    <path d="M 50 50
             Q 100 25 150 50
             T 150 100
             S 125 150 100 150
             A 25 25 0 0 1 50 125
             Z"
          fill="#4285F4"/>
  </svg>
  """

  print("Input SVG:")
  print(svg_content.strip())
  print("\n" + "=" * 60)

  parser = SvgParser()
  ir = parser.parse_svg(svg_content)

  print("📊 Parsed IR Structure:")
  print(f"   • Vector: {ir.name}")
  print(f"   • Dimensions: {ir.default_width}x{ir.default_height} dp")
  print(f"   • Viewport: {ir.viewport_width}x{ir.viewport_height}")
  print(f"   • Paths: {len(ir.nodes)}")

  if ir.nodes:
    path = ir.nodes[0]
    print(f"   • Path commands: {len(path.paths)}")
    for i, cmd in enumerate(path.paths):
      print(f"     {i + 1}. {type(cmd).__name__}")

  print("\n" + "=" * 60)

  generator = ImageVectorGenerator()
  kotlin_code = generator.generate(ir)

  print("🚀 Generated Kotlin Code:")
  print(kotlin_code)

  print("\n" + "=" * 60)
  print("✅ Advanced Features Demonstrated:")
  print("   • Q/q commands → quadTo() / quadToRelative()")
  print("   • T/t commands → reflectiveQuadTo() / reflectiveQuadToRelative()")
  print("   • S/s commands → reflectiveCurveTo() / reflectiveCurveToRelative()")
  print("   • A/a commands → arcTo() / arcToRelative()")
  print("   • Color parsing (#4285F4 → Color(0xFF4285F4))")
  print("   • Complete SVG document parsing")
  print("   • Clean Kotlin code generation")


if __name__ == "__main__":
  demo_advanced_paths()
