"""Command line interface for the proof-of-concept application."""

import typer

from app import __version__

cli = typer.Typer(help="Provider-neutral agent runtime and model gateway demo.")


@cli.command()
def version() -> None:
    """Print the CLI version."""
    typer.echo(__version__)


def main() -> None:
    """Run the CLI application."""
    cli()
