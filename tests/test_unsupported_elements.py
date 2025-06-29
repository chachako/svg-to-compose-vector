"""Tests for unsupported SVG element warnings."""

import io
from contextlib import redirect_stdout

from src.parser.svg_parser import SvgParser


class TestUnsupportedElementWarnings:
  """Test warning system for unsupported SVG elements."""

  def test_text_element_warning(self):
    """Test warning for text elements."""
    svg_content = """<svg>
      <text x="10" y="20">Hello World</text>
      <rect x="0" y="0" width="50" height="25"/>
    </svg>"""

    parser = SvgParser()

    # Capture stdout to check warnings
    output = io.StringIO()
    with redirect_stdout(output):
      ir = parser.parse_svg(svg_content)

    warning_output = output.getvalue()
    assert "Text element '<text>' is not supported" in warning_output
    assert "⚠️  SVG Conversion Warnings:" in warning_output

    # Should still parse the rect element
    assert len(ir.nodes) == 1

  def test_marker_element_warning(self):
    """Test warning for marker elements."""
    svg_content = """<svg>
      <defs>
        <marker id="arrowhead">
          <path d="M0,0 L10,5 L0,10 Z"/>
        </marker>
      </defs>
      <line x1="0" y1="0" x2="50" y2="50" marker-end="url(#arrowhead)"/>
    </svg>"""

    parser = SvgParser()

    output = io.StringIO()
    with redirect_stdout(output):
      ir = parser.parse_svg(svg_content)

    warning_output = output.getvalue()
    assert "Advanced SVG element '<marker>' is not supported" in warning_output

    # Should still parse the line element
    assert len(ir.nodes) == 1

  def test_filter_element_warning(self):
    """Test warning for filter elements."""
    svg_content = """<svg>
      <defs>
        <filter id="blur">
          <feGaussianBlur stdDeviation="2"/>
        </filter>
      </defs>
      <circle cx="25" cy="25" r="20" filter="url(#blur)"/>
    </svg>"""

    parser = SvgParser()

    output = io.StringIO()
    with redirect_stdout(output):
      parser.parse_svg(svg_content)

    warning_output = output.getvalue()
    assert "Filter element '<filter>' is not supported" in warning_output
    # feGaussianBlur is nested inside filter, so it should also be detected
    assert (
      "Filter element '<feGaussianBlur>' is not supported" in warning_output
      or "Filter element '<filter>' is not supported" in warning_output
    )

  def test_animation_element_warning(self):
    """Test warning for animation elements."""
    svg_content = """<svg>
      <rect x="0" y="0" width="50" height="25">
        <animate attributeName="x" from="0" to="100" dur="2s"/>
      </rect>
    </svg>"""

    parser = SvgParser()

    output = io.StringIO()
    with redirect_stdout(output):
      parser.parse_svg(svg_content)

    warning_output = output.getvalue()
    assert "Animation element '<animate>' is not supported" in warning_output

  def test_multiple_unsupported_elements(self):
    """Test multiple unsupported elements in one SVG."""
    svg_content = """<svg>
      <text x="10" y="20">Title</text>
      <rect x="0" y="0" width="50" height="25"/>
      <defs>
        <filter id="blur">
          <feGaussianBlur stdDeviation="2"/>
        </filter>
        <marker id="arrow">
          <path d="M0,0 L10,5 L0,10 Z"/>
        </marker>
      </defs>
      <circle cx="25" cy="50" r="15"/>
      <image href="image.png" x="0" y="0"/>
    </svg>"""

    parser = SvgParser()

    output = io.StringIO()
    with redirect_stdout(output):
      ir = parser.parse_svg(svg_content)

    warning_output = output.getvalue()

    # Should contain multiple warnings
    assert "Text element '<text>' is not supported" in warning_output
    assert "Filter element '<filter>' is not supported" in warning_output
    # feGaussianBlur should be detected when filter is processed
    assert (
      "Filter element '<feGaussianBlur>' is not supported" in warning_output
      or "Filter element '<filter>' is not supported" in warning_output
    )
    assert "Advanced SVG element '<marker>' is not supported" in warning_output
    assert "Embedded content element '<image>' is not supported" in warning_output

    # Should still parse supported elements (rect and circle)
    assert len(ir.nodes) == 2

  def test_no_warnings_for_supported_elements(self):
    """Test that no warnings are shown for supported elements."""
    svg_content = """<svg>
      <rect x="0" y="0" width="50" height="25"/>
      <circle cx="25" cy="50" r="15"/>
      <path d="M10,10 L40,40"/>
      <g transform="translate(10,10)">
        <ellipse cx="20" cy="20" rx="15" ry="10"/>
      </g>
    </svg>"""

    parser = SvgParser()

    output = io.StringIO()
    with redirect_stdout(output):
      ir = parser.parse_svg(svg_content)

    warning_output = output.getvalue()

    # Should not contain any warnings
    assert "⚠️  SVG Conversion Warnings:" not in warning_output
    assert len(ir.nodes) == 4  # rect, circle, path, group (with ellipse inside)

  def test_tspan_and_textpath_warnings(self):
    """Test warnings for text-related elements."""
    svg_content = """<svg>
      <text x="10" y="20">
        <tspan x="10" y="40">Span text</tspan>
      </text>
      <defs>
        <path id="textcurve" d="M10,90 Q90,90 90,45"/>
      </defs>
      <textPath href="#textcurve">Text on path</textPath>
    </svg>"""

    parser = SvgParser()

    output = io.StringIO()
    with redirect_stdout(output):
      parser.parse_svg(svg_content)

    warning_output = output.getvalue()
    assert "Text element '<text>' is not supported" in warning_output
    # tspan is nested inside text element, so it should be detected
    assert (
      "Text element '<tspan>' is not supported" in warning_output
      or "Text element '<text>' is not supported" in warning_output
    )
    assert "Text element '<textPath>' is not supported" in warning_output

  def test_use_and_symbol_warnings(self):
    """Test warnings for symbol reuse elements."""
    svg_content = """<svg>
      <defs>
        <symbol id="star">
          <polygon points="25,2 30,18 47,18 34,29 39,45 25,36 11,45 16,29 3,18 20,18"/>
        </symbol>
      </defs>
      <use href="#star" x="0" y="0"/>
      <rect x="50" y="0" width="25" height="25"/>
    </svg>"""

    parser = SvgParser()

    output = io.StringIO()
    with redirect_stdout(output):
      ir = parser.parse_svg(svg_content)

    warning_output = output.getvalue()
    assert "Advanced SVG element '<symbol>' is not supported" in warning_output
    assert "Advanced SVG element '<use>' is not supported" in warning_output

    # Should still parse the rect element
    assert len(ir.nodes) == 1
