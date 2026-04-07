import pytest

from backend.app import create_app
from config import TestingConfig


@pytest.fixture()
def app():
    app = create_app("testing")
    app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "API_AUTH_TOKEN": None,
    })
    with app.app_context():
        yield app


@pytest.fixture()
def client(app):
    return app.test_client()
