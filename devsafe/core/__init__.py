"""Git configuration management."""

import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from rich.console import Console

console = Console()

# Optional keys a profile may set. When switching to a profile that doesn't
# set one, it is unset so the previous profile's value doesn't carry over.
OPTIONAL_PROFILE_KEYS = ("user.signingkey", "commit.gpgsign")


class GitConfigManager:
    """Manages git configuration operations."""

    def __init__(self):
        self.backup_file = Path.home() / ".devsafe" / "git_config_backup.txt"

    def get_current_config(self) -> Dict[str, str]:
        """Get current git configuration."""
        config = {}
        
        try:
            # Get user.name
            result = subprocess.run(
                ["git", "config", "--global", "user.name"],
                capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                config["user.name"] = result.stdout.strip()

            # Get user.email
            result = subprocess.run(
                ["git", "config", "--global", "user.email"],
                capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                config["user.email"] = result.stdout.strip()

            # Get signing key
            result = subprocess.run(
                ["git", "config", "--global", "user.signingkey"],
                capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                config["user.signingkey"] = result.stdout.strip()

            # Get gpg sign setting
            result = subprocess.run(
                ["git", "config", "--global", "commit.gpgsign"],
                capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                config["commit.gpgsign"] = result.stdout.strip()

        except Exception as e:
            console.print(f"[red]Error reading git config: {e}[/red]")

        return config

    def get_effective_identity(
        self, keys: Tuple[str, ...] = ("user.name", "user.email")
    ) -> Dict[str, str]:
        """Get the settings git will actually use here (default: name/email).

        Unlike get_current_config, this includes repository-local overrides
        and includeIf rules (directory bindings).
        """
        identity = {}

        for key in keys:
            try:
                result = subprocess.run(
                    ["git", "config", key],
                    capture_output=True, text=True, check=False
                )
                if result.returncode == 0:
                    identity[key] = result.stdout.strip()
            except Exception as e:
                console.print(f"[red]Error reading git config {key}: {e}[/red]")

        return identity

    def backup_current_config(self) -> bool:
        """Backup current git configuration."""
        try:
            current_config = self.get_current_config()
            
            self.backup_file.parent.mkdir(exist_ok=True)
            
            with open(self.backup_file, 'w') as f:
                for key, value in current_config.items():
                    f.write(f"{key}={value}\n")
            
            return True
        except Exception as e:
            console.print(f"[red]Error backing up git config: {e}[/red]")
            return False

    def restore_config_from_backup(self) -> bool:
        """Restore git configuration from backup."""
        if not self.backup_file.exists():
            console.print("[yellow]No backup file found[/yellow]")
            return False

        try:
            with open(self.backup_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line:
                        key, value = line.split('=', 1)
                        self.set_git_config(key, value)
            
            return True
        except Exception as e:
            console.print(f"[red]Error restoring git config: {e}[/red]")
            return False

    def set_git_config(self, key: str, value: str) -> bool:
        """Set a git configuration value."""
        try:
            result = subprocess.run(
                ["git", "config", "--global", key, value],
                capture_output=True, text=True, check=True
            )
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Error setting git config {key}: {e}[/red]")
            return False
        except Exception as e:
            console.print(f"[red]Unexpected error setting git config: {e}[/red]")
            return False

    def unset_git_config(self, key: str) -> bool:
        """Unset a git configuration value."""
        try:
            result = subprocess.run(
                ["git", "config", "--global", "--unset", key],
                capture_output=True, text=True, check=False
            )
            return True  # Success even if key didn't exist
        except Exception as e:
            console.print(f"[red]Error unsetting git config {key}: {e}[/red]")
            return False

    def apply_profile_config(self, profile_config: Dict[str, str]) -> bool:
        """Apply a profile's configuration to git."""
        success = True

        for key, value in profile_config.items():
            if not self.set_git_config(key, value):
                success = False

        for key in OPTIONAL_PROFILE_KEYS:
            if key not in profile_config and not self.unset_git_config(key):
                success = False

        return success

    def is_git_repository(self, path: Optional[Path] = None) -> bool:
        """Check if current directory (or given path) is a git repository."""
        if path is None:
            path = Path.cwd()
        
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=path, capture_output=True, check=False
            )
            return result.returncode == 0
        except Exception:
            return False

    def get_repository_root(self) -> Optional[Path]:
        """Get the top-level directory of the current git repository."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                return Path(result.stdout.strip())
        except Exception:
            pass
        return None

    def get_git_dir(self) -> Optional[Path]:
        """Get the absolute git directory, which includeIf "gitdir:" matches."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--absolute-git-dir"],
                capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                return Path(result.stdout.strip())
        except Exception:
            pass
        return None

    def get_identity_origin(self, key: str) -> Optional[str]:
        """Get the config file that sets key here (e.g. "file:/Users/me/.gitconfig")."""
        try:
            result = subprocess.run(
                ["git", "config", "--show-origin", key],
                capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                return result.stdout.split("\t", 1)[0]
        except Exception:
            pass
        return None

    def write_config_file(self, path: Path, settings: Dict[str, str]) -> bool:
        """Write settings to a standalone git config file, replacing it."""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.unlink(missing_ok=True)
            for key, value in settings.items():
                subprocess.run(
                    ["git", "config", "--file", str(path), key, value],
                    capture_output=True, text=True, check=True
                )
            return True
        except Exception as e:
            console.print(f"[red]Error writing {path}: {e}[/red]")
            return False

    def sync_directory_includes(
        self, includes: List[Tuple[str, Path]], managed_dir: Path
    ) -> bool:
        """Make DevSafe's includeIf rules in the global config match includes.

        includes is a list of (directory, config file). Existing rules whose
        file lives in managed_dir are removed and all rules are re-added at
        the end of the file, least specific first: for git, later settings
        win, so nested directories override their parents and no [user]
        section appended later (e.g. by `devsafe switch`) can shadow them.
        """
        success = True
        managed_prefix = str(managed_dir) + "/"

        # -z: keys may contain spaces (e.g. "gitdir:/Users/me/Dev Tools/")
        result = subprocess.run(
            ["git", "config", "--global", "-z", "--get-regexp", r"^includeif\..*\.path$"],
            capture_output=True, text=True, check=False
        )
        for record in filter(None, result.stdout.split("\0")):
            key, _, value = record.partition("\n")
            if value.startswith(managed_prefix):
                subsection = key[len("includeif."):-len(".path")]
                removed = subprocess.run(
                    ["git", "config", "--global", "--remove-section", f"includeIf.{subsection}"],
                    capture_output=True, text=True, check=False
                )
                success = success and removed.returncode == 0

        for directory, config_file in sorted(includes, key=lambda item: len(item[0])):
            pattern = "gitdir:" + directory.rstrip("/") + "/"
            success = self._add_global(f"includeIf.{pattern}.path", str(config_file)) and success

        return success

    def _add_global(self, key: str, value: str) -> bool:
        try:
            subprocess.run(
                ["git", "config", "--global", "--add", key, value],
                capture_output=True, text=True, check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Error setting git config {key}: {e.stderr.strip()}[/red]")
            return False

    def get_hooks_dir(self) -> Optional[Path]:
        """Get the hooks directory of the current git repository.

        Works from subdirectories and worktrees, and honors core.hooksPath.
        """
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-path", "hooks"],
                capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                # Output is relative to the cwd unless it is already absolute
                return Path.cwd() / result.stdout.strip()
        except Exception:
            pass
        return None

    def get_repository_info(self) -> Optional[Dict[str, str]]:
        """Get information about the current git repository."""
        if not self.is_git_repository():
            return None

        info = {}
        
        try:
            # Get remote origin URL
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                info["origin"] = result.stdout.strip()

            # Get current branch
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                info["branch"] = result.stdout.strip()

            # Get repository root
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                info["root"] = result.stdout.strip()

        except Exception as e:
            console.print(f"[red]Error getting repository info: {e}[/red]")

        return info if info else None

    def validate_git_installation(self) -> Tuple[bool, str]:
        """Validate that git is installed and accessible."""
        try:
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True, text=True, check=True
            )
            return True, result.stdout.strip()
        except subprocess.CalledProcessError:
            return False, "Git command failed"
        except FileNotFoundError:
            return False, "Git is not installed or not in PATH"
        except Exception as e:
            return False, f"Unexpected error: {e}"