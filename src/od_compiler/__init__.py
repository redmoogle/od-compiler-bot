from importlib.metadata import version

from flask import abort
from flask import Blueprint
from flask import Flask
from flask import jsonify
from flask import request
from flask import Response
from od_compiler.util.compiler_logger import compile_logger
from od_compiler.util.docker_actions import compileOD

__version__ = version("od-compiler")

compile = Blueprint("compile", __name__, url_prefix="/")


def create_app(logger_override=None) -> Flask:
    app = Flask(__name__)

    if logger_override:
        compile_logger.setLevel(logger_override)

    app.register_blueprint(compile)

    return app


@compile.route("/compile", methods=["POST"])
def startCompile() -> Response:
    """
    Takes in arbitrary OD/DM code and returns a JSON response containing compiler and server logs
    """
    posted_data = request.get_json()
    compile_logger.debug(f"Request incoming containing: {posted_data}")
    if "code_to_compile" in posted_data:
        compile_logger.info("Request received. Attempting to compile...")
        build_args = posted_data["build_config"] if "build_config" in posted_data else "Release"
        compile_args = posted_data["extra_arguments"] if "extra_arguments" in posted_data else None
        return jsonify(compileOD(posted_data["code_to_compile"], compile_args=compile_args, build_config=build_args))
    else:
        compile_logger.warning(f"Bad request received:\n{request.get_json()}")
        return abort(400)


@compile.route("/version", methods=["GET"])
def getVersion() -> Response:
    """
    Returns the current version of the compiler server
    """
    return jsonify({"version": __version__})  # Could expand this to give the revisions from OD
