"""Regression tests for fixed bugs."""

import json
import os
import subprocess
from pathlib import Path

import pytest
from typer.testing import CliRunner

from devsafe import cli
from devsafe.commands.init import HOOK_SOURCE, init_devsafe_in_repo, render_hook
from devsafe.core import GitConfigManager
from devsafe.models import Profile
from devsafe.utils import ConfigError, ConfigManager


@pytest.fixture
def isolated_git(tmp_path, monkeypatch):
    """Point HOME and git's global config at a temporary directory."""
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(tmp_path / ".gitconfig"))
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    return tmp_path


@pytest.fixture
def temp_config_manager(tmp_path):
    manager = ConfigManager()
    manager.config_dir = tmp_path / ".devsafe"
    manager.config_file = manager.config_dir / "config.json"
    return manager


def global_git_config(key):
    result = subprocess.run(
        ["git", "config", "--global", key], capture_output=True, text=True
    )
    return result.stdout.strip() if result.returncode == 0 else None


class TestConfigLoading:
    def test_profile_with_deleted_ssh_key_still_loads(self, temp_config_manager, tmp_path):
        temp_config_manager.config_dir.mkdir()
        temp_config_manager.config_file.write_text(json.dumps({
            "profiles": {
                "work": {
                    "name": "W",
                    "email": "w@corp.com",
                    "ssh_key": str(tmp_path / "deleted_key"),
                }
            },
            "current_profile": "work",
        }))

        config = temp_config_manager.load_config()

        assert "work" in config.profiles
        assert config.current_profile == "work"

    def test_invalid_config_raises_and_file_is_untouched(self, temp_config_manager):
        temp_config_manager.config_dir.mkdir()
        temp_config_manager.config_file.write_text("{not json")

        with pytest.raises(ConfigError):
            temp_config_manager.load_config()

        assert temp_config_manager.config_file.read_text() == "{not json"


class TestProfileSwitching:
    def test_switch_to_unsigned_profile_clears_signing(self, isolated_git):
        git = GitConfigManager()
        signed = Profile(name="W", email="w@corp.com", signing_key="ABC123")
        unsigned = Profile(name="P", email="p@me.com")

        assert git.apply_profile_config(signed.to_dict())
        assert global_git_config("commit.gpgsign") == "true"

        assert git.apply_profile_config(unsigned.to_dict())
        assert global_git_config("user.email") == "p@me.com"
        assert global_git_config("user.signingkey") is None
        assert global_git_config("commit.gpgsign") is None


class TestInit:
    @pytest.fixture
    def repo(self, isolated_git, tmp_path):
        repo = tmp_path / "repo"
        (repo / "sub").mkdir(parents=True)
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        return repo

    def test_hook_ships_inside_package(self):
        import devsafe

        assert HOOK_SOURCE.exists()
        assert Path(devsafe.__file__).parent in HOOK_SOURCE.parents

    def test_init_from_subdirectory(self, repo, monkeypatch):
        monkeypatch.chdir(repo / "sub")

        init_devsafe_in_repo()

        hook = repo / ".git" / "hooks" / "pre-commit"
        assert hook.read_text() == render_hook()
        assert os.access(hook, os.X_OK)
        assert (repo / ".devsafe").is_dir()
        assert not (repo / "sub" / ".devsafe").exists()

    def test_init_outside_repo_fails(self, isolated_git, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        with pytest.raises(cli.typer.Exit):
            init_devsafe_in_repo()

    def test_init_keeps_existing_hook_without_force(self, repo, monkeypatch):
        monkeypatch.chdir(repo)
        hook = repo / ".git" / "hooks" / "pre-commit"
        hook.write_text("#!/bin/sh\necho mine\n")

        with pytest.raises(cli.typer.Exit):
            init_devsafe_in_repo()
        assert hook.read_text() == "#!/bin/sh\necho mine\n"

        init_devsafe_in_repo(force=True)
        assert hook.read_text() == render_hook()
        backup = hook.with_name("pre-commit.devsafe-backup")
        assert backup.read_text() == "#!/bin/sh\necho mine\n"


class TestAddCommand:
    @pytest.fixture
    def runner(self, temp_config_manager, monkeypatch):
        monkeypatch.setattr(cli, "config_manager", temp_config_manager)
        return CliRunner()

    def test_add_rejects_missing_ssh_key(self, runner, temp_config_manager, tmp_path):
        result = runner.invoke(
            cli.app,
            ["add", "work", "-n", "W", "-e", "w@corp.com", "-s", str(tmp_path / "missing")],
            input="\n\n",
        )

        assert result.exit_code == 1
        assert "SSH key file not found" in result.output
        assert not temp_config_manager.config_file.exists()

    def test_switch_failure_is_not_reported_as_create_failure(
        self, runner, temp_config_manager, monkeypatch
    ):
        monkeypatch.setattr(cli.git_manager, "apply_profile_config", lambda _: False)
        monkeypatch.setattr(cli.git_manager, "backup_current_config", lambda: True)

        result = runner.invoke(
            cli.app,
            ["add", "work", "-n", "W", "-e", "w@corp.com", "-d", "x"],
            input="\n\ny\n",
        )

        assert result.exit_code == 1
        assert "Failed to apply profile configuration" in result.output
        assert "Error creating profile" not in result.output
        assert "work" in temp_config_manager.load_config().profiles
