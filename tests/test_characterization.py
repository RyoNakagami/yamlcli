"""Characterization tests: lock the exact CLI output byte-for-byte.

These tests pin the observable behavior (stdout, stderr, exit codes,
trailing newlines) so that refactoring cannot change it unnoticed.
The CLI prints the conversion result, so stdout is EXPECTED_* + "\\n".
"""

import sys

from typer.testing import CliRunner

from yamlcli.cli import app
from yamlcli.library.version import __version__

from tests.expected_outputs import (
    EXPECTED_JSON_COMPACT,
    EXPECTED_JSON_INDENT2,
    EXPECTED_YAML_COMPACT,
    EXPECTED_YAML_INDENT2,
)

runner = CliRunner()


def test_yaml_to_json_default_indent_exact(sample_yaml_file):
    result = runner.invoke(app, [sample_yaml_file, "--to-json"])
    assert result.exit_code == 0
    assert result.stdout == EXPECTED_JSON_INDENT2 + "\n"


def test_yaml_to_json_indent_zero_exact(sample_yaml_file):
    result = runner.invoke(app, [sample_yaml_file, "--to-json", "--indent", "0"])
    assert result.exit_code == 0
    assert result.stdout == EXPECTED_JSON_COMPACT + "\n"


def test_json_to_yaml_default_indent_exact(sample_json_file):
    result = runner.invoke(app, [sample_json_file, "--to-yaml"])
    assert result.exit_code == 0
    assert result.stdout == EXPECTED_YAML_INDENT2 + "\n"


def test_json_to_yaml_indent_zero_exact(sample_json_file):
    result = runner.invoke(app, [sample_json_file, "--to-yaml", "--indent", "0"])
    assert result.exit_code == 0
    assert result.stdout == EXPECTED_YAML_COMPACT + "\n"


def test_version_flag_exact():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    expected = f"yamlcli {__version__}\nPython {sys.version.split()[0]}\n"
    assert result.stdout == expected


def test_error_message_no_flag_exact():
    result = runner.invoke(app, ["file.yaml"])
    assert result.exit_code == 1
    assert result.stderr == "Error: Specify exactly one of --to-json or --to-yaml\n"


def test_error_message_both_flags_exact():
    result = runner.invoke(app, ["file.yaml", "--to-json", "--to-yaml"])
    assert result.exit_code == 1
    assert result.stderr == "Error: Specify exactly one of --to-json or --to-yaml\n"


def test_error_message_file_not_found_exact():
    result = runner.invoke(app, ["/tmp/nonexistent.yaml", "--to-json"])
    assert result.exit_code == 1
    assert result.stderr == "Error: File not found - /tmp/nonexistent.yaml\n"
