"""Tests for the pre-commit hook and `devsafe hook pre-commit`."""

import json
import subprocess
import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

from devsafe import cli
from devsafe.commands.init import init_devsafe_in_repo, render_hook
from devsafe.utils import ConfigManager


@pytest.fixture
def home(tmp_path, monkeypatch):
    """Isolate HOME and git's global config."""
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(home / ".gitconfig"))
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    return home


@pytest.fixture
def repo(home, tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    monkeypatch.chdir(repo)
    return repo


@pytest.fixture
def config_manager(home, monkeypatch):
    manager = ConfigManager()
    manager.config_dir = home / ".devsafe"
    manager.config_file = manager.config_dir / "config.json"
    monkeypatch.setattr(cli, "config_manager", manager)
    return manager


def write_config(manager, current="work"):
    manager.config_dir.mkdir(exist_ok=True)
    manager.config_file.write_text(json.dumps({
        "profiles": {"work": {"name": "W", "email": "w@corp.com"}},
        "current_profile": current,
    }))


def set_identity(name, email):
    subprocess.run(["git", "config", "user.name", name], check=True)
    subprocess.run(["git", "config", "user.email", email], check=True)


def run_hook():
    return CliRunner().invoke(cli.app, ["hook", "pre-commit"])


class TestHookCommand:
    def test_allows_when_devsafe_not_configured(self, repo, config_manager):
        assert run_hook().exit_code == 0

    def test_allows_matching_identity(self, repo, config_manager):
        write_config(config_manager)
        set_identity("W", "w@corp.com")

        result = run_hook()

        assert result.exit_code == 0
        assert "Committing as work" in result.output

    def test_blocks_mismatched_identity(self, repo, config_manager):
        write_config(config_manager)
        set_identity("W", "personal@me.com")

        result = run_hook()

        assert result.exit_code == 1
        assert "doesn't match active profile 'work'" in result.output

    def test_blocks_without_active_profile(self, repo, config_manager):
        write_config(config_manager, current=None)

        result = run_hook()

        assert result.exit_code == 1
        assert "No active DevSafe profile" in result.output

    def test_allows_with_unreadable_config(self, repo, config_manager):
        config_manager.config_dir.mkdir()
        config_manager.config_file.write_text("{not json")

        result = run_hook()

        assert result.exit_code == 0
        assert "Skipping profile check" in result.output


class TestInstalledHook:
    def test_hook_uses_this_python(self):
        assert Path(sys.executable).as_posix() in render_hook()
        assert "__DEVSAFE_PYTHON__" not in render_hook()

    def test_upgrades_old_python_hook_without_force(self, repo):
        hook = repo / ".git" / "hooks" / "pre-commit"
        hook.write_text(
            '#!/usr/bin/env python3\n"""Git pre-commit hook for DevSafe profile validation."""\n'
        )

        init_devsafe_in_repo()

        assert hook.read_text() == render_hook()
        assert not hook.with_name("pre-commit.devsafe-backup").exists()

    def test_git_commit_runs_devsafe_check(self, repo, home):
        write_config(ConfigManager())  # HOME is isolated, so this is the real path
        init_devsafe_in_repo()

        set_identity("W", "personal@me.com")
        blocked = subprocess.run(
            ["git", "commit", "--allow-empty", "-m", "test"],
            capture_output=True, text=True,
        )
        assert blocked.returncode != 0
        assert "doesn't match active profile" in blocked.stdout + blocked.stderr

        set_identity("W", "w@corp.com")
        allowed = subprocess.run(
            ["git", "commit", "--allow-empty", "-m", "test"],
            capture_output=True, text=True,
        )
        assert allowed.returncode == 0, allowed.stdout + allowed.stderr
