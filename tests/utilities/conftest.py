from pathlib import Path
from time import sleep

import pytest


@pytest.fixture(scope="session")
def test_run_dir(build_dir: Path) -> Path:
    temp_run_dir = build_dir.joinpath("runs")
    temp_run_dir.mkdir()
    return temp_run_dir


@pytest.fixture(scope="session", autouse=True)
def make_run_dirs(test_run_dir: Path):
    num_runs = 10
    for run in range(num_runs):
        test_run_dir.joinpath(f"{run + 1}").mkdir()
        sleep(0.1)
