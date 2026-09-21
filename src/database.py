import sqlite3
import pandas as pd
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "ews_cm_database.db")

def init_db():
    """Initializes SQLite tables for Accounts, EWS Scores, and CM Scores."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create EWS Results Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ews_results (
            account_number TEXT PRIMARY KEY,
            ews_01 REAL,
            ews_02 REAL,
            ews_03 REAL,
            ews_01_score REAL,
            ews_02_score REAL,
            ews_03_score REAL,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create CM Results Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cm_results (
            borrower_id TEXT PRIMARY KEY,
            cm_01 REAL,
            cm_02 REAL,
            cm_03 REAL,
            cm_01_score REAL,
            cm_02_score REAL,
            cm_03_score REAL,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print(f"Database initialized at: {DB_PATH}")

def save_dataframe_to_db(df, table_name):
    """Saves output DataFrames into the target database table."""
    conn = sqlite3.connect(DB_PATH)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.close()
    print(f"Successfully saved {len(df)} records to table '{table_name}'.")

if __name__ == "__main__":
    init_db()