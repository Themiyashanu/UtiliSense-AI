"""Authentication routes."""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from .. import db
from ..models import User, Log

auth_bp = Blueprint("auth", __name__)


def log_action(action: str, details: str = "", user_id=None):
    try:
        log = Log(user_id=user_id, action=action, details=details, ip_address=request.remote_addr)
        db.session.add(log)
        db.session.commit()
    except Exception:
        pass


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        if not username or not password:
            flash("Username and password required.", "danger")
            return render_template("auth/register.html")
        if User.query.filter_by(username=username).first():
            flash("Username already taken.", "danger")
            return render_template("auth/register.html")
        user = User(username=username, email=email or None)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        log_action("register", f"User {username} registered")
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            log_action("login", f"User {username} logged in", user.id)
            next_url = request.args.get("next") or url_for("main.dashboard")
            return redirect(next_url)
        flash("Invalid username or password.", "danger")
    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    log_action("logout", f"User {current_user.username} logged out", current_user.id)
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
