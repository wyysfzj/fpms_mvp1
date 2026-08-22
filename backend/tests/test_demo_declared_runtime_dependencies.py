import tomllib
from pathlib import Path


def test_openpyxl_is_a_declared_runtime_dependency() -> None:
    dependencies = tomllib.loads(Path("pyproject.toml").read_text())["project"]["dependencies"]
    tracked_requirements = Path("fpms_api.egg-info/requires.txt").read_text().splitlines()

    assert "openpyxl>=3.1.5,<4" in dependencies
    assert "openpyxl<4,>=3.1.5" in tracked_requirements
