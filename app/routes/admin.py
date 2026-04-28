"""Admin routes: admin authentication, users, logs."""
# UPDATED FILE
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user, login_user

from ..models import User, Log

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated and getattr(current_user, "is_admin", False):
        return redirect(url_for("admin.index"))

    if request.method == "POST":
        from ..models import User

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        admin_user = User.query.filter_by(username=username, is_admin=True).first()

        if admin_user and admin_user.check_password(password):
            login_user(admin_user)
            next_url = request.args.get("next")
            if next_url and next_url.startswith("/admin"):
                return redirect(next_url)
            return redirect(url_for("admin.index"))

        flash("Invalid admin credentials.", "danger")

    return render_template("admin/login.html")


@admin_bp.route("/")
@login_required
def index():
    if not getattr(current_user, "is_admin", False):
        flash("Admin access required.", "warning")
        return redirect(url_for("admin.login"))
    return render_template("admin/index.html")


@admin_bp.route("/users")
@login_required
def users():
    if not getattr(current_user, "is_admin", False):
        flash("Admin access required.", "warning")
        return redirect(url_for("admin.login"))
    users_list = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=users_list)


@admin_bp.route("/logs")
@login_required
def logs():
    if not getattr(current_user, "is_admin", False):
        flash("Admin access required.", "warning")
        return redirect(url_for("admin.login"))
    logs_list = Log.query.order_by(Log.created_at.desc()).limit(200).all()
    return render_template("admin/logs.html", logs=logs_list)
