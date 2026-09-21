import pandas as pd
import numpy as np

def calculate_cm_indicators(borrower_df):
    """
    Computes borrower-level Credit Monitoring (CM) risk indicators
    such as DPD trends, rating downgrades, and financial ratios.
    """
    results = pd.DataFrame()
    results["Borrower_ID"] = borrower_df["Borrower_ID"]

    # CM_01: Days Past Due (DPD) Threshold
    if "Max_DPD_3M" in borrower_df.columns:
        results["CM_01"] = borrower_df["Max_DPD_3M"]

    # CM_02: Financial Leverage Ratio (Total Debt / Tangible Net Worth)
    if "Total_Debt" in borrower_df.columns and "TNW" in borrower_df.columns:
        results["CM_02"] = (
            borrower_df["Total_Debt"] 
            / borrower_df["TNW"].replace(0, np.nan)
        )

    # CM_03: External Credit Rating Notch Change (Negative = Downgrade)
    if "Current_Rating_Score" in borrower_df.columns and "Previous_Rating_Score" in borrower_df.columns:
        results["CM_03"] = borrower_df["Current_Rating_Score"] - borrower_df["Previous_Rating_Score"]

    return results

if __name__ == "__main__":
    # Test execution with sample borrower records
    sample_borrowers = pd.DataFrame({
        "Borrower_ID": ["CUST_001", "CUST_002"],
        "Max_DPD_3M": [15, 60],
        "Total_Debt": [5000000, 12000000],
        "TNW": [2000000, 1500000],
        "Current_Rating_Score": [6, 4],
        "Previous_Rating_Score": [7, 7]
    })

    cm_output = calculate_cm_indicators(sample_borrowers)
    print("=" * 50)
    print("Credit Monitoring Engine Initialized Successfully.")
    print(cm_output.head())
    print("=" * 50)