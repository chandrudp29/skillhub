"""
skillhub — the package manager for AI agent skills.
"""
from __future__ import annotations

import subprocess
import webbrowser
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

app = typer.Typer(
    name="skillhub",
    help="The package manager for AI agent skills.",
    add_completion=False,
    rich_markup_mode="rich",
)
console = Console()

AGENTS = ["claude", "cursor", "codex", "gemini"]
AGENT_LABELS = {
    "claude": "[bold cyan]Claude Code[/]",
    "cursor": "[bold blue]Cursor[/]",
    "codex": "[bold green]Codex[/]",
    "gemini": "[bold yellow]Gemini CLI[/]",
}
AGENT_PATHS = {
    "claude": ".claude/commands/",
    "cursor": ".cursor/rules/",
    "codex": "AGENTS.md",
    "gemini": ".gemini/skills/",
}


def _agent_option():
    return typer.Option("claude", "--agent", "-a", help="Target agent: claude, cursor, codex, gemini")


@app.command()
def search(
    query: str = typer.Argument(..., help="Search term (name, tag, or description)"),
    tag: Optional[str] = typer.Option(None, "--tag", "-t", help="Filter by tag"),
):
    """Search available skills in the registry."""
    from .registry import search_skills

    console.print(f"\n[bold]Searching for[/] [cyan]{query}[/]...\n")
    results = search_skills(query, tags=[tag] if tag else None)

    if not results:
        console.print(f"[yellow]No skills found for '{query}'.[/] Try: [bold]skillhub list[/]")
        raise typer.Exit(1)

    table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
    table.add_column("Skill", style="bold cyan", min_width=24)
    table.add_column("Description", min_width=40)
    table.add_column("Agents", min_width=20)
    table.add_column("Tags", style="dim")

    for skill in results:
        agents_str = " ".join(f"[bold]{a[0].upper()}[/]" for a in skill.get("agents", ["claude"]))
        tags_str = ", ".join(skill.get("tags", []))
        table.add_row(
            skill["name"],
            skill.get("description", "")[:60] + ("…" if len(skill.get("description", "")) > 60 else ""),
            agents_str,
            tags_str,
        )

    console.print(table)
    console.print(f"\n[dim]{len(results)} skill(s) found. Install with:[/] [bold]skillhub install <name>[/]\n")


@app.command(name="list")
def list_skills(
    installed: bool = typer.Option(False, "--installed", "-i", help="Show only installed skills"),
    agent: str = _agent_option(),
):
    """List all available skills (or installed skills in this project)."""
    if installed:
        from .installer import list_installed
        skills = list_installed(agent)
        if not skills:
            console.print(f"[yellow]No skills installed for {agent} in this project.[/]")
            console.print(f"Install one: [bold]skillhub install research-agent[/]")
            return
        console.print(f"\n[bold]Installed skills[/] ({AGENT_LABELS.get(agent, agent)}):\n")
        for s in skills:
            console.print(f"  [green]✓[/] {s}")
        console.print()
        return

    from .registry import list_all_skills
    skills = list_all_skills()

    console.print()
    table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta", title="[bold]skillhub registry[/]")
    table.add_column("Name", style="bold cyan", min_width=26)
    table.add_column("Description", min_width=45)
    table.add_column("Agents")
    table.add_column("v", style="dim", min_width=6)

    for skill in skills:
        agents = skill.get("agents", ["claude"])
        agent_icons = " ".join(
            {"claude": "C", "cursor": "Cu", "codex": "Cx", "gemini": "G"}.get(a, a[0].upper())
            for a in agents
        )
        table.add_row(
            skill["name"],
            skill.get("description", "")[:55] + ("…" if len(skill.get("description", "")) > 55 else ""),
            agent_icons,
            skill.get("version", "1.0.0"),
        )

    console.print(table)
    console.print(f"\n[dim]{len(skills)} skills in registry · Install:[/] [bold]skillhub install <name>[/]\n")


@app.command()
def info(
    name: str = typer.Argument(..., help="Skill name"),
):
    """Show detailed information about a skill."""
    from .registry import get_skill, fetch_skill_content

    skill = get_skill(name)
    if not skill:
        console.print(f"[red]Skill '{name}' not found.[/] Try: [bold]skillhub search {name}[/]")
        raise typer.Exit(1)

    panel_content = Text()
    panel_content.append(f"{skill.get('description', '')}\n\n", style="white")
    panel_content.append("Author:   ", style="dim"); panel_content.append(f"{skill.get('author', 'skillhub-team')}\n", style="cyan")
    panel_content.append("Version:  ", style="dim"); panel_content.append(f"{skill.get('version', '1.0.0')}\n", style="cyan")
    panel_content.append("Agents:   ", style="dim"); panel_content.append(f"{', '.join(skill.get('agents', ['claude']))}\n", style="cyan")
    panel_content.append("Tags:     ", style="dim"); panel_content.append(f"{', '.join(skill.get('tags', []))}\n", style="cyan")

    console.print(Panel(panel_content, title=f"[bold cyan]{name}[/]", border_style="cyan"))
    console.print(f"\nInstall:  [bold]skillhub install {name}[/]")
    console.print(f"Compose:  [bold]skillhub compose {name} <other-skill>[/]\n")


@app.command()
def install(
    name: str = typer.Argument(..., help="Skill name to install"),
    agent: str = _agent_option(),
    all_agents: bool = typer.Option(False, "--all-agents", help="Install for all supported agents"),
    overwrite: bool = typer.Option(False, "--overwrite", "-f", help="Overwrite if already installed"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be installed without writing files"),
):
    """Install a skill into your project."""
    from .installer import install as _install
    from .registry import get_skill
    from .adapters import get_install_path, AGENTS

    # Validate skill exists first
    skill_meta = get_skill(name)
    if not skill_meta:
        console.print(f"[red]Error:[/] Skill '{name}' not found in registry.")
        console.print(f"Try: [bold]skillhub search {name}[/]")
        raise typer.Exit(1)

    agents_label = "all agents" if all_agents else AGENT_LABELS.get(agent, agent)

    if dry_run:
        console.print(f"\n[bold][DRY RUN][/] Would install [cyan]{name}[/] for {agents_label}:\n")
        targets = list(AGENTS.keys()) if all_agents else [agent]
        supported = skill_meta.get("agents", ["claude"])
        for tgt in targets:
            if tgt not in supported:
                continue
            path = get_install_path(tgt, name, Path.cwd())
            rel = path.relative_to(Path.cwd()) if path.is_absolute() else path
            exists = path.exists()
            status = "[yellow](exists)[/]" if exists else "[green](new)[/]"
            console.print(f"  {AGENT_LABELS.get(tgt, tgt)} → [dim]{rel}[/] {status}")
        console.print(f"\n[dim]Run without --dry-run to install.[/]\n")
        return

    console.print(f"\n[bold]Installing[/] [cyan]{name}[/] for {agents_label}...\n")

    try:
        installed = _install(name, agent=agent, all_agents=all_agents, overwrite=overwrite)
    except FileExistsError as e:
        console.print(f"[yellow]Already installed.[/] Use [bold]--overwrite[/] to replace.\n  {e}")
        raise typer.Exit(1)
    except ValueError as e:
        console.print(f"[red]Error:[/] {e}")
        raise typer.Exit(1)

    for tgt, path in installed.items():
        rel = path.relative_to(Path.cwd()) if path.is_absolute() else path
        console.print(f"  [green]✓[/] {AGENT_LABELS.get(tgt, tgt)} → [dim]{rel}[/]")

    console.print(f"\n[green]Done![/] Skill [bold]{name}[/] is ready.\n")


@app.command()
def uninstall(
    name: str = typer.Argument(..., help="Skill name to remove"),
    agent: str = _agent_option(),
):
    """Remove an installed skill from your project."""
    from .installer import uninstall as _uninstall

    console.print(f"\n[bold]Removing[/] [cyan]{name}[/]...\n")
    removed = _uninstall(name, agent=agent)
    if not removed:
        console.print(f"[yellow]Skill '{name}' not found in project.[/]")
        raise typer.Exit(1)
    for path in removed:
        console.print(f"  [red]✗[/] removed {path}")
    console.print()


@app.command()
def update(
    agent: str = _agent_option(),
):
    """Update all installed skills to their latest versions."""
    from .installer import list_installed, install as _install

    installed = list_installed(agent)
    if not installed:
        console.print(f"[yellow]No skills installed for {agent}.[/]")
        return

    console.print(f"\n[bold]Updating {len(installed)} skill(s)...[/]\n")
    for name in installed:
        try:
            _install(name, agent=agent, overwrite=True)
            console.print(f"  [green]✓[/] {name}")
        except Exception as e:
            console.print(f"  [red]✗[/] {name}: {e}")
    console.print()


@app.command()
def compose(
    skills: list[str] = typer.Argument(..., help="Two or more skill names to merge"),
    output: str = typer.Option("composed-skill", "--output", "-o", help="Name for the composed skill"),
    agent: str = _agent_option(),
    no_install: bool = typer.Option(False, "--no-install", help="Print composed skill, don't write to disk"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be composed without writing files"),
):
    """
    Compose multiple skills into one unified skill file.

    Example:
      skillhub compose research-agent rag-evaluator code-reviewer
    """
    from .composer import compose as _compose
    from .registry import get_skill
    from .adapters import get_install_path

    if len(skills) < 2:
        console.print("[red]Compose needs at least 2 skills.[/]")
        raise typer.Exit(1)

    # Validate all skills exist
    missing = [s for s in skills if not get_skill(s)]
    if missing:
        console.print(f"[red]Error:[/] Skill(s) not found: {', '.join(missing)}")
        raise typer.Exit(1)

    if dry_run:
        console.print(f"\n[bold][DRY RUN][/] Would compose:\n")
        for s in skills:
            skill_meta = get_skill(s)
            console.print(f"  [cyan]{s}[/] v{skill_meta.get('version', '1.0.0')}")
        console.print(f"\n  → Output: [bold]{output}[/]")
        path = get_install_path(agent, output, Path.cwd())
        rel = path.relative_to(Path.cwd()) if path.is_absolute() else path
        console.print(f"  → Path: [dim]{rel}[/]")
        console.print(f"\n[dim]Run without --dry-run to compose.[/]\n")
        return

    console.print(f"\n[bold]Composing[/] {' + '.join(f'[cyan]{s}[/]' for s in skills)} → [bold]{output}[/]\n")

    try:
        composed, conflicts = _compose(
            skills,
            output_name=output,
            agent=agent,
            install=not no_install,
        )
    except (ValueError, RuntimeError) as e:
        console.print(f"[red]Error:[/] {e}")
        raise typer.Exit(1)

    if conflicts:
        console.print("[yellow]Conflicts resolved (first-writer wins):[/]")
        for c in conflicts:
            console.print(f"  [yellow]⚠[/] {c}")
        console.print()

    if no_install:
        console.print(Panel(composed, title="[bold]Composed Skill[/]", border_style="cyan"))
    else:
        path_template = AGENT_PATHS.get(agent, ".claude/commands/{name}.md")
        out_path = path_template.format(name=output) if "{name}" in path_template else path_template
        console.print(f"[green]✓[/] Written to [bold]{out_path}[/]\n")


@app.command()
def publish(
    path: Path = typer.Argument(Path("."), help="Path to your skill directory"),
):
    """
    Publish a skill to the skillhub registry (opens a GitHub PR).
    """
    skill_md = path / "SKILL.md"
    skill_json = path / "skill.json"

    if not skill_md.exists():
        console.print(f"[red]No SKILL.md found in {path}[/]")
        console.print("A skill needs at minimum a [bold]SKILL.md[/] with frontmatter (name, description).")
        raise typer.Exit(1)

    console.print(Panel(
        "[bold]Publishing to skillhub registry[/]\n\n"
        "Skills are added via GitHub Pull Request so the community can review quality.\n\n"
        "[bold]Steps:[/]\n"
        "1. Fork [cyan]https://github.com/chandrudp29/skillhub[/]\n"
        "2. Add your skill folder under [bold]skills/<your-skill-name>/[/]\n"
        "3. Add an entry to [bold]registry/index.json[/]\n"
        "4. Open a PR — use the PR template provided\n\n"
        "Run [bold]skillhub publish --help[/] or see [cyan]CONTRIBUTING.md[/] for full guide.",
        title="[bold cyan]Publish Skill[/]",
        border_style="cyan",
    ))

    open_browser = typer.confirm("\nOpen GitHub to fork the repo now?", default=True)
    if open_browser:
        webbrowser.open("https://github.com/chandrudp29/skillhub/fork")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    [bold cyan]skillhub[/] — the package manager for AI agent skills.

    Install, compose, and publish skills for Claude Code, Cursor, Codex, and Gemini CLI.

    [bold]Quick start:[/]
      skillhub install research-agent
      skillhub compose research-agent rag-evaluator
      skillhub list
    """
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())
