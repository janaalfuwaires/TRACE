"""
PDF Investigation Report generator for TRACE.
Uses reportlab only — no external services.
Builds the report entirely from data already produced by
detector.py and compliance_assistant.py.
"""

import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)


def _logo_flowable():
    """
    Draws a simple TRACE/ shield logo using vector shapes,
    so the report doesn't depend on an external image file.
    Replace this with an Image("logo.png", width=3*cm, height=3*cm)
    flowable if you have an actual logo file in your project.
    """
    from reportlab.graphics.shapes import Drawing, Circle, String
    d = Drawing(120, 60)
    d.add(Circle(30, 30, 25, fillColor=colors.HexColor("#8B0000"), strokeColor=None))
    d.add(String(15, 25, "TRACE", fontSize=11, fillColor=colors.white))
    return d


def build_investigation_report_pdf(analysis: dict, compliance_report: dict) -> bytes:
    """
    Builds a full investigation report PDF and returns it as raw bytes.
    `analysis` = response of GET /analysis
    `compliance_report` = response of GET /compliance-report
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=1.5 * cm, bottomMargin=1.5 * cm,
        leftMargin=1.8 * cm, rightMargin=1.8 * cm
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TraceTitle", parent=styles["Title"], textColor=colors.HexColor("#0B132B")
    )
    heading_style = ParagraphStyle(
        "TraceHeading", parent=styles["Heading2"], textColor=colors.HexColor("#8B0000"),
        spaceBefore=14, spaceAfter=6
    )
    normal = styles["Normal"]

    story = []

    # ---- Header / Logo ----
    story.append(_logo_flowable())
    story.append(Spacer(1, 10))
    story.append(Paragraph("TRACE — Investigation Report", title_style))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", normal
    ))
    story.append(Spacer(1, 16))

    # ---- Risk Score ----
    story.append(Paragraph("Risk Score", heading_style))
    story.append(Paragraph(f"<b>{analysis.get('risk_score', 0)}%</b>", normal))
    story.append(Spacer(1, 8))

    # ---- Transaction Statistics ----
    story.append(Paragraph("Transaction Statistics", heading_style))
    stats_table = Table([
        ["Metric", "Value"],
        ["Total Transactions", str(analysis.get("transactions", 0))],
        ["Tracked Accounts", str(analysis.get("accounts", 0))],
        ["Connected Banks", str(analysis.get("banks", 0))],
        ["Suspicious Accounts", str(len(analysis.get("suspicious_accounts", [])))],
    ], colWidths=[8 * cm, 6 * cm])
    stats_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B132B")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
    ]))
    story.append(stats_table)
    story.append(Spacer(1, 12))

    # ---- Reasons (global) ----
    story.append(Paragraph("Detected Risk Factors", heading_style))
    reasons = analysis.get("reasons", [])
    if reasons:
        for r in reasons:
            story.append(Paragraph(f"• {r}", normal))
    else:
        story.append(Paragraph("No specific risk factors detected.", normal))
    story.append(Spacer(1, 12))

    # ---- Suspicious Accounts ----
    story.append(Paragraph("Suspicious Accounts", heading_style))
    suspicious_accounts = analysis.get("suspicious_accounts", [])
    if suspicious_accounts:
        acc_table = Table(
            [["Account ID"]] + [[a] for a in suspicious_accounts],
            colWidths=[14 * cm]
        )
        acc_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B132B")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
        ]))
        story.append(acc_table)
    else:
        story.append(Paragraph("No suspicious accounts identified.", normal))
    story.append(Spacer(1, 12))

    # ---- Investigation Summary (from Compliance Assistant) ----
    story.append(PageBreak())
    story.append(Paragraph("Investigation Summary", heading_style))
    summary_text = compliance_report.get("summary", "No summary available.")
    for line in summary_text.split("\n"):
        story.append(Paragraph(line if line.strip() else "&nbsp;", normal))
    story.append(Spacer(1, 12))

    # ---- AI Recommendations per account ----
    story.append(Paragraph("AI Recommendations", heading_style))
    accounts = compliance_report.get("accounts", [])
    if accounts:
        rec_data = [["Account", "Action", "Urgency", "Reason"]]
        for acc in accounts:
            rec_data.append([
                acc.get("account_id", ""),
                acc.get("action", ""),
                acc.get("urgency", ""),
                Paragraph(acc.get("action_reason", ""), normal),
            ])
        rec_table = Table(rec_data, colWidths=[3 * cm, 3.5 * cm, 2.5 * cm, 5 * cm])
        rec_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B132B")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ]))
        story.append(rec_table)
    else:
        story.append(Paragraph("No account-level recommendations available.", normal))

    story.append(Spacer(1, 20))
    story.append(Paragraph(
        "This report was generated automatically by TRACE's rule-based "
        "compliance engine and must be reviewed by a qualified AML officer "
        "before any action is taken.", normal
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()