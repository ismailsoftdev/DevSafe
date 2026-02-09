#!/bin/bash
# Build script for DevSafe distribution

set -e

echo "🔨 Building DevSafe for distribution..."

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info/

# Build the package
echo "📦 Building package..."
uv build

echo "✅ Build complete! Distribution files created in dist/"
echo ""
echo "To install locally:"
echo "  uv pip install dist/devsafe-*.whl"
echo ""
echo "To install in development mode:"
echo "  uv pip install -e ."
echo ""
echo "To publish to PyPI (when ready):"
echo "  uv publish"
