#!/usr/bin/env python3
"""Demo script showcasing SVG shape element support."""

from pathlib import Path

from src.generator.image_vector_generator import ImageVectorGenerator
from src.parser.svg_parser import SvgParser


def main():
  """Demonstrate shape element parsing and code generation."""

  # Create SVG content with various shapes
  shapes_svg = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">
  <!-- Rectangle with rounded corners -->
  <rect x="10" y="10" width="60" height="40" rx="5" ry="5"
        fill="#3498db" stroke="#2980b9" stroke-width="2"/>

  <!-- Circle -->
  <circle cx="150" cy="30" r="20"
          fill="#e74c3c" stroke="#c0392b" stroke-width="1"/>

  <!-- Ellipse -->
  <ellipse cx="50" cy="100" rx="30" ry="20"
           fill="#f39c12" stroke="#e67e22" stroke-width="1.5"/>

  <!-- Line -->
  <line x1="120" y1="80" x2="180" y2="120"
        stroke="#9b59b6" stroke-width="3" stroke-linecap="round"/>

  <!-- Triangle (polygon) -->
  <polygon points="30,150 60,130 90,150 60,180"
           fill="#2ecc71" stroke="#27ae60" stroke-width="2"/>

  <!-- Zigzag line (polyline) -->
  <polyline points="120,150 140,140 160,160 180,150"
            fill="none" stroke="#34495e" stroke-width="2" stroke-linejoin="round"/>
</svg>"""

  # Parse the SVG
  parser = SvgParser()
  ir = parser.parse_svg(shapes_svg)

  print("=== SVG Shape Elements Demo ===")
  print(f"Parsed {len(ir.nodes)} shape elements:")

  for i, node in enumerate(ir.nodes, 1):
    print(f"  {i}. {node.name}: {len(node.paths)} path commands")

  # Generate Kotlin code
  generator = ImageVectorGenerator()
  kotlin_code = generator.generate(ir)

  print("\n=== Generated Kotlin Code ===")
  print(kotlin_code)

  # Save example SVG file
  svg_file = Path("examples/svg/shapes_demo.svg")
  svg_file.parent.mkdir(parents=True, exist_ok=True)
  svg_file.write_text(shapes_svg)

  # Save generated Kotlin code
  kotlin_file = Path("examples/output/ShapesDemo.kt")
  kotlin_file.parent.mkdir(parents=True, exist_ok=True)
  kotlin_file.write_text(kotlin_code)

  print("\nFiles created:")
  print(f"  - SVG: {svg_file}")
  print(f"  - Kotlin: {kotlin_file}")


def test_individual_shapes():
  """Test each shape type individually."""

  shapes = {
    "rectangle": """<svg><rect x="10" y="10" width="50" height="30" fill="blue"/></svg>""",
    "rounded_rect": """<svg><rect x="0" y="0" width="40" height="40" rx="10" fill="green"/></svg>""",
    "circle": """<svg><circle cx="25" cy="25" r="20" fill="red"/></svg>""",
    "ellipse": """<svg><ellipse cx="30" cy="20" rx="25" ry="15" fill="orange"/></svg>""",
    "line": """<svg><line x1="0" y1="0" x2="50" y2="50" stroke="purple" stroke-width="3"/></svg>""",
    "triangle": """<svg><polygon points="25,5 45,40 5,40" fill="yellow"/></svg>""",
    "star": """<svg><polygon points="25,2 30,18 47,18 34,29 39,45 25,36 11,45 16,29 3,18 20,18" fill="gold"/></svg>""",
    "polyline": """<svg><polyline points="5,5 25,25 45,5 45,45" fill="none" stroke="navy" stroke-width="2"/></svg>""",
  }

  parser = SvgParser()
  generator = ImageVectorGenerator()

  print("\n=== Individual Shape Tests ===")

  for shape_name, svg_content in shapes.items():
    try:
      ir = parser.parse_svg(svg_content)
      kotlin_code = generator.generate(ir)

      print(f"\n{shape_name.upper()}:")
      print(f"  Nodes: {len(ir.nodes)}")
      if ir.nodes:
        print(f"  Path commands: {len(ir.nodes[0].paths)}")

      # Save individual examples
      svg_file = Path(f"examples/svg/{shape_name}_test.svg")
      kotlin_file = Path(f"examples/output/{shape_name.title()}Test.kt")

      svg_file.write_text(svg_content)
      kotlin_file.write_text(kotlin_code)

    except Exception as e:
      print(f"  ERROR: {e}")


if __name__ == "__main__":
  main()
  test_individual_shapes()
