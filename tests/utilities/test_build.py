import pytest
from od_compiler.util.utilities import cleanOldRuns
from od_compiler.util.utilities import stageBuild

from tests.utilities import runs_list


def test_build_staging_create_files_without_main(build_dir):
    code = 'world.log << "Hello!"'
    expected_files = ["code.dm", "map.dmm", "server_config.toml", "test.dme"]
    stage_dir = build_dir.joinpath("staging")
    stage_dir.mkdir()

    stageBuild(codeText=code, dir=stage_dir)
    files = [file.name for file in stage_dir.iterdir()]
    assert expected_files == sorted(files)


def test_build_staging_create_files_with_defined_main(build_dir):
    code = """\
/proc/example()
  world.log << "Hello!"

/proc/main()
  example()
"""
    expected_files = ["code.dm", "map.dmm", "server_config.toml", "test.dme"]
    stage_dir = build_dir.joinpath("staging_proc")
    stage_dir.mkdir()

    stageBuild(codeText=code, dir=stage_dir)
    files = [file.name for file in stage_dir.iterdir()]
    assert expected_files == sorted(files)


@pytest.mark.depends(on=["test_build_staging_create_files_with_defined_main"])
def test_build_staging_verify_file_contents(build_dir):
    expected_output = """\
/var/TEST/aaaaaa=new

/proc/example()
  world.log << "Hello!"

/proc/main()
  example()


/TEST/New()
  world.log << "-------ODC-Start-------"
  main()
  world.log << "--------ODC-End--------"
  shutdown()
"""
    stage_dir = build_dir.joinpath("staging_proc")
    code_output = stage_dir.joinpath("code.dm").read_text()
    assert code_output == expected_output


def test_run_cleanup_final_len(test_run_dir):
    cleanOldRuns(run_dir=test_run_dir, num_to_keep=5)
    runs = runs_list(test_run_dir)
    assert len(runs) == 5


@pytest.mark.depends(on=["test_run_cleanup_final_len"])
def test_run_cleanup_verify_remaining_order(test_run_dir):
    runs = [int(run.name) for run in runs_list(test_run_dir)]
    assert sorted(runs) == list(range(min(runs), max(runs) + 1))
