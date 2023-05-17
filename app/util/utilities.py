import random
import shutil
import string
import re
from app.util.compiler_logger import compile_logger
from pathlib import Path
from os.path import getctime

MAIN_PROC = "proc/main()"
CODE_FILE = Path.cwd().joinpath("templates/code.dm")
TEST_DME = Path.cwd().joinpath("templates/test.dme")
MAP_FILE = Path.cwd().joinpath("templates/map.dmm")
OD_CONF = Path.cwd().joinpath("templates/server_config.toml")

def cleanOldRuns(num_to_keep:int = 5) -> None:
    '''
    Clean up the runs directory
    '''
    run_dir = Path.cwd().joinpath("runs")
    runs = [x for x in run_dir.iterdir() if x.is_dir()]
    runs.sort(key=getctime)
    
    while len(runs) > num_to_keep:
        compile_logger.info(f"Cleanup deleting: {runs[0]}")
        shutil.rmtree(runs.pop(0))

def randomString(stringLength=24) -> string:
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(stringLength))

def splitLogs(logs: str) -> dict:
    logs_regex = re.compile(r'---Start Compiler---(.+?)---End Compiler---.*---Start Server---(.+?)---End Server---', re.MULTILINE|re.DOTALL)
    parsed = {}

    matches = logs_regex.search(logs)
    
    if matches is None or len(matches.groups()) != 2:
        parsed['error'] = "Bad output"
        return parsed

    parsed['compiler'] = matches.group(1)
    parsed['server'] = matches.group(2)

    return parsed

def loadTemplate(line: str, includeProc=True) -> string:
    with open(CODE_FILE) as filein:
        template = string.Template(filein.read())

    if includeProc:
        line = "\n\t".join(line.splitlines())
        d = {"proc": MAIN_PROC, "code": f"{line}\n"}
    else:
        d = {"proc": line, "code": ""}

    return template.substitute(d)

def stageBuild(codeText: str, dir: Path) -> None:
    dir.mkdir(parents=True)
    shutil.copyfile(TEST_DME, dir.joinpath("test.dme"))
    shutil.copyfile(MAP_FILE, dir.joinpath("map.dmm"))
    shutil.copyfile(OD_CONF, dir.joinpath("server_config.toml"))
    with open(dir.joinpath("code.dm"), "a") as fc:
        if MAIN_PROC not in codeText:
            fc.write(loadTemplate(codeText))
        else:
            fc.write(loadTemplate(codeText, False))
