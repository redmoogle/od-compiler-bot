## Requirements:

1. Python 3.11
2. Poetry (Recommended)
3. Docker (**Strongly** recommended that this is ran in rootless mode)
4. ~10GB of disk space

## About:

A simple bot that takes arbitrary code and compiles/executes it within a Docker sandbox environment. The Docker containers lack network, compile/execute code as an unprivileged user, only have access to a read-only volume, and self destruct after 30-seconds. It is recommended that you pair this with a frontend, such as the Discord RedBot cog found here: https://github.com/OpenDreamProject/od-cogs

Whenever the OpenDream repository is updated, the server will build an updated Docker image on the next request. This garuntees that the code is always running on the latest version, but, it can also take a few minutes depending on your network speed and hardware. 

## Install:

Setup the python environment and install the required dependencies. If you have poetry, simply run `poetry install --only main` within the base directory.

## Running

To start an active server, run using gunicorn. You can specify the number of workers and the log level using the below command.

```
gunicorn -b 127.0.0.1:5000 wsgi:app --log-level info --workers 1 --timeout 200
```

Alternatively, you can start the application directly in developer debug mode with

```
python wsgi.py
```

## Development

Setup the python environment with `poetry install`, activate the environment with `poetry shell`, install the pre-commit hooks with `pre-commit install`
