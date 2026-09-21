import os
import pandas as pd
from common.config_loader import load_scoring_rules, load_indicator_master
from common.scoring_engine import calculate_scores
from ews.ews_calculator import calculate_ews_indicators
from credit_monitoring.cm_calculator import calculate_cm_indicators
from src.database import init_db, save_dataframe_to_db
from common.notifier import send_critical_alert_email  # <--- Added Step 2 Import

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_excel_file(filename, default_df):
    """Utility to safely load Excel files from project root or fallback to mock data."""
    file_path = os.path.join(BASE_DIR, filename)
    if os.path.exists(file_path):
        print(f"--> Ingesting real data from: {filename}")
        try:
            return pd.read_excel(file_path)
        except Exception as e:
            print(f"Warning: Could not parse {filename} ({e}). Using fallback data.")
            return default_df
    else:
        print(f"Warning: File '{filename}' not found in project root. Using default data.")
        return default_df

def check_and_send_alerts(df):
    """Scans calculated results for critical risk scores or overrides and sends alerts."""
    if df.empty:
        return
        
    for _, row in df.iterrows():
        account_no = row.get("Account_Number", row.get("Borrower_ID", "N/A"))
        borrower_name = row.get("Borrower_Name", "Unknown Borrower")
        risk_score = row.get("Overall_Risk_Score", row.get("Total_Risk_Score", 0))
        risk_band = row.get("Risk_Band", "N/A")
        override = str(row.get("Critical_Override", "NO"))

        # Trigger condition: Score >= 80 OR Critical Override is YES
        if risk_score >= 80 or override.upper() == "YES":
            send_critical_alert_email(
                account_number=account_no,
                borrower_name=borrower_name,
                risk_score=risk_score,
                risk_band=risk_band,
                override_flag=override
            )

def run_pipeline():
    print("=" * 60)
    print("STARTING EWS & CREDIT MONITORING PIPELINE")
    print("=" * 60)

    # 1. Load Rule Configurations
    rules_df = load_scoring_rules()
    master_df = load_indicator_master()
    print(f"[1/5] Configs Loaded: {len(master_df)} indicators, {len(rules_df)} threshold rules.")

    # 2. Ingest Excel Spreadsheets or Fallback
    fallback_accounts = pd.DataFrame({
        "Account_Number": ["ACC1001", "ACC1002"],
        "Avg_Balance_Current_M": [45000, 12000],
        "Avg_Balance_Prev_M": [50000, 30000],
        "Outstanding_Amount": [85000, 95000],
        "Sanctioned_Limit": [100000, 100000]
    })
    
    fallback_transactions = pd.DataFrame({
        "Account_Number": ["ACC1001", "ACC1001", "ACC1002"],
        "Debit_Amount": [5000, 2000, 15000],
        "Credit_Amount": [4000, 3000, 2000]
    })

    fallback_borrowers = pd.DataFrame({
        "Borrower_ID": ["CUST_001", "CUST_002"],
        "Max_DPD_3M": [15, 60],
        "Total_Debt": [5000000, 12000000],
        "TNW": [2000000, 1500000],
        "Current_Rating_Score": [6, 4],
        "Previous_Rating_Score": [7, 7]
    })

    # Read from root Excel files
    accounts_df = load_excel_file("Synthetic borrower data.xlsx", fallback_accounts)
    transactions_df = fallback_transactions  # Extracted from accounts if multi-sheet
    borrowers_df = load_excel_file("Credit Monitoring Functional Logic Sheet 1.3.xlsx", fallback_borrowers)

    # 3. Calculate Raw Indicators
    ews_raw = calculate_ews_indicators(accounts_df, transactions_df)
    cm_raw = calculate_cm_indicators(borrowers_df)
    print("[2/5] Raw EWS and CM indicators calculated successfully.")

    # 4. Map Risk Scores
    ews_scored = calculate_scores(ews_raw, rules_df)
    cm_scored = calculate_scores(cm_raw, rules_df)
    print("[3/5] Threshold scoring completed.")

    # --- STEP 2 INTEGRATION: Trigger Email Alerts for Critical Accounts ---
    print("[3.5/5] Scanning for critical alert triggers...")
    check_and_send_alerts(ews_scored)
    check_and_send_alerts(cm_scored)

    # 5. Initialize Database & Persist Results
    init_db()
    save_dataframe_to_db(ews_scored, "ews_results")
    save_dataframe_to_db(cm_scored, "cm_results")
    print("[4/5] Results successfully persisted to database.")

    # 6. Display Pipeline Results
    print("\n" + "=" * 25 + " EWS RESULTS " + "=" * 25)
    print(ews_scored)

    print("\n" + "=" * 22 + " CM RESULTS " + "=" * 22)
    print(cm_scored)
    print("=" * 60)

if __name__ == "__main__":
    run_pipeline()