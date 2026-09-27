# DevSafe Installation Guide

## 🚀 Quick Start

### Prerequisites

- Git
- [`uv`](https://docs.astral.sh/uv/) (recommended), or pipx with Python 3.10+

### Install uv (if not already installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

uv downloads a suitable Python automatically, so you don't need one installed.

## 📦 Installation Methods

### Method 1: uv (Recommended)

```bash
uv tool install devsafe

# Verify installation
devsafe --version

# Upgrade later
uv tool upgrade devsafe
```

### Method 2: pipx

```bash
pipx install devsafe
devsafe --version
```

### Method 3: Try without installing

```bash
uvx devsafe --help
```

### Method 4: From source

```bash
git clone https://github.com/ismailsoftdev/DevSafe.git
cd DevSafe

# Install the devsafe command from this checkout
uv tool install --editable .
```

### Method 5: From a wheel file

```bash
uv tool install devsafe-0.1.0-py3-none-any.whl
```

## ✅ Verify Installation

After installation, verify everything works:

```bash
# Check version
devsafe --version

# Check status
devsafe status

# Get help
devsafe --help
```

## 🎯 First Steps

1. **Add your first profile**:

   ```bash
   devsafe add work --name "Your Name" --email "your@work.com"
   ```

2. **Switch to the profile**:

   ```bash
   devsafe switch work
   ```

3. **Initialize in a git repository**:

   ```bash
   cd your-git-repo
   devsafe init
   ```

## 🔧 Troubleshooting

### Command not found

uv and pipx install commands into `~/.local/bin`. If `devsafe` isn't found, add that directory to your PATH:

```bash
uv tool update-shell   # or: pipx ensurepath
```

Then open a new terminal.

### Permission errors

Make sure you have write permissions to your home directory for the config file.

### Git not found

Ensure Git is installed and accessible from your terminal.

## 🛠️ Development Setup

```bash
git clone https://github.com/ismailsoftdev/DevSafe.git
cd DevSafe
uv sync          # creates .venv with DevSafe and dev tools
uv run pytest    # run tests
uv run devsafe --help
```

## 📚 Next Steps

- Read the main [README.md](README.md) for detailed usage
- Open an [issue](https://github.com/ismailsoftdev/DevSafe/issues) if you encounter problems
