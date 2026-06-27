"""Command line interface for the proof-of-concept application."""

import asyncio
import json
from pathlib import Path
from typing import Annotated

import typer

from app import __version__
from app.config import PROJECT_ROOT, build_runner
from app.domain.agent import AgentRunRequest
from app.gateway.registry import load_models, load_profiles
from app.runtime.loader import load_agent
from app.runtime.overlays import apply_overlay, resolve_without_overlay

cli = typer.Typer(help="Provider-neutral agent runtime and model gateway demo.")


@cli.command()
def version() -> None:
    """Print the CLI version."""
    typer.echo(__version__)


@cli.command()
def profiles() -> None:
    """List configured logical model profiles."""
    registry = load_profiles(PROJECT_ROOT / "config/model-profiles.yaml")
    for profile in registry.list():
        typer.echo(profile.name)
        typer.echo(f"  minimum_context_window: {profile.requirements.minimum_context_window}")
        typer.echo(f"  structured_output: {profile.requirements.structured_output}")
        typer.echo("  routes:")
        for route in profile.routes:
            typer.echo(f"    - {route.provider}/{route.model}")


@cli.command()
def models() -> None:
    """List configured provider models."""
    registry = load_models(PROJECT_ROOT / "config/models.yaml")
    for model in registry.list():
        typer.echo(f"{model.provider}/{model.model}")
        typer.echo(f"  context_window: {model.capabilities.max_context_window}")
        typer.echo(f"  structured_output: {model.capabilities.structured_output}")
        typer.echo(f"  tool_calling: {model.capabilities.tool_calling}")


@cli.command("resolve-agent")
def resolve_agent(
    path: Annotated[Path, typer.Argument(help="Path to an agent.yaml file.")],
    overlay: Annotated[Path | None, typer.Option(help="Optional overlay YAML path.")] = None,
) -> None:
    """Print the resolved agent configuration."""
    loaded = load_agent(path)
    resolved = (
        apply_overlay(loaded.definition, path, overlay)
        if overlay is not None
        else resolve_without_overlay(loaded.definition, path)
    )
    typer.echo(json.dumps(resolved.definition.model_dump(mode="json"), indent=2, sort_keys=True))
    typer.echo(json.dumps(resolved.metadata.model_dump(mode="json"), indent=2, sort_keys=True))


@cli.command()
def run(request_json: Annotated[Path, typer.Argument(help="Agent run request JSON file.")]) -> None:
    """Run an agent request through the fake-provider demo path."""
    request_data = json.loads(request_json.read_text(encoding="utf-8"))
    request = AgentRunRequest.model_validate(request_data)
    result = asyncio.run(build_runner().run(request))
    typer.echo(f"Agent: {result.agent.name} {result.agent.version}")
    typer.echo(f"Profile: {result.model_profile}")
    typer.echo(
        "Selected: "
        f"{result.routing_metadata['selected_provider']}/{result.routing_metadata['selected_model']}"
    )
    rejected = result.routing_metadata.get("rejected_candidates", [])
    typer.echo(f"Rejected routes: {json.dumps(rejected, sort_keys=True)}")
    typer.echo(f"Overlay applied: {result.resolution_metadata.overlay_path is not None}")
    typer.echo("Validated result:")
    typer.echo(json.dumps(result.structured_output, indent=2, sort_keys=True))
    typer.echo("Token usage:")
    typer.echo(json.dumps(result.token_usage.model_dump(mode="json"), indent=2, sort_keys=True))


@cli.command()
def serve() -> None:
    """Run the demonstration HTTP server."""
    import uvicorn

    uvicorn.run("app.api:app", host="127.0.0.1", port=8000, reload=True)


def main() -> None:
    """Run the CLI application."""
    cli()
