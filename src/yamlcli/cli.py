import sys
import json
from pathlib import Path
import yaml
import typer

from yamlcli.yamlcli_core import yaml_to_json, json_to_yaml
from yamlcli.library.version import __version__

app = typer.Typer(
    add_completion=False,
)

def version_callback(value: bool):
    if value:
        print(f"yamlcli {__version__}")
        print(f"Python {sys.version.split()[0]}")
        raise typer.Exit()


@app.command()
def converter(
    file: str = typer.Argument(..., help="Input file path"),
    to_json: bool = typer.Option(False, "--to-json", help="Convert YAML → JSON"),
    to_yaml: bool = typer.Option(False, "--to-yaml", help="Convert JSON → YAML"),
    indent: int = typer.Option(2, "--indent", help="Indentation level (default: 2)"),
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version information and exit.",
        callback=version_callback,
        is_eager=True,
    ),
):
    """
    A simple command-line tool to convert between YAML and JSON formats.\n\n
    Features:\n
    - Convert YAML files to JSON\n
    - Convert JSON files to YAML\n
    - Support for custom JSON indentation\n
    - Robust error handling for invalid files or malformed data
    """
    # 排他チェック（pytest 要求）
    if (not to_json and not to_yaml) or (to_json and to_yaml):
        typer.echo("Error: Specify exactly one of --to-json or --to-yaml", err=True)
        raise typer.Exit(code=1)

    if not Path(file).exists():
        typer.echo(f"Error: File not found - {file}", err=True)
        raise typer.Exit(code=1)

    try:
        if to_yaml:
            json_to_yaml(file, indent)
        else:
            yaml_to_json(file, indent)

    except yaml.YAMLError as e:
        typer.echo(f"Error: Parsing failed - {e}", err=True)
        raise typer.Exit(code=1)

    except json.JSONDecodeError as e:
        typer.echo(f"Error: Parsing failed - {e}", err=True)
        raise typer.Exit(code=1)

    except FileNotFoundError:
        typer.echo(f"Error: File not found - {file}", err=True)
        raise typer.Exit(code=1)


def main():
    app()

if __name__ == "__main__":
    app()
