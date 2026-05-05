"""Payment tracking routes."""
from datetime import date
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
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
    return redirect(url_for("payments.checkout", bill_id=bill.id))


def _masked_card(card_number):
    cleaned = "".join(ch for ch in card_number if ch.isdigit())
    if len(cleaned) < 4:
        return "****"
    return f"**** **** **** {cleaned[-4:]}"


@payments_bp.route("/checkout/<int:bill_id>", methods=["GET", "POST"])
@login_required
def checkout(bill_id):
    bill = Bill.query.filter_by(id=bill_id, user_id=current_user.id).first_or_404()
    if Payment.query.filter_by(bill_id=bill_id).first():
        flash("This bill has already been paid.", "info")
        return redirect(url_for("main.dashboard"))

    draft_key = f"payment_draft_{bill_id}"
    draft = session.get(draft_key, {})

    if request.method == "POST":
        method = request.form.get("method", "card").strip().lower()
        card_holder = request.form.get("card_holder", "").strip()
        card_number = request.form.get("card_number", "").strip().replace(" ", "")
        expiry = request.form.get("expiry", "").strip()
        cvv = request.form.get("cvv", "").strip()

        if method not in {"card", "bank_transfer", "wallet"}:
            flash("Please choose a valid payment method.", "danger")
            return redirect(url_for("payments.checkout", bill_id=bill_id))

        if method == "card":
            if not card_holder:
                flash("Card holder name is required.", "danger")
                return redirect(url_for("payments.checkout", bill_id=bill_id))
            if not card_number.isdigit() or len(card_number) < 12 or len(card_number) > 19:
                flash("Enter a valid card number.", "danger")
                return redirect(url_for("payments.checkout", bill_id=bill_id))
            if len(expiry) != 5 or expiry[2] != "/":
                flash("Expiry should be in MM/YY format.", "danger")
                return redirect(url_for("payments.checkout", bill_id=bill_id))
            if not cvv.isdigit() or len(cvv) not in {3, 4}:
                flash("Enter a valid CVV.", "danger")
                return redirect(url_for("payments.checkout", bill_id=bill_id))

        session[draft_key] = {
            "method": method,
            "card_holder": card_holder,
            "card_number_masked": _masked_card(card_number) if method == "card" else "",
            "expiry": expiry if method == "card" else "",
        }
        session.modified = True
        return redirect(url_for("payments.review_payment", bill_id=bill_id))

    return render_template("payments/checkout.html", bill=bill, draft=draft)


@payments_bp.route("/checkout/<int:bill_id>/review", methods=["GET", "POST"])
@login_required
def review_payment(bill_id):
    bill = Bill.query.filter_by(id=bill_id, user_id=current_user.id).first_or_404()
    if Payment.query.filter_by(bill_id=bill_id).first():
        flash("This bill has already been paid.", "info")
        return redirect(url_for("main.dashboard"))

    draft_key = f"payment_draft_{bill_id}"
    draft = session.get(draft_key)
    if not draft:
        flash("Start payment from checkout page.", "warning")
        return redirect(url_for("payments.checkout", bill_id=bill_id))

    if request.method == "POST":
        method_labels = {
            "card": "Card Payment (Simulated)",
            "bank_transfer": "Bank Transfer (Simulated)",
            "wallet": "Digital Wallet (Simulated)",
        }
        payment = Payment(
            user_id=current_user.id,
            bill_id=bill.id,
            amount=bill.total_lkr,
            payment_date=date.today(),
            method=method_labels.get(draft["method"], "Simulated"),
            status="completed",
        )
        db.session.add(payment)
        db.session.commit()

        n = Notification(
            user_id=current_user.id,
            title="Payment Successful",
            message=f"Payment of LKR {bill.total_lkr:,.0f} for {bill.month} completed via {payment.method}.",
            category="success",
        )
        db.session.add(n)
        db.session.commit()

        session.pop(draft_key, None)
        flash(f"Payment successful for {bill.month}.", "success")
        return redirect(url_for("payments.history"))

    return render_template("payments/review.html", bill=bill, draft=draft)
