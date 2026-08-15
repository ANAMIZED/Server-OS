"""CLI smoke tests via Typer runner."""

from typer.testing import CliRunner

from server_os.cli import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "status" in result.stdout
    assert "agents" in result.stdout


def test_cli_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "Server OS" in result.stdout


def test_cli_agents_help():
    result = runner.invoke(app, ["agents", "--help"])
    assert result.exit_code == 0
    assert "list" in result.stdout
    assert "create" in result.stdout
    assert "run" in result.stdout
