from pathlib import Path

import pytest

from od_compiler.util.utilities import splitLogs
from od_compiler.util.utilities import writeOutput


@pytest.fixture(scope="module")
def test_logs() -> str:
    with open("tests/utilities/resources/run_logs.txt", "r") as log_file:
        logs = log_file.read()
    return logs


def test_split_logs_standard(test_logs: str):
    parsed = splitLogs(logs=test_logs, killed=False)
    assert "error" not in parsed.keys()


def test_split_logs_killed(test_logs: str):
    parsed = splitLogs(logs=test_logs[:-200], killed=True)
    assert "error" not in parsed.keys()


def test_split_logs_error():
    logs = "This is an invalid log output"
    parsed = splitLogs(logs=logs, killed=True)
    assert "error" in parsed.keys()


def test_write_output(build_dir):
    log = "PASSED"
    writeOutput(logs=log, dir=build_dir)
    log_out = build_dir.joinpath("run_logs.txt").read_text()
    assert log_out == log
