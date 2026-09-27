"""Tests for directory/repository profile bindings."""

import json
import subprocess
from pathlib import Path

import pytest
from typer.testing import CliRunner

from devsafe import cli
from devsafe.models import DevSafeConfig
from devsafe.utils import ConfigManager


@pytest.fixture
def env(tmp_path, monkeypatch):
    """Isolated HOME, global git config, DevSafe config, and two profiles."""
    home = (tmp_path / "home").resolve()
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(home / ".gitconfig"))
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")

    manager = ConfigManager()
    manager.config_dir = home / ".devsafe"
    manager.config_file = manager.config_dir / "config.json"
    manager.config_dir.mkdir()
    manager.config_file.write_text(json.dumps({
        "profiles": {
            "work": {"name": "W", "email": "w@corp.com", "signing_key": "ABC123"},
            "personal": {"name": "P", "email": "p@me.com"},
        },
    }))
    monkeypatch.setattr(cli, "config_manager", manager)
    monkeypatch.setattr(cli.git_manager, "backup_file", manager.config_dir / "backup.txt")

    # Paths with spaces, like "~/Dev Tools"
    root = (tmp_path / "Dev Tools").resolve()
    root.mkdir()
    return root


def invoke(*args):
    return CliRunner().invoke(cli.app, list(args))


def make_repo(path: Path) -> Path:
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    return path


def git_config(repo: Path, key: str):
    result = subprocess.run(
        ["git", "-C", str(repo), "config", key], capture_output=True, text=True
    )
    return result.stdout.strip() if result.returncode == 0 else None


def saved_bindings():
    return json.loads(cli.config_manager.config_file.read_text()).get("bindings", {})


class TestResolveBinding:
    def test_most_specific_directory_wins(self, tmp_path):
        base = tmp_path.resolve()
        config = DevSafeConfig(bindings={
            str(base / "work"): "work",
            str(base / "work" / "oss"): "personal",
        })

        assert config.resolve_binding(base / "work" / "repo") == (str(base / "work"), "work")
        assert config.resolve_binding(base / "work" / "oss" / "r") == (str(base / "work" / "oss"), "personal")
        assert config.resolve_binding(base / "work") == (str(base / "work"), "work")

    def test_sibling_with_same_prefix_is_not_covered(self, tmp_path):
        base = tmp_path.resolve()
        config = DevSafeConfig(bindings={str(base / "work"): "work"})

        assert config.resolve_binding(base / "workshop" / "repo") is None


class TestBind:
    def test_repos_in_bound_directory_use_profile(self, env):
        assert invoke("switch", "work").exit_code == 0
        bound = env / "personal"
        inside = make_repo(bound / "project")
        outside = make_repo(env / "elsewhere")

        result = invoke("bind", "personal", str(bound))

        assert result.exit_code == 0, result.output
        assert saved_bindings() == {str(bound): "personal"}
        assert git_config(inside, "user.email") == "p@me.com"
        assert git_config(inside, "commit.gpgsign") == "false"  # global work profile signs
        assert git_config(outside, "user.email") == "w@corp.com"

    def test_nested_binding_overrides_parent(self, env):
        parent = env / "clients"
        child = parent / "oss"
        child_repo = make_repo(child / "lib")
        parent_repo = make_repo(parent / "app")

        # Bind the child first to check ordering doesn't depend on bind order
        assert invoke("bind", "personal", str(child)).exit_code == 0
        assert invoke("bind", "work", str(parent)).exit_code == 0

        assert git_config(child_repo, "user.email") == "p@me.com"
        assert git_config(parent_repo, "user.email") == "w@corp.com"

    def test_switch_does_not_shadow_bindings(self, env):
        # No [user] section yet: switch appends one after the includeIf rules
        bound = env / "personal"
        repo = make_repo(bound / "project")
        assert invoke("bind", "personal", str(bound)).exit_code == 0

        result = invoke("switch", "work")

        assert result.exit_code == 0
        assert git_config(repo, "user.email") == "p@me.com"

    def test_bind_defaults_to_repository_root(self, env, monkeypatch):
        repo = make_repo(env / "project")
        (repo / "src").mkdir()
        monkeypatch.chdir(repo / "src")

        assert invoke("bind", "personal").exit_code == 0
        assert saved_bindings() == {str(repo): "personal"}

    def test_bind_rejects_unknown_profile(self, env):
        result = invoke("bind", "nope", str(env))

        assert result.exit_code == 1
        assert saved_bindings() == {}

    def test_rebinding_replaces_profile(self, env):
        repo = make_repo(env / "project")
        assert invoke("bind", "personal", str(repo)).exit_code == 0
        assert invoke("bind", "work", str(repo)).exit_code == 0

        assert saved_bindings() == {str(repo): "work"}
        assert git_config(repo, "user.email") == "w@corp.com"

    def test_user_include_rules_are_left_alone(self, env):
        other = env / "mine.gitconfig"
        other.write_text("[user]\n\temail = mine@x\n")
        subprocess.run(
            ["git", "config", "--global", f"includeIf.gitdir:{env}/own/.path", str(other)],
            check=True,
        )
        repo = make_repo(env / "own" / "r")

        assert invoke("bind", "personal", str(env / "elsewhere")).exit_code != 0  # missing dir
        (env / "elsewhere").mkdir()
        assert invoke("bind", "personal", str(env / "elsewhere")).exit_code == 0
        assert invoke("unbind", str(env / "elsewhere")).exit_code == 0

        assert git_config(repo, "user.email") == "mine@x"


class TestUnbind:
    def test_unbind_restores_global_identity(self, env):
        assert invoke("switch", "work").exit_code == 0
        repo = make_repo(env / "project")
        assert invoke("bind", "personal", str(repo)).exit_code == 0

        result = invoke("unbind", str(repo))

        assert result.exit_code == 0
        assert saved_bindings() == {}
        assert git_config(repo, "user.email") == "w@corp.com"
        assert list((cli.config_manager.config_dir / "profiles").glob("*")) == []

    def test_unbind_points_to_covering_binding(self, env):
        parent = env / "clients"
        repo = make_repo(parent / "app")
        assert invoke("bind", "work", str(parent)).exit_code == 0

        result = invoke("unbind", str(repo))

        assert result.exit_code == 1
        assert "covered by the binding for" in result.output


class TestRemoveBoundProfile:
    def test_removing_profile_removes_its_bindings(self, env):
        assert invoke("switch", "work").exit_code == 0
        repo = make_repo(env / "project")
        assert invoke("bind", "personal", str(repo)).exit_code == 0

        result = invoke("remove", "personal", "--force")

        assert result.exit_code == 0
        assert saved_bindings() == {}
        assert git_config(repo, "user.email") == "w@corp.com"


class TestHookWithBindings:
    def test_bound_repo_passes_when_global_profile_differs(self, env, monkeypatch):
        assert invoke("switch", "work").exit_code == 0
        repo = make_repo(env / "project")
        assert invoke("bind", "personal", str(repo)).exit_code == 0
        monkeypatch.chdir(repo)

        result = invoke("hook", "pre-commit")

        assert result.exit_code == 0, result.output
        assert "Committing as personal" in result.output

    def test_local_override_in_bound_repo_is_blocked(self, env, monkeypatch):
        repo = make_repo(env / "project")
        assert invoke("bind", "personal", str(repo)).exit_code == 0
        monkeypatch.chdir(repo)
        subprocess.run(["git", "config", "user.email", "other@x"], check=True)

        result = invoke("hook", "pre-commit")

        assert result.exit_code == 1
        assert "profile 'personal' (bound to" in result.output


class TestCurrent:
    def test_current_shows_bound_profile_and_identity(self, env, monkeypatch):
        assert invoke("switch", "work").exit_code == 0
        repo = make_repo(env / "project")
        assert invoke("bind", "personal", str(repo)).exit_code == 0
        monkeypatch.chdir(repo)

        result = invoke("current")

        assert result.exit_code == 0
        assert "personal" in result.output
        assert "p@me.com" in result.output
