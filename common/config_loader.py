import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, "docs")

EWS_FILE = os.path.join(DOCS_DIR, "EWS Functional Logic 1.14.xlsx")
CM_FILE = os.path.join(DOCS_DIR, "Credit_Monitoring_Functional_Logic_Sheet 1.3.xlsx")

def read_sheet_smart(file_path, sheet_name):
    """
    Scans the first 6 rows of an Excel sheet to locate the exact row 
    containing the 'UID' column header.
    """
    for header_idx in range(6):
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_idx)
            cleaned_cols = [str(c).strip() for c in df.columns]
            
            # Check for exact or substring 'UID' header
            uid_col = next((c for c in cleaned_cols if "UID" in c.upper()), None)
            
            if uid_col:
                df.columns = cleaned_cols
                return df.dropna(subset=[uid_col]).rename(columns={uid_col: "UID"})
        except Exception:
            continue

    print(f"Warning: 'UID' column not found in {sheet_name} of {os.path.basename(file_path)}")
    return pd.DataFrame()

def load_indicator_master():
    """Loads indicator definitions from both EWS and CM sheets."""
    ews_master = read_sheet_smart(EWS_FILE, "Indicator Master")
    cm_master = read_sheet_smart(CM_FILE, "Indicator Master")
    return pd.concat([ews_master, cm_master], ignore_index=True)

def load_scoring_rules():
    """Loads threshold scoring rules from both EWS and CM sheets."""
    ews_rules = read_sheet_smart(EWS_FILE, "Scoring Engine (Rules)")
    cm_rules = read_sheet_smart(CM_FILE, "Scoring Engine (Rules)")
    return pd.concat([ews_rules, cm_rules], ignore_index=True)

if __name__ == "__main__":
    master_df = load_indicator_master()
    rules_df = load_scoring_rules()
    
    print("=" * 50)
    print(f"Successfully loaded {len(master_df)} total indicators.")
    print(f"Successfully loaded {len(rules_df)} threshold rules.")
    print("=" * 50)