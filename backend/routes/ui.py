"""UI-facing routes (templates only, no business logic)."""

from flask import Blueprint, render_template

ui_bp = Blueprint("ui", __name__)


@ui_bp.route("/chat")
def chat_page():
    """Render the chat interface."""
    return render_template("index.html")
