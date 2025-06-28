#!/usr/bin/env python3

"""
Demonstration of the enhanced template system for SVG to Compose converter.
Shows various output formats using different templates.
"""

import subprocess
import sys
from pathlib import Path

# Add src to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

def run_conversion(template, output_file, description):
  """Run conversion with specified template and save to file."""
  print(f"\n=== {description} ===")
  
  cmd = [
    "uv", "run", "python", "-m", "src.cli", "convert",
    "examples/svg/test_icon.svg",
    "-t", template,
    "-o", f"examples/output/{output_file}"
  ]
  
  result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_root)
  
  if result.returncode == 0:
    print(f"✅ Generated {output_file}")
    # Show first few lines of output
    output_path = project_root / "examples" / "output" / output_file
    if output_path.exists():
      content = output_path.read_text()
      lines = content.split('\n')[:10]
      print("\nFirst 10 lines:")
      for i, line in enumerate(lines, 1):
        print(f"{i:2}: {line}")
      if len(content.split('\n')) > 10:
        print("    ...")
  else:
    print(f"❌ Error: {result.stderr}")

def main():
  """Demonstrate all template features."""
  
  print("🎨 SVG to Compose Template System Demo")
  print("=" * 50)
  
  # Ensure output directory exists
  output_dir = project_root / "examples" / "output"
  output_dir.mkdir(exist_ok=True)
  
  # 1. Default template (basic ImageVector)
  run_conversion("default", "basic_imagevector.kt", "Basic ImageVector (Default Template)")
  
  # 2. Composable function template
  run_conversion("composable_function", "composable_icon.kt", "Composable Function Template")
  
  # 3. Icon object template
  run_conversion("icon_object", "icon_object.kt", "Icon Object Template")
  
  # 4. Val declaration template
  run_conversion("val_declaration", "val_declaration.kt", "Val Declaration Template")
  
  # 5. Custom template
  custom_template_path = project_root / "simple_custom.j2"
  if custom_template_path.exists():
    run_conversion(str(custom_template_path), "custom_template.kt", "Custom Template File")
  
  print(f"\n✨ Demo complete! Check examples/output/ for all generated files.")

if __name__ == "__main__":
  main()