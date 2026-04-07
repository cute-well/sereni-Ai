from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

from flask import Flask
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

from config import get_config
from database import get_db, init_db
from .extensions import csrf, login_manager


def create_app(config_name: str | None = None) -> Flask:
    """Application factory for Sereni.

    Args:
        config_name: Optional explicit config name; defaults to FLASK_ENV.

    Returns:
        Configured Flask app instance.
    """

    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder="../frontend/templates",
        static_folder="../frontend/assets",
        static_url_path="/assets",
    )
    app.config.from_object(get_config(config_name))

    _ensure_instance_folder(app)
    _configure_extensions(app)
    _configure_security(app)
    _register_blueprints(app)
    _register_cli(app)
    _configure_logging(app)

    return app


def _ensure_instance_folder(app: Flask) -> None:
    instance_path = Path(app.instance_path)
    instance_path.mkdir(parents=True, exist_ok=True)


def _configure_extensions(app: Flask) -> None:
    cors_origins = app.config.get(
        "CORS_ORIGINS",
        ["http://localhost:5000", "http://127.0.0.1:5000"],
    )
    CORS(app, resources={r"/api/*": {"origins": cors_origins}})
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)
    init_db(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.session_protection = "strong"


def _configure_security(app: Flask) -> None:
    # Future: add JWT manager, rate limiter, CSRF protection here.
    pass


def _register_blueprints(app: Flask) -> None:
    from .routes.api import api_bp
    from .routes.ui import ui_bp
    from .auth.auth import auth_bp

    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(ui_bp)
    app.register_blueprint(auth_bp)


def _register_cli(app: Flask) -> None:
    @app.cli.command("healthcheck")
    def healthcheck() -> None:  # pragma: no cover - simple utility
        """Basic healthcheck to verify the app boots."""
        click = __import__("click")
        click.echo("Sereni backend is healthy")


def _configure_logging(app: Flask) -> None:
    log_level = getattr(logging, app.config.get("LOG_LEVEL", "INFO"), logging.INFO)
    app.logger.setLevel(log_level)

    log_file = Path(app.config.get("LOG_FILE", "logs/sereni.log"))
    log_file.parent.mkdir(parents=True, exist_ok=True)

    handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3)
    handler.setLevel(log_level)
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s", "%%Y-%%m-%%d %%H:%%M:%%S"
    )
    handler.setFormatter(formatter)

    if not any(isinstance(h, RotatingFileHandler) for h in app.logger.handlers):
        app.logger.addHandler(handler)


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000)
