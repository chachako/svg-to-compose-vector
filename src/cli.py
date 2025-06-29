#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
import sys
from pathlib import Path
from typing import Optional

from .parser.svg_parser import SvgParser
from .generator.image_vector_generator import ImageVectorGenerator
from .generator.template_engine import TemplateEngine
from .core.config import Config
from .utils.naming import NameResolver


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
  "--template",
  "-t",
  type=str,
  help="Template to use. Built-in options: default, composable_function, icon_object, or path to custom template file.",
)
@click.option(
  "--config",
  "-c",
  type=click.Path(exists=True, path_type=Path),
  help="Path to configuration file.",
)
def convert(
  input_file: Path,
  output: Optional[Path],
  name: Optional[str],
  template: Optional[str],
  config: Optional[Path],
):
  """Convert SVG file to Kotlin Compose ImageVector code.

  Examples:

    # Convert to stdout
    svg2compose convert icon.svg

    # Convert to file
    svg2compose convert icon.svg -o Icon.kt

    # With template
    svg2compose convert icon.svg -t composable_function -o HomeIcon.kt

    # With custom template file
    svg2compose convert icon.svg -t my_template.j2 -o CustomIcon.kt
  """
  try:
    # Load configuration
    config_obj = Config()
    if config:
      config_obj = Config.from_file(config)

    # Handle custom template file
    if template and Path(template).exists():
      config_obj.template_path = Path(template)
      template_name = "default"  # Use default processing for custom files
    else:
      template_name = template or "default"

    # Read SVG file
    svg_content = input_file.read_text(encoding="utf-8")

    # Parse SVG
    parser = SvgParser()
    ir = parser.parse_svg(svg_content)

    # Resolve name components using new naming system
    name_resolver = NameResolver()
    name_components = name_resolver.resolve_name(input_file, name)

    # Set the IR name to the final name part for internal consistency
    ir.name = name_components.name_part_pascal

    # Generate Kotlin code
    generator = ImageVectorGenerator()
    core_code, imports = generator.generate_core_code(ir)

    # Apply template with flexible naming
    template_engine = TemplateEngine(config_obj)
    final_code = template_engine.render(
      template_name=template_name,
      build_code=core_code,
      imports=imports,
      name_components=name_components,
    )

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

    # Use name resolver for consistent naming
    name_resolver = NameResolver()
    name_components = name_resolver.resolve_name(input_file)

    click.echo(f"File: {input_file}")
    click.echo(f"Dimensions: {ir.default_width}x{ir.default_height} dp")
    click.echo(f"Viewport: {ir.viewport_width}x{ir.viewport_height}")
    click.echo(f"Vector name: {name_components.name_part_pascal}")
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
def templates():
  """List available built-in templates."""
  try:
    template_engine = TemplateEngine(Config())
    available_templates = template_engine.list_available_templates()
    
    click.echo("Available built-in templates:")
    for template_name in available_templates:
      click.echo(f"  - {template_name}")
    
    if not available_templates:
      click.echo("No templates found. Please check installation.")
      
  except Exception as e:
    click.echo(f"Error listing templates: {e}", err=True)


@cli.command()
def version():
  """Show version information."""
  click.echo("SVG to Compose ImageVector Converter v0.1.0")
  click.echo("Built with modern Python and targeting Compose UI")


if __name__ == "__main__":
  cli()
