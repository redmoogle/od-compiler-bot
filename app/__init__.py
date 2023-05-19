from flask import abort
from flask import Blueprint
from flask import Flask
from flask import jsonify
from flask import request

from app.util.compiler_logger import compile_logger
from app.util.docker_actions import compileOD

compile = Blueprint("compile", __name__, url_prefix="/")


def create_app(logger_override=None) -> Flask:
    app = Flask(__name__)

    if logger_override:
        compile_logger.setLevel(logger_override)

    app.register_blueprint(compile)

    return app


@compile.route("/compile", methods=["POST"])
def startCompile() -> Flask.response_class:
    """
    Takes in arbitrary OD/DM code and returns a JSON response containing compiler and server logs
    """
    if request.method == "POST":
        posted_data = request.get_json()
        compile_logger.debug(f"Request incoming containing: {posted_data}")
        if "code_to_compile" in posted_data:
            compile_logger.info("Request received. Attempting to compile...")
            args = posted_data["extra_arguments"] if "extra_arguments" in posted_data else None
            return jsonify(compileOD(posted_data["code_to_compile"], compile_args=args))
        else:
            compile_logger.warning(f"Bad request received:\n{request.get_json()}")
            abort(400)
