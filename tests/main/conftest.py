from collections.abc import Generator
from logging import CRITICAL

import pytest
from flask.testing import FlaskClient
from od_compiler import create_app


@pytest.fixture(scope="module")
def client() -> Generator[FlaskClient, None, None]:
    app = create_app(logger_override=CRITICAL)
    app.config.update(
        {
            "TESTING": True,
        }
    )

    with app.test_client() as client:
        yield client
