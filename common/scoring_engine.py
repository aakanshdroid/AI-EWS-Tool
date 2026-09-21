import pandas as pd
import numpy as np
from common.config_loader import load_scoring_rules, load_indicator_master

def evaluate_threshold(value, lower_bound, upper_bound, operator_type="between"):
    """Evaluates whether a value falls within defined threshold boundaries."""
    if pd.isna(value):
        return False
        
    try:
        val = float(value)
        if pd.notna(lower_bound) and pd.notna(upper_bound):
            return lower_bound <= val <= upper_bound
        elif pd.notna(lower_bound):
            return val >= lower_bound
        elif pd.notna(upper_bound):
            return val <= upper_bound
    except (ValueError, TypeError):
        pass
        
    return False

def calculate_scores(input_df, rules_df):
    """
    Maps input data against threshold rules to assign risk scores (1-5).
    """
    scored_df = input_df.copy()
    
    for col in input_df.columns:
        if col in rules_df["UID"].values:
            indicator_rules = rules_df[rules_df["UID"] == col]
            
            def assign_score(val):
                for _, rule in indicator_rules.iterrows():
                    lower = rule.get("Lower Bound")
                    upper = rule.get("Upper Bound")
                    score = rule.get("Risk Score", rule.get("Score", np.nan))
                    
                    if evaluate_threshold(val, lower, upper):
                        return score
                return np.nan
                
            scored_df[f"{col}_Score"] = scored_df[col].apply(assign_score)
            
    return scored_df

if __name__ == "__main__":
    rules = load_scoring_rules()
    master = load_indicator_master()
    print("=" * 50)
    print(f"Scoring Engine initialized with {len(rules)} active rules.")
    print(f"Mapped against {len(master)} indicator definitions.")
    print("=" * 50)