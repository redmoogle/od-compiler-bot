WIP project. Not entirely organized just yet
---

----

## Requirements:

1. Python 3.11
2. Poetry (Recommended)
3. Docker

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
