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
echo "  uv tool install dist/devsafe-*.whl"
echo ""
echo "To install from this checkout (editable):"
echo "  uv tool install --editable ."
echo ""
echo "To publish: push a vX.Y.Z tag (see RELEASING.md)"
