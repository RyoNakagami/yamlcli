import pytest
import json
import yaml
import sys
import tempfile
import os
import runpy

import yamlcli


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


def test_yaml_to_json_basic(sample_yaml_file, capsys):
    yamlcli.yaml_to_json(sample_yaml_file, indent=2)
    captured = capsys.readouterr()
    output = captured.out

    # Parse the output back to Python object for comparison
    parsed_output = json.loads(output)
    expected = {
        "name": "John Doe",
        "age": 30,
        "hobbies": ["reading", "coding"],
        "address": {"street": "123 Main St", "city": "Example City"},
    }
    assert parsed_output == expected


def test_yaml_to_json_no_indent(sample_yaml_file, capsys):
    yamlcli.yaml_to_json(sample_yaml_file, indent=0)
    captured = capsys.readouterr()
    output = captured.out

    # Verify it's a single line JSON
    assert len(output.strip().split("\n")) == 1

    # Verify content is correct
    parsed_output = json.loads(output)
    assert parsed_output["name"] == "John Doe"
    assert parsed_output["age"] == 30


def test_yaml_to_json_file_not_found():
    with pytest.raises(FileNotFoundError):
        yamlcli.yaml_to_json("nonexistent.yaml", indent=2)


def test_yaml_to_json_invalid_yaml(tmp_path, capsys):
    invalid_yaml = tmp_path / "invalid.yaml"
    invalid_yaml.write_text(
        """invalid:
  - missing
    indentation
"""
    )

    yamlcli.yaml_to_json(invalid_yaml, indent=2)
    captured = capsys.readouterr()
    output = captured.out
    parsed_output = json.loads(output)

    # Since PyYAML is lenient, check output instead of expecting exception
    assert parsed_output == {"invalid": ["missing indentation"]}


def test_json_to_yaml_basic(sample_json_file, capsys):
    yamlcli.json_to_yaml(sample_json_file, indent=0)
    output = capsys.readouterr().out

    # Parse the output back to Python object for comparison
    parsed_output = yaml.safe_load(output)
    expected = {
        "name": "John Doe",
        "age": 30,
        "hobbies": ["reading", "coding"],
        "address": {"street": "123 Main St", "city": "Example City"},
    }
    assert parsed_output == expected


def test_json_to_yaml_file_not_found():
    with pytest.raises(FileNotFoundError):
        yamlcli.json_to_yaml("nonexistent.json", indent=0)


def test_json_to_yaml_invalid_json(tmp_path, capsys):
    invalid_json = tmp_path / "invalid.json"
    invalid_json.write_text("""
    {
        "invalid": "json",
        missing: quotes
    }
    """)

    with pytest.raises(json.JSONDecodeError):
        yamlcli.json_to_yaml(str(invalid_json), indent=0)


def test_cli_to_json(sample_yaml_file, capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["yamlcli", sample_yaml_file, "--to-json"])
    yamlcli.main()
    output = capsys.readouterr().out
    parsed_output = json.loads(output)
    assert parsed_output["name"] == "John Doe"


def test_cli_to_yaml(sample_json_file, capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["yamlcli", sample_json_file, "--to-yaml"])
    yamlcli.main()
    output = capsys.readouterr().out
    parsed_output = yaml.safe_load(output)
    assert parsed_output["name"] == "John Doe"


def test_cli_no_conversion_flag(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["yamlcli", "file.yaml"])
    with pytest.raises(SystemExit) as exc_info:
        yamlcli.main()
    assert exc_info.value.code == 1


def test_cli_both_flags(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["yamlcli", "file.yaml", "--to-json", "--to-yaml"])
    with pytest.raises(SystemExit) as exc_info:
        yamlcli.main()
    assert exc_info.value.code == 1


def test_cli_custom_indent(sample_yaml_file, capsys, monkeypatch):
    monkeypatch.setattr(
        sys, "argv", ["yamlcli", sample_yaml_file, "--to-json", "--indent", "4"]
    )
    yamlcli.main()
    output = capsys.readouterr().out
    # Check if indentation is 4 spaces
    lines = output.strip().split("\n")
    assert any(line.startswith("    ") for line in lines)


def test_main_guard(sample_yaml_file, capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["yamlcli", sample_yaml_file, "--to-json"])

    runpy.run_module("yamlcli", run_name="__main__")
    output = capsys.readouterr().out
    parsed_output = json.loads(output)
    assert parsed_output["name"] == "John Doe"


def test_main_yaml_error(tmp_path, capsys, monkeypatch):
    # Create an actual temporary YAML file
    tmp_file = tmp_path / "valid.yaml"
    tmp_file.write_text("key: value")

    # Patch yaml.safe_load to raise YAMLError
    monkeypatch.setattr(
        "yaml.safe_load",
        lambda f: (_ for _ in ()).throw(yaml.YAMLError("mock YAML error")),
    )

    # Patch sys.argv to simulate CLI
    monkeypatch.setattr(sys, "argv", ["yamlcli", str(tmp_file), "--to-json"])

    with pytest.raises(SystemExit):
        yamlcli.main()

    captured = capsys.readouterr()
    assert "mock YAML error" in captured.err


def test_main_file_not_found(capsys, monkeypatch):
    # Use a non-existent file path
    fake_file = "/tmp/nonexistent.yaml"
    monkeypatch.setattr(sys, "argv", ["yamlcli", fake_file, "--to-json"])

    # Expect SystemExit
    with pytest.raises(SystemExit) as exc_info:
        yamlcli.main()

    # Capture stderr
    captured = capsys.readouterr()
    assert f"Error: File not found - {fake_file}" in captured.err
    assert exc_info.value.code == 1
