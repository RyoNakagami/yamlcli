"""Use-case tests: repository-metadata YAML consumed via ``yamlcli --to-json | jq``.

Real-world consumers (GitHub Actions version extraction, gh-repo-update
scripts) pipe the CLI output into ``jq``. These tests pin only the
essential contract that makes those pipelines work:

* stdout is strict JSON (parseable by ``jq`` / ``json.loads``)
* hyphenated keys such as ``meta-data`` survive as-is
* ``version: 0.1.0`` stays the string ``"0.1.0"`` (never a number)
* YAML lists become JSON arrays; ``|`` block scalars keep their newline
"""

import json

import pytest
from typer.testing import CliRunner

from yamlcli.cli import app

runner = CliRunner()

REPO_METADATA_YAML = """\
meta-data:
  repository_name: regmonkey-hosting
  visibility: private
  org-name: RyoNakagami
  version: 0.1.0
  tag:
    - hosting-server
    - docker
    - htmlhost
  description: |
    A self-hosted web server for static sites, with Tailscale VPN and a simple file uploader.
  license: mit
"""


@pytest.fixture
def repo_metadata(tmp_path):
    """Convert the metadata YAML via the CLI and return the parsed JSON."""
    path = tmp_path / "gh_repo.yml"
    path.write_text(REPO_METADATA_YAML)
    result = runner.invoke(app, [str(path), "--to-json"])
    assert result.exit_code == 0
    return json.loads(result.stdout)


def test_hyphenated_top_level_key_is_preserved(repo_metadata):
    # jq path: .["meta-data"]
    assert "meta-data" in repo_metadata


def test_version_stays_a_string(repo_metadata):
    # GA: VERSION=$(... | jq -r '.["meta-data"].version'); "0.1.0" must not
    # be coerced into a number or otherwise reformatted.
    assert repo_metadata["meta-data"]["version"] == "0.1.0"


def test_tag_list_becomes_json_array(repo_metadata):
    # gh-repo-update: jq -r '.["meta-data"].tag[]'
    assert repo_metadata["meta-data"]["tag"] == [
        "hosting-server",
        "docker",
        "htmlhost",
    ]


def test_block_scalar_description_keeps_trailing_newline(repo_metadata):
    # gh-repo-update: jq -r '.["meta-data"].description'
    assert repo_metadata["meta-data"]["description"] == (
        "A self-hosted web server for static sites, "
        "with Tailscale VPN and a simple file uploader.\n"
    )


def test_missing_optional_key_is_absent_not_empty_string(repo_metadata):
    # gh-repo-update: jq -r '.["meta-data"].homepage // empty' relies on the
    # key being genuinely absent from the JSON when not in the YAML.
    assert "homepage" not in repo_metadata["meta-data"]
