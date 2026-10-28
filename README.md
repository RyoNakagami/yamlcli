# yamlcli

A command-line tool to convert between YAML and JSON formats.

## Features

- Convert YAML files to JSON format
- Convert JSON files to YAML format
- Customizable JSON indentation
- Error handling for invalid files and formats

## Usage

```bash
# Convert YAML to JSON (default 2-space indent)
yamlcli input.yaml --to-json

# Convert YAML to JSON with custom indentation
yamlcli input.yaml --to-json --indent 4

# Convert JSON to YAML
yamlcli input.json --to-yaml
```

## Install via `uv tool`

```bash
# Install the latest version from the GitHub repository
uv tool install git+https://github.com/RyoNakagami/yamlcli.git

# Install the branch-specific version
uv tool install git+https://github.com/RyoNakagami/yamlcli.git@develop

# Install the tagged version
uv tool install git+https://github.com/RyoNakagami/yamlcli.git@v0.2.0
```

## Upgrade

```bash
uv tool upgrade yamlcli
```

## Uninstall

```bash
uv tool uninstall yamlcli
```

## Development

### Running Tests

Tests are written using pytest. To run the tests:

```bash
uv run pytest
```
