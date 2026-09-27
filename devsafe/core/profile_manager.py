"""Profile management functionality."""

from typing import Dict, List, Optional

from devsafe.models import DevSafeConfig, Profile
from devsafe.utils import ConfigManager


class ProfileManager:
    """Manages git profiles operations."""

    def __init__(self):
        self.config_manager = ConfigManager()

    def create_profile(
        self,
        name: str,
        profile_name: str,
        email: str,
        ssh_key: Optional[str] = None,
        signing_key: Optional[str] = None,
        description: Optional[str] = None,
    ) -> bool:
        """Create a new profile."""
        config = self.config_manager.load_config()
        
        if name in config.profiles:
            return False
        
        profile = Profile(
            name=profile_name,
            email=email,
            ssh_key=ssh_key,
            signing_key=signing_key,
            description=description,
        )
        
        config.add_profile(name, profile)
        return self.config_manager.save_config(config)

    def get_profile(self, name: str) -> Optional[Profile]:
        """Get a profile by name."""
        config = self.config_manager.load_config()
        return config.profiles.get(name)

    def list_profiles(self) -> Dict[str, Profile]:
        """List all profiles."""
        config = self.config_manager.load_config()
        return config.profiles

    def update_profile(self, name: str, **kwargs) -> bool:
        """Update an existing profile."""
        config = self.config_manager.load_config()
        
        if name not in config.profiles:
            return False
        
        profile = config.profiles[name]
        
        # Update fields if provided
        for field, value in kwargs.items():
            if hasattr(profile, field) and value is not None:
                setattr(profile, field, value)
        
        return self.config_manager.save_config(config)

    def delete_profile(self, name: str) -> bool:
        """Delete a profile."""
        config = self.config_manager.load_config()
        
        if config.remove_profile(name):
            return self.config_manager.save_config(config)
        
        return False

    def get_current_profile(self) -> Optional[str]:
        """Get the name of the current active profile."""
        config = self.config_manager.load_config()
        return config.current_profile

    def set_current_profile(self, name: str) -> bool:
        """Set the current active profile."""
        config = self.config_manager.load_config()
        
        if config.switch_profile(name):
            return self.config_manager.save_config(config)
        
        return False