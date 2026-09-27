"""DevSafe initialization command."""

import shutil
from pathlib import Path

import typer
from rich.console import Console

from devsafe.core import GitConfigManager

console = Console()

# Shipped inside the package so it is present in wheel installs
HOOK_SOURCE = Path(__file__).parent.parent / "hooks" / "pre-commit"


def init_devsafe_in_repo(force: bool = False) -> None:
    """Initialize DevSafe in the current git repository."""
    git_manager = GitConfigManager()

    # Check if we're in a git repository (works from subdirectories/worktrees)
    hooks_dir = git_manager.get_hooks_dir()
    repo_root = git_manager.get_repository_root()
    if hooks_dir is None or repo_root is None:
        console.print("[red]Error: Not in a git repository![/red]")
        console.print("Run 'git init' first to initialize a git repository.")
        raise typer.Exit(1)

    if not HOOK_SOURCE.exists():
        console.print(f"[red]Error: DevSafe pre-commit hook not found at {HOOK_SOURCE}[/red]")
        console.print("Your DevSafe installation may be incomplete; try reinstalling it.")
        raise typer.Exit(1)

    # Create hooks directory if it doesn't exist
    hooks_dir.mkdir(parents=True, exist_ok=True)
    pre_commit_dst = hooks_dir / "pre-commit"

    install = True
    if pre_commit_dst.exists():
        if pre_commit_dst.read_bytes() == HOOK_SOURCE.read_bytes():
            console.print("[green]✓[/green] Pre-commit hook already installed")
            install = False
        elif not force:
            console.print(f"[red]Error: A pre-commit hook already exists at {pre_commit_dst}[/red]")
            console.print("Re-run with --force to replace it (the existing hook will be backed up).")
            raise typer.Exit(1)
        else:
            backup = pre_commit_dst.with_name("pre-commit.devsafe-backup")
            shutil.copy2(pre_commit_dst, backup)
            console.print(f"[yellow]Backed up existing hook to {backup}[/yellow]")

    if install:
        shutil.copy2(HOOK_SOURCE, pre_commit_dst)
        pre_commit_dst.chmod(0o755)  # Make executable
        console.print("[green]✓[/green] Installed pre-commit hook")

    # Create .devsafe directory in repo
    repo_devsafe_dir = repo_root / ".devsafe"
    repo_devsafe_dir.mkdir(exist_ok=True)

    console.print("[green]✓[/green] DevSafe initialized in repository")
    console.print("DevSafe will now validate your profile before commits!")


if __name__ == "__main__":
    init_devsafe_in_repo()
