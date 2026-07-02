from fastapi import FastAPI
import sqlite3
import pandas as pd
from backend.db import init_db, load_csv_to_db
from backend.detector import detect_risk

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

@app.get("/analysis")
def analysis():
    df = load_data()

    score, reasons, suspicious_accounts = detect_risk(df)

    accounts = len(set(df["sender"]).union(set(df["receiver"])))

    return {
        "risk_score": score,
        "reasons": reasons,
        "banks": df["from_bank"].nunique(),
        "accounts": accounts,
        "transactions": len(df),
        "suspicious_accounts": suspicious_accounts
    }