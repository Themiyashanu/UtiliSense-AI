"""Payment tracking routes."""
from datetime import date
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from .. import db
from ..models import Bill, Payment, Notification

payments_bp = Blueprint("payments", __name__)


@payments_bp.route("/")
@login_required
def history():
    payments = (
        Payment.query.filter_by(user_id=current_user.id)
        .order_by(Payment.payment_date.desc())
        .all()
    )
    return render_template("payments/history.html", payments=payments)


@payments_bp.route("/pay-now/<int:bill_id>")
@login_required
def pay_now(bill_id):
    bill = Bill.query.filter_by(id=bill_id, user_id=current_user.id).first_or_404()
    existing = Payment.query.filter_by(bill_id=bill_id).first()
    if existing:
        flash("This bill has already been paid.", "info")
        return redirect(url_for("main.dashboard"))

    payment = Payment(
        user_id=current_user.id,
        bill_id=bill.id,
        amount=bill.total_lkr,
        payment_date=date.today(),
        method="simulated",
        status="completed",
    )
    db.session.add(payment)
    db.session.commit()

    n = Notification(
        user_id=current_user.id,
        title="Payment Recorded",
        message=f"Payment of LKR {bill.total_lkr:,.0f} for {bill.month} recorded.",
        category="success",
    )
    db.session.add(n)
    db.session.commit()

    flash(f"Payment of LKR {bill.total_lkr:,.0f} recorded for {bill.month}.", "success")
    return redirect(request.referrer or url_for("main.dashboard"))
