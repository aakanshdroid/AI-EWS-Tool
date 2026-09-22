import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_borrower_data():
    """Reads financial and transactional metrics from the Synthetic Borrower Excel sheet."""
    file_path = os.path.join(BASE_DIR, "Synthetic_Borrower_Data_Generated.xlsx")
    if not os.path.exists(file_path):
        file_path = os.path.join(BASE_DIR, "Synthetic borrower data.xlsx")
        
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file missing: {file_path}")

    # Load primary sheet
    df = pd.read_excel(file_path)
    
    # Standardize column names (strip spaces and replace with underscores)
    df.columns = df.columns.str.strip().str.replace(" ", "_")

    # Automatically map any ID column variant to 'Account_Number' and 'Borrower_ID'
    id_col = None
    for col in df.columns:
        if col.lower() in ["borrower_id", "account_number", "account_no", "account_id", "borrowerid", "accountnumber"]:
            id_col = col
            break

    if id_col:
        df["Account_Number"] = df[id_col].astype(str)
        df["Borrower_ID"] = df[id_col].astype(str)
    else:
        # Fallback: use first column as the primary identifier
        df["Account_Number"] = df.iloc[:, 0].astype(str)
        df["Borrower_ID"] = df.iloc[:, 0].astype(str)

    return df


def load_ews_logic():
    """Reads EWS calculation formulas, logic rules, and thresholds."""
    file_path = os.path.join(BASE_DIR, "EWS Functional Logic V2.xlsx")
    if os.path.exists(file_path):
        return pd.read_excel(file_path)
    return pd.DataFrame()


def load_cm_logic():
    """Reads Credit Monitoring calculation formulas and indicator thresholds."""
    file_path = os.path.join(BASE_DIR, "Credit Monitoring Functional Logic Sheet 1.3.xlsx")
    if os.path.exists(file_path):
        return pd.read_excel(file_path)
    return pd.DataFrame()