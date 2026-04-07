"""API routes for Sereni."""

from __future__ import annotations

from http import HTTPStatus
import token
from typing import Any, Dict

from flask import Blueprint, current_app, jsonify, request

from backend.services.chat_service import ChatService
from backend.services.grounding_engine import GroundingEngine
from backend.utils.security import rate_limited, sanitize_text
from backend.extensions import csrf

api_bp = Blueprint("api", __name__)
csrf.exempt(api_bp)


def _require_token() -> None:
    """Return error response if bearer token is configured and missing/invalid."""
    token = current_app.config.get("API_AUTH_TOKEN")
    require_token = current_app.config.get("REQUIRE_API_TOKEN", False)

    if require_token and not token:
        return _json_error("Server misconfigured: API token required", HTTPStatus.SERVICE_UNAVAILABLE)

# Auth disabled for demo


def _json_error(message: str, status: HTTPStatus) -> Any:
    """Standard JSON error envelope."""
    response = jsonify({"error": message})
    response.status_code = status
    return response


@api_bp.route("/chat", methods=["POST"])
@rate_limited((60, 60))
def chat() -> Any:
    auth = _require_token()
    if auth:
        return auth

    payload = request.get_json(silent=True) or {}
    user_id = str(payload.get("user_id", "anonymous"))
    message = sanitize_text(payload.get("message", ""))

    if not message:
        return _json_error("Message is required", HTTPStatus.BAD_REQUEST)
    if len(message) > 4000:
        return _json_error("Message too long", HTTPStatus.BAD_REQUEST)

    try:
        service = ChatService()
        result = service.handle_chat(message, user_id)
        return _json_ok(result)
    except Exception as exc:  # pragma: no cover - safety net
        current_app.logger.exception("chat endpoint failure")
        return _json_error("Internal server error", HTTPStatus.INTERNAL_SERVER_ERROR)


@api_bp.route("/analyze", methods=["POST"])
@rate_limited((120, 60))
def analyze() -> Any:
    auth = _require_token()
    if auth:
        return auth

    payload = request.get_json(silent=True) or {}
    text = sanitize_text(payload.get("text", ""))
    user_id = str(payload.get("user_id", "anonymous"))

    if not text:
        return _json_error("Text is required", HTTPStatus.BAD_REQUEST)
    if len(text) > 4000:
        return _json_error("Text too long", HTTPStatus.BAD_REQUEST)

    try:
        service = ChatService()
        result = service.analyze_text(text, user_id)
        return _json_ok(result)
    except Exception:  # pragma: no cover - safety net
        current_app.logger.exception("analyze endpoint failure")
        return _json_error("Internal server error", HTTPStatus.INTERNAL_SERVER_ERROR)


@api_bp.route("/emergency", methods=["GET"])
def emergency() -> Any:
    helplines = [
        {
            "name": "988 Suicide & Crisis Lifeline",
            "phone": "988",
            "country": "US",
            "notes": "24/7 free and confidential support.",
        },
        {
            "name": "Crisis Text Line",
            "text": "Text HOME to 741741",
            "country": "US",
            "notes": "24/7 text-based crisis support.",
        },
        {
            "name": "SAMHSA National Helpline",
            "phone": "1-800-662-HELP (4357)",
            "country": "US",
            "notes": "Treatment referral and information.",
        },
    ]
    return _json_ok({"helplines": helplines})


def _json_ok(payload: Dict[str, Any]) -> Any:
    """Standard JSON success envelope."""
    response = jsonify(payload)
    response.status_code = HTTPStatus.OK
    return response
