"""Tests for help output of the CLI."""

from click.testing import CliRunner

from ecosystems_cli.cli import main as cli


def test_main_help_output():
    """Test that main help output includes expected information."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "Ecosystems CLI for interacting with ecosyste.ms APIs" in result.output
    assert "--timeout" in result.output
    assert "--format" in result.output
    assert "--domain" in result.output
    assert "advisories" in result.output


def test_advisories_help_output():
    """Test that advisories command help output includes expected information."""
    runner = CliRunner()
    result = runner.invoke(cli, ["advisories", "--help"])

    assert result.exit_code == 0
    assert "advisories" in result.output.lower()
    assert "--timeout" in result.output
    assert "--format" in result.output


def test_subcommand_help_includes_global_options():
    """Test that subcommand help includes global options."""
    runner = CliRunner()
    result = runner.invoke(cli, ["advisories", "--help"])

    assert result.exit_code == 0
    assert "--timeout" in result.output
    assert "--format" in result.output
    assert "--domain" in result.output


def test_get_registries_help_typo_overridden():
    """The upstream spec's 'list registies' typo is corrected via HELP_OVERRIDES."""
    runner = CliRunner()
    for group in ("commits", "dependabot", "issues", "packages", "repos"):
        result = runner.invoke(cli, [group, "--help"])
        assert "registies" not in result.output, group
        assert "list registries" in result.output, group


def test_opencollective_help_has_no_placeholders():
    """The opencollective spec has no summaries; HELP_OVERRIDES supplies real ones."""
    runner = CliRunner()
    result = runner.invoke(cli, ["opencollective", "--help"])
    assert result.exit_code == 0
    assert "Execute get" not in result.output
    assert "Execute lookup" not in result.output
    assert "list open collective collectives" in result.output


def test_get_advisory_help_grammar():
    """'get a advisories by uuid' (upstream spec) is overridden with correct grammar."""
    runner = CliRunner()
    result = runner.invoke(cli, ["advisories", "--help"])
    assert "get an advisory by uuid" in result.output
    assert "a advisories" not in result.output
