from shutil import copyfile
from shutil import copytree

import pytest


@pytest.fixture(scope="module", autouse=True)
def stage_docker(build_dir):
    copytree("docker", f"{build_dir}/docker")
    copyfile(".dockerignore", f"{build_dir}/.dockerignore")
