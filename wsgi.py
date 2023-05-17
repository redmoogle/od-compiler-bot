import logging

from werkzeug.middleware.proxy_fix import ProxyFix

from app import create_app

if __name__ == "__main__":
    app = create_app(logger_override=logging.DEBUG)
    app.run(host="127.0.0.1", port=5000)
    exit()

gunicorn_logger = logging.getLogger("gunicorn.error")

app = create_app(logger_override=gunicorn_logger.level)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1)
