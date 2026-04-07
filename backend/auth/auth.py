"""Authentication routes and login handling."""

from __future__ import annotations

from typing import Optional

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired, Email
from werkzeug.security import generate_password_hash

from backend.models import User, find_user_by_email, find_user_by_id
from backend.utils.encryption import verify_password
from backend.extensions import login_manager
from database import get_db

auth_bp = Blueprint("auth", __name__)


# ------------------ FORMS ------------------

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])


# ------------------ USER LOADER ------------------

@login_manager.user_loader
def load_user(user_id: str) -> Optional[User]:
    db = get_db()
    return find_user_by_id(db, user_id)


# ------------------ REGISTER ------------------

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("ui.chat_page"))

    if request.method == "POST":
        db = get_db()
        email = request.form.get("email")
        password = request.form.get("password")

        # Check if user exists
        existing_user = find_user_by_email(db, email)
        if existing_user:
            flash("User already exists.", "warning")
            return redirect(url_for("auth.register"))

        # Insert user into MongoDB
        db.users.insert_one({
            "email": email,
            "password_hash": generate_password_hash(password),
            "is_active": True
        })

        flash("Registration successful. Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


# ------------------ LOGIN ------------------

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("ui.chat_page"))

    form = LoginForm()

    if form.validate_on_submit():
        db = get_db()
        user = find_user_by_email(db, form.email.data)

        if user and verify_password(form.password.data, user.password_hash):
            if not user.is_active:
                flash("Account inactive.", "warning")
            else:
                login_user(user)
                return redirect(request.args.get("next") or url_for("ui.chat_page"))
        else:
            flash("Invalid credentials.", "danger")

    return render_template("login.html", form=form)


# ------------------ LOGOUT ------------------

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


# ------------------ HOME ------------------

@auth_bp.route("/")
@login_required
def home():
    return redirect(url_for("ui.chat_page"))


# ------------------ BACKWARD ROUTE ------------------

@auth_bp.route("/auth/login", methods=["GET", "POST"])
def login_redirect():
    return redirect(url_for("auth.login"))