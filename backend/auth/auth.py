"""Authentication routes and login handling."""

from __future__ import annotations

from typing import Optional

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired, Email

from backend.models import User
from backend.utils.encryption import verify_password
from backend.extensions import login_manager

auth_bp = Blueprint("auth", __name__)


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])


@login_manager.user_loader
def load_user(user_id: str) -> Optional[User]:
    return User.query.get(int(user_id))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("api.chat"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and verify_password(form.password.data, user.password_hash):
            if not user.is_active:
                flash("Account inactive. Please contact support.", "warning")
            else:
                login_user(user)
                return redirect(request.args.get("next") or url_for("ui.chat_page"))
        else:
            flash("Invalid credentials.", "danger")

    return render_template("login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth_bp.route("/")
@login_required
def home():
    return render_template("index.html")


@auth_bp.route("/auth/login", methods=["GET", "POST"])
def login_redirect():
    """Backwards-compatible login route."""
    return redirect(url_for("auth.login"))
