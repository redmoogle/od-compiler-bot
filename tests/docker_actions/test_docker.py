from os import chdir

import pytest
from od_compiler.util.docker_actions import compileOD

from docker.errors import BuildError


@pytest.mark.order(index=-1)
def test_standard_compile(build_dir):
    code = 'world.log << "Hello, pytest!"'

    chdir(build_dir)
    test_output = compileOD(codeText=code, compile_args=[""], build_config="Release", timeout=30)
    assert test_output.keys() >= {"compiler", "server", "timeout"}


@pytest.mark.order(index=-1)
def test_complex_compile(build_dir):
    code = """\
/proc/example()
  world.log << "Hello!"

/proc/main()
  example
"""

    chdir(build_dir)
    test_output = compileOD(codeText=code, compile_args=[""], build_config="Release", timeout=30)
    assert test_output.keys() >= {"compiler", "server", "timeout"}


@pytest.mark.order(index=-1)
def test_build_error(build_dir, mocker):
    mocker.patch(
        "od_compiler.util.docker_actions.updateBuildImage", side_effect=BuildError(reason="pytest", build_log="pytest")
    )
    code = 'world.log << "Hello, pytest!"'

    chdir(build_dir)
    test_output = compileOD(codeText=code, compile_args=[""], build_config="Release", timeout=30)
    assert "build_error" in test_output.keys()


@pytest.mark.order(index=-1)
def test_compile_timeout(build_dir):
    code = 'world.log << "Sleeping"\nsleep(500)'

    chdir(build_dir)
    test_output = compileOD(codeText=code, compile_args=[""], build_config="Release", timeout=5)
    assert test_output["timeout"] is True


@pytest.mark.order(index=-1)
def test_compile_bad_logs(build_dir, mocker):
    logs_return = {"error": "pytest"}
    mocker.patch("od_compiler.util.docker_actions.splitLogs", return_value=logs_return)

    chdir(build_dir)
    code = 'world.log << "Hello, pytest!"'
    test_output = compileOD(codeText=code, compile_args=[""], build_config="Release", timeout=30)

    assert "error" in test_output.keys()
