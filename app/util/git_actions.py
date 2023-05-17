from app.util.compiler_logger import compile_logger
from pathlib import Path

from git import Repo

OD_REPO_PATH = Path.cwd().joinpath("OpenDream")

def updateOD() -> None:
    if Path.exists(OD_REPO_PATH):
        od = Repo(OD_REPO_PATH)     
        od.remote().fetch()
        od.head.reset(commit="origin/master",working_tree=True)
        compile_logger.info(f"The OpenDream repo is at: {od.head.commit.hexsha}")
    else:
        compile_logger.info("Repo not found. Cloning from GitHub.")
        od = Repo.clone_from(
            url='https://github.com/OpenDreamProject/OpenDream.git',
            to_path=OD_REPO_PATH,
            multi_options=['--depth 1']
        )
        compile_logger.info(f"The OpenDream repo is at: {od.head.commit.hexsha}")

    updateSubmodules(od_repo=od)


def updateSubmodules(od_repo:Repo) -> None:

    for submodule in od_repo.submodules:
        submodule.update(init=True,recursive=True)
        compile_logger.info(f"{submodule.name} is at {submodule.hexsha}")