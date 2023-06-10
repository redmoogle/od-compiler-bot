from logging import DEBUG
from logging import getLogger

from od_compiler import create_app
from werkzeug.middleware.proxy_fix import ProxyFix


def main():
    app = create_app(logger_override=DEBUG)
    app.run(host="127.0.0.1", port=5000)
    exit()
    # If we run this directly, we don't want to re-create the app immediately after closing.


if __name__ == "__main__":
    main()

gunicorn_logger = getLogger("gunicorn.error")

app = create_app(logger_override=gunicorn_logger.level)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1)  # type: ignore[method-assign]
