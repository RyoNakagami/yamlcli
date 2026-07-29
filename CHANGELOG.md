# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [1.1.0] - 2026-07-29

### Added

- Pure string-based conversion API `convert_yaml_to_json()` / `convert_json_to_yaml()` in `yamlcli_core`, usable as a library without touching the filesystem
- `py.typed` marker so downstream projects can type-check against `yamlcli` (PEP 561)
- Shared pytest fixtures in `tests/conftest.py` and golden outputs in `tests/expected_outputs.py`
- Characterization tests (`tests/test_characterization.py`), version-resolution tests (`tests/test_version.py`), and repository-metadata use-case tests (`tests/test_usecase_repo_metadata.py`)
- CLI tests for JSON decode errors, file removal between existence check and open, and the `main()` entry point

### Changed

- `yaml_to_json()` / `json_to_yaml()` are now thin file wrappers that read with explicit UTF-8 encoding and delegate to the new pure conversion functions
- Simplified the `--to-json` / `--to-yaml` exclusivity check and merged the YAML/JSON parse-error handlers in the CLI
- `get_version()` now tolerates missing `tomllib` on Python < 3.11 and narrows exception handling to `OSError` / `TOMLDecodeError`
- Added type annotations and docstrings across `cli`, `yamlcli_core`, and `helper_func`

### Fixed

- Moved `types-pyyaml` from runtime dependencies to the dev dependency group
