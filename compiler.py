import platform
import random
import shutil
import string
import re
import logging
from pathlib import Path
from time import sleep 

import docker
from git import Repo
from flask import Flask, abort, jsonify, request, Blueprint

compile = Blueprint('compile', __name__, url_prefix='/compile')

logging.basicConfig(
    level=logging.WARNING,
    format="[COMPILER] [%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
compile_logger = logging.getLogger('compiler')


HOST = "127.0.0.1"
PORT = 5000
HOST_OS = platform.system()
MAIN_PROC = "proc/main()"
CODE_FILE = Path.cwd().joinpath("templates/code.dm")
TEST_DME = Path.cwd().joinpath("templates/test.dme")
MAP_FILE = Path.cwd().joinpath("templates/map.dmm")
OD_CONF = Path.cwd().joinpath("templates/server_config.toml")
REPO = Repo(Path.cwd())

client = docker.from_env()
template = None

def create_app(logger_override=None):
    app = Flask(__name__)

    if logger_override:
        app.logger.handlers = logger_override.handlers
        app.logger.setLevel(logger_override.level)
        compile_logger.setLevel(logger_override.level)
        

    app.register_blueprint(compile)

    return app

@compile.route("/", methods=["POST"])
def startCompile():
    if request.method == "POST":
        posted_data = request.get_json()
        if "code_to_compile" in posted_data:
            return jsonify(compileTest(posted_data["code_to_compile"]))
        else:
            compile_logger.warning(f"Bad request recieved:\n\n{request.get_json()}")
            abort(400)


def loadTemplate(line: str, includeProc=True):
    with open(CODE_FILE) as filein:
        template = string.Template(filein.read())

    if includeProc:
        line = "\n\t".join(line.splitlines())
        d = {"proc": MAIN_PROC, "code": f"{line}\n"}
    else:
        d = {"proc": line, "code": ""}

    return template.substitute(d)


def randomString(stringLength=24):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(stringLength))


def updateSubmodules():
    compile_logger.info(f"Updating submodules")
    for submodule in REPO.submodules:
        submodule.update(init=True)


def updateBuild():
    # Check if the version is already built
    try:
        updateSubmodules()
        compile_logger.info(f"Attempting build")
        return client.images.build(
            path=f"{Path.cwd()}",
            dockerfile="Dockerfile",
            rm=True,
            pull=True,
            tag=f"test:latest"
        )
    except docker.errors.BuildError:
        raise


def stageBuild(codeText: str, dir: Path):
    dir.mkdir()
    shutil.copyfile(TEST_DME, dir.joinpath("test.dme"))
    shutil.copyfile(MAP_FILE, dir.joinpath("map.dmm"))
    shutil.copyfile(OD_CONF, dir.joinpath("server_config.toml"))
    with open(dir.joinpath("code.dm"), "a") as fc:
        if MAIN_PROC not in codeText:
            fc.write(loadTemplate(codeText))
        else:
            fc.write(loadTemplate(codeText, False))

def parseLogs(logs: str) -> dict:
    '''
    Why does this work?
    '''
    logs_regex = re.compile(r'---Start Compiler---(.+?)---End Compiler---.*---Start Server---(.+?)---End Server---', re.MULTILINE|re.DOTALL)
    parsed = {}

    matches = logs_regex.search(logs)
    
    if matches is None or len(matches.groups()) != 2:
        parsed['error'] = "Bad output"
        return parsed

    parsed['compiler'] = matches.group(1)
    parsed['server'] = matches.group(2)

    return parsed


def compileTest(codeText: str):
    """
    New version that uses the docker API instead of a subprocess 
    """
    try:
        updateBuild()
    except docker.errors.BuildError as e:
        results = {"build_error": True, "exception": str(e)}
        return results

    randomDir = Path.cwd().joinpath(randomString())
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
    parsed_logs = parseLogs(logs=logs)
    container.remove(v=True, force=True)
    shutil.rmtree(randomDir)
    compile_logger.info(f"Run complete")

    if "error" in parsed_logs.keys():
        results = {"error": 'Invalid output. Please check logs.', "timeout": test_killed}
        compile_logger.warning(f"Failed to parse the log output.\n----------------\n{logs}")
        return results

    results = {"compiler": parsed_logs['compiler'], "server": parsed_logs['server'], "timeout": test_killed}
    compile_logger.debug(f"Run completed. Returning results:\n{results}")
    return results

if __name__ == "__main__":
    print("Run me with 'gunicorn wsgi:app'")
