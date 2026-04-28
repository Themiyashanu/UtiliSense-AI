"""Export reports: CSV and PDF."""
import io
import csv
from flask import Blueprint, send_file, abort, redirect, url_for, flash
from flask_login import login_required, current_user

from ..models import Bill, Payment

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/")
@login_required
def index():
    return redirect(url_for("main.dashboard"))


@reports_bp.route("/export/csv")
@login_required
def export_csv():
    bills = Bill.query.filter_by(user_id=current_user.id).order_by(Bill.month.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Month", "Electricity (LKR)", "Water (LKR)", "Telecom (LKR)", "Total (LKR)"])
    for b in bills:
        writer.writerow([
            b.month,
            b.electricity_lkr or 0,
            b.water_lkr or 0,
            b.telecom_lkr or 0,
            b.total_lkr,
        ])
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode("utf-8")),
        mimetype="text/csv",
        as_attachment=True,
        download_name="utility_bills_export.csv",
    )


@reports_bp.route("/export/pdf")
@login_required
def export_pdf():
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
        from reportlab.lib.styles import getSampleStyleSheet
    except ImportError:
        flash("PDF export requires: pip install reportlab", "warning")
        return redirect(url_for("main.dashboard"))

    bills = Bill.query.filter_by(user_id=current_user.id).order_by(Bill.month.desc()).limit(24).all()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    elements.append(Paragraph("Utility Bill Report", styles["Title"]))
    elements.append(Paragraph(f"User: {current_user.username}", styles["Normal"]))
    data = [["Month", "Electricity", "Water", "Telecom", "Total"]]
    for b in bills:
        data.append([
            b.month,
            f"{b.electricity_lkr or 0:,.0f}",
            f"{b.water_lkr or 0:,.0f}",
            f"{b.telecom_lkr or 0:,.0f}",
            f"{b.total_lkr:,.0f}",
        ])
    t = Table(data)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    elements.append(t)
    doc.build(elements)
    buffer.seek(0)
    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="utility_report.pdf",
    )
