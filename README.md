# DevSafe 🚀

**Git profile manager for developers - Never commit with the wrong credentials again!**

DevSafe is a command-line tool that helps developers manage multiple git profiles (work, personal, client projects, etc.) and switch between them effortlessly. No more embarrassing commits with the wrong email address or name!

## ✨ Features

- 🔄 **Easy Profile Switching** - Switch between profiles with a single command
- 👥 **Multiple Profile Support** - Work, personal, client - manage them all
- 🔐 **SSH & GPG Key Support** - Full support for SSH keys and GPG signing
- 🛡️ **Safety First** - Automatic backups and validation
- 📊 **Clear Status Display** - Always know which profile is active
- 🎯 **Repository-Specific Settings** - Auto-switch based on repository patterns
- 🚀 **Fast & Lightweight** - Written in Python for speed and reliability

## 🚀 Quick Start

### Installation

```bash
pip install devsafe
```

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

# Check current profile
devsafe current

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

# Check current active profile
devsafe current
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
  "auto_switch": true,
  "hooks_enabled": true,
  "backup_enabled": true
}
```

## 🔧 Advanced Features

### Git Hooks (Coming Soon)
DevSafe can install git hooks to prevent commits with the wrong profile:

```bash
devsafe init  # Initialize DevSafe in current repository
```

### Repository-Specific Profiles (Coming Soon)
Set default profiles for specific repositories or patterns:

```bash
# Auto-switch to work profile for company repositories
devsafe config --pattern "*company.com*" --profile work
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/devsafe/devsafe.git
cd devsafe

# Install development dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Run tests
pytest

# Format code
black devsafe/
isort devsafe/
```

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🚨 Security Note

DevSafe modifies your global git configuration. While it creates backups automatically, always ensure you have your own backups of important configurations.

## 📞 Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/devsafe/devsafe/issues)
- 💡 **Feature Requests**: [GitHub Issues](https://github.com/devsafe/devsafe/issues)
- 📖 **Documentation**: [Read the Docs](https://devsafe.readthedocs.io)

## 🎯 Roadmap

- [ ] Git hooks integration
- [ ] Repository-specific auto-switching  
- [ ] Profile templates
- [ ] SSH key management improvements
- [ ] Shell completion support
- [ ] GUI application
- [ ] IDE extensions

---

Made with ❤️ by developers, for developers.