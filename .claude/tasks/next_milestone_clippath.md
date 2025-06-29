# Next Milestone: ClipPath Support Implementation

## Background Discovery
Through careful analysis of AndroidX Compose source code, we discovered that **Compose ImageVector has full clipPath support**! This was previously misunderstood as a limitation.

### Key Evidence from Source Code:
1. `VectorCompose.kt` - `Group()` function has `clipPathData: List<PathNode>` parameter
2. `ImageVector.kt` - `Builder.addGroup()` method supports `clipPathData` 
3. `Vector.kt` - `GroupComponent` implements full clipPath rendering with `clipPath(targetClip)`

## Current Gap
Our SVG parser does not implement `<clipPath>` element parsing, which is why this functionality appears missing.

## Implementation Plan

### Phase 1: Core ClipPath Support
- **clippath_parser_implementation**: Add SVG `<clipPath>` element detection and parsing
- **clippath_ir_support**: Extend `IrVectorGroup` to include `clipPathData` field
- **clippath_generator_support**: Update code generator to output `group(clipPathData = ...)` 

### Phase 2: Testing & Validation
- **clippath_test_cases**: Create comprehensive test suite covering:
  - Simple geometric clipPaths (rectangles, circles)
  - Complex path-based clipPaths
  - Nested clipPath scenarios
  - clipPath with transforms

### Phase 3: Advanced Features (Lower Priority)
- **stroke_dasharray_implementation**: SVG `stroke-dasharray` to `PathEffect.dashPathEffect`
- **path_optimization**: Optimize generated path data for cleaner output
- **performance_optimization**: Handle large/complex SVG files efficiently

## Technical Approach

### ClipPath Parsing Strategy:
1. Detect `<clipPath>` elements in `<defs>` section
2. Parse child elements (paths, shapes) within clipPath
3. Convert to unified path representation
4. Reference clipPath by ID in groups that use it

### Code Generation:
```kotlin
group(
  name = "clipped-content",
  clipPathData = listOf(
    PathNode.MoveTo(0f, 0f),
    PathNode.LineTo(100f, 0f),
    // ... path commands
  )
) {
  // group content
}
```

## Expected Outcome
Full SVG clipPath support bringing the parser much closer to complete SVG compatibility for Compose ImageVector use cases.

## Files to Modify:
- `src/parser/svg_parser.py` - Add clipPath parsing logic
- `src/ir/vector_node.py` - Add clipPathData to IrVectorGroup
- `src/generator/image_vector_generator.py` - Support clipPathData in output
- `tests/test_clippath.py` - New test file for clipPath functionality