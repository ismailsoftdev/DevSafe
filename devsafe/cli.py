"""DevSafe CLI entry point."""

import sys
from pathlib import Path
from typing import Dict, Optional, Tuple
from urllib.parse import quote

import typer
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table

from devsafe import __description__, __version__
from devsafe.core import GitConfigManager
from devsafe.models import DevSafeConfig, Profile
from devsafe.utils import ConfigError, ConfigManager

console = Console()
app = typer.Typer(
    name="devsafe",
    help=__description__,
    rich_markup_mode="rich",
    add_completion=False,
)

# Initialize managers
config_manager = ConfigManager()
git_manager = GitConfigManager()


def load_config() -> DevSafeConfig:
    """Load the config, exiting instead of continuing with an empty one."""
    try:
        return config_manager.load_config()
    except ConfigError as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print("Fix or remove the config file, then try again.")
        raise typer.Exit(1)


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        console.print(f"DevSafe version: {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True,
        help="Show version and exit"
    ),
) -> None:
    """
    DevSafe - Git profile manager for developers.
    
    Never commit with the wrong credentials again! 🚀
    """
    pass


@app.command()
def add(
    profile_name: str = typer.Argument(..., help="Name of the profile to add"),
    name: str = typer.Option(None, "--name", "-n", help="Full name for git commits"),
    email: str = typer.Option(None, "--email", "-e", help="Email address for git commits"),
    ssh_key: str = typer.Option(None, "--ssh-key", "-s", help="Path to SSH private key"),
    signing_key: str = typer.Option(None, "--signing-key", "-g", help="GPG signing key ID"),
    description: str = typer.Option(None, "--description", "-d", help="Profile description"),
) -> None:
    """Add a new git profile."""
    config = load_config()
    
    # Check if profile already exists
    if profile_name in config.profiles:
        console.print(f"[red]Profile '{profile_name}' already exists![/red]")
        console.print("Use 'devsafe edit' to modify existing profiles.")
        raise typer.Exit(1)
    
    # Interactive input if options not provided
    if not name:
        name = typer.prompt("Full name")
    if not email:
        email = typer.prompt("Email address")
    
    # Optional fields
    if not ssh_key:
        ssh_key_input = typer.prompt("SSH key path (optional)", default="", show_default=False)
        ssh_key = ssh_key_input if ssh_key_input else None
    
    if not signing_key:
        signing_key_input = typer.prompt("GPG signing key ID (optional)", default="", show_default=False)
        signing_key = signing_key_input if signing_key_input else None
    
    if not description:
        description_input = typer.prompt("Profile description (optional)", default="", show_default=False)
        description = description_input if description_input else None
    
    if ssh_key and not Path(ssh_key).expanduser().exists():
        console.print(f"[red]SSH key file not found: {Path(ssh_key).expanduser()}[/red]")
        raise typer.Exit(1)

    try:
        # Create profile
        profile = Profile(
            name=name,
            email=email,
            ssh_key=Path(ssh_key) if ssh_key else None,
            signing_key=signing_key,
            description=description,
        )
    except ValidationError as e:
        console.print(f"[red]Error creating profile: {e}[/red]")
        raise typer.Exit(1)

    # Add to config
    config.add_profile(profile_name, profile)

    # Save config
    if not config_manager.save_config(config):
        console.print("[red]Failed to save configuration![/red]")
        raise typer.Exit(1)

    console.print(f"[green]✓[/green] Profile '{profile_name}' added successfully!")

    # Ask if user wants to switch to this profile
    if typer.confirm("Switch to this profile now?", default=True):
        switch_to_profile(profile_name, config)


@app.command()
def list() -> None:
    """List all profiles."""
    config = load_config()
    
    if not config.profiles:
        console.print("[yellow]No profiles found. Use 'devsafe add' to create one.[/yellow]")
        return
    
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Profile", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Email", style="white")
    table.add_column("SSH Key", style="dim")
    table.add_column("GPG", style="dim")
    table.add_column("Description", style="dim")
    table.add_column("Status", style="green")
    
    for profile_name, profile in config.profiles.items():
        status = "🟢 Active" if profile_name == config.current_profile else ""
        ssh_key = str(profile.ssh_key) if profile.ssh_key else ""
        gpg_key = profile.signing_key or ""
        description = profile.description or ""
        
        table.add_row(
            profile_name,
            profile.name,
            str(profile.email),
            ssh_key,
            gpg_key,
            description,
            status,
        )
    
    console.print(table)


@app.command()
def switch(
    profile_name: str = typer.Argument(..., help="Name of the profile to switch to"),
) -> None:
    """Switch to a different profile."""
    config = load_config()
    switch_to_profile(profile_name, config)


@app.command()
def current() -> None:
    """Show which profile and git identity apply in the current directory."""
    config = load_config()
    binding = resolve_binding_here(config)

    if not config.current_profile and binding is None:
        console.print("[yellow]No profile is currently active.[/yellow]")
        console.print("Use 'devsafe switch <profile>' to activate a profile.")
        return

    identity = git_manager.get_effective_identity(
        ("user.name", "user.email", "user.signingkey", "commit.gpgsign")
    )

    table = Table(show_header=True, header_style="bold blue", title="Current Profile")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Active profile", config.current_profile or "None")
    if binding:
        table.add_row("Bound profile", f"{binding[1]} (for {display_path(binding[0])})")

    if "user.name" in identity:
        table.add_row("Name", identity["user.name"])
    if "user.email" in identity:
        table.add_row("Email", identity["user.email"])
        origin = git_manager.get_identity_origin("user.email")
        if origin:
            table.add_row("Set in", display_path(origin[len("file:"):]) if origin.startswith("file:") else origin)
    if "user.signingkey" in identity:
        table.add_row("GPG Key", identity["user.signingkey"])
    if "commit.gpgsign" in identity:
        table.add_row("GPG Signing", identity["commit.gpgsign"])

    console.print(table)

    if binding and git_manager.get_git_dir() is None:
        console.print(f"[dim]Profile '{binding[1]}' applies inside git repositories here.[/dim]")


@app.command()
def bind(
    profile_name: str = typer.Argument(..., help="Profile to use in the directory"),
    path: Optional[Path] = typer.Argument(
        None, help="Directory to bind (default: the current repository's root, else the current directory)"
    ),
) -> None:
    """Use a profile for every git repository inside a directory."""
    config = load_config()

    if profile_name not in config.profiles:
        console.print(f"[red]Profile '{profile_name}' not found![/red]")
        console.print("Use 'devsafe list' to see available profiles.")
        raise typer.Exit(1)

    directory = resolve_bind_path(path)
    if not directory.is_dir():
        console.print(f"[red]Not a directory: {directory}[/red]")
        raise typer.Exit(1)

    previous_bindings = dict(config.bindings)
    config.bindings[str(directory)] = profile_name
    update_bindings(config, previous_bindings)

    profile = config.profiles[profile_name]
    console.print(f"[green]✓[/green] Bound {display_path(directory)} to profile '{profile_name}'")
    console.print(f"Repositories inside it now commit as {profile.name} <{profile.email}>")

    # If we're in a repository this binding applies to, confirm git agrees
    here = resolve_binding_here(config)
    if git_manager.get_git_dir() is not None and here is not None and here[0] == str(directory):
        identity = git_manager.get_effective_identity()
        if identity.get("user.email") != str(profile.email):
            origin = git_manager.get_identity_origin("user.email") or "unknown"
            console.print(
                f"[yellow]Warning: this repository still uses {identity.get('user.email')} "
                f"(set in {origin}), which overrides the binding.[/yellow]"
            )


@app.command()
def unbind(
    path: Optional[Path] = typer.Argument(
        None, help="Bound directory (default: the current repository's root, else the current directory)"
    ),
) -> None:
    """Remove a directory's profile binding."""
    config = load_config()
    directory = str(resolve_bind_path(path))

    if directory not in config.bindings:
        console.print(f"[red]No binding for {display_path(directory)}[/red]")
        covering = config.resolve_binding(Path(directory))
        if covering:
            console.print(
                f"It is covered by the binding for {display_path(covering[0])} (profile '{covering[1]}'). "
                f"To remove that, run: devsafe unbind \"{covering[0]}\""
            )
        raise typer.Exit(1)

    previous_bindings = dict(config.bindings)
    profile_name = config.bindings.pop(directory)
    update_bindings(config, previous_bindings)
    console.print(f"[green]✓[/green] Removed binding of {display_path(directory)} to profile '{profile_name}'")


@app.command()
def bindings() -> None:
    """List directories bound to profiles."""
    config = load_config()

    if not config.bindings:
        console.print("[yellow]No bindings. Use 'devsafe bind <profile> \\[path]' to add one.[/yellow]")
        return

    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Directory", style="cyan")
    table.add_column("Profile", style="white")
    table.add_column("Identity", style="white")

    for directory, profile_name in sorted(config.bindings.items()):
        profile = config.profiles.get(profile_name)
        identity = f"{profile.name} <{profile.email}>" if profile else "[red]profile missing[/red]"
        shown_directory = display_path(directory) if Path(directory).is_dir() else f"{display_path(directory)} [red](missing)[/red]"
        table.add_row(shown_directory, profile_name, identity)

    console.print(table)


@app.command()
def remove(
    profile_name: str = typer.Argument(..., help="Name of the profile to remove"),
    force: bool = typer.Option(False, "--force", "-f", help="Force removal without confirmation"),
) -> None:
    """Remove a profile."""
    config = load_config()
    
    if profile_name not in config.profiles:
        console.print(f"[red]Profile '{profile_name}' not found![/red]")
        raise typer.Exit(1)
    
    bound_directories = [d for d, p in config.bindings.items() if p == profile_name]

    # Confirm removal
    if not force:
        if bound_directories:
            console.print(f"Profile '{profile_name}' is bound to these directories, which will be unbound:")
            for directory in bound_directories:
                console.print(f"  {directory}")
        if not typer.confirm(f"Are you sure you want to remove profile '{profile_name}'?"):
            console.print("Cancelled.")
            return

    # Remove profile
    if config.remove_profile(profile_name):
        if bound_directories:
            for directory in bound_directories:
                del config.bindings[directory]
            if not sync_bindings(config):
                console.print("[red]Failed to update git configuration for bindings![/red]")
                raise typer.Exit(1)
        if config_manager.save_config(config):
            console.print(f"[green]✓[/green] Profile '{profile_name}' removed successfully!")
        else:
            console.print("[red]Failed to save configuration![/red]")
            raise typer.Exit(1)
    else:
        console.print(f"[red]Failed to remove profile '{profile_name}'![/red]")
        raise typer.Exit(1)


@app.command()
def init(
    force: bool = typer.Option(
        False, "--force", "-f",
        help="Replace an existing pre-commit hook (it is backed up first)"
    ),
) -> None:
    """Initialize DevSafe in the current git repository."""
    from devsafe.commands.init import init_devsafe_in_repo
    init_devsafe_in_repo(force=force)


hook_app = typer.Typer(help="Git hook entry points (run by installed hooks).")
app.add_typer(hook_app, name="hook", hidden=True)


@hook_app.command("pre-commit")
def hook_pre_commit() -> None:
    """Validate the active profile before a commit."""
    from devsafe.commands.hook import run_pre_commit
    raise typer.Exit(run_pre_commit(config_manager, git_manager))


@app.command()
def status() -> None:
    """Show DevSafe status and configuration."""
    # Validate git installation
    git_valid, git_version = git_manager.validate_git_installation()
    
    console.print("[bold blue]DevSafe Status[/bold blue]")
    console.print(f"Version: {__version__}")
    console.print(f"Git: {'✓' if git_valid else '✗'} {git_version}")
    
    # Configuration info
    config_info = config_manager.get_config_info()
    console.print(f"Config directory: {config_info['config_dir']}")
    console.print(f"Config file: {'✓' if config_info['config_exists'] else '✗'} {config_info['config_file']}")
    
    # Load config
    config = load_config()
    console.print(f"Profiles: {len(config.profiles)}")
    console.print(f"Current profile: {config.current_profile or 'None'}")
    console.print(f"Bindings: {len(config.bindings)}")
    console.print(f"Auto-switch: {'✓' if config.auto_switch else '✗'}")
    console.print(f"Hooks enabled: {'✓' if config.hooks_enabled else '✗'}")
    
    # Repository info
    repo_info = git_manager.get_repository_info()
    if repo_info:
        console.print("\n[bold blue]Current Repository[/bold blue]")
        console.print(f"Root: {repo_info.get('root', 'Unknown')}")
        console.print(f"Branch: {repo_info.get('branch', 'Unknown')}")
        console.print(f"Origin: {repo_info.get('origin', 'No remote')}")
    else:
        console.print("\n[yellow]Not in a git repository[/yellow]")


def switch_to_profile(profile_name: str, config: DevSafeConfig) -> None:
    """Helper function to switch to a profile."""
    if profile_name not in config.profiles:
        console.print(f"[red]Profile '{profile_name}' not found![/red]")
        console.print("Use 'devsafe list' to see available profiles.")
        raise typer.Exit(1)
    
    profile = config.profiles[profile_name]
    
    # Backup current config if enabled
    if config.backup_enabled:
        git_manager.backup_current_config()
    
    # Apply profile configuration
    profile_config = profile.to_dict()
    
    if git_manager.apply_profile_config(profile_config):
        # Setting global values may have appended a [user] section after the
        # binding rules; re-add them last so bindings keep precedence
        if config.bindings and not sync_bindings(config):
            console.print("[yellow]Warning: failed to refresh directory bindings.[/yellow]")

        # Update current profile in config
        config.switch_profile(profile_name)
        if config_manager.save_config(config):
            console.print(f"[green]✓[/green] Switched to profile '{profile_name}'")
            console.print(f"Git name: {profile.name}")
            console.print(f"Git email: {profile.email}")

            binding = resolve_binding_here(config)
            if binding and binding[1] != profile_name:
                console.print(
                    f"[yellow]Note: {display_path(binding[0])} is bound to profile '{binding[1]}'; "
                    "repositories there keep using it.[/yellow]"
                )
        else:
            console.print("[yellow]Profile applied but failed to save configuration.[/yellow]")
    else:
        console.print("[red]Failed to apply profile configuration![/red]")
        raise typer.Exit(1)


def display_path(path) -> str:
    """Show a path with the home directory abbreviated to ~."""
    home = str(Path.home())
    text = str(path)
    return "~" + text[len(home):] if text == home or text.startswith(home + "/") else text


def resolve_bind_path(path: Optional[Path]) -> Path:
    """Directory a bind/unbind refers to: given path, else repo root, else cwd."""
    if path is not None:
        return path.expanduser().resolve()
    return (git_manager.get_repository_root() or Path.cwd()).resolve()


def resolve_binding_here(config: DevSafeConfig) -> Optional[Tuple[str, str]]:
    """Binding that applies here, matched the way git matches includeIf gitdir."""
    return config.resolve_binding(git_manager.get_git_dir() or Path.cwd())


def profile_config_file(profile_name: str) -> Path:
    """Generated git config file for a profile, included for bound directories."""
    return config_manager.config_dir / "profiles" / f"{quote(profile_name, safe='')}.gitconfig"


def sync_bindings(config: DevSafeConfig) -> bool:
    """Write bound profiles' config files and update git's includeIf rules."""
    profiles_dir = config_manager.config_dir / "profiles"
    success = True
    includes = []

    for directory, profile_name in config.bindings.items():
        if profile_name not in config.profiles:
            console.print(f"[yellow]Skipping binding of {directory}: profile '{profile_name}' not found[/yellow]")
            continue
        includes.append((directory, profile_config_file(profile_name)))

    bound_files = {config_file for _, config_file in includes}
    for profile_name, profile in config.profiles.items():
        config_file = profile_config_file(profile_name)
        if config_file in bound_files:
            success = git_manager.write_config_file(config_file, profile.to_include_config()) and success

    success = git_manager.sync_directory_includes(includes, profiles_dir) and success

    # Remove files of profiles that are no longer bound
    if profiles_dir.is_dir():
        for config_file in profiles_dir.glob("*.gitconfig"):
            if config_file not in bound_files:
                config_file.unlink()

    return success


def update_bindings(config: DevSafeConfig, previous_bindings: Dict[str, str]) -> None:
    """Apply changed bindings to git and save them, rolling back on failure."""
    if sync_bindings(config) and config_manager.save_config(config):
        return

    config.bindings = previous_bindings
    sync_bindings(config)
    console.print("[red]Failed to update bindings; no changes were made.[/red]")
    raise typer.Exit(1)


def cli_main() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    cli_main()