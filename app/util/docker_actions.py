from app.util.compiler_logger import compile_logger
from app.util.utilities import randomString, cleanOldRuns, splitLogs, stageBuild
from app.util.git_actions import updateOD
from pathlib import Path
from time import sleep 
import docker

client = docker.from_env()


def updateBuild() -> None:
    # Check if the version is already built
    try:
        updateOD()
        compile_logger.info(f"Attempting build")
        client.images.build(
            path=f"{Path.cwd()}",
            dockerfile="Dockerfile",
            forcerm=True,
            pull=True,
            encoding="gzip",
            tag=f"test:latest"
        )
    except docker.errors.BuildError:
        raise

def compileTest(codeText: str) -> dict:
    """
    New version that uses the docker API instead of a subprocess 
    """
    try:
        updateBuild()
    except docker.errors.BuildError as e:
        results = {"build_error": True, "exception": str(e)}
        return results

    randomDir = Path.cwd().joinpath(f"runs/{randomString()}")
    stageBuild(codeText=codeText, dir=randomDir)
    
    compile_logger.info("Starting run...")
    container = client.containers.run(
        "test:latest",
        detach=True,
        network_disabled=True,
        volumes=[f"{randomDir}:/app/code:ro"]
    )

    timeout = 30
    stop_time = 3
    elapsed_time = 0
    test_killed = False

    while container.status != 'exited' and elapsed_time < timeout:
        sleep(stop_time)
        elapsed_time += stop_time
        container.reload()
        continue

    if elapsed_time >= timeout:
        compile_logger.warning(f"Killing the container after {elapsed_time} seconds!")
        container.kill()
        test_killed = True

    logs = container.logs().decode("utf-8")
    parsed_logs = splitLogs(logs=logs)
    container.remove(v=True, force=True)
    cleanOldRuns(5)
    compile_logger.info(f"Run complete")

    if "error" in parsed_logs.keys():
        results = {"error": 'Invalid output. Please check logs.', "timeout": test_killed}
        compile_logger.error(f"Failed to parse the log output:\n{logs}")
        return results

    results = {"compiler": parsed_logs['compiler'], "server": parsed_logs['server'], "timeout": test_killed}
    compile_logger.debug(f"Run completed. Returning results:\n{results}")
    return results
