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
