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


@cli.command()
@click.argument("input_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option(
  "--output",
  "-o", 
  type=click.Path(path_type=Path),
  help="Output directory. Defaults to current directory.",
)
@click.option(
  "--template",
  "-t",
  type=str,
  default="val_declaration",
  help="Template to use for each file. Defaults to 'val_declaration'.",
)
@click.option(
  "--namespace-dirs/--no-namespace-dirs",
  "--ns",
  default=True,
  help="Create namespace subdirectories (default: enabled).",
)
@click.option(
  "--overwrite",
  is_flag=True,
  help="Overwrite existing files without asking.",
)
@click.option(
  "--config",
  "-c",
  type=click.Path(exists=True, path_type=Path),
  help="Path to configuration file.",
)
@click.option(
  "--dry-run",
  is_flag=True,
  help="Show what would be generated without creating files.",
)
def batch(
  input_dir: Path,
  output: Optional[Path],
  template: str,
  namespace_dirs: bool,
  overwrite: bool,
  config: Optional[Path],
  dry_run: bool,
):
  """Convert all SVG files in a directory to Kotlin ImageVector files.
  
  This command processes all .svg files in the input directory and generates
  corresponding .kt files with ImageVector definitions. Files are organized
  by namespace when using hierarchical naming (e.g., 'media.play24.svg').

  Examples:

    # Convert all SVGs in icons/ to current directory  
    svg2compose batch icons/

    # Convert with namespace subdirectories to output/
    svg2compose batch icons/ -o output/ --ns

    # Preview what would be generated
    svg2compose batch icons/ --dry-run

    # Use custom template
    svg2compose batch icons/ -t composable_function
  """
  try:
    # Setup
    output_dir = output or Path.cwd()
    output_dir = output_dir.resolve()
    
    # Load configuration
    config_obj = Config()
    if config:
      config_obj = Config.from_file(config)

    # Handle custom template file
    if template and Path(template).exists():
      config_obj.template_path = Path(template)
      template_name = "default"
    else:
      template_name = template

    # Find all SVG files
    svg_files = list(input_dir.glob("*.svg"))
    if not svg_files:
      click.echo(f"No SVG files found in {input_dir}")
      return

    click.echo(f"Found {len(svg_files)} SVG files in {input_dir}")
    
    # Process each file
    parser = SvgParser()
    generator = ImageVectorGenerator()
    template_engine = TemplateEngine(config_obj)
    name_resolver = NameResolver()
    
    processed_files = []
    skipped_files = []
    errors = []

    for svg_file in svg_files:
      try:
        # Parse name components
        name_components = name_resolver.resolve_name(svg_file)
        
        # Determine output path
        if namespace_dirs and name_components.namespace_path_components_lowercase:
          # Create nested namespace subdirectories (lowercase)
          namespace_dir = output_dir / name_components.namespace_nested_path_lowercase
          kt_file = namespace_dir / f"{name_components.name_part_pascal}.kt"
        else:
          # Place in root output directory
          kt_file = output_dir / f"{name_components.name_part_pascal}.kt"
        
        # Check if file exists and handle overwrite
        if kt_file.exists() and not overwrite and not dry_run:
          choice = click.confirm(f"File {kt_file} exists. Overwrite?")
          if not choice:
            skipped_files.append((svg_file, kt_file, "User skipped"))
            continue
        
        if dry_run:
          processed_files.append((svg_file, kt_file, "Would create"))
          continue
        
        # Read and parse SVG
        svg_content = svg_file.read_text(encoding="utf-8")
        ir = parser.parse_svg(svg_content)
        ir.name = name_components.name_part_pascal
        
        # Generate code
        core_code, imports = generator.generate_core_code(ir)
        final_code = template_engine.render(
          template_name=template_name,
          build_code=core_code,
          imports=imports,
          name_components=name_components,
        )
        
        # Create directory and write file
        kt_file.parent.mkdir(parents=True, exist_ok=True)
        kt_file.write_text(final_code, encoding="utf-8")
        
        processed_files.append((svg_file, kt_file, "Created"))
        
      except Exception as e:
        errors.append((svg_file, str(e)))
        continue

    # Report results
    click.echo(f"\n{'DRY RUN - ' if dry_run else ''}Batch conversion complete!")
    click.echo(f"✅ Successfully processed: {len(processed_files)}")
    
    if processed_files:
      click.echo("\nGenerated files:")
      for svg_file, kt_file, status in processed_files:
        namespace_info = ""
        name_components = name_resolver.resolve_name(svg_file)
        if name_components.namespace_path_components_lowercase:
          namespace_info = f" (namespace: {name_components.namespace_part_pascal})"
        click.echo(f"  {status}: {kt_file.relative_to(output_dir)}{namespace_info}")
    
    if skipped_files:
      click.echo(f"\n⚠️  Skipped: {len(skipped_files)}")
      for svg_file, kt_file, reason in skipped_files:
        click.echo(f"  {kt_file.relative_to(output_dir)}: {reason}")
    
    if errors:
      click.echo(f"\n❌ Errors: {len(errors)}")
      for svg_file, error in errors:
        click.echo(f"  {svg_file.name}: {error}")
      sys.exit(1)
        
  except Exception as e:
    click.echo(f"Error during batch conversion: {e}", err=True)
    sys.exit(1)


if __name__ == "__main__":
  cli()
