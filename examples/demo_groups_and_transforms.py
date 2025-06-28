#!/usr/bin/env python3
"""
Demo script for groups and transforms functionality.

This script demonstrates the SVG to Compose ImageVector converter's 
ability to handle complex group structures with transformations.
"""

from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.parser.svg_parser import SvgParser
from src.generator.image_vector_generator import ImageVectorGenerator


def main():
    """Demonstrate groups and transforms conversion."""
    
    # Initialize parser and generator
    parser = SvgParser()
    generator = ImageVectorGenerator()
    
    # Load the groups test SVG
    svg_path = Path(__file__).parent / "svg" / "groups_test.svg"
    
    if not svg_path.exists():
        print(f"Error: SVG file not found at {svg_path}")
        return
    
    print(f"Converting SVG with groups and transforms: {svg_path.name}")
    print("=" * 60)
    
    # Parse SVG to IR
    try:
        ir = parser.parse_svg(svg_path)
        print("✅ Parsed SVG successfully")
        print(f"   - Icon name: {ir.name}")
        print(f"   - Dimensions: {ir.default_width}×{ir.default_height}")
        print(f"   - Viewport: {ir.viewport_width}×{ir.viewport_height}")
        print(f"   - Root nodes: {len(ir.nodes)}")
        
        # Analyze structure
        analyze_structure(ir.nodes, level=0)
        
    except Exception as e:
        print(f"❌ Error parsing SVG: {e}")
        return
    
    print("\n" + "=" * 60)
    print("Generated Kotlin Code:")
    print("=" * 60)
    
    # Generate Kotlin code
    try:
        kotlin_code = generator.generate(ir)
        print(kotlin_code)
        
        # Save to file
        output_path = Path(__file__).parent / "output" / "GroupsTest.kt"
        output_path.parent.mkdir(exist_ok=True)
        output_path.write_text(kotlin_code)
        print(f"\n✅ Kotlin code saved to: {output_path}")
        
    except Exception as e:
        print(f"❌ Error generating Kotlin code: {e}")
        return

    # Show statistics
    print("\n" + "=" * 60)
    print("Conversion Statistics:")
    print("=" * 60)
    
    lines = kotlin_code.split('\n')
    group_count = sum(1 for line in lines if 'group' in line and '{' in line)
    path_count = sum(1 for line in lines if 'path' in line and '{' in line)
    transform_params = sum(1 for line in lines if any(param in line for param in 
                          ['translationX', 'translationY', 'scaleX', 'scaleY', 'rotate']))
    
    print(f"   - Groups generated: {group_count}")
    print(f"   - Paths generated: {path_count}")
    print(f"   - Transform parameters: {transform_params}")
    print(f"   - Total lines: {len(lines)}")


def analyze_structure(nodes, level=0):
    """Recursively analyze the IR structure."""
    from src.ir.vector_node import IrVectorGroup, IrVectorPath
    
    indent = "   " * level
    
    for i, node in enumerate(nodes):
        if isinstance(node, IrVectorGroup):
            print(f"{indent}📁 Group: {node.name}")
            
            # Show transforms
            transforms = []
            if node.translation_x != 0.0 or node.translation_y != 0.0:
                transforms.append(f"translate({node.translation_x}, {node.translation_y})")
            if node.scale_x != 1.0 or node.scale_y != 1.0:
                transforms.append(f"scale({node.scale_x}, {node.scale_y})")
            if node.rotation != 0.0:
                transforms.append(f"rotate({node.rotation}°)")
            
            if transforms:
                print(f"{indent}   🔄 Transforms: {', '.join(transforms)}")
            
            print(f"{indent}   📦 Children: {len(node.children)}")
            
            # Recursively analyze children
            analyze_structure(node.children, level + 1)
            
        elif isinstance(node, IrVectorPath):
            print(f"{indent}🎨 Path: {node.name}")
            
            # Show styling
            styles = []
            if node.fill:
                styles.append(f"fill={node.fill.to_compose_color()}")
            if node.stroke:
                styles.append(f"stroke={node.stroke.to_compose_color()}")
            if node.stroke_line_width != 0.0:
                styles.append(f"width={node.stroke_line_width}")
            
            if styles:
                print(f"{indent}   🎨 Style: {', '.join(styles)}")
            
            print(f"{indent}   📐 Path commands: {len(node.paths)}")


if __name__ == "__main__":
    main()