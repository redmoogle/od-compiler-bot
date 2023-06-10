from datetime import datetime
from pathlib import Path
from time import sleep

from gitdb.exc import BadName
from od_compiler.util.compiler_logger import compile_logger
from od_compiler.util.git_actions import updateOD
from od_compiler.util.utilities import cleanOldRuns
from od_compiler.util.utilities import splitLogs
from od_compiler.util.utilities import stageBuild
from od_compiler.util.utilities import writeOutput

from docker.client import from_env as docker_from_env
from docker.errors import BuildError

client = docker_from_env()


def updateBuildImage() -> None:
    """
    Update OpenDream and then use Docker's build context to see if we need to build a new image.
    """
    od_path = Path.cwd().joinpath("OpenDream")
    try:
        updateOD(od_repo_path=od_path)
    except BadName:
        compile_logger.warning("There was an error updating the repo. Cleaning up and trying again.")
        updateOD(od_repo_path=od_path, clean=True)

    compile_logger.info("Building the docker image...")
    client.images.build(
        path=f"{Path.cwd()}",
        dockerfile=Path.cwd().joinpath("docker/Dockerfile"),
        forcerm=True,
        pull=True,
        encoding="gzip",
        tag="od-compiler:latest",
    )
    client.images.prune(filters={"dangling": True})


def compileOD(codeText: str, compile_args: list[str], timeout: int = 30) -> dict[str, object]:
    """
    Create an OpenDream docker container to compile and run arbitrary code.
    Returns A dictionary containing the compiler and server logs.

    The docker container will not have networking and will self-destruct after `timeout` seconds.

    codeText: Arbitrary code to be compiled & Ran
    timeout: Maximum duration a container is allowed to run for
    """
    try:
        updateBuildImage()
    except BuildError as e:
        results = {"build_error": True, "exception": str(e)}
        return results

    timestamp = datetime.now().strftime("%Y%m%d-%H.%M.%S.%f")
    randomDir = Path.cwd().joinpath(f"runs/{timestamp}")
    randomDir.mkdir(parents=True)

    stageBuild(codeText=codeText, dir=randomDir)

    compile_logger.info("Starting run...")
    container = client.containers.run(
        image="od-compiler:latest",
        detach=True,
        network_disabled=True,
        volumes=[f"{randomDir}:/app/code:ro"],
        command=compile_args,
        cgroup_parent="od_compiler.slice",
    )

    stop_time = 3
    elapsed_time = 0
    test_killed = False

    while container.status != "exited" and elapsed_time < timeout:
        sleep(stop_time)
        elapsed_time += stop_time
        container.reload()
        continue

    if elapsed_time >= timeout:
        compile_logger.warning(f"Killing the container after {elapsed_time} seconds!")
        container.kill()
        test_killed = True

    # Container logs are byte encoded
    logs = container.logs().decode("utf-8")
    parsed_logs = splitLogs(logs=logs, killed=test_killed)
    container.remove(v=True, force=True)
    writeOutput(logs=logs, dir=randomDir)
    cleanOldRuns(run_dir=Path.cwd().joinpath("runs"))
    compile_logger.info("Run complete!")

    if "error" in parsed_logs.keys():
        results = {"error": "Invalid output. Please check logs.", "timeout": test_killed}
        compile_logger.error(f"Failed to parse the log output:\n{logs}")
        return results

    results = {"compiler": parsed_logs["compiler"], "server": parsed_logs["server"], "timeout": test_killed}
    compile_logger.debug(f"Returning results:\n{results}")
    return results
