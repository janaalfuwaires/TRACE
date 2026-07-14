import sqlite3
import pandas as pd
import os
import glob

DB_NAME = "data/transactions.db"


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


    csv_files = glob.glob("data/*.csv")

    if not csv_files:
        raise FileNotFoundError("No CSV file found inside data folder.")

    latest_csv = max(csv_files, key=os.path.getmtime)

    print(f"Loading dataset: {latest_csv}")

    conn = sqlite3.connect(DB_NAME)

    # حذف البيانات القديمة
    conn.execute("DROP TABLE IF EXISTS transactions")

    conn.execute("""
    CREATE TABLE transactions (
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

    df = pd.read_csv(latest_csv, nrows=1000)

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
    import uuid
from datetime import datetime


def init_cases_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS investigation_cases (
        case_id TEXT PRIMARY KEY,
        account_id TEXT,
        status TEXT DEFAULT 'Open',
        priority TEXT,
        assigned_officer TEXT,
        notes TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()


def generate_case_id():
    date_part = datetime.now().strftime("%Y%m%d")
    unique_part = uuid.uuid4().hex[:6].upper()
    return f"CASE-{date_part}-{unique_part}"


def create_case(account_id, priority, assigned_officer, notes):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    case_id = generate_case_id()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    c.execute("""
        INSERT INTO investigation_cases
        (case_id, account_id, status, priority, assigned_officer, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (case_id, account_id, "Open", priority, assigned_officer, notes, created_at))

    conn.commit()
    conn.close()
    return case_id


def get_all_cases():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM investigation_cases ORDER BY created_at DESC", conn)
    conn.close()
    return df


def get_cases_by_account(account_id):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query(
        "SELECT * FROM investigation_cases WHERE account_id = ? ORDER BY created_at DESC",
        conn, params=(account_id,)
    )
    conn.close()
    return df


def update_case_status(case_id, new_status, new_notes=None):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    if new_notes is not None:
        c.execute(
            "UPDATE investigation_cases SET status = ?, notes = ? WHERE case_id = ?",
            (new_status, new_notes, case_id)
        )
    else:
        c.execute(
            "UPDATE investigation_cases SET status = ? WHERE case_id = ?",
            (new_status, case_id)
        )

    conn.commit()
    conn.close()