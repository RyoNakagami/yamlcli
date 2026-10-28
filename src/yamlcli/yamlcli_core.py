import datetime
import json
from pathlib import Path

import yaml


class RegmonkeyDumper(yaml.Dumper):
    """yaml.Dumper that indents block sequences under their parent key."""

    def increase_indent(self, flow: bool = False, indentless: bool = False):
        return super().increase_indent(flow, False)


def _json_default(obj: object) -> str:
    """Serialize YAML timestamps (``date`` / ``datetime``) as ISO 8601 strings."""
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


def convert_yaml_to_json(text: str, indent: int, ensure_ascii: bool = True) -> str:
    """Convert a YAML document to a JSON string.

    ``indent <= 0`` produces a compact single-line JSON.
    ``ensure_ascii=True`` escapes non-ASCII characters as ``\\uXXXX``.
    """
    data = yaml.safe_load(text)

    if indent <= 0:
        return json.dumps(data, ensure_ascii=ensure_ascii, default=_json_default)
    return json.dumps(
        data, indent=indent, ensure_ascii=ensure_ascii, default=_json_default
    )


def convert_json_to_yaml(text: str, indent: int, ensure_ascii: bool = True) -> str:
    """Convert a JSON document to a YAML string.

    ``indent <= 0`` uses the default ``yaml.safe_dump`` style; a positive
    ``indent`` indents block sequences via :class:`RegmonkeyDumper`.
    ``ensure_ascii=True`` escapes non-ASCII characters as ``\\uXXXX``.
    """
    data = json.loads(text)

    if indent <= 0:
        return yaml.safe_dump(data, sort_keys=False, allow_unicode=not ensure_ascii)
    return yaml.dump(
        data,
        Dumper=RegmonkeyDumper,
        sort_keys=False,
        default_flow_style=False,
        indent=indent,
        allow_unicode=not ensure_ascii,
    )


def yaml_to_json(file_path: str | Path, indent: int, ensure_ascii: bool = True) -> None:
    """Read a YAML file and print it as JSON to stdout."""
    with open(file_path, "r", encoding="utf-8") as f:
        print(convert_yaml_to_json(f.read(), indent, ensure_ascii))


def json_to_yaml(file_path: str | Path, indent: int, ensure_ascii: bool = True) -> None:
    """Read a JSON file and print it as YAML to stdout."""
    with open(file_path, "r", encoding="utf-8") as f:
        print(convert_json_to_yaml(f.read(), indent, ensure_ascii))
