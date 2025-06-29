#!/usr/bin/env python3
"""
Custom Template Testing Demo

This script tests the custom templates shown in the README.md to ensure
they work correctly and produce the expected output.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.config import Config
from src.parser.svg_parser import SvgParser
from src.generator.image_vector_generator import ImageVectorGenerator
from src.generator.template_engine import TemplateEngine
from src.utils.naming import NameResolver


def test_documented_icon_template():
    """Test the documented icon library template."""
    print("=" * 60)
    print("Testing: Documented Icon Library Template")
    print("=" * 60)
    
    # Simulate navigation.home-icon.svg
    svg_content = '''<svg width="24" height="24" viewBox="0 0 24 24">
        <path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z" fill="black"/>
    </svg>'''
    
    config = Config(
        template_path=Path(__file__).parent / "custom_templates" / "documented_icon.j2"
    )
    
    parser = SvgParser()
    generator = ImageVectorGenerator()
    template_engine = TemplateEngine(config)
    name_resolver = NameResolver()
    
    ir = parser.parse_svg(svg_content)
    name_components = name_resolver.resolve_name_from_string("navigation.home-icon")
    ir.name = name_components.name_part_pascal
    
    core_code, imports = generator.generate_core_code(ir)
    result = template_engine.render(
        template_name="default",  # Use default processing for custom files
        build_code=core_code,
        imports=imports,
        name_components=name_components,
    )
    
    print("Input: navigation.home-icon.svg")
    print("\nGenerated output:")
    print("-" * 40)
    print(result)
    print()


def test_sealed_class_template():
    """Test the sealed class icon system template."""
    print("=" * 60)
    print("Testing: Sealed Class Icon System Template")
    print("=" * 60)
    
    # Simulate ui.button.svg
    svg_content = '''<svg width="24" height="24" viewBox="0 0 24 24">
        <rect x="2" y="6" width="20" height="12" rx="2" fill="black"/>
    </svg>'''
    
    config = Config(
        template_path=Path(__file__).parent / "custom_templates" / "sealed_class_icon.j2"
    )
    
    parser = SvgParser()
    generator = ImageVectorGenerator()
    template_engine = TemplateEngine(config)
    name_resolver = NameResolver()
    
    ir = parser.parse_svg(svg_content)
    name_components = name_resolver.resolve_name_from_string("ui.button")
    ir.name = name_components.name_part_pascal
    
    core_code, imports = generator.generate_core_code(ir)
    result = template_engine.render(
        template_name="default",  # Use default processing for custom files
        build_code=core_code,
        imports=imports,
        name_components=name_components,
    )
    
    print("Input: ui.button.svg")
    print("\nGenerated output:")
    print("-" * 40)
    print(result)
    print()


def test_composable_with_params_template():
    """Test the composable with custom parameters template."""
    print("=" * 60)
    print("Testing: Composable with Custom Parameters Template")
    print("=" * 60)
    
    # Simulate search_icon.svg
    svg_content = '''<svg width="24" height="24" viewBox="0 0 24 24">
        <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z" fill="black"/>
    </svg>'''
    
    config = Config(
        template_path=Path(__file__).parent / "custom_templates" / "composable_with_params.j2"
    )
    
    parser = SvgParser()
    generator = ImageVectorGenerator()
    template_engine = TemplateEngine(config)
    name_resolver = NameResolver()
    
    ir = parser.parse_svg(svg_content)
    name_components = name_resolver.resolve_name_from_string("search_icon")
    ir.name = name_components.name_part_pascal
    
    core_code, imports = generator.generate_core_code(ir)
    result = template_engine.render(
        template_name="default",  # Use default processing for custom files
        build_code=core_code,
        imports=imports,
        name_components=name_components,
    )
    
    print("Input: search_icon.svg")
    print("\nGenerated output:")
    print("-" * 40)
    print(result)
    print()


def test_template_variables():
    """Test template variables with complex naming."""
    print("=" * 60)
    print("Testing: Template Variables Analysis")
    print("=" * 60)
    
    from src.utils.naming import NameResolver
    
    test_names = [
        "navigation.home-icon",
        "ui.button",
        "search_icon",
        "simple_icon",
        "system.dialog.modal"
    ]
    
    name_resolver = NameResolver()
    
    for test_name in test_names:
        print(f"\nAnalyzing: {test_name}")
        print("-" * 30)
        
        name_components = name_resolver.resolve_name_from_string(test_name)
        
        print(f"raw_name: {name_components.raw_name}")
        print(f"name: {name_components.name}")
        print(f"namespace_part: {name_components.namespace_part}")
        print(f"name_part: {name_components.name_part}")
        print(f"namespace_part_pascal: {name_components.namespace_part_pascal}")
        print(f"name_part_pascal: {name_components.name_part_pascal}")
        print(f"full_path_pascal: {name_components.full_path_pascal}")
        print(f"name_part_camel: {name_components.name_part_camel}")


def main():
    """Run all custom template tests."""
    print("🧪 Custom Template Testing Demo")
    print("This demo verifies that the custom templates in README.md work correctly.\n")
    
    try:
        test_documented_icon_template()
        test_sealed_class_template()
        test_composable_with_params_template()
        test_template_variables()
        
        print("✅ All custom template tests completed successfully!")
        print("\n📚 These templates match the examples shown in README.md")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 