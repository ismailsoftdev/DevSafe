"""Git configuration management."""

import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from rich.console import Console

console = Console()


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