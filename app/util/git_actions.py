from pathlib import Path

from git import Repo

from app.util.compiler_logger import compile_logger


OD_REPO_PATH = Path.cwd().joinpath("OpenDream")


def updateOD(clean: int = False) -> None:
    """
    Update the OpenDream repository if it exists. If it doesn't, clone a fresh copy.
    """
    if clean:
        from shutil import rmtree

        rmtree(OD_REPO_PATH)

    if Path.exists(OD_REPO_PATH):
        od = Repo(OD_REPO_PATH)
        od.remote().fetch()
        # We reset HEAD to the upstream commit as a faster and more reliable way to stay up to date
        od.head.reset(commit="origin/master", working_tree=True)
    else:
        compile_logger.info("Repo not found. Cloning from GitHub.")
        od = Repo.clone_from(
            url="https://github.com/OpenDreamProject/OpenDream.git", to_path=OD_REPO_PATH, multi_options=["--depth 1"]
        )

    compile_logger.info(f"The OpenDream repo is at: {od.head.commit.hexsha}")
    updateSubmodules(od_repo=od)


def updateSubmodules(od_repo: Repo) -> None:
    """
    Recursively update and initialize submodules

    od_repo: OpenDream repository with the submodules
    """
    for submodule in od_repo.submodules:
        submodule.update(init=True, recursive=True)
        compile_logger.info(f"{submodule.name} is at {submodule.hexsha}")
