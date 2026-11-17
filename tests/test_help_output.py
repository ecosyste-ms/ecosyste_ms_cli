"""Tests for help output of the CLI."""

from unittest import mock

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
    """The upstream spec's 'list registies' typo is corrected via HELP_OVERRIDES.

    Upstream renamed this operation to getHosts in the commits, issues and repos
    specs (and fixed the typo there); dependabot and packages still expose it as
    getRegistries, and dependabot still carries the typo.
    """
    runner = CliRunner()
    for group in ("dependabot", "packages"):
        result = runner.invoke(cli, [group, "--help"])
        assert "registies" not in result.output, group
        assert "list registries" in result.output, group


def test_get_hosts_replaces_get_registries():
    """commits, issues and repos expose /hosts as get_hosts, not get_registries."""
    runner = CliRunner()
    for group in ("commits", "issues", "repos"):
        result = runner.invoke(cli, [group, "--help"])
        assert result.exit_code == 0, group
        assert "get_hosts" in result.output, group
        assert "get_registries" not in result.output, group
        assert "registies" not in result.output, group


def test_opencollective_help_has_no_placeholders():
    """HELP_OVERRIDES replaces the opencollective spec's terse descriptions."""
    runner = CliRunner()
    result = runner.invoke(cli, ["opencollective", "--help"])
    assert result.exit_code == 0
    assert "Execute get" not in result.output
    assert "Execute lookup" not in result.output
    assert "list open collective collectives" in result.output


def test_awesome_help_has_no_placeholders():
    """HELP_OVERRIDES replaces the awesome spec's terse descriptions."""
    runner = CliRunner()
    result = runner.invoke(cli, ["awesome", "--help"])
    assert result.exit_code == 0
    assert "Execute get" not in result.output
    assert "Execute lookup" not in result.output
    assert "list awesome lists" in result.output


def test_awesome_list_help_recommends_owner_name():
    """Numeric list ids redirect upstream and lose query params; help steers users to owner/name."""
    runner = CliRunner()
    result = runner.invoke(cli, ["awesome", "get_list_projects", "--help"])
    assert result.exit_code == 0
    assert "owner/name" in result.output


def test_operation_description_used_when_summary_missing():
    """Specs without summaries often still have descriptions; prefer those over placeholders."""
    import click

    from ecosystems_cli.commands.generator import APICommandGenerator

    spec = {"paths": {"/things": {"get": {"operationId": "getThings", "description": "get all things"}}}}
    group = click.Group("demo")
    with mock.patch("ecosystems_cli.commands.generator.load_api_spec", return_value=spec):
        APICommandGenerator._register_commands(group, "demo")

    assert group.commands["get_things"].help == "get all things"


def test_get_advisory_help_grammar():
    """'get a advisories by uuid' (upstream spec) is overridden with correct grammar."""
    runner = CliRunner()
    result = runner.invoke(cli, ["advisories", "--help"])
    assert "get an advisory by uuid" in result.output
    assert "a advisories" not in result.output


def test_help_overrides_match_spec_operations():
    """Every HELP_OVERRIDES key names an operation in the vendored spec.

    Catches overrides left behind when an upstream spec refresh removes or
    renames an operation.
    """
    from ecosystems_cli.commands.generator import HELP_OVERRIDES
    from ecosystems_cli.helpers.load_api_spec import load_api_spec

    operations = {}
    for api_name, _ in HELP_OVERRIDES:
        if api_name not in operations:
            spec = load_api_spec(api_name)
            operations[api_name] = {
                op.get("operationId") for path in spec["paths"].values() for op in path.values() if isinstance(op, dict)
            }

    stale = [key for key in HELP_OVERRIDES if key[1] not in operations[key[0]]]
    assert stale == []
