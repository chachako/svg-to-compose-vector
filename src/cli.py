#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
import sys
from pathlib import Path
from typing import Optional

from .parser.svg_parser import SvgParser
from .generator.image_vector_generator import ImageVectorGenerator


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
  """SVG to Compose ImageVector converter.

  Convert SVG files to Kotlin Compose ImageVector code with template-based output.
  """
  if ctx.invoked_subcommand is None:
    click.echo(ctx.get_help())


@cli.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option(
  "--output",
  "-o",
  type=click.Path(path_type=Path),
  help="Output file path. If not specified, prints to stdout.",
)
@click.option(
  "--name", "-n", type=str, help="Name for the ImageVector. Defaults to input filename."
)
@click.option(
  "--wrapper-start",
  "-ws",
  type=str,
  default="",
  help='Code to insert before ImageVector.Builder. e.g., "val MyIcon: ImageVector = "',
)
@click.option(
  "--wrapper-end", "-we", type=str, default="", help='Code to insert after .build(). e.g., ""'
)
def convert(
  input_file: Path,
  output: Optional[Path],
  name: Optional[str],
  wrapper_start: str,
  wrapper_end: str,
):
  """Convert SVG file to Kotlin Compose ImageVector code.

  Examples:

    # Convert to stdout
    svg2compose convert icon.svg

    # Convert to file
    svg2compose convert icon.svg -o Icon.kt

    # With custom wrapper
    svg2compose convert icon.svg -ws "val HomeIcon: ImageVector = " -o HomeIcon.kt
  """
  try:
    # Read SVG file
    svg_content = input_file.read_text(encoding="utf-8")

    # Parse SVG
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    # Override name if provided
    if name:
      ir.name = name
    elif ir.name == "UnnamedIcon":
      # Use filename as default name if not specified in SVG
      ir.name = input_file.stem.replace("-", "_").replace(" ", "_")

    # Generate Kotlin code
    generator = ImageVectorGenerator()
    core_code = generator.generate(ir)

    # Apply wrapper
    final_code = wrapper_start + core_code + wrapper_end

    # Output result
    if output:
      output.write_text(final_code, encoding="utf-8")
      click.echo(f"Generated {output}")
    else:
      click.echo(final_code)

  except Exception as e:
    click.echo(f"Error: {e}", err=True)
    sys.exit(1)


@cli.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
def info(input_file: Path):
  """Show information about an SVG file.

  Display parsed structure, dimensions, and path details.
  """
  try:
    svg_content = input_file.read_text(encoding="utf-8")

    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    click.echo(f"File: {input_file}")
    click.echo(f"Dimensions: {ir.default_width}x{ir.default_height} dp")
    click.echo(f"Viewport: {ir.viewport_width}x{ir.viewport_height}")
    click.echo(f"Vector name: {ir.name}")
    click.echo(f"Auto-mirror: {ir.auto_mirror}")
    click.echo(f"Nodes: {len(ir.nodes)}")

    for i, node in enumerate(ir.nodes):
      if hasattr(node, "paths"):
        click.echo(f"  Path {i + 1}: {len(node.paths)} commands")
        if node.fill:
          click.echo(f"    Fill: {node.fill.to_compose_color()}")
        if node.stroke:
          click.echo(f"    Stroke: {node.stroke.to_compose_color()}")
      else:
        click.echo(f"  Group {i + 1}: {len(getattr(node, 'children', []))} children")

  except Exception as e:
    click.echo(f"Error: {e}", err=True)
    sys.exit(1)


@cli.command()
def version():
  """Show version information."""
  click.echo("SVG to Compose ImageVector Converter v0.1.0")
  click.echo("Built with modern Python and targeting Compose UI")


if __name__ == "__main__":
  cli()
