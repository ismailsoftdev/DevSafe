"""DevSafe initialization command."""

import shutil
from pathlib import Path

import typer
from rich.console import Console

console = Console()


def init_devsafe_in_repo() -> None:
    """Initialize DevSafe in the current git repository."""
    # Check if we're in a git repository
    git_dir = Path.cwd() / ".git"
    if not git_dir.exists():
        console.print("[red]Error: Not in a git repository![/red]")
        console.print("Run 'git init' first to initialize a git repository.")
        raise typer.Exit(1)
    
    # Create hooks directory if it doesn't exist
    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(exist_ok=True)
    
    # Path to DevSafe hooks
    devsafe_hooks_dir = Path(__file__).parent.parent.parent / "hooks"
    
    # Install pre-commit hook
    pre_commit_src = devsafe_hooks_dir / "pre-commit"
    pre_commit_dst = hooks_dir / "pre-commit"
    
    if pre_commit_src.exists():
        shutil.copy2(pre_commit_src, pre_commit_dst)
        pre_commit_dst.chmod(0o755)  # Make executable
        console.print("[green]✓[/green] Installed pre-commit hook")
    else:
        console.print("[yellow]Warning: DevSafe pre-commit hook not found[/yellow]")
    
    # Create .devsafe directory in repo
    repo_devsafe_dir = Path.cwd() / ".devsafe"
    repo_devsafe_dir.mkdir(exist_ok=True)
    
    console.print("[green]✓[/green] DevSafe initialized in repository")
    console.print("DevSafe will now validate your profile before commits!")
                      

if __name__ == "__main__":
    init_devsafe_in_repo()