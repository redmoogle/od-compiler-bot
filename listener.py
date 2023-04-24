import platform
import random
import shutil
import string
from pathlib import Path
from time import sleep 

import docker
from git import Repo
from flask import Flask, abort, jsonify, request


app = Flask(__name__)
client = docker.from_env()

HOST = "127.0.0.1"
PORT = 5000
HOST_OS = platform.system()
MAIN_PROC = "proc/main()"
CODE_FILE = Path.cwd().joinpath("templates/code.dm")
TEST_DME = Path.cwd().joinpath("templates/test.dme")
MAP_FILE = Path.cwd().joinpath("templates/map.dmm")
OD_CONF = Path.cwd().joinpath("templates/server_config.toml")

template = None

repo = Repo(Path.cwd())
sms = repo.submodules


@app.route("/compile", methods=["POST"])
def startCompile():
    if request.method == "POST":
        posted_data = request.get_json()
        if "code_to_compile" in posted_data:
            return jsonify(compileTestNew(posted_data["code_to_compile"]))
        else:
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


def checkVersions(version: str):
    try:
        image_list = client.images.list(name="test")
    except IndexError:
        return False

    for image in image_list:
        if f"test:{version}" in image.tags:
            return True

    return False

def updateSubmodules():
    print(f"Updating submodules")
    for submodule in repo.submodules:
        submodule.update(init=True)

def updateBuild():
    # Check if the version is already built
    try:
        updateSubmodules()
        print(f"Attempting build")
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


def compileTestNew(codeText: str):
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
        print(container.status)
        sleep(stop_time)
        elapsed_time += stop_time
        container.reload()
        continue

    if elapsed_time >= timeout:
        print("Killing the container")
        container.kill()
        test_killed = True

    logs = container.logs().decode("utf-8")
    container.remove(v=True, force=True)
    shutil.rmtree(randomDir)

    results = {"logs": logs, "timeout": test_killed}

    print(results)
    return results

if __name__ == "__main__":
    app.run(host=HOST, port=PORT)
