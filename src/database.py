import sqlite3
import pandas as pd
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "ews_cm_database.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ews_results (
            account_number TEXT PRIMARY KEY,
            ews_01 REAL,
            ews_02 REAL,
            ews_03 REAL,
            overall_risk_score REAL,
            risk_band TEXT,
            critical_override TEXT,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cm_results (
            borrower_id TEXT PRIMARY KEY,
            cm_01 REAL,
            cm_02 REAL,
            cm_03 REAL,
            overall_risk_score REAL,
            risk_band TEXT,
            critical_override TEXT,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

def save_dataframe_to_db(df, table_name):
    conn = sqlite3.connect(DB_PATH)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.close()