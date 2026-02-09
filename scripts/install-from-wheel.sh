#!/bin/bash
# Install DevSafe from wheel file

set -e

WHEEL_FILE=""

# Check if wheel file is provided
if [ $# -eq 0 ]; then
    echo "❌ Please provide a wheel file path"
    echo "Usage: $0 <path-to-wheel-file>"
    exit 1
fi

WHEEL_FILE="$1"

# Check if wheel file exists
if [ ! -f "$WHEEL_FILE" ]; then
    echo "❌ Wheel file not found: $WHEEL_FILE"
    exit 1
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install uv first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "🚀 Installing DevSafe from wheel: $WHEEL_FILE"

# Install from wheel
uv pip install "$WHEEL_FILE"

echo "✅ DevSafe installed successfully!"
echo ""
echo "You can now use:"
echo "  devsafe --help"
echo "  devsafe add work --name 'Your Name' --email 'your@email.com'"
echo "  devsafe switch work"
