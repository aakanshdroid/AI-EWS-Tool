import pandas as pd
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

EWS_FILE = (
    BASE_DIR
    / "docs"
    / "EWS Functional Logic V2.xlsx"
)

CM_FILE = (
    BASE_DIR
    / "docs"
    / "Credit Monitoring Functional Logic Sheet 1.3.xlsx"
)


# ============================================================
# STANDARD OUTPUT COLUMNS
# ============================================================

PLAYBOOK_COLUMNS = [
    "Rule_ID",
    "Parameter",
    "Score",
    "What_it_signals",
    "Remedial_Action",
    "Primary_Owner",
]


# ============================================================
# HELPER — FIND COLUMN
# ============================================================

def find_column(df, possible_names):

    if df.empty:
        return None

    # Exact match
    for name in possible_names:
        if name in df.columns:
            return name

    # Case-insensitive + trimmed match
    normalized = {
        str(col).strip().lower(): col
        for col in df.columns
    }

    for name in possible_names:

        key = str(name).strip().lower()

        if key in normalized:
            return normalized[key]

    return None


# ============================================================
# HELPER — NORMALISE COLUMN NAME
# ============================================================

def clean_text(value):

    if pd.isna(value):
        return ""

    return str(value).strip()


# ============================================================
# HELPER — NORMALISE RULE ID
# ============================================================

def normalise_rule_id(value):

    if pd.isna(value):
        return ""

    return (
        str(value)
        .strip()
        .upper()
        .replace(" ", "")
    )


# ============================================================
# HELPER — NORMALISE SCORE
# ============================================================

def normalise_score(value):

    if pd.isna(value):
        return None

    try:

        numeric_value = pd.to_numeric(
            value,
            errors="coerce"
        )

        if pd.isna(numeric_value):
            return None

        return round(float(numeric_value), 6)

    except Exception:

        return None


# ============================================================
# STANDARDISE FUNCTIONAL LOGIC
# ============================================================

def standardise_playbook_columns(df):

    if df.empty:

        return pd.DataFrame(
            columns=PLAYBOOK_COLUMNS
        )

    df = df.copy()

    # --------------------------------------------------------
    # Clean column names
    # --------------------------------------------------------

    df.columns = [
        str(col).strip()
        for col in df.columns
    ]

    # Remove completely empty columns
    df = df.dropna(
        axis=1,
        how="all"
    )

    # ========================================================
    # IDENTIFY FUNCTIONAL LOGIC COLUMNS
    # ========================================================

    # Rule ID
    rule_col = find_column(
        df,
        [
            "UID",
            "Rule_ID",
            "Rule ID",
            "RuleID",
            "Indicator_ID",
            "Indicator ID",
            "EWS_ID",
            "CM_ID"
        ]
    )

    # Parameter
    parameter_col = find_column(
        df,
        [
            "Metric / Input",
            "Metric/Input",
            "Parameter",
            "Indicator",
            "Metric"
        ]
    )

    # Raw Score
    score_col = find_column(
        df,
        [
            "Raw Score",
            "Raw_Score",
            "Score",
            "RawScore"
        ]
    )

    # What it signals
    signal_col = find_column(
        df,
        [
            "What it signals & likely drivers",
            "What_it_signals",
            "What it signals",
            "What It Signals",
            "What it signals and likely drivers"
        ]
    )

    # Remedial action
    action_col = find_column(
        df,
        [
            "Remedial action plan (step-by-step)",
            "Remedial_Action",
            "Remedial Action",
            "Remedial action",
            "Remedial_Action_Plan",
            "Remedial action plan"
        ]
    )

    # Primary owner
    owner_col = find_column(
        df,
        [
            "Primary Owner",
            "Primary_Owner",
            "Primary owner",
            "Owner"
        ]
    )

    # Additional columns used for matching/debugging
    condition_col = find_column(
        df,
        [
            "Condition",
            "condition"
        ]
    )

    lower_col = find_column(
        df,
        [
            "Lower Bound",
            "Lower_Bound",
            "Lower bound"
        ]
    )

    upper_col = find_column(
        df,
        [
            "Upper Bound",
            "Upper_Bound",
            "Upper bound"
        ]
    )

    band_order_col = find_column(
        df,
        [
            "Band Order",
            "Band_Order",
            "Band order"
        ]
    )

    rule_type_col = find_column(
        df,
        [
            "Rule Type",
            "Rule_Type",
            "Rule type"
        ]
    )

    # ========================================================
    # DEBUGGING
    # ========================================================

    print("\n============================================================")
    print("FUNCTIONAL LOGIC COLUMN MAPPING")
    print("============================================================")

    print("Rule ID       :", rule_col)
    print("Parameter     :", parameter_col)
    print("Score         :", score_col)
    print("What signals  :", signal_col)
    print("Remedial      :", action_col)
    print("Primary owner :", owner_col)
    print("Condition     :", condition_col)
    print("Lower bound   :", lower_col)
    print("Upper bound   :", upper_col)
    print("Band order    :", band_order_col)
    print("Rule type     :", rule_type_col)

    print("============================================================")

    # ========================================================
    # CREATE STANDARD TABLE
    # ========================================================

    result = pd.DataFrame(
        index=df.index
    )

    # --------------------------------------------------------
    # Rule ID
    # --------------------------------------------------------

    if rule_col:

        result["Rule_ID"] = (
            df[rule_col]
            .apply(normalise_rule_id)
        )

    else:

        result["Rule_ID"] = ""

    # --------------------------------------------------------
    # Parameter
    # --------------------------------------------------------

    if parameter_col:

        result["Parameter"] = (
            df[parameter_col]
            .apply(clean_text)
        )

    else:

        result["Parameter"] = ""

    # --------------------------------------------------------
    # Score
    # --------------------------------------------------------

    if score_col:

        result["Score"] = (
            df[score_col]
            .apply(normalise_score)
        )

    else:

        result["Score"] = None

    # --------------------------------------------------------
    # What it signals
    # --------------------------------------------------------

    if signal_col:

        result["What_it_signals"] = (
            df[signal_col]
            .apply(clean_text)
        )

    else:

        result["What_it_signals"] = ""

    # --------------------------------------------------------
    # Remedial action
    # --------------------------------------------------------

    if action_col:

        result["Remedial_Action"] = (
            df[action_col]
            .apply(clean_text)
        )

    else:

        result["Remedial_Action"] = ""

    # --------------------------------------------------------
    # Primary owner
    # --------------------------------------------------------

    if owner_col:

        result["Primary_Owner"] = (
            df[owner_col]
            .apply(clean_text)
        )

    else:

        result["Primary_Owner"] = ""

    # ========================================================
    # INTERNAL MATCHING COLUMNS
    # ========================================================

    if condition_col:

        result["_Condition"] = (
            df[condition_col]
            .apply(clean_text)
        )

    else:

        result["_Condition"] = ""

    if lower_col:

        result["_Lower_Bound"] = pd.to_numeric(
            df[lower_col],
            errors="coerce"
        )

    else:

        result["_Lower_Bound"] = None

    if upper_col:

        result["_Upper_Bound"] = pd.to_numeric(
            df[upper_col],
            errors="coerce"
        )

    else:

        result["_Upper_Bound"] = None

    if band_order_col:

        result["_Band_Order"] = pd.to_numeric(
            df[band_order_col],
            errors="coerce"
        )

    else:

        result["_Band_Order"] = None

    if rule_type_col:

        result["_Rule_Type"] = (
            df[rule_type_col]
            .apply(clean_text)
        )

    else:

        result["_Rule_Type"] = ""

    # ========================================================
    # REMOVE INVALID RULE IDS
    # ========================================================

    result = result[
        result["Rule_ID"].astype(str).str.strip() != ""
    ].copy()

    # ========================================================
    # IMPORTANT
    # ========================================================
    #
    # DO NOT REMOVE DUPLICATE RULE IDS.
    #
    # One Rule_ID can legitimately have multiple rows:
    #
    # EWS-021 -> score 0
    # EWS-021 -> score 25
    # EWS-021 -> score 50
    # EWS-021 -> score 75
    # EWS-021 -> score 100
    #
    # These rows contain different explanations/actions.
    #
    # Therefore we retain every functional-logic row.
    # ========================================================

    result = result.reset_index(
        drop=True
    )

    print(
        f"Functional logic rows retained: {len(result)}"
    )

    print(
        "\nFirst functional logic rows:"
    )

    print(
        result[
            [
                "Rule_ID",
                "Parameter",
                "Score",
                "What_it_signals",
                "Remedial_Action",
                "Primary_Owner"
            ]
        ]
        .head(10)
        .to_string(index=False)
    )

    return result


# ============================================================
# LOAD EWS PLAYBOOK
# ============================================================

def get_ews_playbook():

    if not EWS_FILE.exists():

        print(
            f"\nEWS file not found:\n{EWS_FILE}"
        )

        return pd.DataFrame()

    try:

        df = pd.read_excel(
            EWS_FILE,
            sheet_name="Scoring Engine (Rules)",
            header=3
        )

        print(
            "\n============================================================"
        )

        print(
            "EWS FUNCTIONAL LOGIC LOADED"
        )

        print(
            "============================================================"
        )

        print(
            "Excel columns:"
        )

        print(
            list(df.columns)
        )

        result = standardise_playbook_columns(
            df
        )

        print(
            "\nEWS playbook rows:",
            len(result)
        )

        return result

    except Exception as e:

        print(
            f"\nError loading EWS playbook: {e}"
        )

        return pd.DataFrame()


# ============================================================
# LOAD CREDIT MONITORING PLAYBOOK
# ============================================================

def get_cm_playbook():

    if not CM_FILE.exists():

        print(
            f"\nCredit Monitoring file not found:\n{CM_FILE}"
        )

        return pd.DataFrame()

    try:

        df = pd.read_excel(
            CM_FILE,
            sheet_name="Scoring Engine (Rules)",
            header=2
        )

        print(
            "\n============================================================"
        )

        print(
            "CREDIT MONITORING FUNCTIONAL LOGIC LOADED"
        )

        print(
            "============================================================"
        )

        print(
            "Excel columns:"
        )

        print(
            list(df.columns)
        )

        result = standardise_playbook_columns(
            df
        )

        print(
            "\nCredit Monitoring playbook rows:",
            len(result)
        )

        return result

    except Exception as e:

        print(
            f"\nError loading Credit Monitoring playbook: {e}"
        )

        return pd.DataFrame()


# ============================================================
# FIND SCORE COLUMN IN SCORE DATA
# ============================================================

def find_score_column(df):

    return find_column(
        df,
        [
            "Score",
            "Raw_Score",
            "Raw Score",
            "Indicator_Score",
            "Indicator Score",
            "EWS_Score",
            "EWS Score",
            "CM_Score",
            "CM Score"
        ]
    )


# ============================================================
# FIND PARAMETER COLUMN IN SCORE DATA
# ============================================================

def find_parameter_column(df):

    return find_column(
        df,
        [
            "Parameter",
            "Metric / Input",
            "Metric/Input",
            "Indicator",
            "Metric"
        ]
    )


# ============================================================
# MATCH ONE SCORE TO PLAYBOOK
# ============================================================

def match_playbook_row(
    score_row,
    candidates
):

    if candidates.empty:

        return None

    score_value = normalise_score(
        score_row.get("Score")
    )

    parameter_value = clean_text(
        score_row.get("Parameter", "")
    )

    # ========================================================
    # STEP 1 — PARAMETER MATCH
    # ========================================================

    if parameter_value:

        parameter_matches = candidates[
            candidates["Parameter"]
            .astype(str)
            .str.strip()
            .str.lower()
            ==
            parameter_value.strip().lower()
        ]

        if not parameter_matches.empty:

            candidates = parameter_matches.copy()

    # ========================================================
    # STEP 2 — EXACT SCORE MATCH
    # ========================================================

    if score_value is not None:

        score_matches = candidates[
            candidates["Score"]
            .apply(normalise_score)
            .apply(
                lambda x:
                x is not None
                and abs(x - score_value) < 0.000001
            )
        ]

        if not score_matches.empty:

            candidates = score_matches.copy()

    # ========================================================
    # STEP 3 — RANGE MATCH
    # ========================================================
    #
    # This is useful if the functional logic uses:
    #
    # Lower Bound
    # Upper Bound
    #
    # instead of an exact Raw Score.
    # ========================================================

    if (
        score_value is not None
        and not candidates.empty
    ):

        range_matches = []

        for idx, candidate in candidates.iterrows():

            lower = candidate.get(
                "_Lower_Bound"
            )

            upper = candidate.get(
                "_Upper_Bound"
            )

            lower_valid = (
                pd.notna(lower)
            )

            upper_valid = (
                pd.notna(upper)
            )

            matched = False

            if lower_valid and upper_valid:

                matched = (
                    score_value >= float(lower)
                    and
                    score_value <= float(upper)
                )

            elif lower_valid:

                matched = (
                    score_value >= float(lower)
                )

            elif upper_valid:

                matched = (
                    score_value <= float(upper)
                )

            if matched:

                range_matches.append(
                    idx
                )

        if range_matches:

            candidates = candidates.loc[
                range_matches
            ]

    # ========================================================
    # STEP 4 — SELECT BEST ROW
    # ========================================================

    if candidates.empty:

        return None

    # Prefer rows having actual explanatory content
    candidates = candidates.copy()

    candidates["_Content_Score"] = (
        candidates["What_it_signals"]
        .fillna("")
        .astype(str)
        .str.len()
        +
        candidates["Remedial_Action"]
        .fillna("")
        .astype(str)
        .str.len()
        +
        candidates["Primary_Owner"]
        .fillna("")
        .astype(str)
        .str.len()
    )

    # Prefer highest band order where multiple
    # equally valid rows exist.
    candidates["_Band_Sort"] = (
        pd.to_numeric(
            candidates["_Band_Order"],
            errors="coerce"
        )
        .fillna(-999999)
    )

    candidates = candidates.sort_values(
        by=[
            "_Content_Score",
            "_Band_Sort"
        ],
        ascending=[
            False,
            False
        ]
    )

    return candidates.iloc[0]


# ============================================================
# ATTACH PLAYBOOK TO INDICATOR SCORES
# ============================================================

def attach_playbook(
    indicator_scores,
    playbook_df
):

    # ========================================================
    # EMPTY SCORE DATA
    # ========================================================

    if indicator_scores.empty:

        return pd.DataFrame(
            columns=PLAYBOOK_COLUMNS
        )

    # ========================================================
    # EMPTY PLAYBOOK
    # ========================================================

    if playbook_df.empty:

        result = indicator_scores.copy()

        for col in PLAYBOOK_COLUMNS:

            if col not in result.columns:

                result[col] = ""

        return result[
            [
                "Rule_ID",
                "Parameter",
                "Score",
                "What_it_signals",
                "Remedial_Action",
                "Primary_Owner"
            ]
        ]

    scores = indicator_scores.copy()

    playbook = playbook_df.copy()

    # ========================================================
    # FIND RULE ID
    # ========================================================

    score_rule_col = find_column(
        scores,
        [
            "Rule_ID",
            "Rule ID",
            "RuleID",
            "UID",
            "Indicator_ID",
            "Indicator ID",
            "EWS_ID",
            "CM_ID"
        ]
    )

    if score_rule_col is None:

        print(
            "\nERROR: Could not find Rule ID "
            "column in score dataframe."
        )

        print(
            "Available columns:"
        )

        print(
            list(scores.columns)
        )

        return scores

    # Rename to common name
    if score_rule_col != "Rule_ID":

        scores = scores.rename(
            columns={
                score_rule_col:
                "Rule_ID"
            }
        )

    # ========================================================
    # FIND SCORE
    # ========================================================

    score_data_col = find_score_column(
        scores
    )

    if score_data_col:

        if score_data_col != "Score":

            scores = scores.rename(
                columns={
                    score_data_col:
                    "Score"
                }
            )

    else:

        # If no score exists, create blank
        scores["Score"] = None

    # ========================================================
    # FIND PARAMETER
    # ========================================================

    score_parameter_col = find_parameter_column(
        scores
    )

    if (
        score_parameter_col
        and score_parameter_col != "Parameter"
    ):

        scores = scores.rename(
            columns={
                score_parameter_col:
                "Parameter"
            }
        )

    if "Parameter" not in scores.columns:

        scores["Parameter"] = ""

    # ========================================================
    # NORMALISE SCORE DATA
    # ========================================================

    scores["Rule_ID"] = (
        scores["Rule_ID"]
        .apply(normalise_rule_id)
    )

    scores["Score"] = (
        scores["Score"]
        .apply(normalise_score)
    )

    scores["Parameter"] = (
        scores["Parameter"]
        .apply(clean_text)
    )

    # ========================================================
    # NORMALISE PLAYBOOK
    # ========================================================

    playbook["Rule_ID"] = (
        playbook["Rule_ID"]
        .apply(normalise_rule_id)
    )

    playbook["Score"] = (
        playbook["Score"]
        .apply(normalise_score)
    )

    playbook["Parameter"] = (
        playbook["Parameter"]
        .apply(clean_text)
    )

    # ========================================================
    # MATCH EACH INDICATOR INDIVIDUALLY
    # ========================================================
    #
    # IMPORTANT:
    #
    # We intentionally do NOT use:
    #
    # scores.merge(playbook, on="Rule_ID")
    #
    # because one Rule_ID can have several functional
    # logic rows corresponding to different score conditions.
    # ========================================================

    matched_rows = []

    for _, score_row in scores.iterrows():

        rule_id = score_row.get(
            "Rule_ID",
            ""
        )

        candidates = playbook[
            playbook["Rule_ID"] == rule_id
        ].copy()

        matched = match_playbook_row(
            score_row,
            candidates
        )

        # Start with the actual score record
        output_row = score_row.to_dict()

        # ====================================================
        # ADD MATCHED PLAYBOOK DATA
        # ====================================================

        if matched is not None:

            output_row[
                "Parameter"
            ] = (
                clean_text(
                    score_row.get(
                        "Parameter",
                        ""
                    )
                )
                or
                clean_text(
                    matched.get(
                        "Parameter",
                        ""
                    )
                )
            )

            output_row[
                "What_it_signals"
            ] = clean_text(
                matched.get(
                    "What_it_signals",
                    ""
                )
            )

            output_row[
                "Remedial_Action"
            ] = clean_text(
                matched.get(
                    "Remedial_Action",
                    ""
                )
            )

            output_row[
                "Primary_Owner"
            ] = clean_text(
                matched.get(
                    "Primary_Owner",
                    ""
                )
            )

        else:

            output_row[
                "What_it_signals"
            ] = ""

            output_row[
                "Remedial_Action"
            ] = ""

            output_row[
                "Primary_Owner"
            ] = ""

        matched_rows.append(
            output_row
        )

    # ========================================================
    # CREATE RESULT
    # ========================================================

    result = pd.DataFrame(
        matched_rows
    )

    # ========================================================
    # REQUIRED COLUMNS
    # ========================================================

    for col in PLAYBOOK_COLUMNS:

        if col not in result.columns:

            result[col] = ""

    # ========================================================
    # FINAL COLUMN ORDER
    # ========================================================

    result = result[
        [
            "Rule_ID",
            "Parameter",
            "Score",
            "What_it_signals",
            "Remedial_Action",
            "Primary_Owner"
        ]
    ]

    # ========================================================
    # DEBUG SUMMARY
    # ========================================================

    matched_count = (
        result["What_it_signals"]
        .astype(str)
        .str.strip()
        .ne("")
        .sum()
    )

    unmatched_count = (
        len(result)
        - matched_count
    )

    print(
        "\n============================================================"
    )

    print(
        "PLAYBOOK ATTACHMENT SUMMARY"
    )

    print(
        "============================================================"
    )

    print(
        "Total score rows       :",
        len(result)
    )

    print(
        "Matched playbook rows  :",
        matched_count
    )

    print(
        "Unmatched score rows   :",
        unmatched_count
    )

    print(
        "============================================================"
    )

    # Show sample
    print(
        "\nFINAL PLAYBOOK SAMPLE:"
    )

    print(
        result.head(10).to_string(
            index=False
        )
    )

    return result


# ============================================================
# TEST / DEBUG
# ============================================================

if __name__ == "__main__":

    print(
        "\n\n============================================================"
    )

    print(
        "TESTING EWS PLAYBOOK"
    )

    print(
        "============================================================"
    )

    ews_playbook = get_ews_playbook()

    if not ews_playbook.empty:

        print(
            "\nEWS PLAYBOOK SAMPLE:"
        )

        print(
            ews_playbook[
                [
                    "Rule_ID",
                    "Parameter",
                    "Score",
                    "What_it_signals",
                    "Remedial_Action",
                    "Primary_Owner"
                ]
            ]
            .head(20)
            .to_string(index=False)
        )

    print(
        "\n\n============================================================"
    )

    print(
        "TESTING CREDIT MONITORING PLAYBOOK"
    )

    print(
        "============================================================"
    )

    cm_playbook = get_cm_playbook()

    if not cm_playbook.empty:

        print(
            "\nCREDIT MONITORING PLAYBOOK SAMPLE:"
        )

        print(
            cm_playbook[
                [
                    "Rule_ID",
                    "Parameter",
                    "Score",
                    "What_it_signals",
                    "Remedial_Action",
                    "Primary_Owner"
                ]
            ]
            .head(20)
            .to_string(index=False)
        )