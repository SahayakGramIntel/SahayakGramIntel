"""SQLite persistence for GramIntel assessments."""

import os
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "gramintel.db")


def get_connection():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            location TEXT,
            business_idea TEXT,
            category TEXT,
            investment REAL,
            monthly_sales REAL,
            monthly_expenses REAL,
            loan_amount REAL,
            interest_rate REAL,
            loan_tenure INTEGER,
            revenue REAL,
            profit REAL,
            profit_margin REAL,
            emi REAL,
            roi REAL,
            break_even REAL,
            feasibility_score INTEGER,
            feasibility_reasons TEXT,
            swot_data TEXT,
            recommendations TEXT,
            created_at TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assessment_id INTEGER,
            sender TEXT,
            message TEXT,
            timestamp TEXT
        )
        """
    )
    _ensure_columns(conn)
    conn.commit()
    conn.close()


def _ensure_columns(conn):
    report_cols = {row[1] for row in conn.execute("PRAGMA table_info(reports)").fetchall()}
    extras = {
        "roi": "REAL",
        "break_even": "REAL",
        "feasibility_reasons": "TEXT",
        "swot_data": "TEXT",
        "recommendations": "TEXT",
    }
    for name, col_type in extras.items():
        if name not in report_cols:
            conn.execute(f"ALTER TABLE reports ADD COLUMN {name} {col_type}")

    chat_cols = {row[1] for row in conn.execute("PRAGMA table_info(chat_messages)").fetchall()}
    if "assessment_id" not in chat_cols and "report_id" in chat_cols:
        pass
    if "sender" not in chat_cols and "role" in chat_cols:
        try:
            conn.execute("ALTER TABLE chat_messages ADD COLUMN sender TEXT")
            conn.execute("UPDATE chat_messages SET sender = role WHERE sender IS NULL")
        except sqlite3.OperationalError:
            pass
    if "timestamp" not in chat_cols and "created_at" in chat_cols:
        try:
            conn.execute("ALTER TABLE chat_messages ADD COLUMN timestamp TEXT")
            conn.execute("UPDATE chat_messages SET timestamp = created_at WHERE timestamp IS NULL")
        except sqlite3.OperationalError:
            pass
    if "assessment_id" not in chat_cols:
        try:
            conn.execute("ALTER TABLE chat_messages ADD COLUMN assessment_id INTEGER")
            if "report_id" in chat_cols:
                conn.execute("UPDATE chat_messages SET assessment_id = report_id WHERE assessment_id IS NULL")
        except sqlite3.OperationalError:
            pass


def save_report(payload):
    conn = get_connection()
    cursor = conn.execute(
        """
        INSERT INTO reports (
            name, location, business_idea, category, investment,
            monthly_sales, monthly_expenses, loan_amount, interest_rate,
            loan_tenure, revenue, profit, profit_margin, emi, roi, break_even,
            feasibility_score, feasibility_reasons, swot_data, recommendations,
            created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            payload.get("name"),
            payload.get("location"),
            payload.get("business_idea"),
            payload.get("category"),
            payload.get("investment"),
            payload.get("monthly_sales"),
            payload.get("monthly_expenses"),
            payload.get("loan_amount"),
            payload.get("interest_rate"),
            payload.get("loan_tenure"),
            payload.get("revenue"),
            payload.get("profit"),
            payload.get("profit_margin"),
            payload.get("emi"),
            payload.get("roi"),
            payload.get("break_even"),
            payload.get("feasibility_score"),
            payload.get("feasibility_reasons"),
            payload.get("swot_data"),
            payload.get("recommendations"),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )
    report_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return report_id


def get_report(report_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def save_chat_message(assessment_id, sender, message):
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO chat_messages (assessment_id, sender, message, timestamp)
        VALUES (?, ?, ?, ?)
        """,
        (
            assessment_id,
            sender,
            message,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )
    conn.commit()
    conn.close()


def list_chat_messages(assessment_id, limit=80):
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT id, assessment_id, sender, message, timestamp
        FROM chat_messages
        WHERE assessment_id = ?
        ORDER BY id ASC
        LIMIT ?
        """,
        (assessment_id, limit),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def list_reports():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM reports ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]
