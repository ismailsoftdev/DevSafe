# DevSafe Installation Guide

## 🚀 Quick Start

### Prerequisites

- Python 3.8.1 or higher
- `uv` package manager (recommended)

### Install uv (if not already installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 📦 Installation Methods

### Method 1: Development Installation (Recommended for contributors)

```bash
# Clone the repository
git clone https://github.com/ismailsoftdev/DevSafe.git
cd DevSafe

# Install in development mode
uv pip install -e .

# Verify installation
uv run devsafe --version
```

### Method 2: Install from Wheel File

```bash
# Download the wheel file from releases
uv pip install devsafe-0.1.0-py3-none-any.whl

# Verify installation
uv run devsafe --version
```

### Method 3: Install from Source

```bash
# Clone and install
git clone https://github.com/ismailsoftdev/DevSafe.git
cd DevSafe
uv pip install .
```

## ✅ Verify Installation

After installation, verify everything works:

```bash
# Check version
uv run devsafe --version

# Check status
uv run devsafe status

# Get help
uv run devsafe --help
```

## 🎯 First Steps

1. **Add your first profile**:

   ```bash
   uv run devsafe add work --name "Your Name" --email "your@work.com"
   ```

2. **Switch to the profile**:

   ```bash
   uv run devsafe switch work
   ```

3. **Initialize in a git repository**:

   ```bash
   cd your-git-repo
   uv run devsafe init
   ```

## 🔧 Troubleshooting

### Command not found

If `devsafe` command is not found, use `uv run devsafe` instead, or ensure your PATH includes the uv bin directory.

### Permission errors

Make sure you have write permissions to your home directory for the config file.

### Git not found

Ensure Git is installed and accessible from your terminal.

## 📚 Next Steps

- Read the main [README.md](README.md) for detailed usage
- Check [DISTRIBUTION.md](DISTRIBUTION.md) for development setup
- Open an issue if you encounter problems
