"""Prediction routes - ML-based next month forecast."""
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime

from .. import db
from ..models import Bill, Prediction, BudgetSetting, Notification


def get_predict_service():
    try:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
        from src.predict import predict_next_month
        return predict_next_month
    except Exception:
        return None


predict_bp = Blueprint("predict", __name__)


@predict_bp.route("/")
@login_required
def predict_page():
    bills = Bill.query.filter_by(user_id=current_user.id).order_by(Bill.month.desc()).limit(12).all()
    return render_template("predict/index.html", bills=bills)


@predict_bp.route("/api", methods=["POST"])
@login_required
def predict_api():
    """API: Predict next month. Expects JSON with optional user_recent_bills or uses DB bills."""
    data = request.get_json() or {}
    user_bills = data.get("user_recent_bills")

    if not user_bills:
        # Use bills from DB
        bills = Bill.query.filter_by(user_id=current_user.id).order_by(Bill.month.desc()).limit(3).all()
        user_bills = [
            {
                "month": b.month,
                "electricity": float(b.electricity_lkr or 0),
                "water": float(b.water_lkr or 0),
                "telecom": float(b.telecom_lkr or 0),
                "total": float(b.total_lkr),
            }
            for b in reversed(bills)
        ]

    predict_fn = get_predict_service()
    if predict_fn:
        try:
            result = predict_fn(user_bills, return_breakdown=True)
        except Exception:
            result = _fallback_prediction_from_bills(user_bills)
    else:
        result = _fallback_prediction_from_bills(user_bills)

    # Store prediction
    next_month = _next_month_str()
    pred = Prediction(
        user_id=current_user.id,
        month=next_month,
        predicted_total=result.get("total", 0),
        predicted_electricity=result.get("electricity"),
        predicted_water=result.get("water"),
        predicted_telecom=result.get("telecom"),
        confidence=result.get("confidence", "low"),
    )
    db.session.add(pred)
    db.session.commit()

    # Budget alert
    budget = BudgetSetting.query.filter_by(user_id=current_user.id).first()
    if budget and result.get("total", 0) > budget.monthly_budget:
        n = Notification(
            user_id=current_user.id,
            title="Budget Alert",
            message=f"Predicted bill ({result['total']:.0f} LKR) exceeds your budget ({budget.monthly_budget:.0f} LKR) for {next_month}.",
            category="warning",
        )
        db.session.add(n)
        db.session.commit()

    return jsonify(result)


def _fallback_prediction_from_bills(user_bills):
    """Fallback when ML model unavailable."""
    if not user_bills:
        return {"total": 0, "electricity": 0, "water": 0, "telecom": 0, "confidence": "low"}
    last = user_bills[-1]
    return {
        "total": last.get("total", 0),
        "electricity": last.get("electricity", 0),
        "water": last.get("water", 0),
        "telecom": last.get("telecom", 0),
        "confidence": "low",
    }


def _next_month_str():
    now = datetime.now()
    month, year = now.month, now.year
    month += 1
    if month > 12:
        month, year = 1, year + 1
    return f"{year}-{month:02d}"
