import pytest

from od_compiler.util.git_actions import updateOD


def test_update_repo_clean(od_repo_path):
    updateOD(od_repo_path=od_repo_path, clean=True)


@pytest.mark.depends(on=["test_update_repo_clean"])
def test_update_repo_existing(od_repo_path):
    updateOD(od_repo_path=od_repo_path)
