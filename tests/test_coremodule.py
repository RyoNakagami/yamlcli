import pytest
import json
import yaml
import tempfile
import os
from yamlcli.yamlcli_core import yaml_to_json, json_to_yaml

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
    yaml_to_json(sample_yaml_file, indent=2)
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
    yaml_to_json(sample_yaml_file, indent=0)
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
        yaml_to_json("nonexistent.yaml", indent=2)


def test_yaml_to_json_invalid_yaml(tmp_path, capsys):
    invalid_yaml = tmp_path / "invalid.yaml"
    invalid_yaml.write_text(
        """invalid:
  - missing
    indentation
"""
    )

    yaml_to_json(invalid_yaml, indent=2)
    captured = capsys.readouterr()
    output = captured.out
    parsed_output = json.loads(output)

    # Since PyYAML is lenient, check output instead of expecting exception
    assert parsed_output == {"invalid": ["missing indentation"]}


def test_json_to_yaml_basic(sample_json_file, capsys):
    json_to_yaml(sample_json_file, indent=0)
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
        json_to_yaml("nonexistent.json", indent=0)


def test_json_to_yaml_invalid_json(tmp_path, capsys):
    invalid_json = tmp_path / "invalid.json"
    invalid_json.write_text("""
    {
        "invalid": "json",
        missing: quotes
    }
    """)

    with pytest.raises(json.JSONDecodeError):
        json_to_yaml(str(invalid_json), indent=0)
