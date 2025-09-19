"""Configuration management utilities."""

import json
from pathlib import Path
from typing import Optional

from rich.console import Console

from devsafe.models import DevSafeConfig, RepoConfig

console = Console()


class ConfigManager:
    """Manages DevSafe configuration files."""

    def __init__(self):
        self.home_dir = Path.home()
        self.config_dir = self.home_dir / ".devsafe"
        self.config_file = self.config_dir / "config.json"
        self.repo_config_file = Path.cwd() / ".devsafe" / "repo-config.json"

    def ensure_config_dir(self) -> None:
        """Ensure configuration directory exists."""
        self.config_dir.mkdir(exist_ok=True)

    def load_config(self) -> DevSafeConfig:
        """Load DevSafe configuration."""
        self.ensure_config_dir()
        
        if not self.config_file.exists():
            return DevSafeConfig()

        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
            return DevSafeConfig(**data)
        except (json.JSONDecodeError, Exception) as e:
            console.print(f"[red]Error loading config: {e}[/red]")
            return DevSafeConfig()

    def save_config(self, config: DevSafeConfig) -> bool:
        """Save DevSafe configuration."""
        self.ensure_config_dir()
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config.model_dump(), f, indent=2, default=str)
            return True
        except Exception as e:
            console.print(f"[red]Error saving config: {e}[/red]")
            return False

    def load_repo_config(self) -> Optional[RepoConfig]:
        """Load repository-specific configuration."""
        if not self.repo_config_file.exists():
            return None

        try:
            with open(self.repo_config_file, 'r') as f:
                data = json.load(f)
            return RepoConfig(**data)
        except (json.JSONDecodeError, Exception) as e:
            console.print(f"[red]Error loading repo config: {e}[/red]")
            return None

    def save_repo_config(self, config: RepoConfig) -> bool:
        """Save repository-specific configuration."""
        self.repo_config_file.parent.mkdir(exist_ok=True)
        
        try:
            with open(self.repo_config_file, 'w') as f:
                json.dump(config.model_dump(), f, indent=2)
            return True
        except Exception as e:
            console.print(f"[red]Error saving repo config: {e}[/red]")
            return False

    def get_config_info(self) -> dict:
        """Get information about configuration files and directories."""
        return {
            "config_dir": str(self.config_dir),
            "config_file": str(self.config_file),
            "config_exists": self.config_file.exists(),
            "repo_config_file": str(self.repo_config_file),
            "repo_config_exists": self.repo_config_file.exists(),
        }