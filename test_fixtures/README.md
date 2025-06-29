# Test Fixtures

This directory contains SVG test files used for development and debugging. These are synthetic test cases designed to cover specific features and edge cases.

## Directory Structure

### `bugs/`
SVG files that reproduce specific bugs that were found and fixed:

- `evenodd_fill_rule.svg` - Tests `fill-rule="evenodd"` attribute parsing and `PathFillType.EvenOdd` generation
- `gradient_order_dependency.svg` - Tests gradient parsing when `<defs>` appears after path elements that reference gradients
- `integer_dimension_format.svg` - Tests proper formatting of integer dimensions (e.g., `12.dp` vs `12f.dp`)

### `features/`
SVG files that test specific supported features:

- `basic_shapes.svg` - Rectangle, circle, and line elements
- `complex_paths.svg` - Advanced path commands including curves, arcs, and relative coordinates  
- `transforms_and_groups.svg` - Group elements with transforms (translate, rotate, scale)
- `multi_stop_gradient.svg` - Linear gradients with multiple color stops
- `gradient_simple.svg` - Basic two-stop gradient
- `gradient_user_space_units.svg` - Gradient with `gradientUnits="userSpaceOnUse"`
- `decimal_dimensions.svg` - Non-integer width/height values
- `fill_rule_basic.svg` - Basic fill-rule attribute testing

### `edge_cases/`
SVG files that test edge cases and unusual input:

- `empty_paths.svg` - Empty path data and minimal path elements
- `unusual_attributes.svg` - Scientific notation, percentages, high precision decimals
- `namespace_variations.svg` - Different XML namespace declarations
- `test_case_sensitivity.svg` - Uppercase attribute values (e.g., `fill-rule="EVENODD"`)

## Usage

These files can be used with the CLI tool for testing:

```bash
# Test a specific feature
uv run python -m src.cli convert test_fixtures/features/basic_shapes.svg

# Test all files in a category
for file in test_fixtures/bugs/*.svg; do
  echo "Testing: $file"
  uv run python -m src.cli convert "$file"
done
```

## Guidelines

- Keep test files small and focused on specific features
- Use descriptive filenames that explain what is being tested
- Include comments in SVG files to document the test purpose
- Avoid using real business icons or copyrighted content
- Use simple, geometric shapes for clarity