import pandas as pd
import numpy as np

def calculate_ews_indicators(account_df, transactions_df):
    """
    Computes raw Early Warning Signal (EWS) indicator values 
    for each account based on transactional and account-level data.
    """
    results = pd.DataFrame()
    results["Account_Number"] = account_df["Account_Number"]

    # EWS_01: Average Balance Trend / Monthly Average Balance Decay
    if "Avg_Balance_Current_M" in account_df.columns and "Avg_Balance_Prev_M" in account_df.columns:
        results["EWS_01"] = (
            (account_df["Avg_Balance_Current_M"] - account_df["Avg_Balance_Prev_M"]) 
            / account_df["Avg_Balance_Prev_M"].replace(0, np.nan)
        ) * 100

    # EWS_02: Utilization of Credit Limits
    if "Outstanding_Amount" in account_df.columns and "Sanctioned_Limit" in account_df.columns:
        results["EWS_02"] = (
            account_df["Outstanding_Amount"] 
            / account_df["Sanctioned_Limit"].replace(0, np.nan)
        ) * 100

    # EWS_03: Total Debit-to-Credit Ratio from Transactions
    if not transactions_df.empty and "Account_Number" in transactions_df.columns:
        tx_summary = transactions_df.groupby("Account_Number").agg(
            total_debit=("Debit_Amount", "sum"),
            total_credit=("Credit_Amount", "sum")
        ).reset_index()
        
        tx_summary["EWS_03"] = (
            tx_summary["total_debit"] 
            / tx_summary["total_credit"].replace(0, np.nan)
        )
        
        results = results.merge(tx_summary[["Account_Number", "EWS_03"]], on="Account_Number", how="left")

    return results

if __name__ == "__main__":
    # Test execution with dummy account and transaction records
    sample_accounts = pd.DataFrame({
        "Account_Number": ["ACC1001", "ACC1002"],
        "Avg_Balance_Current_M": [45000, 12000],
        "Avg_Balance_Prev_M": [50000, 30000],
        "Outstanding_Amount": [85000, 95000],
        "Sanctioned_Limit": [100000, 100000]
    })
    
    sample_txs = pd.DataFrame({
        "Account_Number": ["ACC1001", "ACC1001", "ACC1002"],
        "Debit_Amount": [5000, 2000, 15000],
        "Credit_Amount": [4000, 3000, 2000]
    })

    ews_output = calculate_ews_indicators(sample_accounts, sample_txs)
    print("=" * 50)
    print("EWS Calculation Engine Initialized Successfully.")
    print(ews_output.head())
    print("=" * 50)