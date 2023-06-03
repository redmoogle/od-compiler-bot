from pathlib import Path

from git.repo import Repo

from od_compiler.util.compiler_logger import compile_logger


def updateOD(od_repo_path: Path, clean: int = False) -> None:
    """
    Update the OpenDream repository if it exists. If it doesn't, clone a fresh copy.
    """
    if clean:
        from shutil import rmtree

        rmtree(od_repo_path)

    if Path.exists(od_repo_path):
        od = Repo(od_repo_path)
        od.remote().fetch()
        # We reset HEAD to the upstream commit as a faster and more reliable way to stay up to date
        od.head.reset(commit="origin/master", working_tree=True)
    else:
        compile_logger.info("Repo not found. Cloning from GitHub.")
        od = Repo.clone_from(
            url="https://github.com/OpenDreamProject/OpenDream.git",
            to_path=od_repo_path,
            multi_options=["--depth 1", "--recurse-submodules", "--shallow-submodules"],
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
        compile_logger.info(f"{submodule.name} is at: {submodule.hexsha}")
