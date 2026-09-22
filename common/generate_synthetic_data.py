import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime

# Initialize Faker with Indian locale for realistic corporate names & locations
fake = Faker('en_IN')
Faker.seed(42)
np.random.seed(42)
random.seed(42)

def generate_synthetic_borrowers(num_records=200):
    sectors = [
        'Electronics & Electricals', 'Hospitality & Services', 'Auto Components',
        'Textiles & Apparel', 'Pharmaceuticals', 'Chemicals', 'Steel & Metals',
        'Infrastructure & Construction', 'IT & Software Services', 'FMCG'
    ]
    
    constitutions = ['Private Limited', 'Public Limited', 'LLP', 'Partnership']
    listings = ['Unlisted', 'Listed']
    facility_types = ['WC + TL + NFB (LC/BG)', 'WC + TL', 'WC + NFB (LC/BG)', 'Working Capital (WC)', 'Term Loan (TL)']
    banking_arrangements = ['Sole Banking', 'Consortium', 'Multiple Banking']
    states = ['Andhra Pradesh', 'Kerala', 'Delhi NCR', 'Maharashtra', 'Tamil Nadu', 'Karnataka', 'Gujarat', 'Maharashtra']
    ratings = ['AAA', 'AA+', 'AA', 'AA-', 'A+', 'A', 'A-', 'BBB+', 'BBB', 'BBB-', 'BB+', 'BB', 'B', 'C', 'D']
    rms = ['Rahul Bose', 'Neha Rao', 'Sneha Shah', 'Priya Shah', 'Amit Sharma', 'Rohan Mehta', 'Kavita Singh']

    company_suffixes = ['Pvt Ltd', 'Ltd', 'LLP', 'Enterprises', 'Industries', 'Corporation', 'Logistics']

    data = []

    for i in range(1, num_records + 1):
        borrower_id = f"EWSB-{i:04d}"
        
        # Synthetic Company Name Generation
        company_base = fake.company().split()[0].replace(',', '')
        suffix = random.choice(company_suffixes)
        borrower_name = f"{company_base} {suffix}"
        
        constitution = random.choice(constitutions)
        listing = 'Listed' if constitution == 'Public Limited' and random.random() > 0.6 else 'Unlisted'
        sector = random.choice(sectors)
        state = random.choice(states)
        facility = random.choice(facility_types)
        banking = random.choice(banking_arrangements)
        
        # Sanctioned & Outstanding Limit (in ₹ Cr)
        sanctioned_limit = round(float(np.random.uniform(5.0, 500.0)), 1)
        # Outstanding is generally <= Sanctioned limit
        outstanding = round(float(sanctioned_limit * np.random.uniform(0.3, 0.98)), 1)
        
        rating = random.choice(ratings)
        rm = random.choice(rms)
        assessment_date = "2026-08-31"

        data.append({
            "Borrower ID": borrower_id,
            "Borrower Name": borrower_name,
            "Constitution": constitution,
            "Listing": listing,
            "Sector": sector,
            "State": state,
            "Facility Type": facility,
            "Banking Arrangement": banking,
            "Sanctioned Limit (₹ Cr)": sanctioned_limit,
            "Outstanding (₹ Cr)": outstanding,
            "Internal Rating": rating,
            "Relationship Manager": rm,
            "Assessment Date": assessment_date
        })

    df = pd.DataFrame(data)
    return df

if __name__ == "__main__":
    num_borrowers = 200
    df_synthetic = generate_synthetic_borrowers(num_borrowers)
    
    # Save to Excel
    output_filename = "Synthetic_Borrower_Data_Generated.xlsx"
    df_synthetic.to_excel(output_filename, index=False, sheet_name="Borrower Master")
    print(f"✅ Successfully generated {num_borrowers} synthetic corporate borrowers!")
    print(f"📁 Saved to: {output_filename}")
    print("\nPreview:")
    print(df_synthetic.head())

    # ============================================================
# QUARTERLY FINANCIAL HISTORY GENERATOR
# ============================================================

from pathlib import Path
import pandas as pd
import numpy as np


def generate_quarterly_history(
    borrower_file="output/borrower_master_200.csv",
    ews_raw_file="output/ews_raw_inputs_200.csv",
    output_file="output/quarterly_financial_history_800.csv"
):
    """
    Generate 4-quarter synthetic financial history
    for the existing borrower population.

    200 borrowers x 4 quarters = 800 records.

    The current borrower data is treated as the latest
    quarter and earlier quarters are derived backwards
    using the available EWS movement variables.
    """

    borrower_df = pd.read_csv(borrower_file)
    ews_df = pd.read_csv(ews_raw_file)

    # --------------------------------------------------------
    # Merge borrower master and EWS raw data
    # --------------------------------------------------------

    df = borrower_df.merge(
        ews_df,
        on="Borrower_ID",
        how="left",
        suffixes=("", "_EWS")
    )

    # --------------------------------------------------------
    # Helper for numeric conversion
    # --------------------------------------------------------

    def num(column, default=0.0):

        if column not in df.columns:
            return pd.Series(
                default,
                index=df.index,
                dtype=float
            )

        return pd.to_numeric(
            df[column],
            errors="coerce"
        ).fillna(default)

    # --------------------------------------------------------
    # Current values
    # --------------------------------------------------------

    sales = num(
        "Annual_Turnover_Cr",
        100
    )

    debt = num(
        "Total_Debt_Cr",
        20
    )

    tnw = num(
        "TNW_Cr",
        10
    )

    current_ratio = num(
        "Current_Ratio",
        1.5
    )

    dscr = num(
        "DSCR",
        1.5
    )

    debt_to_tnw = num(
        "Debt_to_TNW",
        2.0
    )

    # --------------------------------------------------------
    # Change indicators from EWS raw data
    # --------------------------------------------------------

    sales_change = num(
        "sales_change_pct",
        0
    )

    ebitda_change = num(
        "ebitda_margin_change_pct",
        0
    )

    debtor_change = num(
        "debtor_days_change_pct",
        0
    )

    inventory_change = num(
        "inventory_days_change_pct",
        0
    )

    creditor_change = num(
        "creditor_days_change_pct",
        0
    )

    dscr_change = num(
        "dscr_change_pct",
        0
    )

    # --------------------------------------------------------
    # Current EBITDA margin
    # --------------------------------------------------------

    if "EBITDA_Margin_pct" in df.columns:

        ebitda_margin = num(
            "EBITDA_Margin_pct",
            12
        )

    elif "ebitda_margin_pct" in df.columns:

        ebitda_margin = num(
            "ebitda_margin_pct",
            12
        )

    else:

        # Synthetic starting value
        ebitda_margin = pd.Series(
            12.0,
            index=df.index
        )

    # --------------------------------------------------------
    # Current working-capital days
    # --------------------------------------------------------

    if "debtor_days" in df.columns:

        debtor_days = num(
            "debtor_days",
            50
        )

    elif "Debtor_Days" in df.columns:

        debtor_days = num(
            "Debtor_Days",
            50
        )

    else:

        debtor_days = pd.Series(
            50.0,
            index=df.index
        )

    if "inventory_days" in df.columns:

        inventory_days = num(
            "inventory_days",
            60
        )

    elif "Inventory_Days" in df.columns:

        inventory_days = num(
            "Inventory_Days",
            60
        )

    else:

        inventory_days = pd.Series(
            60.0,
            index=df.index
        )

    if "creditor_days" in df.columns:

        creditor_days = num(
            "creditor_days",
            45
        )

    elif "Creditor_Days" in df.columns:

        creditor_days = num(
            "Creditor_Days",
            45
        )

    else:

        creditor_days = pd.Series(
            45.0,
            index=df.index
        )

    # --------------------------------------------------------
    # Generate four quarters
    # --------------------------------------------------------

    records = []

    quarters = [
        ("Q1", 0.75),
        ("Q2", 0.50),
        ("Q3", 0.25),
        ("Q4", 0.00)
    ]

    for quarter, factor in quarters:

        q_df = pd.DataFrame({

            "Borrower_ID":
                df["Borrower_ID"].astype(str),

            "Borrower_Name":
                df["Borrower_Name"]
                if "Borrower_Name" in df.columns
                else "",

            "Sector":
                df["Sector"]
                if "Sector" in df.columns
                else "",

            "Risk_Profile":
                df["Risk_Profile"]
                if "Risk_Profile" in df.columns
                else "",

            "Quarter":
                quarter,

            # ------------------------------------------------
            # Financial metrics
            # ------------------------------------------------

            "Sales_Cr":
                sales * (
                    1 - (sales_change / 100) * factor
                ),

            "EBITDA_Margin_pct":
                ebitda_margin - (
                    ebitda_change * factor
                ),

            "DSCR":
                dscr - (
                    dscr_change / 100
                    * dscr
                    * factor
                ),

            "Debt_to_TNW":
                debt_to_tnw * (
                    1 + 0.05 * factor
                ),

            "Current_Ratio":
                current_ratio * (
                    1 + 0.03 * factor
                ),

            "Debtor_Days":
                debtor_days * (
                    1 - (debtor_change / 100) * factor
                ),

            "Inventory_Days":
                inventory_days * (
                    1 - (inventory_change / 100) * factor
                ),

            "Creditor_Days":
                creditor_days * (
                    1 - (creditor_change / 100) * factor
                ),

            "Total_Debt_Cr":
                debt * (
                    1 + 0.04 * factor
                ),

            "TNW_Cr":
                tnw * (
                    1 - 0.02 * factor
                )
        })

        records.append(q_df)

    # --------------------------------------------------------
    # Combine all quarters
    # --------------------------------------------------------

    quarterly_df = pd.concat(
        records,
        ignore_index=True
    )

    # --------------------------------------------------------
    # Clean numeric values
    # --------------------------------------------------------

    numeric_columns = [
        "Sales_Cr",
        "EBITDA_Margin_pct",
        "DSCR",
        "Debt_to_TNW",
        "Current_Ratio",
        "Debtor_Days",
        "Inventory_Days",
        "Creditor_Days",
        "Total_Debt_Cr",
        "TNW_Cr"
    ]

    for column in numeric_columns:

        quarterly_df[column] = pd.to_numeric(
            quarterly_df[column],
            errors="coerce"
        ).round(2)

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    Path(output_file).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    quarterly_df.to_csv(
        output_file,
        index=False
    )

    print(
        f"Quarterly history generated: "
        f"{len(quarterly_df)} records"
    )

    print(
        f"Saved to: {output_file}"
    )

    print(
        quarterly_df.head(12).to_string(
            index=False
        )
    )

    return quarterly_df


# ============================================================
# RUN QUARTERLY HISTORY GENERATION
# ============================================================

if __name__ == "__main__":

    generate_quarterly_history()