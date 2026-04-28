"""Bills routes: add, list, edit, delete."""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from .. import db
from ..models import Bill, Notification

bills_bp = Blueprint("bills", __name__)


@bills_bp.route("/")
@login_required
def list_bills():
    bills = Bill.query.filter_by(user_id=current_user.id).order_by(Bill.month.desc()).all()
    return render_template("bills/list.html", bills=bills)


@bills_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        month = request.form.get("month", "").strip()
        electricity = float(request.form.get("electricity", 0) or 0)
        water = float(request.form.get("water", 0) or 0)
        telecom = float(request.form.get("telecom", 0) or 0)
        total = float(request.form.get("total", 0) or (electricity + water + telecom))
        notes = request.form.get("notes", "").strip()

        if not month:
            flash("Month is required.", "danger")
            return render_template("bills/add.html")

        existing = Bill.query.filter_by(user_id=current_user.id, month=month).first()
        if existing:
            flash(f"Bill for {month} already exists. Edit it instead.", "warning")
            return redirect(url_for("bills.edit", bill_id=existing.id))

        bill = Bill(
            user_id=current_user.id,
            month=month,
            electricity_lkr=electricity,
            water_lkr=water,
            telecom_lkr=telecom,
            total_lkr=total,
            notes=notes,
        )
        db.session.add(bill)
        db.session.commit()
        flash("Bill added successfully.", "success")
        return redirect(url_for("bills.list_bills"))
    return render_template("bills/add.html")


@bills_bp.route("/edit/<int:bill_id>", methods=["GET", "POST"])
@login_required
def edit(bill_id):
    bill = Bill.query.filter_by(id=bill_id, user_id=current_user.id).first_or_404()
    if request.method == "POST":
        bill.month = request.form.get("month", bill.month).strip()
        bill.electricity_lkr = float(request.form.get("electricity", 0) or 0)
        bill.water_lkr = float(request.form.get("water", 0) or 0)
        bill.telecom_lkr = float(request.form.get("telecom", 0) or 0)
        bill.total_lkr = float(request.form.get("total", 0) or (
            bill.electricity_lkr + bill.water_lkr + bill.telecom_lkr
        ))
        bill.notes = request.form.get("notes", "").strip()
        db.session.commit()
        flash("Bill updated.", "success")
        return redirect(url_for("bills.list_bills"))
    return render_template("bills/edit.html", bill=bill)


@bills_bp.route("/delete/<int:bill_id>")
@login_required
def delete(bill_id):
    bill = Bill.query.filter_by(id=bill_id, user_id=current_user.id).first_or_404()
    db.session.delete(bill)
    db.session.commit()
    flash("Bill deleted.", "info")
    return redirect(url_for("bills.list_bills"))
