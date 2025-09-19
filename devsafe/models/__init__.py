"""Data models for DevSafe."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict


class Profile(BaseModel):
    """Git profile model."""

    name: str = Field(..., description="Full name for git commits")
    email: EmailStr = Field(..., description="Email address for git commits")
    ssh_key: Optional[Path] = Field(None, description="Path to SSH private key")
    signing_key: Optional[str] = Field(None, description="GPG signing key ID")
    description: Optional[str] = Field(None, description="Profile description")

    @field_validator("ssh_key", mode="before")
    @classmethod
    def validate_ssh_key_path(cls, v):
        """Validate SSH key path exists if provided."""
        if v is None:
            return v
        
        path = Path(v).expanduser()
        if not path.exists():
            raise ValueError(f"SSH key file not found: {path}")
        return path

    model_config = ConfigDict(
        json_encoders={Path: str}
    )

    def to_dict(self) -> Dict[str, str]:
        """Convert profile to dictionary for git config."""
        config = {
            "user.name": self.name,
            "user.email": str(self.email),
        }
        
        if self.signing_key:
            config["user.signingkey"] = self.signing_key
            config["commit.gpgsign"] = "true"
        
        return config


class DevSafeConfig(BaseModel):
    """DevSafe configuration model."""

    profiles: Dict[str, Profile] = Field(default_factory=dict)
    current_profile: Optional[str] = Field(None, description="Currently active profile")
    auto_switch: bool = Field(True, description="Enable automatic profile switching")
    hooks_enabled: bool = Field(True, description="Enable git hooks")
    backup_enabled: bool = Field(True, description="Backup git config before changes")

    def get_current_profile(self) -> Optional[Profile]:
        """Get the currently active profile."""
        if self.current_profile and self.current_profile in self.profiles:
            return self.profiles[self.current_profile]
        return None

    def add_profile(self, name: str, profile: Profile) -> None:
        """Add a new profile."""
        self.profiles[name] = profile

    def remove_profile(self, name: str) -> bool:
        """Remove a profile. Returns True if removed, False if not found."""
        if name in self.profiles:
            del self.profiles[name]
            if self.current_profile == name:
                self.current_profile = None
            return True
        return False

    def list_profiles(self) -> Dict[str, Profile]:
        """Get all profiles."""
        return self.profiles.copy()

    def switch_profile(self, name: str) -> bool:
        """Switch to a profile. Returns True if successful, False if profile not found."""
        if name in self.profiles:
            self.current_profile = name
            return True
        return False


class RepoConfig(BaseModel):
    """Repository-specific configuration."""

    default_profile: Optional[str] = Field(None, description="Default profile for this repo")
    auto_switch_patterns: Dict[str, str] = Field(
        default_factory=dict,
        description="Patterns to automatically switch profiles"
    )

    model_config = ConfigDict(extra="allow")