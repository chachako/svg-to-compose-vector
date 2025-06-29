from src.parser.svg_parser import SvgParser
from src.generator.image_vector_generator import ImageVectorGenerator
from src.ir.vector_node import IrVectorGroup


class TestClipPath:
  """Test SVG clipPath element parsing and code generation."""

  def setup_method(self):
    self.parser = SvgParser()
    self.generator = ImageVectorGenerator()

  def test_basic_clippath_parsing(self):
    """Test basic clipPath element with rectangle."""
    svg_content = '''
    <svg viewBox="0 0 100 100">
      <defs>
        <clipPath id="myClip">
          <rect x="10" y="10" width="80" height="80"/>
        </clipPath>
      </defs>
      <g clip-path="url(#myClip)">
        <circle cx="50" cy="50" r="40" fill="red"/>
      </g>
    </svg>
    '''
    
    result = self.parser.parse_svg(svg_content)
    assert len(result.nodes) == 1
    
    group = result.nodes[0]
    assert isinstance(group, IrVectorGroup)
    assert len(group.clip_path_data) > 0
    assert len(group.children) == 1

  def test_clippath_with_multiple_shapes(self):
    """Test clipPath containing multiple shapes."""
    svg_content = '''
    <svg viewBox="0 0 100 100">
      <defs>
        <clipPath id="complexClip">
          <rect x="0" y="0" width="50" height="50"/>
          <circle cx="75" cy="75" r="20"/>
        </clipPath>
      </defs>
      <g clip-path="url(#complexClip)">
        <rect x="0" y="0" width="100" height="100" fill="blue"/>
      </g>
    </svg>
    '''
    
    result = self.parser.parse_svg(svg_content)
    group = result.nodes[0]
    
    assert isinstance(group, IrVectorGroup)
    # Should have path data from both rect and circle
    assert len(group.clip_path_data) > 5

  def test_clippath_with_path_element(self):
    """Test clipPath containing path element."""
    svg_content = '''
    <svg viewBox="0 0 100 100">
      <defs>
        <clipPath id="pathClip">
          <path d="M10,10 L90,10 L50,90 Z"/>
        </clipPath>
      </defs>
      <g clip-path="url(#pathClip)">
        <rect x="0" y="0" width="100" height="100" fill="green"/>
      </g>
    </svg>
    '''
    
    result = self.parser.parse_svg(svg_content)
    group = result.nodes[0]
    
    assert isinstance(group, IrVectorGroup)
    assert len(group.clip_path_data) == 4  # MoveTo, LineTo, LineTo, Close

  def test_nested_groups_with_clippath(self):
    """Test nested groups where parent has clipPath."""
    svg_content = '''
    <svg viewBox="0 0 100 100">
      <defs>
        <clipPath id="outerClip">
          <rect x="20" y="20" width="60" height="60"/>
        </clipPath>
      </defs>
      <g clip-path="url(#outerClip)">
        <g transform="rotate(45)">
          <rect x="0" y="0" width="100" height="100" fill="orange"/>
        </g>
      </g>
    </svg>
    '''
    
    result = self.parser.parse_svg(svg_content)
    outer_group = result.nodes[0]
    
    assert isinstance(outer_group, IrVectorGroup)
    assert len(outer_group.clip_path_data) > 0
    assert len(outer_group.children) == 1
    
    inner_group = outer_group.children[0]
    assert isinstance(inner_group, IrVectorGroup)
    assert inner_group.rotation == 45.0

  def test_missing_clippath_reference(self):
    """Test group with clip-path reference to non-existent clipPath."""
    svg_content = '''
    <svg viewBox="0 0 100 100">
      <g clip-path="url(#nonExistent)">
        <circle cx="50" cy="50" r="40" fill="red"/>
      </g>
    </svg>
    '''
    
    result = self.parser.parse_svg(svg_content)
    # Should parse without error, but no clip path data
    assert len(result.nodes) == 1

  def test_clippath_code_generation(self):
    """Test Kotlin code generation for clipPath."""
    svg_content = '''
    <svg viewBox="0 0 100 100">
      <defs>
        <clipPath id="testClip">
          <rect x="10" y="10" width="80" height="80"/>
        </clipPath>
      </defs>
      <g clip-path="url(#testClip)">
        <circle cx="50" cy="50" r="40" fill="red"/>
      </g>
    </svg>
    '''
    
    ir = self.parser.parse_svg(svg_content)
    code = self.generator.generate(ir)
    
    # Verify clipPathData is included in generated code
    assert "clipPathData = listOf(" in code
    assert "PathNode.MoveTo(10f, 10f)" in code
    assert "PathNode.LineTo(90f, 10f)" in code
    assert "PathNode.Close" in code

  def test_clippath_with_transforms(self):
    """Test clipPath combined with group transforms."""
    svg_content = '''
    <svg viewBox="0 0 100 100">
      <defs>
        <clipPath id="transformClip">
          <rect x="0" y="0" width="50" height="50"/>
        </clipPath>
      </defs>
      <g clip-path="url(#transformClip)" transform="translate(25,25) scale(2)">
        <rect x="0" y="0" width="25" height="25" fill="purple"/>
      </g>
    </svg>
    '''
    
    result = self.parser.parse_svg(svg_content)
    group = result.nodes[0]
    
    assert isinstance(group, IrVectorGroup)
    assert len(group.clip_path_data) > 0
    assert group.translation_x == 25.0
    assert group.translation_y == 25.0
    assert group.scale_x == 2.0
    assert group.scale_y == 2.0

  def test_clippath_import_generation(self):
    """Test that clipPath usage generates correct imports."""
    svg_content = '''
    <svg viewBox="0 0 100 100">
      <defs>
        <clipPath id="importTest">
          <circle cx="50" cy="50" r="40"/>
        </clipPath>
      </defs>
      <g clip-path="url(#importTest)">
        <rect x="0" y="0" width="100" height="100" fill="black"/>
      </g>
    </svg>
    '''
    
    ir = self.parser.parse_svg(svg_content)
    code, imports = self.generator.generate_core_code(ir)
    
    # Verify PathNode import is included
    assert "androidx.compose.ui.graphics.vector.PathNode" in imports

  def test_empty_clippath(self):
    """Test empty clipPath element."""
    svg_content = '''
    <svg viewBox="0 0 100 100">
      <defs>
        <clipPath id="emptyClip">
        </clipPath>
      </defs>
      <g clip-path="url(#emptyClip)">
        <rect x="0" y="0" width="100" height="100" fill="yellow"/>
      </g>
    </svg>
    '''
    
    result = self.parser.parse_svg(svg_content)
    group = result.nodes[0]
    
    assert isinstance(group, IrVectorGroup)
    # Empty clipPath should result in empty clip_path_data
    assert len(group.clip_path_data) == 0

  def test_clippath_with_ellipse(self):
    """Test clipPath containing ellipse element."""
    svg_content = '''
    <svg viewBox="0 0 100 100">
      <defs>
        <clipPath id="ellipseClip">
          <ellipse cx="50" cy="50" rx="40" ry="20"/>
        </clipPath>
      </defs>
      <g clip-path="url(#ellipseClip)">
        <rect x="0" y="0" width="100" height="100" fill="cyan"/>
      </g>
    </svg>
    '''
    
    result = self.parser.parse_svg(svg_content)
    group = result.nodes[0]
    
    assert isinstance(group, IrVectorGroup)
    assert len(group.clip_path_data) > 0
    # Ellipse should be converted to arc commands
    path_types = [type(node).__name__ for node in group.clip_path_data]
    assert any("Arc" in path_type for path_type in path_types)

  def test_clippath_flattening_behavior(self):
    """Test that groups are not flattened when they have clipPath."""
    svg_content = '''
    <svg viewBox="0 0 100 100">
      <defs>
        <clipPath id="noFlattenClip">
          <rect x="10" y="10" width="80" height="80"/>
        </clipPath>
      </defs>
      <g clip-path="url(#noFlattenClip)">
        <path d="M0,0 L100,100" stroke="black"/>
      </g>
    </svg>
    '''
    
    result = self.parser.parse_svg(svg_content)
    
    # Should create a group even with single child due to clipPath
    assert len(result.nodes) == 1
    assert isinstance(result.nodes[0], IrVectorGroup)
    assert len(result.nodes[0].clip_path_data) > 0

  def test_clippath_complete_output_simple_rect(self):
    """Test complete Kotlin output for simple rect clipPath (multiline format)."""
    svg_content = '''
    <svg viewBox="0 0 100 100">
      <defs>
        <clipPath id="rectClip">
          <rect x="20" y="20" width="60" height="60"/>
        </clipPath>
      </defs>
      <g clip-path="url(#rectClip)">
        <circle cx="50" cy="50" r="30" fill="blue"/>
      </g>
    </svg>
    '''
    
    ir = self.parser.parse_svg(svg_content)
    code = self.generator.generate(ir)
    
    expected_output = '''ImageVector.Builder(
  name = "UnnamedIcon",
  defaultWidth = 24f.dp,
  defaultHeight = 24f.dp,
  viewportWidth = 100f,
  viewportHeight = 100f,
).apply {
  group(
    name = "group",
    clipPathData = listOf(
      PathNode.MoveTo(20f, 20f),
      PathNode.LineTo(80f, 20f),
      PathNode.LineTo(80f, 80f),
      PathNode.LineTo(20f, 80f),
      PathNode.Close
    ),
  ) {
    path(
      fill = SolidColor(Color.Blue),
    ) {
      moveTo(20f, 50f)
      arcTo(30f, 30f, 0f, false, true, 50f, 20f)
      arcTo(30f, 30f, 0f, false, true, 80f, 50f)
      arcTo(30f, 30f, 0f, false, true, 50f, 80f)
      arcTo(30f, 30f, 0f, false, true, 20f, 50f)
      close()
    }
  }
}.build()'''
    
    assert code.strip() == expected_output.strip()

  def test_clippath_complete_output_single_line_format(self):
    """Test complete Kotlin output for simple clipPath (single line format)."""
    svg_content = '''
    <svg viewBox="0 0 100 100">
      <defs>
        <clipPath id="simpleClip">
          <path d="M0,0 L50,50 Z"/>
        </clipPath>
      </defs>
      <g clip-path="url(#simpleClip)">
        <rect x="0" y="0" width="100" height="100" fill="red"/>
      </g>
    </svg>
    '''
    
    ir = self.parser.parse_svg(svg_content)
    code = self.generator.generate(ir)
    
    expected_output = '''ImageVector.Builder(
  name = "UnnamedIcon",
  defaultWidth = 24f.dp,
  defaultHeight = 24f.dp,
  viewportWidth = 100f,
  viewportHeight = 100f,
).apply {
  group(
    name = "group",
    clipPathData = listOf(PathNode.MoveTo(0f, 0f), PathNode.LineTo(50f, 50f), PathNode.Close),
  ) {
    path(
      fill = SolidColor(Color.Red),
    ) {
      moveTo(0f, 0f)
      lineTo(100f, 0f)
      lineTo(100f, 100f)
      lineTo(0f, 100f)
      close()
    }
  }
}.build()'''
    
    assert code.strip() == expected_output.strip()

  def test_clippath_complete_output_multiline_format(self):
    """Test complete Kotlin output for complex clipPath with multiline format."""
    svg_content = '''
    <svg viewBox="0 0 200 200">
      <defs>
        <clipPath id="complexClip">
          <path d="M10,10 L190,10 L190,100 Q150,150 100,100 Q50,150 10,100 Z"/>
        </clipPath>
      </defs>
      <g clip-path="url(#complexClip)" transform="rotate(45)">
        <rect x="0" y="0" width="200" height="200" fill="red"/>
      </g>
    </svg>
    '''
    
    ir = self.parser.parse_svg(svg_content)
    code = self.generator.generate(ir)
    
    # Verify multiline clipPath format for complex paths
    assert "clipPathData = listOf(" in code
    assert "  PathNode.MoveTo(10f, 10f)," in code
    assert "  PathNode.LineTo(190f, 10f)," in code
    assert "  PathNode.QuadTo(" in code  # Q commands become PathNode.QuadTo in clipPath
    assert "  PathNode.Close" in code
    
    # Verify the listOf block is properly structured with correct opening and closing
    assert "clipPathData = listOf(" in code
    assert "    )," in code  # Verify the listOf is properly closed with correct indentation
    
    # Verify the complete structure by checking the sequence
    clippath_start = code.find("clipPathData = listOf(")
    clippath_end = code.find("    ),", clippath_start)
    assert clippath_end > clippath_start, "clipPathData listOf block is not properly closed"
    
    # Extract the clipPath section and verify it contains all expected elements
    clippath_section = code[clippath_start:clippath_end]
    assert "PathNode.MoveTo" in clippath_section
    assert "PathNode.LineTo" in clippath_section
    assert "PathNode.QuadTo" in clippath_section
    assert "PathNode.Close" in clippath_section
    
    # Verify rotation is preserved
    assert "rotate = 45f," in code

  def test_clippath_complete_output_with_transforms(self):
    """Test complete Kotlin output for clipPath with transform parameters."""
    svg_content = '''
    <svg viewBox="0 0 100 100">
      <defs>
        <clipPath id="transformClip">
          <circle cx="50" cy="50" r="40"/>
        </clipPath>
      </defs>
      <g clip-path="url(#transformClip)" transform="translate(10,20) scale(1.5)">
        <rect x="0" y="0" width="100" height="100" fill="green"/>
      </g>
    </svg>
    '''
    
    ir = self.parser.parse_svg(svg_content)
    code = self.generator.generate(ir)
    
    expected_patterns = [
      "group(",
      'name = "group",',
      "translationX = 10f,",
      "translationY = 20f,",
      "scaleX = 1.5f,",
      "scaleY = 1.5f,",
      "clipPathData = listOf(",
      "PathNode.MoveTo(10f, 50f)",
      "PathNode.ArcTo(",
      "PathNode.Close",
      ") {",
      "path(",
      "fill = SolidColor(Color(0xFF008000)),",  # Green is stored as hex, not named color
    ]
    
    for pattern in expected_patterns:
      assert pattern in code, f"Missing pattern: {pattern}"

  def test_clippath_complete_output_empty_clippath(self):
    """Test complete Kotlin output for empty clipPath reference."""
    svg_content = '''
    <svg viewBox="0 0 100 100">
      <defs>
        <clipPath id="emptyClip">
        </clipPath>
      </defs>
      <g clip-path="url(#emptyClip)">
        <rect x="10" y="10" width="80" height="80" fill="orange"/>
      </g>
    </svg>
    '''
    
    ir = self.parser.parse_svg(svg_content)
    code = self.generator.generate(ir)
    
    expected_output = '''ImageVector.Builder(
  name = "UnnamedIcon",
  defaultWidth = 24f.dp,
  defaultHeight = 24f.dp,
  viewportWidth = 100f,
  viewportHeight = 100f,
).apply {
  group(
    name = "group",
  ) {
    path(
      fill = SolidColor(Color(0xFFFFA500)),
    ) {
      moveTo(10f, 10f)
      lineTo(90f, 10f)
      lineTo(90f, 90f)
      lineTo(10f, 90f)
      close()
    }
  }
}.build()'''
    
    assert code.strip() == expected_output.strip()

  def test_clippath_complete_output_nested_groups(self):
    """Test complete Kotlin output for nested groups with clipPath."""
    svg_content = '''
    <svg viewBox="0 0 100 100">
      <defs>
        <clipPath id="outerClip">
          <rect x="10" y="10" width="80" height="80"/>
        </clipPath>
      </defs>
      <g clip-path="url(#outerClip)">
        <g transform="rotate(30)" id="innerGroup">
          <circle cx="50" cy="50" r="20" fill="purple"/>
        </g>
      </g>
    </svg>
    '''
    
    ir = self.parser.parse_svg(svg_content)
    code = self.generator.generate(ir)
    
    # Verify outer group with clipPath
    assert 'name = "group",' in code
    assert "clipPathData = listOf(" in code
    assert "PathNode.MoveTo(10f, 10f)" in code
    
    # Verify inner group with rotation
    assert 'name = "innerGroup",' in code
    assert "rotate = 30f," in code
    
    # Verify proper nesting structure
    lines = code.split('\n')
    group_indent_found = False
    inner_group_indent_found = False
    
    for line in lines:
      if 'name = "group",' in line:
        group_indent_found = True
        assert line.startswith('  ')  # First level indent
      if 'name = "innerGroup",' in line:
        inner_group_indent_found = True
        assert line.startswith('    ')  # Second level indent
    
    assert group_indent_found and inner_group_indent_found