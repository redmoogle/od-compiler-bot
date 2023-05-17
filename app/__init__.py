from app.util.compiler_logger import compile_logger
from app.util.docker_actions import compileTest
from logging import INFO
from flask import Flask, abort, jsonify, request, Blueprint

compile = Blueprint('compile', __name__, url_prefix='/')

def create_app(logger_override=None) -> Flask:
    app = Flask(__name__)

    if logger_override:
        compile_logger.setLevel(logger_override)
        
    app.register_blueprint(compile)

    return app

@compile.route("/compile", methods=["POST"])
def startCompile() -> Flask.response_class:
    if request.method == "POST":
        posted_data = request.get_json()
        if "code_to_compile" in posted_data:
            return jsonify(compileTest(posted_data["code_to_compile"]))
        else:
            compile_logger.warning(f"Bad request recieved:\n{request.get_json()}")
            abort(400)
