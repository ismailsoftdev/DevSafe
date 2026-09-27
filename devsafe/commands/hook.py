"""Git hook logic, run by the installed hook via `devsafe hook pre-commit`."""

from rich.console import Console

from devsafe.core import GitConfigManager
from devsafe.utils import ConfigError, ConfigManager

# No hard wrapping: git shows hook output verbatim, and wrapped commands mislead
console = Console(soft_wrap=True)


def run_pre_commit(config_manager: ConfigManager, git_manager: GitConfigManager) -> int:
    """Check git's identity against the active profile. Returns the exit code."""
    if not config_manager.config_file.exists():
        # DevSafe not configured, allow commit
        return 0

    try:
        config = config_manager.load_config()
    except ConfigError as e:
        # Don't block commits because DevSafe itself is misconfigured
        console.print(f"⚠️  DevSafe: {e}")
        console.print("Skipping profile check.")
        return 0

    # A directory binding takes precedence over the global active profile
    git_dir = git_manager.get_git_dir()
    binding = config.resolve_binding(git_dir) if git_dir else None
    if binding:
        bound_directory, profile_name = binding
        profile = config.profiles.get(profile_name)
        if profile is None:
            console.print(
                f"⚠️  {bound_directory} is bound to profile '{profile_name}', which doesn't exist!",
                markup=False,
            )
            console.print(f"Run 'devsafe unbind \"{bound_directory}\"' or bind it to another profile.", markup=False)
            return 1
        description = f"profile '{profile_name}' (bound to {bound_directory})"
    else:
        profile_name = config.current_profile
        profile = config.get_current_profile()
        if profile is None:
            console.print("⚠️  No active DevSafe profile!")
            console.print("Use 'devsafe switch <profile>' to set an active profile.")
            return 1
        description = f"active profile '{profile_name}'"

    identity = git_manager.get_effective_identity()
    name = identity.get("user.name")
    email = identity.get("user.email")

    if name != profile.name or email != str(profile.email):
        console.print(f"⚠️  Git configuration doesn't match {description}!", markup=False)
        console.print(f"Expected: {profile.name} <{profile.email}>", markup=False)
        console.print(f"Current:  {name or 'Unknown'} <{email or 'Unknown'}>", markup=False)
        origin = git_manager.get_identity_origin("user.email")
        if origin:
            console.print(f"Your email is set in: {origin}", markup=False)
        if binding:
            console.print(
                "Something overrides the binding here; check 'git config --local --list'.",
                markup=False,
            )
        else:
            console.print(f"Run 'devsafe switch {profile_name}' to fix this.", markup=False)
            console.print(
                "If it still doesn't match, this repository overrides your identity; "
                "check 'git config --local --list'.",
                markup=False,
            )
        return 1

    console.print(f"✅ Committing as {profile_name}: {name} <{email}>", markup=False)
    return 0
