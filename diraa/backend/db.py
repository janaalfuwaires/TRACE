import sqlite3
import pandas as pd
import os

DB_NAME = "data/transactions.db"
CSV_FILE = "data/HI-Small_Trans.csv"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        receiver TEXT,
        amount REAL,
        timestamp TEXT,
        from_bank TEXT,
        to_bank TEXT,
        payment_format TEXT,
        is_laundering INTEGER
    )
    """)

    conn.commit()
    conn.close()


def load_csv_to_db():
    conn = sqlite3.connect(DB_NAME)

    # إذا الجدول فيه بيانات، لا نعيد الإدخال
    count = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    if count > 0:
        conn.close()
        return

    # قراءة أول 1000 عملية فقط (سريع للهاكاثون)
    df = pd.read_csv(CSV_FILE, nrows=1000)

    # إعادة تسمية الأعمدة المتكررة
    cols = list(df.columns)
    cols[2] = "sender"
    cols[4] = "receiver"
    df.columns = cols

    records = []

    for _, row in df.iterrows():
        records.append((
            str(row["sender"]),
            str(row["receiver"]),
            float(row["Amount Received"]),
            str(row["Timestamp"]),
            str(row["From Bank"]),
            str(row["To Bank"]),
            str(row["Payment Format"]),
            int(row["Is Laundering"])
        ))

    conn.executemany("""
    INSERT INTO transactions
    (sender, receiver, amount, timestamp,
     from_bank, to_bank, payment_format, is_laundering)
    VALUES (?,?,?,?,?,?,?,?)
    """, records)

    conn.commit()
    conn.close()