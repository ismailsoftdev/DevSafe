# DevSafe 🚀

**Git profile manager for developers - Never commit with the wrong credentials again!**

DevSafe is a command-line tool that helps developers manage multiple git profiles (work, personal, client projects, etc.) and switch between them effortlessly. No more embarrassing commits with the wrong email address or name!

## ✨ Features

- 🔄 **Easy Profile Switching** - Switch between profiles with a single command
- 👥 **Multiple Profile Support** - Work, personal, client - manage them all
- 🔐 **SSH & GPG Key Support** - Full support for SSH keys and GPG signing
- 🛡️ **Safety First** - Pre-commit hooks prevent wrong profile commits
- 📊 **Clear Status Display** - Always know which profile is active
- 📁 **Per-Directory Profiles** - Bind a folder or repository to a profile; git uses it automatically
- 🎯 **Repository Integration** - Git-aware status and repository management
- 🚀 **Fast & Lightweight** - Written in Python for speed and reliability
- ✅ **Git Hooks** - Automatic validation before commits
- 🔧 **Easy Setup** - Simple `devsafe init` to protect any repository

## 🚀 Quick Start

### Installation

DevSafe installs straight from GitHub. Recommended: use [uv](https://docs.astral.sh/uv/). It keeps DevSafe in its own environment and downloads a suitable Python if you don't have one.

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install DevSafe
uv tool install git+https://github.com/ismailsoftdev/DevSafe

# Upgrade to the latest version
uv tool upgrade devsafe
```

Alternative: [pipx](https://pipx.pypa.io/) works the same way (requires Python 3.10+):

```bash
pipx install git+https://github.com/ismailsoftdev/DevSafe
pipx upgrade devsafe
```

> **Note:** The repository is currently private. You need access to it, and git must be able to authenticate to GitHub. Or use SSH: `uv tool install git+ssh://git@github.com/ismailsoftdev/DevSafe.git`

See [INSTALL.md](https://github.com/ismailsoftdev/DevSafe/blob/main/INSTALL.md) for installing a specific version, trying DevSafe without installing, and troubleshooting.

### Basic Usage

```bash
# Add your first profile
devsafe add work --name "John Doe" --email "john@company.com"

# Add a personal profile
devsafe add personal --name "John Doe" --email "john@gmail.com"

# List all profiles
devsafe list

# Switch between profiles
devsafe switch work
devsafe switch personal

# Check which profile applies here
devsafe current

# Always use your personal profile for repos under ~/personal
devsafe bind personal ~/personal

# Initialize DevSafe in a git repository (adds safety hooks)
devsafe init

# See status
devsafe status
```

## 📖 Documentation

### Adding Profiles

```bash
# Interactive mode (recommended for first-time setup)
devsafe add myprofile

# Command line mode
devsafe add work \
  --name "John Doe" \
  --email "john@company.com" \
  --ssh-key "~/.ssh/work_key" \
  --signing-key "ABC123" \
  --description "Work profile for Company XYZ"
```

### Profile Management

```bash
# List all profiles with details
devsafe list

# Remove a profile
devsafe remove oldprofile

# Remove without confirmation
devsafe remove oldprofile --force
```

### Switching Profiles

```bash
# Switch to a profile
devsafe switch work

# Check which profile and identity apply in the current directory
devsafe current
```

### Per-Directory and Per-Repository Profiles

Bind a directory to a profile, and every git repository inside it uses that profile, whatever profile is active globally:

```bash
# All repos under ~/work commit as your work identity
devsafe bind work ~/work

# Inside a repository: bind just this repository (its root)
devsafe bind personal

# See and remove bindings
devsafe bindings
devsafe unbind ~/work
```

The most specific binding wins, so `~/work/oss` can be bound to `personal` while the rest of `~/work` stays on `work`. Directories without a binding use the profile chosen with `devsafe switch`.

Bindings use git's own [conditional includes](https://git-scm.com/docs/git-config#_conditional_includes) (`includeIf "gitdir:..."`), so they apply in every tool (terminal, IDEs, GUI clients) with no switching and no background process. DevSafe writes one file per bound profile to `~/.devsafe/profiles/` and keeps its rules at the end of `~/.gitconfig`. The pre-commit hook checks commits against the directory's bound profile.

### Repository Safety

```bash
# Initialize DevSafe in a git repository
devsafe init

# DevSafe will now validate profiles before commits
git commit -m "Your commit message"
# ✅ Allowed if profile matches git config
# ❌ Blocked if profile doesn't match with helpful error message
```

### Status and Information

```bash
# Show DevSafe status and configuration
devsafe status

# Show version
devsafe --version
```

## 🛠️ Configuration

DevSafe stores its configuration in `~/.devsafe/config.json`. The configuration includes:

```json
{
  "profiles": {
    "work": {
      "name": "John Doe",
      "email": "john@company.com",
      "ssh_key": "/Users/john/.ssh/work_key",
      "signing_key": "ABC123",
      "description": "Work profile"
    },
    "personal": {
      "name": "John Doe", 
      "email": "john@gmail.com",
      "description": "Personal projects"
    }
  },
  "current_profile": "work",
  "bindings": {
    "/Users/john/personal": "personal"
  },
  "auto_switch": true,
  "hooks_enabled": true,
  "backup_enabled": true
}
```

## 🔧 Advanced Features

### Git Hooks ✅

DevSafe includes git hooks to prevent commits with the wrong profile:

```bash
devsafe init  # Initialize DevSafe in current repository
```

Once initialized, DevSafe will:

- 🛡️ Validate your profile before every commit
- ❌ Block commits if profile doesn't match git config
- 📋 Show clear guidance to fix profile mismatches
- ✅ Allow commits when profile is correctly set

### Remote-Based Profiles (Coming Soon)

Choose a profile by the repository's remote URL, e.g. every repository cloned from your company's GitHub organization, wherever it lives on disk.

## 🤝 Contributing

We welcome contributions! Open an [issue](https://github.com/ismailsoftdev/DevSafe/issues) to discuss a change, or send a pull request.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/ismailsoftdev/DevSafe.git
cd DevSafe

# Create the development environment (installs DevSafe and dev tools)
uv sync

# Run tests
uv run pytest

# Format code
uv run black devsafe/ tests/
uv run isort devsafe/ tests/
```

## 📝 License

MIT License - see [LICENSE](https://github.com/ismailsoftdev/DevSafe/blob/main/LICENSE) file for details.

## 🚨 Security Note

DevSafe modifies your global git configuration. While it creates backups automatically, always ensure you have your own backups of important configurations.

## 📞 Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/ismailsoftdev/DevSafe/issues)
- 💡 **Feature Requests**: [GitHub Issues](https://github.com/ismailsoftdev/DevSafe/issues)

## 🎯 Roadmap

### ✅ Completed Features

- [x] **Git hooks integration** - Pre-commit validation and safety features
- [x] **Profile management** - Add, list, switch, remove profiles with full CLI
- [x] **Git configuration management** - Automatic git config updates
- [x] **Safety validation** - Profile mismatch detection and prevention
- [x] **Repository awareness** - Status shows current repo information
- [x] **Cross-platform support** - Works on macOS, Linux, and Windows
- [x] **Comprehensive testing** - Full test suite with pytest
- [x] **Modern Python packaging** - Uses pyproject.toml and modern standards
- [x] **Per-directory and per-repository profiles** - `devsafe bind` ties a profile to a folder or repository

### 🚧 In Progress

- [ ] **Remote-based profiles** - Pick a profile by the repository's remote URL
- [ ] **Enhanced documentation** - More examples and use cases

### 🎯 Future Features

- [ ] **Profile templates** - Pre-configured profile templates for common setups
- [ ] **SSH key management improvements** - Better SSH key handling and validation
- [ ] **Shell completion support** - Tab completion for bash/zsh/fish
- [ ] **Configuration GUI** - Desktop application for profile management
- [ ] **IDE extensions** - VS Code, IntelliJ, and other IDE integrations
- [ ] **Team sharing** - Share profile configurations across teams
- [ ] **Multi-repository management** - Bulk operations across multiple repos
- [ ] **Profile analytics** - Track profile usage and switch frequency

---

Made with ❤️ by developers, for developers.
