import os
import pandas as pd
from common.config_loader import load_scoring_rules, load_indicator_master
from common.scoring_engine import calculate_scores
from ews.ews_calculator import calculate_ews_indicators
from credit_monitoring.cm_calculator import calculate_cm_indicators
from src.database import init_db, save_dataframe_to_db

def run_pipeline():
    print("=" * 60)
    print("STARTING EWS & CREDIT MONITORING PIPELINE")
    print("=" * 60)

    # 1. Load Rule Configurations
    rules_df = load_scoring_rules()
    master_df = load_indicator_master()
    print(f"[1/5] Configs Loaded: {len(master_df)} indicators, {len(rules_df)} threshold rules.")

    # 2. Mock Ingestion Data
    accounts_df = pd.DataFrame({
        "Account_Number": ["ACC1001", "ACC1002"],
        "Avg_Balance_Current_M": [45000, 12000],
        "Avg_Balance_Prev_M": [50000, 30000],
        "Outstanding_Amount": [85000, 95000],
        "Sanctioned_Limit": [100000, 100000]
    })
    
    transactions_df = pd.DataFrame({
        "Account_Number": ["ACC1001", "ACC1001", "ACC1002"],
        "Debit_Amount": [5000, 2000, 15000],
        "Credit_Amount": [4000, 3000, 2000]
    })

    borrowers_df = pd.DataFrame({
        "Borrower_ID": ["CUST_001", "CUST_002"],
        "Max_DPD_3M": [15, 60],
        "Total_Debt": [5000000, 12000000],
        "TNW": [2000000, 1500000],
        "Current_Rating_Score": [6, 4],
        "Previous_Rating_Score": [7, 7]
    })

    # 3. Calculate Raw Indicators
    ews_raw = calculate_ews_indicators(accounts_df, transactions_df)
    cm_raw = calculate_cm_indicators(borrowers_df)
    print("[2/5] Raw EWS and CM indicators calculated successfully.")

    # 4. Map Risk Scores
    ews_scored = calculate_scores(ews_raw, rules_df)
    cm_scored = calculate_scores(cm_raw, rules_df)
    print("[3/5] Threshold scoring completed.")

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