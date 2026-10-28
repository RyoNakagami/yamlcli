import pytest
import json
import yaml

from yamlcli.yamlcli_core import (
    convert_json_to_yaml,
    convert_yaml_to_json,
    json_to_yaml,
    yaml_to_json,
)

from tests.expected_outputs import (
    EXPECTED_JSON_COMPACT,
    EXPECTED_JSON_INDENT2,
    EXPECTED_JSON_INDENT4,
    EXPECTED_YAML_COMPACT,
    EXPECTED_YAML_INDENT2,
    SAMPLE_DATA,
    SAMPLE_YAML,
)


# ---------------------------------------------------------------------------
# Pure conversion functions (str -> str)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    ("indent", "expected"),
    [
        (0, EXPECTED_JSON_COMPACT),
        (2, EXPECTED_JSON_INDENT2),
        (4, EXPECTED_JSON_INDENT4),
    ],
)
def test_convert_yaml_to_json_exact(indent, expected):
    assert convert_yaml_to_json(SAMPLE_YAML, indent=indent) == expected


def test_convert_yaml_to_json_negative_indent_is_compact():
    assert convert_yaml_to_json(SAMPLE_YAML, indent=-1) == EXPECTED_JSON_COMPACT


def test_convert_yaml_to_json_dates_as_iso_strings():
    text = "start: 2026-04-02\nend: null\nat: 2026-04-02 10:30:00\n"
    assert json.loads(convert_yaml_to_json(text, indent=0)) == {
        "start": "2026-04-02",
        "end": None,
        "at": "2026-04-02T10:30:00",
    }


def test_convert_yaml_to_json_dates_with_indent():
    text = "start: 2026-04-02\nend: null\n"
    assert convert_yaml_to_json(text, indent=2) == (
        '{\n  "start": "2026-04-02",\n  "end": null\n}'
    )


def test_convert_yaml_to_json_aware_datetime_keeps_offset():
    text = "at: 2026-04-02 10:30:00+09:00\n"
    assert json.loads(convert_yaml_to_json(text, indent=0)) == {
        "at": "2026-04-02T10:30:00+09:00",
    }


def test_convert_yaml_to_json_other_unserializable_types_still_raise():
    # !!binary is loaded as bytes, which is not a YAML timestamp
    with pytest.raises(TypeError, match="Object of type bytes"):
        convert_yaml_to_json("data: !!binary aGk=\n", indent=0)


@pytest.mark.parametrize(
    ("indent", "expected"),
    [
        (0, EXPECTED_YAML_COMPACT),
        (2, EXPECTED_YAML_INDENT2),
    ],
)
def test_convert_json_to_yaml_exact(indent, expected):
    text = json.dumps(SAMPLE_DATA)
    assert convert_json_to_yaml(text, indent=indent) == expected


def test_convert_json_to_yaml_preserves_key_order():
    text = '{"zebra": 1, "apple": 2, "mango": 3}'
    assert convert_json_to_yaml(text, indent=2) == "zebra: 1\napple: 2\nmango: 3\n"


def test_convert_roundtrip_yaml_json_yaml():
    json_text = convert_yaml_to_json(SAMPLE_YAML, indent=2)
    yaml_text = convert_json_to_yaml(json_text, indent=2)
    assert yaml.safe_load(yaml_text) == SAMPLE_DATA


def test_convert_yaml_to_json_invalid_yaml_raises():
    with pytest.raises(yaml.YAMLError):
        convert_yaml_to_json("key: [unclosed", indent=2)


def test_convert_json_to_yaml_invalid_json_raises():
    with pytest.raises(json.JSONDecodeError):
        convert_json_to_yaml("{not json}", indent=2)


@pytest.mark.parametrize("indent", [0, 2])
def test_convert_yaml_to_json_escapes_non_ascii_by_default(indent):
    output = convert_yaml_to_json("名前: 山田\n", indent=indent)
    assert "\\u540d\\u524d" in output
    assert "名前" not in output


@pytest.mark.parametrize("indent", [0, 2])
def test_convert_yaml_to_json_keeps_non_ascii_when_disabled(indent):
    output = convert_yaml_to_json("名前: 山田\n", indent=indent, ensure_ascii=False)
    assert json.loads(output) == {"名前": "山田"}
    assert "名前" in output


@pytest.mark.parametrize("indent", [0, 2])
def test_convert_json_to_yaml_escapes_non_ascii_by_default(indent):
    output = convert_json_to_yaml('{"名前": "山田"}', indent=indent)
    assert "名前" not in output
    assert yaml.safe_load(output) == {"名前": "山田"}


@pytest.mark.parametrize("indent", [0, 2])
def test_convert_json_to_yaml_keeps_non_ascii_when_disabled(indent):
    output = convert_json_to_yaml('{"名前": "山田"}', indent=indent, ensure_ascii=False)
    assert output == "名前: 山田\n"


# ---------------------------------------------------------------------------
# File-based wrappers (read + convert + print)
# ---------------------------------------------------------------------------


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
