#!/usr/bin/env python3
"""
Demo: SVG Gradient Support

This script demonstrates the gradient support capabilities of the SVG to Compose converter.
It shows how SVG linear and radial gradients are converted to Compose Brush objects.
"""

from pathlib import Path
from src.parser.svg_parser import SvgParser
from src.generator.image_vector_generator import ImageVectorGenerator


def main():
  """Demonstrate gradient conversion capabilities."""
  print("🎨 SVG Gradient Support Demo")
  print("=" * 50)

  # Create output directory
  output_dir = Path("examples/output")
  output_dir.mkdir(exist_ok=True)

  # Demo 1: Linear Gradient
  print("\n1️⃣ Linear Gradient Demo")
  linear_gradient_svg = '''<svg width="200" height="100" viewBox="0 0 200 100">
    <defs>
      <linearGradient id="sunset" x1="0%" y1="0%" x2="100%" y2="0%">
        <stop offset="0%" stop-color="#ff6b35" />
        <stop offset="50%" stop-color="#f7931e" />
        <stop offset="100%" stop-color="#ffcc02" />
      </linearGradient>
    </defs>
    <path d="M 20,20 L 180,20 L 180,80 L 20,80 Z" fill="url(#sunset)" />
  </svg>'''

  parser = SvgParser()
  generator = ImageVectorGenerator()
  
  ir = parser.parse_svg(linear_gradient_svg)
  kotlin_code = generator.generate(ir)
  
  print(f"📊 Parsed {len(ir.nodes)} path(s)")
  print(f"📦 Generated {len(generator.get_required_imports())} imports")
  
  # Save output
  output_file = output_dir / "LinearGradientDemo.kt"
  output_file.write_text(kotlin_code)
  print(f"💾 Saved to {output_file}")
  
  print("\n🎯 Key Features Demonstrated:")
  print("  ✅ Multi-stop linear gradient")
  print("  ✅ Percentage-based offsets")
  print("  ✅ Brush.linearGradient() generation")
  print("  ✅ Offset coordinates")

  # Demo 2: Radial Gradient
  print("\n2️⃣ Radial Gradient Demo")

  # Note: This demo shows circle path conversion since we don't have direct circle support yet
  circle_as_path_svg = '''<svg width="120" height="120" viewBox="0 0 120 120">
    <defs>
      <radialGradient id="spotlight" cx="50%" cy="30%" r="60%">
        <stop offset="0%" stop-color="#ffffff" stop-opacity="1.0" />
        <stop offset="70%" stop-color="#87ceeb" stop-opacity="0.9" />
        <stop offset="100%" stop-color="#191970" stop-opacity="0.8" />
      </radialGradient>
    </defs>
    <path d="M 110,60 A 50,50 0 1,1 10,60 A 50,50 0 1,1 110,60 Z" fill="url(#spotlight)" />
  </svg>'''

  ir2 = parser.parse_svg(circle_as_path_svg)
  kotlin_code2 = generator.generate(ir2)
  
  print(f"📊 Parsed {len(ir2.nodes)} path(s)")
  print(f"📦 Generated {len(generator.get_required_imports())} imports")
  
  # Save output
  output_file2 = output_dir / "RadialGradientDemo.kt"
  output_file2.write_text(kotlin_code2)
  print(f"💾 Saved to {output_file2}")
  
  print("\n🎯 Key Features Demonstrated:")
  print("  ✅ Multi-stop radial gradient")
  print("  ✅ Custom center point (cx, cy)")
  print("  ✅ Stop opacity handling")
  print("  ✅ Brush.radialGradient() generation")
  print("  ✅ Center Offset and radius")

  # Demo 3: Complex Gradient with Style Attributes
  print("\n3️⃣ Complex Gradient with Style Attributes")
  complex_gradient_svg = '''<svg width="300" height="150" viewBox="0 0 300 150">
    <defs>
      <linearGradient id="complexGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color:#e74c3c; stop-opacity:1.0" />
        <stop offset="25%" style="stop-color:#f39c12; stop-opacity:0.8" />
        <stop offset="50%" stop-color="#f1c40f" stop-opacity="0.6" />
        <stop offset="75%" style="stop-color:#27ae60; stop-opacity:0.8" />
        <stop offset="100%" stop-color="#3498db" />
      </linearGradient>
    </defs>
    <path d="M 50,25 L 250,25 L 275,75 L 250,125 L 50,125 L 25,75 Z" fill="url(#complexGrad)" />
  </svg>'''

  ir3 = parser.parse_svg(complex_gradient_svg)
  kotlin_code3 = generator.generate(ir3)
  
  print(f"📊 Parsed {len(ir3.nodes)} path(s)")
  print(f"📦 Generated {len(generator.get_required_imports())} imports")
  
  # Save output
  output_file3 = output_dir / "ComplexGradientDemo.kt"
  output_file3.write_text(kotlin_code3)
  print(f"💾 Saved to {output_file3}")
  
  print("\n🎯 Key Features Demonstrated:")
  print("  ✅ 5-stop gradient")
  print("  ✅ Mixed style and attribute definitions")
  print("  ✅ Diagonal gradient (x1=0%, y1=0%, x2=100%, y2=100%)")
  print("  ✅ Variable opacity stops")
  print("  ✅ Hexagon-like path shape")

  # Summary
  print("\n" + "=" * 50)
  print("🏆 Gradient Support Summary")
  print("=" * 50)
  print("✅ Linear gradients with Brush.linearGradient()")
  print("✅ Radial gradients with Brush.radialGradient()")
  print("✅ Multiple color stops with proper offsets")
  print("✅ Stop opacity handling with alpha channels")
  print("✅ CSS style attribute parsing")
  print("✅ Gradient reference resolution (url(#id))")
  print("✅ Automatic import management")
  print("✅ Fallback to solid colors for missing references")
  
  print(f"\n📁 All output files saved to: {output_dir.absolute()}")
  print("\n🎉 Gradient demo completed successfully!")


if __name__ == "__main__":
  main()