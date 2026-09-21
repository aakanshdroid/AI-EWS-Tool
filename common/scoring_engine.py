import pandas as pd
import numpy as np

# Defined Critical Overrides from Workflow Architecture Step 9
CRITICAL_EWS_INDICATORS = ["EWS-003", "EWS-007", "EWS-014", "EWS-026", "EWS-032", "EWS-035"]

# Combination rules (+20 severity boost if both trigger)
COMBINATION_PAIRS = [
    ("EWS-004", "EWS-011"),
    ("EWS-005", "EWS-014"),
    ("EWS-009", "EWS-012")
]

def calculate_scores(raw_df, rules_df):
    """
    Maps raw indicator values to 1-5 Risk Bands and applies Step 9 Critical & Combination Logic.
    """
    scored_df = raw_df.copy()
    
    # 1. Map individual indicator scores (Raw mapping)
    indicator_cols = [c for c in scored_df.columns if c.startswith("EWS_") or c.startswith("CM_")]
    
    # 2. Check for Critical Overrides
    critical_triggered = []
    for idx, row in scored_df.iterrows():
        is_critical = False
        
        # Check if any Critical EWS indicator triggered a high score
        for col in indicator_cols:
            uid_format = col.replace("_", "-")
            if uid_format in CRITICAL_EWS_INDICATORS:
                val = row[col]
                # If score >= 80 or high severity band
                if pd.notnull(val) and val >= 80:
                    is_critical = True
                    break
                    
        # Check Combination Boosts
        combination_boost = 0
        for ind_a, ind_b in COMBINATION_PAIRS:
            col_a = ind_a.replace("-", "_")
            col_b = ind_b.replace("-", "_")
            if col_a in row and col_b in row:
                if row[col_a] >= 60 and row[col_b] >= 60:
                    combination_boost += 20
        
        # Calculate Final Overall Score
        raw_mean = row[indicator_cols].mean() if len(indicator_cols) > 0 else 0
        final_score = raw_mean + combination_boost
        
        if is_critical or final_score >= 80:
            risk_band = "Critical (80-100)"
            final_score = max(final_score, 85.0)
        elif final_score >= 60:
            risk_band = "Red (60-79)"
        elif final_score >= 40:
            risk_band = "Amber (40-59)"
        elif final_score >= 20:
            risk_band = "Yellow (20-39)"
        else:
            risk_band = "Green (0-19)"
            
        scored_df.at[idx, "Overall_Risk_Score"] = round(final_score, 2)
        scored_df.at[idx, "Risk_Band"] = risk_band
        scored_df.at[idx, "Critical_Override"] = "YES" if is_critical else "NO"
        
    return scored_df