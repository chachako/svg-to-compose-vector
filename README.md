# Svg to Compose-Vector

Convert SVG files to Kotlin Compose ImageVector code with high fidelity and production-ready output.

`svg-to-compose-vector` is a Python command-line tool that transforms SVG graphics into Compose ImageVector Kotlin code. It supports advanced SVG features including paths, shapes, gradients, transforms, and strokes, generating clean, optimized Compose code.

[Installation](#installation) • [Usage](#usage) • [Features](#features) • [Templates](#templates) • [Multicolor Templates](#multicolor-templates) • [Examples](#examples)

## Features

* **Complete SVG Support**: Handles paths, basic shapes (rect, circle, ellipse, line, polygon), groups, transforms, gradients, and strokes
* **High Fidelity Conversion**: Mathematically precise shape-to-path conversion with proper coordinate handling
* **Production-Ready Output**: Generates clean Kotlin code following Compose best practices with optimal parameter usage
* **Flexible Templates**: Built-in templates for different use cases (val declarations, composable functions, icon objects)
* **Advanced Color Support**: Full support for hex, RGB, HSL, named colors, and gradients (linear and radial)
* **Multicolor Template System**: Intelligent color mapping with parameterized @Composable generation for theme-aware icons
* **Smart Optimizations**: Uses Compose built-in colors (Color.Red vs Color(0xFFFF0000)) and omits default parameters
* **Comprehensive Error Handling**: Clear warnings for unsupported SVG features with graceful degradation
* **Batch Processing**: Convert entire directories of SVG files at once

## Quick Example

Convert an SVG file to Compose ImageVector code:

```bash
svg2compose convert icon.svg
```

Output:
```kotlin
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.dp

ImageVector.Builder(
  name = "Icon",
  defaultWidth = 24.dp,
  defaultHeight = 24.dp,
  viewportWidth = 24f,
  viewportHeight = 24f,
).apply {
  path(fill = SolidColor(Color.Black)) {
    moveTo(12f, 2f)
    lineTo(22f, 12f)
    lineTo(12f, 22f)
    lineTo(2f, 12f)
    close()
  }
}.build()
```

### Multicolor Template Example

Create theme-aware icons with automatic color parameterization:

```bash
svg2compose convert icon.svg --multicolor-template theme.j2
```

Template (theme.j2):
```jinja2
{%- set color_mappings = {
    "#FF0000": {"semantic_name": "errorColor", "replacement": "MaterialTheme.colorScheme.error"},
    "#0000FF": "MaterialTheme.colorScheme.primary"
} -%}

@Composable
fun {{ name.name_part_pascal }}(
{%- for color_hex, mapping in color_mappings.items() if color_hex in used_colors and mapping.semantic_name is defined %}
  {{ mapping.semantic_name }}: Color = {{ mapping.replacement }}{{ "," if not loop.last }}
{%- endfor %}
): ImageVector { /* ... */ }
```

Output:
```kotlin
@Composable
fun MyIcon(errorColor: Color = MaterialTheme.colorScheme.error): ImageVector {
  return ImageVector.Builder(...).apply {
    path(fill = SolidColor(errorColor)) { /* red elements */ }
    path(fill = SolidColor(MaterialTheme.colorScheme.primary)) { /* blue elements */ }
  }.build()
}
```

## Installation

### From PyPI (Recommended)

```bash
pip install svg-to-compose-vector
```

### From source using uv

```bash
git clone https://github.com/chachako/svg-to-compose-vector.git
cd svg-to-compose-vector
uv sync
uv run python -m src.cli --help
```

### From source using pip

```bash
git clone https://github.com/chachako/svg-to-compose-vector.git
cd svg-to-compose-vector
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
svg2compose --help
```

## Usage

### Basic conversion

```bash
# Convert to stdout
svg2compose convert icon.svg

# Convert to file
svg2compose convert icon.svg -o Icon.kt

# Specify icon name
svg2compose convert icon.svg -n HomeIcon
```

### Using templates

```bash
# List available templates
svg2compose templates

# Use specific template
svg2compose convert icon.svg -t composable_function -o HomeIcon.kt

# Use custom template file
svg2compose convert icon.svg -t my_template.j2 -o CustomIcon.kt
```

### Batch processing

```bash
# Convert all SVG files in a directory
svg2compose batch icons/ output/

# With custom naming pattern
svg2compose batch icons/ output/ --naming "Icon{name}"

# Using specific template
svg2compose batch icons/ output/ -t composable_function
```

### Multicolor templates

```bash
# Use multicolor template for theme-aware icons
svg2compose convert icon.svg --multicolor-template multicolor.j2

# Combine with regular templates (fallback when colors don't match)
svg2compose convert icon.svg -t composable_function --multicolor-template theme.j2

# Batch convert with multicolor support
svg2compose batch icons/ output/ -t val_declaration --multicolor-template theme_template.j2
```

### File information

```bash
# Show SVG file details
svg2compose info icon.svg
```

## Templates

`svg-to-compose-vector` provides four built-in templates for different use cases:

### 1. Default Template (`default`)

Basic ImageVector.Builder code without wrapper - ideal for embedding in existing code.

**Usage:**
```bash
svg2compose convert icon.svg -t default
```

**Output:**
```kotlin
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.dp

ImageVector.Builder(
  name = "Icon",
  defaultWidth = 24.dp,
  defaultHeight = 24.dp,
  viewportWidth = 24f,
  viewportHeight = 24f,
).apply {
  path(fill = SolidColor(Color.Red)) {
    moveTo(12f, 12f)
    lineTo(18f, 12f)
    // ... more path commands
  }
}.build()
```

### 2. Val Declaration Template (`val_declaration`)

Creates a lazy val property - perfect for icon collections and design systems.

**Usage:**
```bash
svg2compose convert home_icon.svg -t val_declaration
```

**Output:**
```kotlin
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.dp

val HomeIconIcon: ImageVector = ImageVector.Builder(
  name = "HomeIcon",
  defaultWidth = 24.dp,
  defaultHeight = 24.dp,
  viewportWidth = 24f,
  viewportHeight = 24f,
).apply {
  path(fill = SolidColor(Color.Black)) {
    moveTo(10f, 20f)
    verticalLineTo(14f)
    // ... more path commands
  }
}.build()
```

### 3. Composable Function Template (`composable_function`)

Generates a @Composable function with modifier and tint parameters - ideal for reusable components.

**Usage:**
```bash
svg2compose convert search_icon.svg -t composable_function
```

**Output:**
```kotlin
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.dp
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier

@Composable
fun SearchIconIcon(
  modifier: Modifier = Modifier,
  tint: Color = Color.Unspecified
): ImageVector {
  return remember {
    ImageVector.Builder(
      name = "SearchIcon",
      defaultWidth = 24.dp,
      defaultHeight = 24.dp,
      viewportWidth = 24f,
      viewportHeight = 24f,
    ).apply {
      path(fill = SolidColor(Color.Black)) {
        moveTo(15.5f, 14f)
        horizontalLineTo(14.71f)
        // ... more path commands
      }
    }.build()
  }
}
```

### 4. Icon Object Template (`icon_object`)

Creates an object with a lazy ImageVector property - useful for organized icon libraries.

**Usage:**
```bash
svg2compose convert settings_icon.svg -t icon_object
```

**Output:**
```kotlin
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.dp

object SettingsIconIcon {
  val imageVector: ImageVector by lazy {
    ImageVector.Builder(
      name = "SettingsIcon",
      defaultWidth = 24.dp,
      defaultHeight = 24.dp,
      viewportWidth = 24f,
      viewportHeight = 24f,
    ).apply {
      path(fill = SolidColor(Color.Black)) {
        moveTo(19.14f, 12.94f)
        curveTo(19.18f, 12.64f, 19.2f, 12.33f, 19.2f, 12f)
        // ... more path commands
      }
    }.build()
  }
}
```

### Custom Templates

Create powerful custom Jinja2 templates using the complete set of available variables and filters.

#### Available Template Variables

| Variable | Type | Description | Example Value |
|----------|------|-------------|---------------|
| `imports` | str | Formatted import statements | `import androidx.compose.ui.graphics.Color` |
| `build_code` | str | Complete ImageVector.Builder code | `ImageVector.Builder(...)` |
| `name` | NameComponents | Complete name object with all properties | See properties below |
| `namespace` | str | Namespace in PascalCase | `Navigation` |
| `icon` | str | Icon name in PascalCase | `HomeIcon` |
| `full_name` | str | Full hierarchical name | `Navigation.HomeIcon` |
| `icon_name` | str | Raw icon name for filters | `home_icon` |

#### NameComponents Properties

The `name` object provides extensive naming options, for example, if the input is `navigation.home-icon.svg`:
| Property | Description | Output |
|----------|-------------|----------------|
| `name.raw_name` | Original input name | `navigation.home-icon` |
| `name.name` | Clean base name | `home_icon` |
| `name.namespace_part` | Namespace portion | `navigation` |
| `name.name_part` | Name portion | `home_icon` |
| `name.full_path` | Complete path | `navigation.home_icon` |
| `name.namespace_part_pascal` | Namespace in PascalCase | `Navigation` |
| `name.name_part_pascal` | Name in PascalCase | `HomeIcon` |
| `name.full_path_pascal` | Full path in PascalCase | `Navigation.HomeIcon` |
| `name.namespace_part_camel` | Namespace in camelCase | `navigation` |
| `name.name_part_camel` | Name in camelCase | `homeIcon` |
| `name.full_path_camel` | Full path in camelCase | `navigation.homeIcon` |

#### Available Filters

Transform any string with built-in filters:

| Filter | Description | Example Usage | Input | Output |
|--------|-------------|---------------|-------|--------|
| `pascal_case` | Convert to PascalCase | `{{ "home-icon" \| pascal_case }}` | `home-icon` | `HomeIcon` |
| `camel_case` | Convert to camelCase | `{{ "home-icon" \| camel_case }}` | `home-icon` | `homeIcon` |
| `snake_case` | Convert to snake_case | `{{ "HomeIcon" \| snake_case }}` | `HomeIcon` | `home_icon` |
| `indent` | Add indentation | `{{ build_code \| indent(4, first=False) }}` | Code block | Indented code |

#### Template Examples

**1. Icon Library with Documentation**

```jinja2
{{- imports }}

/**
 * {{ name.name_part_pascal }} icon from {{ name.namespace_part_pascal or "Default" }} category
 * Generated from: {{ name.raw_name }}
 */
val {{ name.name_part_pascal }}Icon: ImageVector by lazy {
  {{ build_code | indent(2, first=False) }}
}
```

<details>
<summary>Kotlin Output:</summary>

```kotlin
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.dp

/**
 * HomeIcon icon from Navigation category
 * Generated from: navigation.home-icon
 */
 val HomeIconIcon: ImageVector by lazy {
    ImageVector.Builder(
    name = "HomeIcon",
    defaultWidth = 24.dp,
    defaultHeight = 24.dp,
    viewportWidth = 24f,
    viewportHeight = 24f,
    ).apply {
    path(fill = SolidColor(Color.Black)) {
      moveTo(10f, 20f)
      verticalLineTo(14f)
      horizontalLineTo(14f)
      // ... path data
    }
    }.build()
 }
```

</details>

**2. Sealed Class Icon System**

```jinja2
{{- imports }}

sealed class {{ name.namespace_part_pascal or "Icons" }} {
  object {{ name.name_part_pascal }} : {{ name.namespace_part_pascal or "Icons" }}() {
    val imageVector: ImageVector by lazy {
      {{ build_code | indent(6, first=False) }}
    }
  }
}
```

<details>
<summary>Kotlin Output:</summary>

```kotlin
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.dp

sealed class Ui {
  object Button : Ui() {
    val imageVector: ImageVector by lazy {
      ImageVector.Builder(
        name = "Button",
        defaultWidth = 24.dp,
        defaultHeight = 24.dp,
        viewportWidth = 24f,
        viewportHeight = 24f,
      ).apply {
        path(fill = SolidColor(Color.Black)) {
          moveTo(2f, 6f)
          curveTo(2f, 4.9f, 2.9f, 4f, 4f, 4f)
          // ... path data
        }
      }.build()
    }
  }
}
```

</details>

**3. Composable with Custom Parameters**

```jinja2
{{- imports }}
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.Dp

@Composable
fun {{ name.name_part_pascal }}(
  size: Dp = 24.dp,
  tint: Color = Color.Unspecified,
  contentDescription: String? = "{{ name.name_part | replace("_", " ") | title }}"
): ImageVector {
  return remember(size, tint) {
    {{ build_code | indent(4, first=False) }}
  }
}
```

<details>
<summary>Kotlin Output:</summary>

```kotlin
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.dp
import androidx.compose.runtime.Composable
import androidx.compose.ui.unit.Dp

@Composable
fun SearchIcon(
  size: Dp = 24.dp,
  tint: Color = Color.Unspecified,
  contentDescription: String? = "Search Icon"
): ImageVector {
  return remember(size, tint) {
    ImageVector.Builder(
      name = "SearchIcon",
      defaultWidth = 24.dp,
      defaultHeight = 24.dp,
      viewportWidth = 24f,
      viewportHeight = 24f,
    ).apply {
      path(fill = SolidColor(Color.Black)) {
        moveTo(15.5f, 14f)
        horizontalLineTo(14.71f)
        // ... path data
      }
    }.build()
  }
}
```

</details>

#### Advanced Usage

**Conditional Logic:**
```jinja2
{{- imports }}

{% if name.namespace_part %}
// {{ name.namespace_part_pascal }} Category Icons
package com.myapp.icons.{{ name.namespace_part | snake_case }}
{% endif %}

{% if name.namespace_part == "navigation" %}
@NavigationIcon
{% elif name.namespace_part == "action" %}
@ActionIcon
{% endif %}
val {{ name.name_part_pascal }}Icon: ImageVector = {{ build_code }}
```

**Loop Through Categories:**
```jinja2
{{- imports }}

// Generated icon path: {{ name.categories | join(" → ") }}
{% for category in name.categories[:-1] %}
// Category: {{ category | pascal_case }}
{% endfor %}
// Icon: {{ name.categories[-1] | pascal_case }}

val {{ name.full_path_pascal | replace(".", "") }}Icon: ImageVector = {{ build_code }}
```

**Using Custom Template:**
```bash
# Create your template file
svg2compose convert navigation.home.svg -t my_custom_template.j2 -o HomeIcon.kt

# The template receives all the variables and can generate any format you need
```

## Multicolor Templates

Transform SVG files with multiple colors into theme-aware @Composable functions using intelligent color mapping.

### Overview

Multicolor templates enable automatic color parameterization, allowing icons to adapt to different themes:

- **Smart Color Detection**: Automatically extracts colors from SVG files
- **Intelligent Template Selection**: Uses multicolor template when SVG colors match mappings, falls back to regular template otherwise
- **Works with Any Template**: Combine with `default`, `composable_function`, `val_declaration`, or custom templates
- **Partial Mapping Support**: Unmapped colors retain original hex values
- **Transparency Support**: Full ARGB support for transparent colors

### Template Formats

#### Full Format (with parameters)
Creates function parameters for theme customization:

```jinja2
{{- imports }}

{%- set color_mappings = {
    "#FF0000": {"semantic_name": "errorColor", "replacement": "Color.Red"},
    "#0000FF": {"semantic_name": "primaryColor", "replacement": "MaterialTheme.colorScheme.primary"}
} -%}

@Composable
fun {{ name.name_part_pascal }}(
{%- for color_hex, mapping in color_mappings.items() if color_hex in used_colors %}
  {{ mapping.semantic_name }}: Color = {{ mapping.replacement }}{{ "," if not loop.last }}
{%- endfor %}
): ImageVector {
  return {{ build_code_with_color_params }}
}
```

**Generated Output:**
```kotlin
@Composable
fun MyIcon(
  errorColor: Color = Color.Red,
  primaryColor: Color = MaterialTheme.colorScheme.primary
): ImageVector {
  return ImageVector.Builder(...).apply {
    path(fill = SolidColor(errorColor)) { /* red paths */ }
    path(fill = SolidColor(primaryColor)) { /* blue paths */ }
  }.build()
}
```

#### Simplified Format (direct replacement)
Directly replaces colors without creating parameters:

```jinja2
{{- imports }}

{%- set color_mappings = {
    "#FF0000": "MaterialTheme.colorScheme.error",
    "#0000FF": "MaterialTheme.colorScheme.primary"
} -%}

@Composable
fun {{ name.name_part_pascal }}(): ImageVector {
  return {{ build_code_with_color_params }}
}
```

**Generated Output:**
```kotlin
@Composable
fun MyIcon(): ImageVector {
  return ImageVector.Builder(...).apply {
    path(fill = SolidColor(MaterialTheme.colorScheme.error)) { /* red paths */ }
    path(fill = SolidColor(MaterialTheme.colorScheme.primary)) { /* blue paths */ }
  }.build()
}
```

#### Mixed Format
Combine both approaches in a single template:

```jinja2
{%- set color_mappings = {
    "#FF0000": {"semantic_name": "errorColor", "replacement": "Color.Red"},
    "#0000FF": "MaterialTheme.colorScheme.primary",
    "#00FF00": "MaterialTheme.colorScheme.secondary"
} -%}
```

### Template Variables

Multicolor templates have access to additional variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `build_code_with_color_params` | ImageVector code with color substitution | `ImageVector.Builder(...)` |
| `used_colors` | Set of colors found in SVG | `{"#FF0000", "#0000FF"}` |
| `color_mappings` | Your color mapping configuration | `{...}` |

### Usage Examples

**Theme-aware icon library:**
```bash
# Convert with multicolor template only
svg2compose convert icon.svg --multicolor-template examples/templates/material_theme.j2

# Combine multicolor with composable function template (recommended)
svg2compose convert icon.svg -t composable_function --multicolor-template material_theme.j2

# Batch convert entire icon set with fallback template
svg2compose batch icons/ src/icons/ -t val_declaration --multicolor-template material_theme.j2
```

**What happens:**
- **Match found**: Uses `material_theme.j2` with color parameterization
- **No match**: Falls back to specified template (`composable_function` or `val_declaration`)
- **No template specified**: Falls back to `default` template
- **Result**: Consistent output format regardless of color content

**Custom color scheme:**
```bash
svg2compose convert brand_icon.svg -t icon_object --multicolor-template brand_colors.j2
```

### Template Selection Logic

The system intelligently chooses when to use multicolor templates:

1. **Color Intersection Check**: When SVG colors overlap with template color mappings
2. **Use Multicolor Template**: Apply color substitution when matches are found
3. **Fallback to Regular Template**: When no colors match, use the specified template without color substitution

**Important**: Multicolor templates work with any regular template. The system behavior:

- **With both templates**: `svg2compose convert icon.svg -t composable_function --multicolor-template theme.j2`
  - Use `theme.j2` when colors match
  - Fall back to `composable_function` when no matches
  
- **Multicolor only**: `svg2compose convert icon.svg --multicolor-template theme.j2`
  - Use `theme.j2` when colors match  
  - Fall back to `default` template when no matches

This ensures you always get a valid output while gaining color parameterization when applicable.

#### Jinja2 Features

All standard Jinja2 features are available:
- **Conditionals:** `{% if %}`, `{% elif %}`, `{% else %}`
- **Loops:** `{% for item in list %}`
- **Macros:** `{% macro %}` for reusable code blocks
- **Comments:** `{# This is a comment #}`
- **String operations:** `{{ string | upper | replace("_", "-") }}`

## Advanced Examples

### Batch processing with templates

Convert multiple SVG files at once with consistent formatting:

```bash
# Convert all icons to composable functions
svg2compose batch icons/ src/main/kotlin/icons/ -t composable_function
```

**Input directory structure:**
```
icons/
├── home.svg
├── search.svg
└── settings.svg
```

**Output directory structure:**
```
src/main/kotlin/icons/
├── Home.kt
├── Search.kt
└── Settings.kt
```

**Generated file content** (Home.kt):
```kotlin
@Composable
fun HomeIcon(
  modifier: Modifier = Modifier,
  tint: Color = Color.Unspecified
): ImageVector {
  return remember {
    ImageVector.Builder(
      name = "Home",
      defaultWidth = 24.dp,
      defaultHeight = 24.dp,
      viewportWidth = 24f,
      viewportHeight = 24f,
    ).apply {
      path(fill = SolidColor(Color.Black)) {
        moveTo(10f, 20f)
        verticalLineTo(14f)
        horizontalLineTo(14f)
        // ... more path commands
      }
    }.build()
  }
}
```

### Complex SVG with gradients and transforms

```bash
svg2compose convert complex_icon.svg -t composable_function
```

Automatically handles gradients and transforms:
```kotlin
@Composable
fun ComplexIcon(): ImageVector {
  return remember {
    ImageVector.Builder(
      name = "ComplexIcon",
      defaultWidth = 48.dp,
      defaultHeight = 48.dp,
      viewportWidth = 48f,
      viewportHeight = 48f,
    ).apply {
      group(
        name = "rotated-group",
        rotate = 45f,
        pivotX = 24f,
        pivotY = 24f,
      ) {
        path(
          fill = Brush.linearGradient(
            colorStops = arrayOf(
              0f to Color.Red,
              0.5f to Color.Yellow,
              1f to Color.Blue,
            ),
            start = Offset(0f, 0f),
            end = Offset(48f, 48f),
          ),
        ) {
          // path data...
        }
      }
    }.build()
  }
}
```

## Supported SVG Features

| Feature | Support | Notes |
|---------|---------|-------|
| **Paths** | ✅ Complete | All path commands (M, L, C, A, Z, etc.) |
| **Basic Shapes** | ✅ Complete | rect, circle, ellipse, line, polygon, polyline |
| **Groups & Transforms** | ✅ Complete | translate, scale, rotate, matrix decomposition |
| **Colors** | ✅ Complete | hex, rgb, hsl, named colors with alpha support |
| **Gradients** | ✅ Complete | Linear and radial gradients with multiple stops |
| **Strokes** | ✅ Complete | Width, opacity, caps, joins, gradient strokes |
| **ClipPath** | ✅ Basic | Simple clipPath support for groups |
| **Text** | ⚠️ Warning | Text elements not supported by Compose ImageVector |
| **Filters** | ⚠️ Warning | Filter effects not supported by Compose ImageVector |
| **Animations** | ⚠️ Warning | Animation elements not supported (static conversion only) |

## Configuration

Use configuration files for consistent settings across projects:

```json
{
  "template": "composable_function",
  "indent_size": 2,
  "use_named_colors": true,
  "optimize_output": true
}
```

```bash
svg2compose convert icon.svg -c config.json
```

## Development

```bash
git clone https://github.com/chachako/svg-to-compose-vector.git
cd svg-to-compose-vector

# Setup development environment
uv sync --dev

# Run tests
uv run pytest

# Code formatting and linting
uv run ruff check
uv run ruff format
```

## Requirements

* Python 3.13+
* Dependencies: jinja2, click (automatically installed)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## Acknowledgments

This project was inspired by the [Valkyrie](https://github.com/ComposeGears/Valkyrie) project.
