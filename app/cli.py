from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from app import __version__
from app.generator import GenerationError, generate_evidence_pack

cli = typer.Typer(help="Generate audit-ready evidence packs from findings and evidence files.")
console = Console()


@cli.command("generate")
def generate(
    input_dir: Path = typer.Option(..., "--input", exists=True, file_okay=False, dir_okay=True, readable=True),
    output_dir: Path = typer.Option(..., "--output", file_okay=False, dir_okay=True, writable=True),
) -> None:
    """Generate HTML evidence pack, normalized findings JSON, and manifest."""
    try:
        with console.status("[bold green]Generating evidence pack..."):
            result = generate_evidence_pack(input_dir=input_dir, output_dir=output_dir)
    except GenerationError as exc:
        console.print(f"[bold red]Generation failed:[/bold red] {exc}")
        raise typer.Exit(code=1)

    table = Table(title="Evidence Pack Generated")
    table.add_column("Metric")
    table.add_column("Value", style="bold")
    table.add_row("Findings", str(result.findings_count))
    table.add_row("Evidence files", str(result.evidence_count))
    table.add_row("Output directory", str(output_dir))

    console.print(table)
    for file_path in result.output_files:
        console.print(f"[green]- {file_path}[/green]")


@cli.command("version")
def version() -> None:
    """Show installed tool version."""
    console.print(__version__)


def run() -> None:
    cli()


if __name__ == "__main__":
    run()
