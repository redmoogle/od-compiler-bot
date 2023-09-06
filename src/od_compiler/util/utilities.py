import re
import shutil
import string
from os.path import getctime
from pathlib import Path

from od_compiler.util.compiler_logger import compile_logger

MAIN_PROC = "/proc/main()"
CODE_FILE = Path.cwd().joinpath("templates/code.dm")
TEST_DME = Path.cwd().joinpath("templates/test.dme")
MAP_FILE = Path.cwd().joinpath("templates/map.dmm")
OD_CONF = Path.cwd().joinpath("templates/server_config.toml")


def cleanOldRuns(run_dir: Path, num_to_keep: int = 5) -> None:
    """
    Remove the oldest runs, keeping the n most recent runs.

    num_to_keep: Number of historic runs that should be maintained
    """
    runs = [x for x in run_dir.iterdir() if x.is_dir()]
    runs.sort(key=getctime)

    while len(runs) > num_to_keep:
        compile_logger.info(f"Cleanup deleting: {runs[0]}")
        shutil.rmtree(runs.pop(0))


def splitLogs(logs: str, killed: bool = False) -> dict[str, str]:
    """
    Split the container logs into compiler and server logs.
    Returns a dictionary containing 'compiler' and 'server' logs.

    logs: Docker container log output to be parsed
    killed: Boolean indicating if the run was killed early or not
    """
    if killed:
        logs_regex = re.compile(
            r"---Start Compiler---(.+?)---End Compiler---.*---Start Server---(.+)",
            re.MULTILINE | re.DOTALL,
        )
    else:
        logs_regex = re.compile(
            r"---Start Compiler---(.+?)---End Compiler---.*---Start Server---(.+?)---End Server---",
            re.MULTILINE | re.DOTALL,
        )

    parsed = {}

    matches = logs_regex.search(logs)

    if matches is None or len(matches.groups()) != 2:
        parsed["error"] = "Bad output"
        return parsed

    compile_log = matches.group(1)
    run_log = matches.group(2)

    parsed["compiler"] = compile_log
    parsed["server"] = run_log

    return parsed


def loadTemplate(line: str, includeProc=True) -> str:
    """
    Replaces the placeholder lines within the template file with the provided run-code.
    Returns a template string which can be written to a run file.

    line: Code to be included
    includeProc: If True, a 'MAIN_PROC' will be injected into the template
    """
    with open(CODE_FILE) as filein:
        template = string.Template(filein.read())

    if includeProc:
        line = "\n\t".join(line.splitlines())
        d = {"proc": MAIN_PROC, "code": f"\t{line}\n"}
    else:
        d = {"proc": line, "code": ""}

    return template.substitute(d)


def stageBuild(codeText: str, dir: Path) -> None:
    """
    Create a directory for the current run and copy over the needed files.
    Creates the run file containing provided arbitrary code.

    codeText: Arbitrary code to be loaded into a template file
    dir: Run directory that'll house all of the needed files
    """
    shutil.copyfile(TEST_DME, dir.joinpath("test.dme"))
    shutil.copyfile(MAP_FILE, dir.joinpath("map.dmm"))
    shutil.copyfile(OD_CONF, dir.joinpath("server_config.toml"))
    with open(dir.joinpath("code.dm"), "a") as fc:
        if MAIN_PROC not in codeText:
            fc.write(loadTemplate(codeText))
        else:
            fc.write(loadTemplate(codeText, False))


def writeOutput(logs: str, dir: Path) -> None:
    """
    Writes the log output into the run directory
    """
    with open(dir.joinpath("run_logs.txt"), "w") as rl:
        rl.write(logs)
