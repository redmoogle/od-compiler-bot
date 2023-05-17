import logging

logging.basicConfig(
    level=logging.WARNING, format="[COMPILER] [%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

compile_logger = logging.getLogger("compiler")
