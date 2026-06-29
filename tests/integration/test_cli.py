"""CLI smoke tests."""

from typer.testing import CliRunner

from app.cli import cli


def test_cli_lists_profiles() -> None:
    """The profiles command lists configured logical profiles."""
    result = CliRunner().invoke(cli, ["profiles"])

    assert result.exit_code == 0
    assert "coding_high" in result.stdout


def test_cli_runs_fake_provider_example() -> None:
    """The run command executes the sample request without credentials."""
    result = CliRunner().invoke(cli, ["run", "examples/pr-reviewer-request.json"])

    assert result.exit_code == 0
    assert "Agent: pr-reviewer 0.1.0" in result.stdout
    assert "Selected: fake/fake-coding-model" in result.stdout


def test_cli_resolves_agent_with_overlay() -> None:
    """The resolve-agent command prints the merged overlay configuration."""
    result = CliRunner().invoke(
        cli,
        [
            "resolve-agent",
            "agents/pr-reviewer/agent.yaml",
            "--overlay",
            "agents/overlays/payments-team.yaml",
        ],
    )

    assert result.exit_code == 0
    assert "payment idempotency" in result.stdout
    assert '"severity_threshold": "medium"' in result.stdout


def test_cli_resolves_model_request() -> None:
    """The resolve-model command returns a resolver-only decision."""
    result = CliRunner().invoke(cli, ["resolve-model", "examples/resolve-model-request.json"])

    assert result.exit_code == 0
    assert '"provider": "fake"' in result.stdout
    assert '"budget_scope": "department:payments"' in result.stdout
