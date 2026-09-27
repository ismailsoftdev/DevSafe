# DevSafe Installation Guide

DevSafe is installed directly from its GitHub repository.

## 🚀 Quick Start

### Prerequisites

- Git
- [`uv`](https://docs.astral.sh/uv/) (recommended), or pipx with Python 3.10+
- Access to the repository (it is currently private; see [Authentication](#-authentication))

### Install uv (if not already installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

uv downloads a suitable Python automatically, so you don't need one installed.

## 📦 Installation Methods

### Method 1: uv (Recommended)

```bash
uv tool install git+https://github.com/ismailsoftdev/DevSafe

# Verify installation
devsafe --version
```

### Method 2: pipx

```bash
pipx install git+https://github.com/ismailsoftdev/DevSafe
devsafe --version
```

### Method 3: A specific version

Every release is a git tag (see [Releases](https://github.com/ismailsoftdev/DevSafe/releases)):

```bash
uv tool install git+https://github.com/ismailsoftdev/DevSafe@v0.2.0
```

A pinned install stays on that version; `uv tool upgrade` won't move it.
To change versions, run the same command with `--force` and the new tag.

### Method 4: Try without installing

```bash
uvx --from git+https://github.com/ismailsoftdev/DevSafe devsafe --help
```

### Method 5: From a local checkout

```bash
git clone https://github.com/ismailsoftdev/DevSafe.git
cd DevSafe

# Install the devsafe command from this checkout (editable)
uv tool install --editable .
```

### Method 6: From a release wheel

Each [release](https://github.com/ismailsoftdev/DevSafe/releases) has a wheel
attached. Download it (for a private repository, from the Releases page while
signed in, or with `gh release download v0.2.0 --repo ismailsoftdev/DevSafe`), then:

```bash
uv tool install ./devsafe-0.2.0-py3-none-any.whl
```

## ⬆️ Upgrading

```bash
uv tool upgrade devsafe   # or: pipx upgrade devsafe
```

This installs the latest commit on `main`, which CI tests on every push.
If you installed a specific version (Method 3), reinstall with the new tag instead.

## 🔐 Authentication

While the repository is private, installs clone it with your own git
credentials, so you need access to the repository and git must be able to
authenticate to GitHub. Any of these works:

- **HTTPS with the GitHub CLI**: `gh auth login`, then `gh auth setup-git`.
- **HTTPS with a credential helper**: e.g. macOS Keychain or Git Credential
  Manager, storing a personal access token with read access to the repository.
- **SSH**: if you already push over SSH, use the SSH URL:

  ```bash
  uv tool install git+ssh://git@github.com/ismailsoftdev/DevSafe.git
  ```

Quick check: `git ls-remote https://github.com/ismailsoftdev/DevSafe` should list
branches without prompting for a password.

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

### "Repository not found" or authentication errors

GitHub reports a private repository you can't access as "not found". Check that
you have access and that git can authenticate (see [Authentication](#-authentication)).

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
