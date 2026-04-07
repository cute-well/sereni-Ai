"""Database initialization and session utilities."""

from __future__ import annotations

from flask_sqlalchemy import SQLAlchemy

# Global SQLAlchemy instance to be initialized in the application factory
# Keeping the instance here avoids circular imports across blueprints.
db = SQLAlchemy()


def init_db(app) -> None:
    """Bind the SQLAlchemy instance to the app and create tables if needed."""
    db.init_app(app)

    with app.app_context():
        db.create_all()
