"""Tests for DevSafe."""

import pytest
import json
import tempfile
from pathlib import Path

from devsafe.models import Profile, DevSafeConfig
from devsafe.utils import ConfigManager


class TestProfile:
    """Test Profile model."""
    
    def test_create_profile(self):
        """Test creating a profile."""
        profile = Profile(
            name="John Doe",
            email="john@example.com",
            description="Test profile"
        )
        
        assert profile.name == "John Doe"
        assert profile.email == "john@example.com"
        assert profile.description == "Test profile"
        assert profile.ssh_key is None
        assert profile.signing_key is None
    
    def test_profile_to_dict(self):
        """Test converting profile to git config dictionary."""
        profile = Profile(
            name="John Doe",
            email="john@example.com",
            signing_key="ABC123"
        )
        
        config = profile.to_dict()
        
        assert config["user.name"] == "John Doe"
        assert config["user.email"] == "john@example.com"
        assert config["user.signingkey"] == "ABC123"
        assert config["commit.gpgsign"] == "true"


class TestDevSafeConfig:
    """Test DevSafeConfig model."""
    
    def test_create_empty_config(self):
        """Test creating empty configuration."""
        config = DevSafeConfig()
        
        assert len(config.profiles) == 0
        assert config.current_profile is None
        assert config.auto_switch is True
        assert config.hooks_enabled is True
    
    def test_add_profile(self):
        """Test adding a profile to configuration."""
        config = DevSafeConfig()
        profile = Profile(name="John Doe", email="john@example.com")
        
        config.add_profile("work", profile)
        
        assert "work" in config.profiles
        assert config.profiles["work"] == profile
    
    def test_switch_profile(self):
        """Test switching active profile."""
        config = DevSafeConfig()
        profile = Profile(name="John Doe", email="john@example.com")
        config.add_profile("work", profile)
        
        result = config.switch_profile("work")
        
        assert result is True
        assert config.current_profile == "work"
        
        # Test switching to non-existent profile
        result = config.switch_profile("nonexistent")
        assert result is False
    
    def test_remove_profile(self):
        """Test removing a profile."""
        config = DevSafeConfig()
        profile = Profile(name="John Doe", email="john@example.com")
        config.add_profile("work", profile)
        config.switch_profile("work")
        
        result = config.remove_profile("work")
        
        assert result is True
        assert "work" not in config.profiles
        assert config.current_profile is None
    
    def test_get_current_profile(self):
        """Test getting current active profile."""
        config = DevSafeConfig()
        profile = Profile(name="John Doe", email="john@example.com")
        config.add_profile("work", profile)
        
        # No current profile
        assert config.get_current_profile() is None
        
        # Set current profile
        config.switch_profile("work")
        current = config.get_current_profile()
        assert current == profile


class TestConfigManager:
    """Test ConfigManager functionality."""
    
    def test_config_paths(self):
        """Test configuration file paths."""
        manager = ConfigManager()
        
        assert manager.home_dir == Path.home()
        assert manager.config_dir == Path.home() / ".devsafe"
        assert manager.config_file == Path.home() / ".devsafe" / "config.json"
    
    def test_load_nonexistent_config(self):
        """Test loading configuration when file doesn't exist."""
        # Use temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ConfigManager()
            manager.config_dir = Path(temp_dir) / ".devsafe"
            manager.config_file = manager.config_dir / "config.json"
            
            config = manager.load_config()
            
            assert isinstance(config, DevSafeConfig)
            assert len(config.profiles) == 0


# Integration test
def test_full_workflow():
    """Test a complete workflow with temporary config."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Setup temporary config manager
        manager = ConfigManager()
        manager.config_dir = Path(temp_dir) / ".devsafe"
        manager.config_file = manager.config_dir / "config.json"
        
        # Load empty config
        config = manager.load_config()
        assert len(config.profiles) == 0
        
        # Add a profile
        profile = Profile(
            name="John Doe",
            email="john@example.com",
            description="Test profile"
        )
        config.add_profile("work", profile)
        
        # Save config
        success = manager.save_config(config)
        assert success is True
        assert manager.config_file.exists()
        
        # Load config again and verify
        loaded_config = manager.load_config()
        assert len(loaded_config.profiles) == 1
        assert "work" in loaded_config.profiles
        assert loaded_config.profiles["work"].name == "John Doe"
        assert loaded_config.profiles["work"].email == "john@example.com"


if __name__ == "__main__":
    pytest.main([__file__])