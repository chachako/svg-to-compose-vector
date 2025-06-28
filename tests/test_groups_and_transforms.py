import pytest
from src.parser.svg_parser import SvgParser
from src.parser.transform_parser import TransformParser
from src.generator.image_vector_generator import ImageVectorGenerator
from src.ir.vector_node import IrVectorGroup


class TestTransformParser:
  """Test SVG transform parsing."""

  def setup_method(self):
    self.parser = TransformParser()

  def test_translate_transform(self):
    """Test translate transform parsing."""
    result = self.parser.parse_transform("translate(10, 20)")
    
    assert result.translation_x == 10.0
    assert result.translation_y == 20.0
    assert result.scale_x == 1.0
    assert result.scale_y == 1.0
    assert result.rotation == 0.0

  def test_translate_single_parameter(self):
    """Test translate with single parameter."""
    result = self.parser.parse_transform("translate(15)")
    
    assert result.translation_x == 15.0
    assert result.translation_y == 0.0

  def test_scale_transform(self):
    """Test scale transform parsing."""
    result = self.parser.parse_transform("scale(2, 0.5)")
    
    assert result.scale_x == 2.0
    assert result.scale_y == 0.5
    assert result.translation_x == 0.0
    assert result.translation_y == 0.0

  def test_scale_uniform(self):
    """Test uniform scale transform."""
    result = self.parser.parse_transform("scale(1.5)")
    
    assert result.scale_x == 1.5
    assert result.scale_y == 1.5

  def test_rotate_transform(self):
    """Test rotate transform parsing."""
    result = self.parser.parse_transform("rotate(45)")
    
    assert result.rotation == pytest.approx(45.0, abs=1e-6)
    assert result.scale_x == pytest.approx(1.0, abs=1e-6)
    assert result.scale_y == pytest.approx(1.0, abs=1e-6)

  def test_rotate_with_center(self):
    """Test rotate transform with center point."""
    result = self.parser.parse_transform("rotate(90, 10, 20)")
    
    assert result.rotation == 90.0
    # Translation should account for rotation center
    assert result.translation_x != 0.0
    assert result.translation_y != 0.0

  def test_combined_transforms(self):
    """Test combined transform operations."""
    result = self.parser.parse_transform("translate(10, 5) scale(2) rotate(45)")
    
    # All transforms should be applied
    assert result.translation_x != 0.0
    assert result.translation_y != 0.0
    assert result.scale_x != 1.0
    assert result.rotation != 0.0

  def test_matrix_transform(self):
    """Test matrix transform parsing."""
    # Identity matrix
    result = self.parser.parse_transform("matrix(1, 0, 0, 1, 10, 20)")
    
    assert result.translation_x == 10.0
    assert result.translation_y == 20.0
    assert result.scale_x == pytest.approx(1.0, abs=1e-6)
    assert result.scale_y == pytest.approx(1.0, abs=1e-6)

  def test_parse_transform_to_group_params(self):
    """Test convenience method for group parameters."""
    params = self.parser.parse_transform_to_group_params("translate(10, 20) scale(2)")
    
    assert "translation_x" in params
    assert "translation_y" in params
    assert "scale_x" in params
    assert "scale_y" in params
    
    assert params["translation_x"] == 10.0
    assert params["translation_y"] == 20.0

  def test_empty_transform(self):
    """Test empty transform string."""
    result = self.parser.parse_transform("")
    
    assert result.translation_x == 0.0
    assert result.translation_y == 0.0
    assert result.scale_x == 1.0
    assert result.scale_y == 1.0
    assert result.rotation == 0.0

  def test_invalid_transform(self):
    """Test invalid transform function."""
    result = self.parser.parse_transform("invalid(10, 20)")
    
    # Should return identity transform
    assert result.translation_x == 0.0
    assert result.translation_y == 0.0
    assert result.scale_x == 1.0
    assert result.scale_y == 1.0


class TestGroupParsing:
  """Test SVG group element parsing."""

  def setup_method(self):
    self.parser = SvgParser()

  def test_simple_group(self):
    """Test basic group parsing without transforms."""
    svg_content = '''
    <svg viewBox="0 0 24 24">
      <g id="test-group">
        <path d="M 0 0 L 10 10" fill="red"/>
        <path d="M 5 5 L 15 15" fill="blue"/>
      </g>
    </svg>
    '''
    
    result = self.parser.parse_svg(svg_content)
    
    assert len(result.nodes) == 1
    assert isinstance(result.nodes[0], IrVectorGroup)
    group = result.nodes[0]
    assert group.name == "test-group"
    assert len(group.children) == 2

  def test_group_with_translate(self):
    """Test group with translate transform."""
    svg_content = '''
    <svg viewBox="0 0 24 24">
      <g transform="translate(10, 20)">
        <path d="M 0 0 L 10 10" fill="red"/>
      </g>
    </svg>
    '''
    
    result = self.parser.parse_svg(svg_content)
    
    assert len(result.nodes) == 1
    group = result.nodes[0]
    assert isinstance(group, IrVectorGroup)
    assert group.translation_x == 10.0
    assert group.translation_y == 20.0

  def test_group_with_scale(self):
    """Test group with scale transform."""
    svg_content = '''
    <svg viewBox="0 0 24 24">
      <g transform="scale(2, 0.5)">
        <path d="M 0 0 L 10 10" fill="red"/>
      </g>
    </svg>
    '''
    
    result = self.parser.parse_svg(svg_content)
    
    group = result.nodes[0]
    assert group.scale_x == 2.0
    assert group.scale_y == 0.5

  def test_group_with_rotation(self):
    """Test group with rotation transform."""
    svg_content = '''
    <svg viewBox="0 0 24 24">
      <g transform="rotate(45)">
        <path d="M 0 0 L 10 10" fill="red"/>
      </g>
    </svg>
    '''
    
    result = self.parser.parse_svg(svg_content)
    
    group = result.nodes[0]
    assert group.rotation == pytest.approx(45.0, abs=1e-6)

  def test_nested_groups(self):
    """Test nested group structures."""
    svg_content = '''
    <svg viewBox="0 0 24 24">
      <g id="outer" transform="translate(5, 5)">
        <g id="inner" transform="scale(2)">
          <path d="M 0 0 L 10 10" fill="red"/>
        </g>
      </g>
    </svg>
    '''
    
    result = self.parser.parse_svg(svg_content)
    
    assert len(result.nodes) == 1
    outer_group = result.nodes[0]
    assert outer_group.name == "outer"
    assert outer_group.translation_x == 5.0
    
    assert len(outer_group.children) == 1
    inner_group = outer_group.children[0]
    assert isinstance(inner_group, IrVectorGroup)
    assert inner_group.name == "inner"
    assert inner_group.scale_x == 2.0

  def test_group_flattening(self):
    """Test that groups without transforms and single child get flattened."""
    svg_content = '''
    <svg viewBox="0 0 24 24">
      <g>
        <path d="M 0 0 L 10 10" fill="red"/>
      </g>
    </svg>
    '''
    
    result = self.parser.parse_svg(svg_content)
    
    # Group should be flattened since it has no transform and single child
    assert len(result.nodes) == 1
    # First node should be the path directly
    from src.ir.vector_node import IrVectorPath
    assert isinstance(result.nodes[0], IrVectorPath)

  def test_empty_group(self):
    """Test empty group handling."""
    svg_content = '''
    <svg viewBox="0 0 24 24">
      <g transform="translate(10, 10)">
      </g>
    </svg>
    '''
    
    result = self.parser.parse_svg(svg_content)
    
    # Empty groups should not be included
    assert len(result.nodes) == 0


class TestGroupCodeGeneration:
  """Test Kotlin code generation for groups."""

  def setup_method(self):
    self.generator = ImageVectorGenerator()

  def test_group_with_transforms_code_generation(self):
    """Test code generation for group with transforms."""
    from src.ir.image_vector import IrImageVector
    from src.ir.vector_node import IrVectorGroup, IrVectorPath
    from src.ir.path_node import IrMoveTo, IrLineTo
    from src.ir.color import IrColor

    path = IrVectorPath(
      paths=[IrMoveTo(0.0, 0.0), IrLineTo(10.0, 10.0)],
      fill=IrColor.from_hex("#ff0000")
    )
    
    group = IrVectorGroup(
      children=[path],
      translation_x=10.0,
      translation_y=20.0,
      scale_x=2.0,
      rotation=45.0
    )
    
    image_vector = IrImageVector(
      name="TestIcon",
      default_width=24.0,
      default_height=24.0,
      viewport_width=24.0,
      viewport_height=24.0,
      nodes=[group]
    )
    
    code = self.generator.generate(image_vector)
    
    # Check that group code is generated
    assert "group(" in code
    assert "translationX = 10f," in code
    assert "translationY = 20f," in code
    assert "scaleX = 2f," in code
    assert "rotate = 45f," in code

  def test_simple_group_code_generation(self):
    """Test code generation for group without transforms."""
    from src.ir.image_vector import IrImageVector
    from src.ir.vector_node import IrVectorGroup, IrVectorPath
    from src.ir.path_node import IrMoveTo, IrLineTo
    from src.ir.color import IrColor

    path1 = IrVectorPath(
      paths=[IrMoveTo(0.0, 0.0), IrLineTo(10.0, 10.0)],
      fill=IrColor.from_hex("#ff0000")
    )
    
    path2 = IrVectorPath(
      paths=[IrMoveTo(5.0, 5.0), IrLineTo(15.0, 15.0)],
      fill=IrColor.from_hex("#0000ff")
    )
    
    group = IrVectorGroup(children=[path1, path2])
    
    image_vector = IrImageVector(
      name="TestIcon",
      default_width=24.0,
      default_height=24.0,
      viewport_width=24.0,
      viewport_height=24.0,
      nodes=[group]
    )
    
    code = self.generator.generate(image_vector)
    
    # Check that simple group code is generated
    assert "group {" in code
    assert "group(" not in code  # No parameters
    assert "moveTo(0f, 0f)" in code
    assert "moveTo(5f, 5f)" in code


class TestEndToEndGroupsAndTransforms:
  """End-to-end tests for groups and transforms."""

  def setup_method(self):
    self.parser = SvgParser()
    self.generator = ImageVectorGenerator()

  def test_complete_svg_to_kotlin_with_groups(self):
    """Test complete SVG to Kotlin conversion with groups and transforms."""
    svg_content = '''
    <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <g id="icon-base" transform="translate(2, 2)">
        <g id="background" transform="scale(0.8)">
          <path d="M 0 0 L 20 0 L 20 20 L 0 20 Z" fill="#e0e0e0"/>
        </g>
        <g id="foreground" transform="translate(5, 5) rotate(45)">
          <path d="M 0 0 L 10 0 L 10 10 L 0 10 Z" fill="#2196f3"/>
        </g>
      </g>
    </svg>
    '''
    
    # Parse SVG
    ir = self.parser.parse_svg(svg_content)
    
    # Generate Kotlin code
    kotlin_code = self.generator.generate(ir)
    
    # Verify structure
    assert "group(" in kotlin_code
    assert "translationX" in kotlin_code
    assert "translationY" in kotlin_code
    assert "scaleX" in kotlin_code or "scaleY" in kotlin_code
    assert "rotate" in kotlin_code
    
    # Verify nested structure
    lines = kotlin_code.split('\n')
    group_lines = [line for line in lines if 'group' in line]
    assert len(group_lines) >= 3  # At least 3 group declarations
    
    print("Generated Kotlin code:")
    print(kotlin_code)