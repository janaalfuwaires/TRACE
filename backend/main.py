
from fastapi import FastAPI
from fastapi.responses import Response
import sqlite3
import pandas as pd
from pydantic import BaseModel
from backend.detector import (
    detect_risk,
    calculate_network_similarity
)

from backend.db import (
    init_db,
    load_csv_to_db,
)

from backend.compliance_assistant import generate_compliance_report
from backend.pdf_report import build_investigation_report_pdf

app = FastAPI()

DB = "data/transactions.db"

init_db()
load_csv_to_db()


def load_data():
    conn = sqlite3.connect(DB)
    df = pd.read_sql_query("SELECT * FROM transactions", conn)
    conn.close()
    return df


@app.get("/transactions")
def get_transactions():
    return load_data().to_dict(orient="records")

network_similarity = calculate_network_similarity(
    df,
    suspicious_accounts
)
@app.get("/analysis")
def analysis():
    df = load_data()

    score, explanation, suspicious_accounts = detect_risk(df)
)
    accounts = len(set(df["sender"]).union(set(df["receiver"])))

    return {
        "risk_score": score,
        "explanation": explanation,
        "banks": df["from_bank"].nunique(),
        "accounts": accounts,
        "transactions": len(df),
        "suspicious_accounts": suspicious_accounts,
        "network_similarity": network_similarity,
    }


@app.get("/compliance-report")
def compliance_report():
    df = load_data()

    score, explanation, suspicious_accounts = detect_risk(df)   
    report = generate_compliance_report(
        df,
        score,
        [x["factor"] for x in explanation],
        suspicious_accounts,
    )

    return report


@app.get("/export-pdf")
def export_pdf():
    df = load_data()

    score, explanation, suspicious_accounts = detect_risk(df)
    accounts_count = len(set(df["sender"]).union(set(df["receiver"])))
    network_similarity = calculate_network_similarity(df,suspicious_accounts)
    analysis_data = {
        "risk_score": score,
        "reasons": [x["factor"] for x in explanation],
        "banks": df["from_bank"].nunique(),
        "accounts": accounts_count,
        "transactions": len(df),
        "suspicious_accounts": suspicious_accounts,
        "network_similarity": network_similarity,

    }

    compliance_data = generate_compliance_report(
        df,
        score,
        [x["factor"] for x in explanation],
        suspicious_accounts,
    )

    pdf_bytes = build_investigation_report_pdf(
        analysis_data,
        compliance_data,
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=TRACE_Investigation_Report.pdf"
        },
    )