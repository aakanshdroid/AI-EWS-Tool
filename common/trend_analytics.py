import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUT_DIR = BASE_DIR / "output"

QUARTERLY_FILE = OUTPUT_DIR / "quarterly_financial_history_800.csv"

TREND_OUTPUT_FILE = OUTPUT_DIR / "quarterly_metric_deterioration.csv"


# ============================================================
# LOAD QUARTERLY DATA
# ============================================================

def load_quarterly_data():

    if not QUARTERLY_FILE.exists():

        print(
            f"[Trend Analytics] File not found: "
            f"{QUARTERLY_FILE}"
        )

        return pd.DataFrame()

    df = pd.read_csv(
        QUARTERLY_FILE
    )

    return df


# ============================================================
# HELPER — FIND COLUMN
# ============================================================

def find_column(df, possible_names):

    for name in possible_names:

        if name in df.columns:
            return name

    return None


# ============================================================
# PREPARE DATA
# ============================================================

def prepare_data(df):

    if df.empty:
        return df

    df = df.copy()

    borrower_col = find_column(
        df,
        [
            "Borrower_ID",
            "Account_Number",
            "BorrowerID"
        ]
    )

    quarter_col = find_column(
        df,
        [
            "Quarter",
            "quarter",
            "Financial_Quarter"
        ]
    )

    if not borrower_col or not quarter_col:

        print(
            "[Trend Analytics] "
            "Borrower_ID or Quarter column missing."
        )

        return pd.DataFrame()

    # Ensure quarter ordering
    quarter_order = {
        "Q1": 1,
        "Q2": 2,
        "Q3": 3,
        "Q4": 4
    }

    df["_Quarter_Order"] = (
        df[quarter_col]
        .astype(str)
        .str.upper()
        .map(quarter_order)
        .fillna(0)
    )

    df = df.sort_values(
        [
            borrower_col,
            "_Quarter_Order"
        ]
    )

    return df


# ============================================================
# METRIC DEFINITIONS
# ============================================================

METRICS = {

    "Sales_Cr": {
        "label": "Sales",
        "direction": "decrease"
    },

    "EBITDA_Margin_pct": {
        "label": "EBITDA Margin",
        "direction": "decrease"
    },

    "DSCR": {
        "label": "DSCR",
        "direction": "decrease"
    },

    "Debt_to_TNW": {
        "label": "Debt / TNW",
        "direction": "increase"
    },

    "Current_Ratio": {
        "label": "Current Ratio",
        "direction": "decrease"
    },

    "Debtor_Days": {
        "label": "Debtor Days",
        "direction": "increase"
    },

    "Inventory_Days": {
        "label": "Inventory Days",
        "direction": "increase"
    },

    "Creditor_Days": {
        "label": "Creditor Days",
        "direction": "increase"
    }
}


# ============================================================
# CALCULATE QUARTER-ON-QUARTER CHANGE
# ============================================================

def calculate_qoq_change(current, previous):

    if pd.isna(current) or pd.isna(previous):

        return np.nan

    if previous == 0:

        return np.nan

    return (
        (current - previous)
        / abs(previous)
    ) * 100


# ============================================================
# DETERMINE DETERIORATION
# ============================================================

def determine_deterioration(
    current,
    previous,
    direction,
    threshold=10
):

    if pd.isna(current) or pd.isna(previous):

        return False

    change = calculate_qoq_change(
        current,
        previous
    )

    if pd.isna(change):

        return False

    if direction == "decrease":

        return change <= -threshold

    if direction == "increase":

        return change >= threshold

    return False


# ============================================================
# GENERATE BORROWER TREND ANALYSIS
# ============================================================

def generate_trend_analysis():

    df = load_quarterly_data()

    if df.empty:

        return pd.DataFrame()

    df = prepare_data(df)

    if df.empty:

        return pd.DataFrame()

    borrower_col = find_column(
        df,
        [
            "Borrower_ID",
            "Account_Number",
            "BorrowerID"
        ]
    )

    borrower_name_col = find_column(
        df,
        [
            "Borrower_Name",
            "Company_Name"
        ]
    )

    quarter_col = find_column(
        df,
        [
            "Quarter",
            "quarter",
            "Financial_Quarter"
        ]
    )

    results = []

    # ========================================================
    # BORROWER LOOP
    # ========================================================

    for borrower_id, borrower_group in df.groupby(
        borrower_col
    ):

        borrower_group = borrower_group.sort_values(
            "_Quarter_Order"
        )

        borrower_name = (
            borrower_group[
                borrower_name_col
            ].iloc[0]
            if borrower_name_col
            else ""
        )

        rows = borrower_group.to_dict(
            orient="records"
        )

        # Compare consecutive quarters
        for i in range(1, len(rows)):

            previous = rows[i - 1]

            current = rows[i]

            previous_quarter = previous.get(
                quarter_col
            )

            current_quarter = current.get(
                quarter_col
            )

            for metric, config in METRICS.items():

                if metric not in borrower_group.columns:
                    continue

                current_value = pd.to_numeric(
                    current.get(metric),
                    errors="coerce"
                )

                previous_value = pd.to_numeric(
                    previous.get(metric),
                    errors="coerce"
                )

                if pd.isna(
                    current_value
                ) or pd.isna(
                    previous_value
                ):

                    continue

                qoq_change = calculate_qoq_change(
                    current_value,
                    previous_value
                )

                deteriorated = determine_deterioration(
                    current_value,
                    previous_value,
                    config["direction"]
                )

                if deteriorated:

                    results.append(
                        {
                            "Borrower_ID":
                                borrower_id,

                            "Borrower_Name":
                                borrower_name,

                            "Previous_Quarter":
                                previous_quarter,

                            "Current_Quarter":
                                current_quarter,

                            "Metric":
                                config["label"],

                            "Metric_Column":
                                metric,

                            "Previous_Value":
                                round(
                                    previous_value,
                                    2
                                ),

                            "Current_Value":
                                round(
                                    current_value,
                                    2
                                ),

                            "QoQ_Change_pct":
                                round(
                                    qoq_change,
                                    2
                                ),

                            "Direction":
                                config["direction"],

                            "Deterioration":
                                "Yes"
                        }
                    )

    result_df = pd.DataFrame(
        results
    )

    # ========================================================
    # SAVE RESULT
    # ========================================================

    if not result_df.empty:

        result_df.to_csv(
            TREND_OUTPUT_FILE,
            index=False
        )

        print(
            "[Trend Analytics] "
            f"Generated {len(result_df)} deterioration records."
        )

        print(
            f"[Trend Analytics] Saved to: "
            f"{TREND_OUTPUT_FILE}"
        )

    else:

        # Create empty file with expected columns
        result_df = pd.DataFrame(
            columns=[
                "Borrower_ID",
                "Borrower_Name",
                "Previous_Quarter",
                "Current_Quarter",
                "Metric",
                "Metric_Column",
                "Previous_Value",
                "Current_Value",
                "QoQ_Change_pct",
                "Direction",
                "Deterioration"
            ]
        )

        result_df.to_csv(
            TREND_OUTPUT_FILE,
            index=False
        )

        print(
            "[Trend Analytics] "
            "No deterioration detected."
        )

    return result_df


# ============================================================
# PEER GROUP BENCHMARKING
# ============================================================

def generate_peer_benchmark(borrower_id, borrower_master_df):
    """
    Generate peer-group benchmarking for the selected borrower.

    Peer group:
    - Same sector as the selected borrower
    - Excludes the selected borrower itself

    Benchmark metrics:
    - Annual Turnover
    - Total Debt
    - TNW
    - Debt / TNW
    - Current Ratio
    """

    if borrower_master_df is None or borrower_master_df.empty:
        return pd.DataFrame()

    df = borrower_master_df.copy()

    # --------------------------------------------------------
    # Clean column names
    # --------------------------------------------------------
    df.columns = [
        str(c).strip()
        for c in df.columns
    ]

    # --------------------------------------------------------
    # Check borrower
    # --------------------------------------------------------
    borrower_match = df[
        df["Borrower_ID"].astype(str) == str(borrower_id)
    ]

    if borrower_match.empty:
        return pd.DataFrame()

    borrower = borrower_match.iloc[0]

    # --------------------------------------------------------
    # Identify sector
    # --------------------------------------------------------
    borrower_sector = borrower.get("Sector", "")

    if pd.isna(borrower_sector):
        borrower_sector = ""

    borrower_sector = str(borrower_sector).strip()

    # --------------------------------------------------------
    # Create peer group
    # --------------------------------------------------------
    if borrower_sector:

        peers = df[
            df["Sector"]
            .astype(str)
            .str.strip()
            .str.lower()
            == borrower_sector.lower()
        ].copy()

    else:
        peers = df.copy()

    # Exclude selected borrower
    peers = peers[
        peers["Borrower_ID"].astype(str)
        != str(borrower_id)
    ].copy()

    # Need at least one peer
    if peers.empty:
        return pd.DataFrame()

    # --------------------------------------------------------
    # Helper for numeric columns
    # --------------------------------------------------------
    def numeric(series):
        return pd.to_numeric(
            series,
            errors="coerce"
        )

    # --------------------------------------------------------
    # Calculate Debt / TNW
    # --------------------------------------------------------
    if "Total_Debt_Cr" in df.columns and "TNW_Cr" in df.columns:

        df["Debt_to_TNW"] = (
            numeric(df["Total_Debt_Cr"])
            / numeric(df["TNW_Cr"]).replace(0, pd.NA)
        )

        peers["Debt_to_TNW"] = (
            numeric(peers["Total_Debt_Cr"])
            / numeric(peers["TNW_Cr"]).replace(0, pd.NA)
        )

    # --------------------------------------------------------
    # Calculate peer median
    # --------------------------------------------------------
    metric_map = {
        "Annual Turnover": "Annual_Turnover_Cr",
        "Total Debt": "Total_Debt_Cr",
        "TNW": "TNW_Cr",
        "Debt / TNW": "Debt_to_TNW",
        "Current Ratio": "Current_Ratio",
    }

    rows = []

    for metric_name, column_name in metric_map.items():

        if column_name not in df.columns:
            continue

        borrower_value = pd.to_numeric(
            pd.Series([borrower.get(column_name)]),
            errors="coerce"
        ).iloc[0]

        peer_values = pd.to_numeric(
            peers[column_name],
            errors="coerce"
        ).dropna()

        if peer_values.empty:
            continue

        peer_median = peer_values.median()
        peer_average = peer_values.mean()

        if pd.isna(borrower_value):
            variance_pct = None
        elif peer_median == 0:
            variance_pct = None
        else:
            variance_pct = (
                (borrower_value - peer_median)
                / abs(peer_median)
            ) * 100

        # ----------------------------------------------------
        # Position relative to peer median
        # ----------------------------------------------------
        if variance_pct is None:
            position = "Not Available"

        elif variance_pct > 5:
            position = "Above peer median"

        elif variance_pct < -5:
            position = "Below peer median"

        else:
            position = "Near peer median"

        rows.append({
            "Borrower_ID": borrower_id,
            "Borrower_Name": borrower.get(
                "Borrower_Name",
                ""
            ),
            "Sector": borrower_sector,
            "Peer_Count": len(peers),
            "Metric": metric_name,
            "Borrower_Value": borrower_value,
            "Peer_Median": peer_median,
            "Peer_Average": peer_average,
            "Variance_vs_Peer_Median_pct": variance_pct,
            "Position": position
        })

    return pd.DataFrame(rows)

# ============================================================
# RUN DIRECTLY
# ============================================================

if __name__ == "__main__":

    trend_df = generate_trend_analysis()

    print("\n========== TREND ANALYTICS SAMPLE ==========\n")

    if trend_df.empty:

        print(
            "No quarterly deterioration records."
        )

    else:

        print(
            trend_df.head(20)
            .to_string(index=False)
        )