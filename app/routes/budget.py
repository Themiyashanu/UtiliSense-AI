"""Budget settings routes."""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from .. import db
from ..models import BudgetSetting

budget_bp = Blueprint("budget", __name__)


@budget_bp.route("/", methods=["GET", "POST"])
@login_required
def settings():
    budget = BudgetSetting.query.filter_by(user_id=current_user.id).first()
    if not budget:
        budget = BudgetSetting(user_id=current_user.id, monthly_budget=20000)
        db.session.add(budget)
        db.session.commit()

    if request.method == "POST":
        budget.monthly_budget = float(request.form.get("monthly_budget", 20000) or 20000)
        budget.alert_threshold = float(request.form.get("alert_threshold", 1.0) or 1.0)
        db.session.commit()
        flash("Budget settings saved.", "success")
        return redirect(url_for("budget.settings"))

    return render_template("budget/settings.html", budget=budget)
