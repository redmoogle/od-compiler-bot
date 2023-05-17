from pathlib import Path
from time import sleep

import docker

from app.util.compiler_logger import compile_logger
from app.util.git_actions import updateOD
from app.util.utilities import cleanOldRuns
from app.util.utilities import randomString
from app.util.utilities import splitLogs
from app.util.utilities import stageBuild

client = docker.from_env()


def updateBuildImage() -> None:
    """
    Update OpenDream and then use Docker's build context to see if we need to build a new image.
    """
    try:
        updateOD()
        compile_logger.info("Building the docker image...")
        client.images.build(
            path=f"{Path.cwd()}",
            dockerfile="Dockerfile",
            forcerm=True,
            pull=True,
            encoding="gzip",
            tag="od-compiler:latest",
        )
    except docker.errors.BuildError:
        raise


def compileOD(codeText: str, timeout: int = 30) -> dict:
    """
    Create an OpenDream docker container to compile and run arbitrary code.
    Returns A dictionary containing the compiler and server logs.

    The docker container will not have networking and will self-destruct after `timeout` seconds.

    codeText: Arbitrary code to be compiled & Ran
    timeout: Maximum duration a container is allowed to run for
    """
    try:
        updateBuildImage()
    except docker.errors.BuildError as e:
        results = {"build_error": True, "exception": str(e)}
        return results

    randomDir = Path.cwd().joinpath(f"runs/{randomString()}")
    stageBuild(codeText=codeText, dir=randomDir)

    compile_logger.info("Starting run...")
    container = client.containers.run(
        image="od-compiler:latest",
        detach=True,
        network_disabled=True,
        volumes=[f"{randomDir}:/app/code:ro"],
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
    parsed_logs = splitLogs(logs=logs)
    container.remove(v=True, force=True)
    cleanOldRuns()
    compile_logger.info("Run complete!")

    if "error" in parsed_logs.keys():
        results = {"error": "Invalid output. Please check logs.", "timeout": test_killed}
        compile_logger.error(f"Failed to parse the log output:\n{logs}")
        return results

    results = {"compiler": parsed_logs["compiler"], "server": parsed_logs["server"], "timeout": test_killed}
    compile_logger.debug(f"Run completed. Returning results:\n{results}")
    return results
