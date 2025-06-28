#!/usr/bin/env python3
"""
Demonstrate complete SVG to Compose ImageVector conversion workflow.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.parser.svg_parser import SvgParser
from src.generator.image_vector_generator import ImageVectorGenerator

def demo_star_icon():
  """Demonstrate star icon conversion."""
  print("=== Star Icon Demo ===")
  
  # Material Design inspired star SVG
  star_svg = '''<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 2 L15.09 8.26 L22 9 L17 14.14 L18.18 21.02 L12 17.77 L5.82 21.02 L7 14.14 L2 9 L8.91 8.26 Z" 
            fill="#FFC107" id="star"/>
  </svg>'''
  
  # Parse SVG
  parser = SvgParser()
  ir = parser.parse_svg(star_svg)
  
  print("Parse result:")
  print(f"  Name: {ir.name}")
  print(f"  Dimensions: {ir.default_width}x{ir.default_height}")
  print(f"  Viewport: {ir.viewport_width}x{ir.viewport_height}")
  print(f"  Node count: {len(ir.nodes)}")
  
  if ir.nodes:
    path = ir.nodes[0]
    print(f"  Path name: {path.name}")
    print(f"  Fill color: {path.fill.to_compose_color()}")
    print(f"  Path commands: {len(path.paths)}")
  
  # Generate Kotlin code
  generator = ImageVectorGenerator()
  kotlin_code = generator.generate(ir)
  
  print("\nGenerated Kotlin code:")
  print("=" * 60)
  print(kotlin_code)
  print("=" * 60)
  
  return kotlin_code

def demo_simple_shapes():
  """Demonstrate simple shape conversion."""
  print("\n=== Simple Shapes Demo ===")
  
  # Simple rectangle
  rect_svg = '''<svg width="100" height="60" viewBox="0 0 100 60">
      <path d="M 10 10 L 90 10 L 90 50 L 10 50 Z" fill="#2196F3" id="rectangle"/>
  </svg>'''
  
  parser = SvgParser()
  ir = parser.parse_svg(rect_svg)
  
  generator = ImageVectorGenerator()
  kotlin_code = generator.generate(ir)
  
  print("Rectangle SVG -> Kotlin:")
  print("-" * 40)
  print(kotlin_code)
  print("-" * 40)

def demo_multiple_paths():
  """Demonstrate multi-path SVG conversion."""
  print("\n=== Multi-path SVG Demo ===")
  
  # SVG with multiple paths (red, green, blue blocks)
  multi_path_svg = '''<svg width="60" height="20" viewBox="0 0 60 20">
      <path d="M 0 0 L 20 0 L 20 20 L 0 20 Z" fill="red" id="red_block"/>
      <path d="M 20 0 L 40 0 L 40 20 L 20 20 Z" fill="green" id="green_block"/>
      <path d="M 40 0 L 60 0 L 60 20 L 40 20 Z" fill="blue" id="blue_block"/>
  </svg>'''
  
  parser = SvgParser()
  ir = parser.parse_svg(multi_path_svg)
  
  print(f"Parsed {len(ir.nodes)} paths")
  for index, node in enumerate(ir.nodes):
    print(f"  Path {index + 1}: {node.name}, color: {node.fill.to_compose_color()}")
  
  generator = ImageVectorGenerator()
  kotlin_code = generator.generate(ir)
  
  print("\nMulti-path Kotlin code:")
  print("-" * 40)
  print(kotlin_code)
  print("-" * 40)

if __name__ == "__main__":
  print("SVG to Compose ImageVector Converter Demo")
  print("=" * 50)
  
  try:
    demo_star_icon()
    demo_simple_shapes()
    demo_multiple_paths()
    
    print("\n✅ Demo completed! SVG document parser working correctly.")
    print("\nNext steps to consider:")
    print("- Add more SVG path command support (S, Q, T, A)")
    print("- Create CLI interface")
    print("- Add styling and transform support")
    
  except Exception as error:
    print(f"\n❌ Error during demo: {error}")
    import traceback
    traceback.print_exc()