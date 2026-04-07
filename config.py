import os
from datetime import timedelta


class BaseConfig:
    """Base configuration shared across environments."""

    # Security
    SECRET_KEY = os.getenv("SERENI_SECRET_KEY")
    if not SECRET_KEY and os.getenv("FLASK_ENV", "development") == "production":
        raise RuntimeError("SERENI_SECRET_KEY must be set in production for session security.")
    SECRET_KEY = SECRET_KEY or os.urandom(32)
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Database
    MONGO_URI = os.getenv(
        "MONGO_URI",
        "mongodb://localhost:27017/sereni",
    )

    # JWT / Auth (future-proof for upgrade)
    ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    REFRESH_TOKEN_EXPIRES = timedelta(days=7)

    # Rate limiting / throttling
    RATELIMIT_DEFAULT = "60/minute"
    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", "memory://")

    # AI pipeline
    AI_DEFAULT_MODEL = "vader"  # placeholder for future BERT/transformer upgrade
    AI_RISK_THRESHOLD = float(os.getenv("AI_RISK_THRESHOLD", 0.65))
    ANALYTICS_MAX_POINTS = int(os.getenv("ANALYTICS_MAX_POINTS", 500))
    REQUIRE_API_TOKEN = os.getenv("REQUIRE_API_TOKEN", "false").lower() == "true"

    # API auth (optional shared token for simple protection)
    API_AUTH_TOKEN = os.getenv("SERENI_API_TOKEN")

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", os.path.join(os.path.dirname(__file__), "logs", "sereni.log"))

    # Frontend
    FRONTEND_CSP = "default-src 'self'; connect-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'"


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_ECHO = False


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


class ProductionConfig(BaseConfig):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = "https"
    REQUIRE_API_TOKEN = True


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(name: str | None = None) -> type[BaseConfig]:
    """Return the config class based on the given name or environment."""
    env_name = name or os.getenv("FLASK_ENV", "development").lower()
    return config_by_name.get(env_name, DevelopmentConfig)
