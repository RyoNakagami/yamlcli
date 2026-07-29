import tomllib
from importlib.metadata import PackageNotFoundError
from pathlib import Path

from yamlcli.library import helper_func
from yamlcli.library.helper_func import get_version


def _raise_package_not_found(name):
    raise PackageNotFoundError(name)


def test_get_version_from_installed_metadata():
    version = get_version()
    assert version != "0.0.0"
    assert version[0].isdigit()


def test_get_version_pyproject_fallback(monkeypatch):
    monkeypatch.setattr(helper_func, "version", _raise_package_not_found)

    repo_pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    with repo_pyproject.open("rb") as f:
        expected = tomllib.load(f)["project"]["version"]

    assert get_version() == expected


def test_get_version_fallback_without_tomllib(monkeypatch):
    # Simulate Python < 3.11 where tomllib is unavailable
    monkeypatch.setattr(helper_func, "version", _raise_package_not_found)
    monkeypatch.setattr(helper_func, "tomllib", None)

    assert get_version() == "0.0.0"


def test_get_version_skips_invalid_pyproject(tmp_path, monkeypatch):
    monkeypatch.setattr(helper_func, "version", _raise_package_not_found)

    # Point the module's __file__ at a tree whose pyproject.toml is invalid
    pkg_dir = tmp_path / "pkg"
    pkg_dir.mkdir()
    (tmp_path / "pyproject.toml").write_text("this is [not valid TOML")
    monkeypatch.setattr(helper_func, "__file__", str(pkg_dir / "helper_func.py"))

    assert get_version() == "0.0.0"
