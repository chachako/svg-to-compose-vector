# Examples & Demos

This directory contains example files and demonstration scripts for the SVG to Compose Vector converter.

## Directory Structure

```
examples/
├── svg/                    # Sample SVG files for testing and demonstration
│   ├── test_icon.svg      # Simple icon with basic path commands
│   └── advanced_test.svg  # Complex icon with advanced path commands (Q, T, S, A)
├── output/                # Generated Kotlin code examples (gitignored)
│   └── TestIcon.kt        # Example output from test_icon.svg
├── demo_svg_to_kotlin.py  # Basic conversion demonstration
└── demo_advanced_paths.py # Advanced features demonstration
```

## Usage

### CLI Commands

Convert any SVG file using the CLI:

```bash
# Convert to stdout
uv run python -m src.cli convert examples/svg/test_icon.svg

# Convert to file with wrapper
uv run python -m src.cli convert examples/svg/test_icon.svg \
  -ws "val TestIcon: ImageVector = " \
  -o examples/output/TestIcon.kt

# Get SVG information
uv run python -m src.cli info examples/svg/advanced_test.svg
```

### Demo Scripts

Run the demonstration scripts to see the converter in action:

```bash
# Run basic demo
uv run python examples/demo_svg_to_kotlin.py

# Run advanced features demo
uv run python examples/demo_advanced_paths.py
```

## Demo Features

### demo_svg_to_kotlin.py
- Basic demonstration of the core conversion functionality
- Shows step-by-step conversion process
- Includes a star icon example with basic path commands

### demo_advanced_paths.py  
- Demonstrates advanced SVG path command support
- Shows all modern path commands: Q, T, S, A
- Includes detailed output analysis and feature breakdown
- Perfect for understanding the full capabilities

### What You'll See

The demos will show:
- 📄 Input SVG content
- 📊 Parsed IR structure analysis  
- 🚀 Generated Kotlin ImageVector code
- ✅ Feature breakdown and validation

## SVG Features Demonstrated

### test_icon.svg
- Basic path commands (M, L, V, Z)
- Simple polygon shapes
- Solid color fills

### advanced_test.svg  
- Quadratic Bezier curves (Q)
- Smooth quadratic curves (T)
- Smooth cubic curves (S)
- Elliptical arcs (A)
- Complex color values

## Use Cases

These examples are great for:
- Understanding the conversion process
- Testing new features
- Showcasing capabilities to others
- Learning about SVG path commands
- Validating output quality