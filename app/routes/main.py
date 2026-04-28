# UPDATED FILE
"""Main routes: dashboard, recommendations, notifications."""
from flask import Blueprint, render_template
from flask_login import login_required, current_user

from ..models import Bill, BudgetSetting, Notification, Prediction

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    if current_user.is_authenticated:
        from flask import redirect, url_for
        return redirect(url_for("main.dashboard"))
    return render_template("auth/login.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    bills = Bill.query.filter_by(user_id=current_user.id).order_by(Bill.month.desc()).all()
    latest_prediction = Prediction.query.filter_by(user_id=current_user.id).order_by(Prediction.created_at.desc()).first()
    budget = BudgetSetting.query.filter_by(user_id=current_user.id).first()
    if not budget:
        from .. import db
        budget = BudgetSetting(user_id=current_user.id, monthly_budget=20000)
        db.session.add(budget)
        db.session.commit()
    notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).order_by(
        Notification.created_at.desc()
    ).limit(10).all()

    chart_labels = [b.month for b in reversed(bills)]
    chart_totals = [float(b.total_lkr) for b in reversed(bills)]
    chart_electricity = [float(b.electricity_lkr or 0) for b in reversed(bills)]
    chart_water = [float(b.water_lkr or 0) for b in reversed(bills)]
    chart_telecom = [float(b.telecom_lkr or 0) for b in reversed(bills)]

    current_total = float(bills[0].total_lkr) if bills else 0
    predicted_total = float(latest_prediction.predicted_total) if latest_prediction else current_total
    budget_limit = float(budget.monthly_budget) if budget else 0
    budget_status = "Safe" if predicted_total <= budget_limit else "Warning"

    prediction_vs_actual_labels = chart_labels[-6:] if chart_labels else []
    prediction_vs_actual_actual = chart_totals[-6:] if chart_totals else []
    prediction_vs_actual_predicted = [predicted_total for _ in prediction_vs_actual_labels] if prediction_vs_actual_labels else []

    return render_template(
        "dashboard.html",
        bills=bills,
        budget=budget,
        latest_prediction=latest_prediction,
        notifications=notifications,
        current_total=current_total,
        predicted_total=predicted_total,
        budget_limit=budget_limit,
        budget_status=budget_status,
        chart_labels=chart_labels or [""],
        chart_totals=chart_totals or [0],
        chart_electricity=chart_electricity or [0],
        chart_water=chart_water or [0],
        chart_telecom=chart_telecom or [0],
        prediction_vs_actual_labels=prediction_vs_actual_labels,
        prediction_vs_actual_actual=prediction_vs_actual_actual,
        prediction_vs_actual_predicted=prediction_vs_actual_predicted,
    )


@main_bp.route("/recommendations")
@login_required
def recommendations():
    bills = Bill.query.filter_by(user_id=current_user.id).order_by(Bill.month.desc()).limit(6).all()
    budget = BudgetSetting.query.filter_by(user_id=current_user.id).first()
    recommendations_list = []
    if bills and budget:
        avg_total = sum(b.total_lkr for b in bills) / len(bills)
        if avg_total > budget.monthly_budget:
            recommendations_list.append({
                "type": "warning",
                "title": "Over budget",
                "text": f"Your average bill ({avg_total:.0f} LKR) exceeds your budget ({budget.monthly_budget:.0f} LKR). Consider reducing electricity or telecom usage."
            })
        if bills and bills[0].electricity_lkr and bills[0].electricity_lkr > 8000:
            recommendations_list.append({
                "type": "info",
                "title": "High electricity",
                "text": "Your electricity bill is high. Try using energy-efficient appliances and switching off unused devices."
            })
        if not recommendations_list:
            recommendations_list.append({
                "type": "success",
                "title": "On track",
                "text": "Your utility expenses appear to be within normal range. Keep tracking to maintain good habits."
            })
    else:
        recommendations_list.append({
            "type": "info",
            "title": "Add data",
            "text": "Add your utility bills to get personalized recommendations."
        })
    return render_template("recommendations.html", recommendations=recommendations_list)


@main_bp.route("/notifications")
@login_required
def notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(
        Notification.created_at.desc()
    ).all()
    return render_template("notifications.html", notifications=notifications)


@main_bp.route("/mark-notification-read/<int:nid>")
@login_required
def mark_notification_read(nid):
    from .. import db
    n = Notification.query.filter_by(id=nid, user_id=current_user.id).first()
    if n:
        n.is_read = True
        db.session.commit()
    from flask import redirect, url_for
    return redirect(url_for("main.notifications"))
