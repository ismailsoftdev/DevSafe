"""DevSafe CLI entry point."""

import sys
from pathlib import Path

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
    """Show current profile information."""
    config = load_config()
    
    if not config.current_profile:
        console.print("[yellow]No profile is currently active.[/yellow]")
        console.print("Use 'devsafe switch <profile>' to activate a profile.")
        return
    
    current_git_config = git_manager.get_current_config()
    
    table = Table(show_header=True, header_style="bold blue", title="Current Profile")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("Profile", config.current_profile)
    
    if "user.name" in current_git_config:
        table.add_row("Name", current_git_config["user.name"])
    if "user.email" in current_git_config:
        table.add_row("Email", current_git_config["user.email"])
    if "user.signingkey" in current_git_config:
        table.add_row("GPG Key", current_git_config["user.signingkey"])
    if "commit.gpgsign" in current_git_config:
        table.add_row("GPG Signing", current_git_config["commit.gpgsign"])
    
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
    
    # Confirm removal
    if not force:
        if not typer.confirm(f"Are you sure you want to remove profile '{profile_name}'?"):
            console.print("Cancelled.")
            return
    
    # Remove profile
    if config.remove_profile(profile_name):
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
        # Update current profile in config
        config.switch_profile(profile_name)
        if config_manager.save_config(config):
            console.print(f"[green]✓[/green] Switched to profile '{profile_name}'")
            console.print(f"Git name: {profile.name}")
            console.print(f"Git email: {profile.email}")
        else:
            console.print("[yellow]Profile applied but failed to save configuration.[/yellow]")
    else:
        console.print("[red]Failed to apply profile configuration![/red]")
        raise typer.Exit(1)


def cli_main() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    cli_main()