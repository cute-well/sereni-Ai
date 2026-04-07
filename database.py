"""MongoDB connection helper."""

from __future__ import annotations

from flask import current_app
from pymongo import MongoClient

_client: MongoClient | None = None


def init_db(app) -> None:
    """Initialize Mongo client and attach to Flask app."""
    global _client
    if _client is None:
        _client = MongoClient(app.config["MONGO_URI"])
    app.mongo_client = _client
    app.db = _client.get_default_database()


def get_db():
    """Return the current database handle."""
    return current_app.db
