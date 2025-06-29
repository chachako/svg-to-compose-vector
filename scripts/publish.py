#!/usr/bin/env python3
"""
Publishing script for svg-to-compose-vector
"""
import subprocess
import sys
from pathlib import Path


def run_command(cmd: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result

def main():
    """Main publishing workflow."""
    print("🚀 Starting publication process for svg-to-compose-vector")

    # Ensure we're in the project root
    project_root = Path(__file__).parent.parent
    if not (project_root / "pyproject.toml").exists():
        print("❌ Error: pyproject.toml not found. Are you in the project root?")
        sys.exit(1)

    print("\n📋 Step 1: Running tests")
    try:
        run_command("uv run pytest")
        print("✅ All tests passed!")
    except subprocess.CalledProcessError:
        print("❌ Tests failed. Please fix issues before publishing.")
        sys.exit(1)

    print("\n🧹 Step 2: Running linting")
    try:
        run_command("uv run ruff check src/ tests/")
        run_command("uv run ruff format --check src/ tests/")
        print("✅ Code quality checks passed!")
    except subprocess.CalledProcessError:
        print("❌ Code quality issues found. Please fix before publishing.")
        sys.exit(1)

    print("\n��️  Step 3: Building package")
    try:
        run_command("rm -rf dist/")
        run_command("uv build")
        print("✅ Package built successfully!")
    except subprocess.CalledProcessError:
        print("❌ Package build failed.")
        sys.exit(1)

    print("\n📦 Step 4: Checking package")
    try:
        run_command("uv run twine check dist/*")
        print("✅ Package check passed!")
    except subprocess.CalledProcessError:
        print("❌ Package check failed.")
        sys.exit(1)

    # Ask for confirmation before uploading
    print("\n🔍 Package contents:")
    run_command("ls -la dist/")

    upload_choice = input("\n❓ Upload to PyPI? (test/prod/no): ").lower().strip()

    if upload_choice == "test":
        print("\n🧪 Uploading to Test PyPI")
        try:
            run_command("uv run twine upload --repository testpypi dist/*")
            print("✅ Successfully uploaded to Test PyPI!")
            print("   Install with: pip install --index-url https://test.pypi.org/simple/ svg-to-compose-vector")
        except subprocess.CalledProcessError:
            print("❌ Upload to Test PyPI failed.")
            sys.exit(1)

    elif upload_choice == "prod":
        print("\n🌟 Uploading to Production PyPI")
        try:
            run_command("uv run twine upload dist/*")
            print("✅ Successfully uploaded to PyPI!")
            print("   Install with: pip install svg-to-compose-vector")
        except subprocess.CalledProcessError:
            print("❌ Upload to PyPI failed.")
            sys.exit(1)

    else:
        print("📦 Package built and ready in dist/")
        print("   To upload manually:")
        print("   - Test PyPI: uv run twine upload --repository testpypi dist/*")
        print("   - Production: uv run twine upload dist/*")

    print("\n🎉 Publication process completed!")

if __name__ == "__main__":
    main()
