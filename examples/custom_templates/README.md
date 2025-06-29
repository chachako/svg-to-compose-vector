# Custom Template Testing

This directory contains custom templates used in the main README.md examples, along with a comprehensive test script to verify that all templates work correctly.

## Files

- `documented_icon.j2` - Icon library template with documentation comments
- `sealed_class_icon.j2` - Sealed class icon system template  
- `composable_with_params.j2` - Composable function with custom parameters
- `../demo_custom_templates.py` - Test script that verifies all templates

## Running the Tests

```bash
# Run the comprehensive test suite
uv run python examples/demo_custom_templates.py
```

This will test:
1. **Documented Icon Template** - With `navigation.home-icon.svg`
2. **Sealed Class Template** - With `ui.button.svg` 
3. **Composable Parameters Template** - With `search_icon.svg`
4. **Template Variables Analysis** - Show all naming variations

## Testing with CLI

You can also test these templates using the CLI:

```bash
# Test documented icon template
uv run python -m src.cli convert examples/svg/circle_test.svg -t examples/custom_templates/documented_icon.j2 -n navigation.home-icon

# Test sealed class template  
uv run python -m src.cli convert examples/svg/rectangle_test.svg -t examples/custom_templates/sealed_class_icon.j2 -n ui.button

# Test composable parameters template
uv run python -m src.cli convert examples/svg/star_test.svg -t examples/custom_templates/composable_with_params.j2 -n search_icon
```

## Verification

The test script verifies that:
- ✅ All templates render without errors
- ✅ Generated code matches README.md examples
- ✅ Template variables work correctly with complex naming
- ✅ Import statements are properly generated
- ✅ Kotlin code follows proper formatting

This ensures that users can trust the examples in the README.md and use them as starting points for their own custom templates. 