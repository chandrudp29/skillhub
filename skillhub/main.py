"""
skillhub — the package manager for AI agent skills.
"""
from __future__ import annotations

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

__version__ = "0.3.0"

COMPOSE_TEMPLATES: dict[str, dict] = {
    "fastapi-expert": {
        "skills": ["python-patterns", "security-review", "api-design"],
        "description": "FastAPI backend expert: Python best practices + OWASP security + REST design",
    },
    "fullstack-expert": {
        "skills": ["react-patterns", "python-patterns", "api-design"],
        "description": "Full-stack expert: React 18+ frontend + Python backend + REST API",
    },
    "ml-platform": {
        "skills": ["agent-builder", "mle-workflow", "llm-evaluator"],
        "description": "ML platform engineer: LangGraph agents + ML workflow + LLM evaluation",
    },
    "pre-pr-reviewer": {
        "skills": ["code-reviewer", "security-review", "test-writer"],
        "description": "Pre-PR expert: code quality + security audit + test coverage",
    },
    "research-analyst": {
        "skills": ["research-agent", "rag-evaluator", "doc-generator"],
        "description": "Research analyst: deep research + RAG evaluation + documentation",
    },
}


def _suggest_similar(name: str, threshold: float = 0.6) -> list[str]:
    """Find similar skill names for 'did you mean' suggestions."""
    from difflib import SequenceMatcher
    from .registry import list_all_skills

    skills = list_all_skills()
    suggestions = []
    for skill in skills:
        skill_name = skill["name"]
        ratio = SequenceMatcher(None, name.lower(), skill_name.lower()).ratio()
        if ratio >= threshold or name.lower() in skill_name.lower():
            suggestions.append((ratio, skill_name))

    # Sort by similarity and return top 3
    suggestions.sort(reverse=True, key=lambda x: x[0])
    return [s[1] for s in suggestions[:3]]


def _version_callback(value: bool):
    if value:
        console.print(f"skillhub version {__version__}")
        raise typer.Exit()

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
            console.print("Install one: [bold]skillhub install research-agent[/]")
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
    from .registry import get_skill

    skill = get_skill(name)
    if not skill:
        console.print(f"[red]Skill '{name}' not found.[/]")
        suggestions = _suggest_similar(name)
        if suggestions:
            console.print(f"[yellow]Did you mean:[/] {', '.join(f'[cyan]{s}[/]' for s in suggestions)}")
        console.print(f"\nTry: [bold]skillhub search {name}[/] or [bold]skillhub list[/]")
        raise typer.Exit(1)

    panel_content = Text()
    panel_content.append(f"{skill.get('description', '')}\n\n", style="white")
    panel_content.append("Author:   ", style="dim")
    panel_content.append(f"{skill.get('author', 'skillhub-team')}\n", style="cyan")
    panel_content.append("Version:  ", style="dim")
    panel_content.append(f"{skill.get('version', '1.0.0')}\n", style="cyan")
    panel_content.append("Agents:   ", style="dim")
    panel_content.append(f"{', '.join(skill.get('agents', ['claude']))}\n", style="cyan")
    panel_content.append("Tags:     ", style="dim")
    panel_content.append(f"{', '.join(skill.get('tags', []))}\n", style="cyan")

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
        suggestions = _suggest_similar(name)
        if suggestions:
            console.print(f"[yellow]Did you mean:[/] {', '.join(f'[cyan]{s}[/]' for s in suggestions)}")
        console.print(f"\nTry: [bold]skillhub search {name}[/] or [bold]skillhub list[/]")
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
        console.print("\n[dim]Run without --dry-run to install.[/]\n")
        return

    console.print(f"\n[bold]Installing[/] [cyan]{name}[/] for {agents_label}...\n")

    try:
        installed = _install(name, agent=agent, all_agents=all_agents, overwrite=overwrite)
    except FileExistsError as e:
        console.print(f"[yellow]Already installed.[/] Use [bold]--overwrite[/] to replace.\n  {e}")
        raise typer.Exit(1)
    except PermissionError:
        console.print("[red]Error:[/] Cannot write to the current directory.\n")
        console.print("  [dim]You need to be inside your project folder. Run:[/]")
        console.print("  cd your-project")
        console.print(f"  skillhub install {name}\n")
        console.print("  [dim]Or create a new project folder:[/]")
        console.print("  mkdir my-project && cd my-project")
        console.print(f"  skillhub install {name}\n")
        raise typer.Exit(1)
    except ValueError as e:
        console.print(f"[red]Error:[/] {e}")
        raise typer.Exit(1)

    agents_installed = set(installed.keys())
    for tgt, path in installed.items():
        rel = path.relative_to(Path.cwd()) if path.is_absolute() else path
        console.print(f"  [green]✓[/] {AGENT_LABELS.get(tgt, tgt)} → [dim]{rel}[/]")

    console.print(f"\n[green]Done![/] Skill [bold]{name}[/] is ready.")

    if "claude" in agents_installed:
        console.print(f"  [dim]→ In Claude Code, type [bold]/{name}[/] to use it.[/]")
        console.print("  [dim]→ Restart Claude Code if the command isn't showing yet.[/]")
    console.print()


@app.command()
def uninstall(
    name: str = typer.Argument(..., help="Skill name to remove"),
    agent: str = _agent_option(),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
):
    """Remove an installed skill from your project."""
    from .installer import uninstall as _uninstall
    from .adapters import get_install_path

    # Check if skill exists first
    path = get_install_path(agent, name, Path.cwd())
    if not path.exists() and agent != "codex":
        console.print(f"[yellow]Skill '{name}' not found in project.[/]")
        console.print("Check installed skills: [bold]skillhub list --installed[/]")
        raise typer.Exit(1)

    # Show what will be removed and confirm
    if not yes:
        rel_path = path.relative_to(Path.cwd()) if path.is_absolute() else path
        console.print(f"\n[bold]Will remove:[/] [dim]{rel_path}[/]")
        if not typer.confirm("Continue?", default=True):
            console.print("[dim]Cancelled.[/]")
            raise typer.Exit(0)

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
    skills: list[str] = typer.Argument(None, help="Skill names or sources to merge (skills.sh:name, github:owner/repo/path, ./local.md)"),
    output: str = typer.Option("composed-skill", "--output", "-o", help="Name for the composed skill"),
    agent: str = _agent_option(),
    strategy: str = typer.Option("first-wins", "--strategy", "-s", help="Merge strategy: first-wins or ai"),
    template: Optional[str] = typer.Option(None, "--template", "-t", help="Use a pre-built compose template"),
    no_install: bool = typer.Option(False, "--no-install", help="Print composed skill, don't write to disk"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be composed without writing files"),
):
    """
    Compose multiple skills into one unified skill file.

    Pull from any source: skillhub registry, skills.sh, GitHub, or local files.

    Pull from any source and merge:

      skillhub compose python-patterns security-review -o secure-python
      skillhub compose python-patterns security-review -o secure-python --strategy ai
      skillhub compose --template fastapi-expert

    Cross-platform — merge skills already installed across different agents:

      skillhub compose claude:debug-agent cursor:debug-agent -o unified-debug
      skillhub compose claude:python-patterns cursor:react-patterns -o fullstack

    Cross-ecosystem — pull from any registry:

      skillhub compose agency-agents:frontend-developer python-patterns -o frontend-expert
      skillhub compose skills.sh:react-expert ./my-team-skill.md -o team-expert
      skillhub compose github:addyosmani/agent-skills/skills/code-review-and-quality/SKILL.md debug-agent -o reviewer

    Source prefixes:
      name                        skillhub registry
      claude:name                 installed in Claude Code  (.claude/commands/)
      cursor:name                 installed in Cursor       (.cursor/rules/)
      codex:name                  installed in Codex        (AGENTS.md block)
      gemini:name                 installed in Gemini CLI   (.gemini/skills/)
      agency-agents:name          msitarzewski/agency-agents repo
      skills.sh:name              Vercel skills.sh registry
      github:owner/repo/path.md   any public GitHub file
      ./path/to/skill.md          local file on disk
    """
    from .composer import compose as _compose, _is_external
    from .registry import get_skill
    from .adapters import get_install_path

    # Expand template
    if template:
        if template not in COMPOSE_TEMPLATES:
            console.print(f"[red]Unknown template '{template}'.[/] Available:")
            for name, t in COMPOSE_TEMPLATES.items():
                console.print(f"  [cyan]{name}[/]  [dim]{t['description']}[/]")
            raise typer.Exit(1)
        tmpl = COMPOSE_TEMPLATES[template]
        skills = tmpl["skills"]
        if output == "composed-skill":
            output = template
        console.print(f"\n[dim]Template:[/] [bold]{template}[/]")
        console.print(f"[dim]Expands to:[/] {' + '.join(f'[cyan]{s}[/]' for s in skills)}\n")

    if not skills or len(skills) < 2:
        console.print("[red]Compose needs at least 2 skills (or use --template).[/]")
        console.print("\nExamples:")
        console.print("  skillhub compose python-patterns security-review -o secure-python")
        console.print("  skillhub compose --template fastapi-expert")
        console.print("  skillhub templates")
        raise typer.Exit(1)

    if strategy not in ("first-wins", "ai"):
        console.print("[red]--strategy must be 'first-wins' or 'ai'[/]")
        raise typer.Exit(1)

    # Validate registry skills (skip external sources)
    missing = [s for s in skills if not _is_external(s) and not get_skill(s)]
    if missing:
        console.print(f"[red]Error:[/] Skill(s) not found in registry: {', '.join(missing)}")
        console.print(f"Tip: [dim]Use 'skills.sh:name' to pull from skills.sh, or check: skillhub list[/]")
        raise typer.Exit(1)

    if dry_run:
        console.print("\n[bold][DRY RUN][/] Would compose:\n")
        for s in skills:
            prefix = "[dim](external)[/] " if _is_external(s) else ""
            console.print(f"  [cyan]{s}[/] {prefix}")
        console.print(f"\n  → Output: [bold]{output}[/]")
        console.print(f"  → Strategy: [bold]{strategy}[/]")
        path = get_install_path(agent, output, Path.cwd())
        rel = path.relative_to(Path.cwd()) if path.is_absolute() else path
        console.print(f"  → Path: [dim]{rel}[/]")
        console.print("\n[dim]Run without --dry-run to compose.[/]\n")
        return

    strategy_label = "[bold magenta]AI-powered merge[/]" if strategy == "ai" else "first-wins"
    console.print(f"\n[bold]Composing[/] {' + '.join(f'[cyan]{s}[/]' for s in skills)}")
    console.print(f"[dim]Strategy:[/] {strategy_label}  →  [bold]{output}[/]\n")

    try:
        composed, conflicts = _compose(
            skills,
            output_name=output,
            agent=agent,
            install=not no_install,
            strategy=strategy,
        )
    except (ValueError, RuntimeError) as e:
        console.print(f"[red]Error:[/] {e}")
        raise typer.Exit(1)

    if conflicts:
        label = "[magenta]AI-merged[/]" if strategy == "ai" else "[yellow]Conflicts resolved (first-wins):[/]"
        console.print(f"{label}")
        for c in conflicts:
            icon = "[magenta]✦[/]" if strategy == "ai" else "[yellow]⚠[/]"
            console.print(f"  {icon} {c}")
        console.print()

    if no_install:
        console.print(Panel(composed, title="[bold]Composed Skill[/]", border_style="cyan"))
    else:
        path_template = AGENT_PATHS.get(agent, ".claude/commands/{name}.md")
        out_path = path_template.format(name=output) if "{name}" in path_template else path_template
        console.print(f"[green]✓[/] Written to [bold]{out_path}[/]")
        if agent == "claude":
            console.print(f"  [dim]→ In Claude Code, type [bold]/{output}[/] to use it.[/]")
        console.print()


@app.command()
def diff(
    skill_a: str = typer.Argument(..., help="First skill (name, skills.sh:name, github:owner/repo/path, ./local.md)"),
    skill_b: str = typer.Argument(..., help="Second skill to compare against"),
    agent: str = _agent_option(),
):
    """
    Compare two skills section by section before composing.

    Shows which sections are unique to each skill and which will conflict.

    Examples:
      skillhub diff python-patterns react-patterns
      skillhub diff python-patterns skills.sh:react-expert
    """
    from .composer import diff as _diff
    from rich.table import Table

    console.print(f"\n[bold]Comparing[/] [cyan]{skill_a}[/] ← → [cyan]{skill_b}[/]\n")

    try:
        result = _diff(skill_a, skill_b, agent)
    except (ValueError, RuntimeError) as e:
        console.print(f"[red]Error:[/] {e}")
        raise typer.Exit(1)

    name_a = result["skill_a_name"]
    name_b = result["skill_b_name"]
    only_a = result["only_a"]
    only_b = result["only_b"]
    conflicts = result["conflicts"]

    table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
    table.add_column("Section", style="bold", min_width=28)
    table.add_column(f"{name_a}", min_width=16, justify="center")
    table.add_column(f"{name_b}", min_width=16, justify="center")
    table.add_column("Status", min_width=12)

    for s in only_a:
        table.add_row(s, "[green]✓ here[/]", "[dim]—[/]", "[green]unique[/]")
    for s in conflicts:
        table.add_row(s, "[yellow]✓ here[/]", "[yellow]✓ here[/]", "[yellow]⚠ conflict[/]")
    for s in only_b:
        table.add_row(s, "[dim]—[/]", "[blue]✓ here[/]", "[blue]unique[/]")

    console.print(table)

    total_unique = len(only_a) + len(only_b)
    console.print(f"\n  [green]{total_unique} unique section(s)[/]  [yellow]{len(conflicts)} conflict(s)[/]")

    if conflicts:
        console.print(f"\n[dim]Compose with default (first-wins):[/]")
        console.print(f"  skillhub compose {skill_a} {skill_b} -o merged")
        console.print(f"[dim]Compose with AI merge (resolves conflicts intelligently):[/]")
        console.print(f"  skillhub compose {skill_a} {skill_b} -o merged --strategy ai")
    else:
        console.print(f"\n[green]No conflicts — safe to compose:[/]")
        console.print(f"  skillhub compose {skill_a} {skill_b} -o merged")
    console.print()


@app.command()
def templates():
    """List all built-in compose templates."""
    console.print()
    table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta", title="[bold]Compose Templates[/]")
    table.add_column("Template", style="bold cyan", min_width=20)
    table.add_column("Skills", min_width=40)
    table.add_column("Description", min_width=40)

    for name, tmpl in COMPOSE_TEMPLATES.items():
        skills_str = " + ".join(tmpl["skills"])
        table.add_row(name, skills_str, tmpl["description"])

    console.print(table)
    console.print("\n[dim]Use a template:[/]  [bold]skillhub compose --template fastapi-expert[/]")
    console.print("[dim]With AI merge:[/]   [bold]skillhub compose --template fastapi-expert --strategy ai[/]\n")


@app.command(name="init")
def init_skill(
    name: str = typer.Argument(..., help="Skill name (use kebab-case, e.g. my-skill)"),
):
    """Scaffold a new skill locally. Creates <name>/SKILL.md with a template."""
    import re

    if not re.match(r'^[a-z][a-z0-9-]*$', name):
        console.print("[red]Error:[/] Skill names must be lowercase kebab-case (e.g. [bold]my-skill[/]).")
        raise typer.Exit(1)

    skill_dir = Path.cwd() / name
    skill_md = skill_dir / "SKILL.md"

    if skill_md.exists():
        console.print(f"[yellow]{skill_md} already exists.[/] Edit it directly or delete and re-run.")
        raise typer.Exit(1)

    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_md.write_text(f"""---
name: {name}
description: What this skill makes your agent do (one sentence, start with a verb)
version: 1.0.0
agents: [claude, cursor, codex, gemini]
tags: [your, tags, here]
triggers: ['keyword one', 'keyword two', 'phrase that activates this']
author: your-github-username
license: MIT
---

# {name.replace('-', ' ').title()}

<!-- Describe what this skill is and when to use it -->

## When to Use

- Situation 1 where this skill applies
- Situation 2 where this skill applies

## Approach

<!-- The methodology, process, or discipline you want the agent to follow -->

### Step 1 — ...

### Step 2 — ...

### Step 3 — ...

## Output Format

<!-- How should the agent structure its response? -->

- Format item 1
- Format item 2
""")

    console.print(f"\n[green]✓[/] Created [bold]{name}/SKILL.md[/]\n")
    console.print("[dim]Edit the file, then:[/]")
    console.print(f"  [bold]skillhub install {name}[/]     [dim]# test it locally[/]")
    console.print(f"  [bold]skillhub publish {name}/[/]    [dim]# submit to registry[/]\n")


@app.command()
def publish(
    path: Path = typer.Argument(Path("."), help="Path to your skill directory"),
):
    """
    Publish a skill to the skillhub registry (opens a GitHub PR).
    """
    skill_md = path / "SKILL.md"

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
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-v", callback=_version_callback, is_eager=True, help="Show version"),
):
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
