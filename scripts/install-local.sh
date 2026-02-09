#!/bin/bash
# Local installation script for DevSafe

set -e

echo "🚀 Installing DevSafe locally..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install uv first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Install in development mode
echo "📦 Installing DevSafe in development mode..."
uv pip install -e .

echo "✅ DevSafe installed successfully!"
echo ""
echo "You can now use:"
echo "  devsafe --help"
echo "  devsafe add work --name 'Your Name' --email 'your@email.com'"
echo "  devsafe switch work"
