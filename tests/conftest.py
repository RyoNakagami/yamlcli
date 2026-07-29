import json

import pytest

from tests.expected_outputs import SAMPLE_DATA, SAMPLE_YAML


@pytest.fixture
def sample_yaml_file(tmp_path):
    path = tmp_path / "sample.yaml"
    path.write_text(SAMPLE_YAML)
    return str(path)


@pytest.fixture
def sample_json_file(tmp_path):
    path = tmp_path / "sample.json"
    path.write_text(json.dumps(SAMPLE_DATA, indent=2))
    return str(path)
