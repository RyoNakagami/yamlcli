import json
import sys

import pytest
import yaml
from typer.testing import CliRunner

from yamlcli.cli import app

runner = CliRunner()


def test_cli_to_json(sample_yaml_file):
    result = runner.invoke(app, [sample_yaml_file, "--to-json"])
    assert result.exit_code == 0

    parsed_output = json.loads(result.stdout)
    assert parsed_output["name"] == "John Doe"


def test_cli_to_yaml(sample_json_file):
    result = runner.invoke(app, [sample_json_file, "--to-yaml"])
    assert result.exit_code == 0

    parsed_output = yaml.safe_load(result.stdout)
    assert parsed_output["name"] == "John Doe"


def test_cli_no_conversion_flag():
    result = runner.invoke(app, ["file.yaml"])
    assert result.exit_code == 1
    assert "Error" in result.stderr


def test_cli_both_flags():
    result = runner.invoke(app, ["file.yaml", "--to-yaml", "--to-json"])
    assert result.exit_code == 1
    assert "Error" in result.stderr


def test_cli_custom_indent(sample_yaml_file):
    result = runner.invoke(app, [sample_yaml_file, "--to-json", "--indent", "4"])

    assert result.exit_code == 0

    output = result.stdout
    lines = output.strip().split("\n")

    # Check if indentation is 4 spaces
    assert any(line.startswith("    ") for line in lines)


def test_main_guard(sample_yaml_file):
    result = runner.invoke(app, [sample_yaml_file, "--to-json"])

    assert result.exit_code == 0

    parsed = json.loads(result.stdout)
    assert parsed["name"] == "John Doe"


def test_main_yaml_error(tmp_path, monkeypatch):
    tmp_file = tmp_path / "valid.yaml"
    tmp_file.write_text("key: value")

    # Force YAML error (patch only the module used by yamlcli_core)
    monkeypatch.setattr(
        "yamlcli.yamlcli_core.yaml.safe_load",
        lambda text: (_ for _ in ()).throw(yaml.YAMLError("mock YAML error")),
    )

    result = runner.invoke(app, [str(tmp_file), "--to-json"])

    # Typer(click) returns exit code 1
    assert result.exit_code != 0
    assert "mock YAML error" in result.stderr


def test_main_file_not_found():
    fake_file = "/tmp/nonexistent.yaml"
    result = runner.invoke(app, [fake_file, "--to-json"])

    assert result.exit_code != 0
    assert f"Error: File not found - {fake_file}" in result.stderr


def test_main_json_decode_error(tmp_path):
    invalid_json = tmp_path / "invalid.json"
    invalid_json.write_text('{"invalid": "json", missing: quotes}')

    result = runner.invoke(app, [str(invalid_json), "--to-yaml"])

    assert result.exit_code != 0
    assert "Error: Parsing failed" in result.stderr


def test_main_file_removed_after_check(sample_yaml_file, monkeypatch):
    # File passes the existence check but disappears before it is opened
    def raise_file_not_found(file_path, indent):
        raise FileNotFoundError(file_path)

    monkeypatch.setattr("yamlcli.cli.yaml_to_json", raise_file_not_found)

    result = runner.invoke(app, [sample_yaml_file, "--to-json"])

    assert result.exit_code != 0
    assert f"Error: File not found - {sample_yaml_file}" in result.stderr


def test_main_entry_point(sample_yaml_file, monkeypatch, capsys):
    from yamlcli.cli import main

    monkeypatch.setattr(sys, "argv", ["yamlcli", sample_yaml_file, "--to-json"])

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 0
    parsed = json.loads(capsys.readouterr().out)
    assert parsed["name"] == "John Doe"
