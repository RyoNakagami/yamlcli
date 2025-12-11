import pytest
import json
import yaml
import sys
import tempfile
import os
import runpy
from typer.testing import CliRunner

from yamlcli.cli import app

runner = CliRunner()


@pytest.fixture
def sample_yaml_file():
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
        f.write("""
name: John Doe
age: 30
hobbies:
  - reading
  - coding
address:
  street: 123 Main St
  city: Example City
""")
    yield f.name
    os.unlink(f.name)


@pytest.fixture
def sample_json_file():
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        json.dump(
            {
                "name": "John Doe",
                "age": 30,
                "hobbies": ["reading", "coding"],
                "address": {"street": "123 Main St", "city": "Example City"},
            },
            f,
            indent=2,
        )
    yield f.name
    os.unlink(f.name)


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

    # Force YAML error
    monkeypatch.setattr(
        "yaml.safe_load",
        lambda f: (_ for _ in ()).throw(yaml.YAMLError("mock YAML error")),
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
