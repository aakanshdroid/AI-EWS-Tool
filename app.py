import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path

from common.rule_playbook_loader import (
    get_ews_playbook,
    get_cm_playbook,
    attach_playbook
)

from common.trend_analytics import (
    generate_peer_benchmark
)


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DB_PATH = (
    BASE_DIR
    / "data"
    / "ews_cm_database.db"
)

OUTPUT_DIR = (
    BASE_DIR
    / "output"
)

BORROWER_FILE = (
    OUTPUT_DIR
    / "borrower_master_200.csv"
)

EWS_FILE = (
    OUTPUT_DIR
    / "ews_results_200.csv"
)

EWS_RAW_FILE = (
    OUTPUT_DIR
    / "ews_raw_inputs_200.csv"
)

CM_FILE = (
    OUTPUT_DIR
    / "credit_monitoring_results_200.csv"
)

CM_RAW_FILE = (
    OUTPUT_DIR
    / "credit_monitoring_raw_inputs_200.csv"
)

ALERT_FILE = (
    OUTPUT_DIR
    / "ews_alerts.csv"
)

TREND_FILE = (
    OUTPUT_DIR
    / "quarterly_metric_deterioration.csv"
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI EWS & Credit Monitoring",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# HEADER
# ============================================================

st.title(
    "🚨 AI Early Warning System & Credit Monitoring"
)

st.caption(
    "Corporate Borrower Risk Monitoring | "
    "EWS • Credit Monitoring • Explainability • "
    "Human Review • Audit"
)


# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data(ttl=30)
def load_csv(file_path):

    if not file_path.exists():
        return pd.DataFrame()

    try:

        df = pd.read_csv(
            file_path
        )

        for col in df.columns:

            if df[col].dtype == "object":

                df[col] = (
                    df[col]
                    .astype(str)
                    .replace(
                        "nan",
                        ""
                    )
                )

        return df

    except Exception as e:

        st.error(
            f"Error reading {file_path.name}: {e}"
        )

        return pd.DataFrame()


@st.cache_data(ttl=30)
def load_db_table(table_name):

    if not DB_PATH.exists():
        return pd.DataFrame()

    conn = sqlite3.connect(
        DB_PATH
    )

    try:

        df = pd.read_sql_query(
            f"SELECT * FROM {table_name}",
            conn
        )

        for col in df.columns:

            if df[col].dtype == "object":

                df[col] = (
                    df[col]
                    .astype(str)
                    .replace(
                        "nan",
                        ""
                    )
                )

    except Exception:

        df = pd.DataFrame()

    finally:

        conn.close()

    return df


# ============================================================
# SAVE HUMAN REVIEW / AUDIT ACTION
# ============================================================

def save_audit_action(
    account_num,
    decision,
    rationale,
    reviewer_id="CO_001"
):

    DB_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    conn = sqlite3.connect(
        DB_PATH
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_trail (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            account_number TEXT,

            decision TEXT,

            rationale TEXT,

            reviewer_id TEXT,

            timestamp TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        INSERT INTO audit_trail
        (
            account_number,
            decision,
            rationale,
            reviewer_id
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            account_num,
            decision,
            rationale,
            reviewer_id
        )
    )

    conn.commit()
    conn.close()

    st.cache_data.clear()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def find_column(
    df,
    possible_names
):

    if df.empty:
        return None

    # Exact match
    for name in possible_names:

        if name in df.columns:
            return name

    # Case-insensitive match
    normalized = {
        str(col).strip().lower(): col
        for col in df.columns
    }

    for name in possible_names:

        key = (
            str(name)
            .strip()
            .lower()
        )

        if key in normalized:
            return normalized[key]

    return None


# ============================================================
# EXTRACT BORROWER-LEVEL INDICATOR SCORES
# ============================================================

def extract_borrower_indicator_scores(
    borrower_row,
    prefix
):

    """
    Converts wide borrower-level score columns into
    a simple Rule_ID + Score dataframe.

    Example:

        EWS-001_Score = 50
        EWS-002_Score = 20

    becomes:

        Rule_ID    Score
        EWS-001    50
        EWS-002    20
    """

    records = []

    if borrower_row is None:

        return pd.DataFrame(
            columns=[
                "Rule_ID",
                "Score"
            ]
        )

    for column in borrower_row.index:

        column_name = str(
            column
        ).strip()

        if (
            column_name.startswith(prefix)
            and column_name.endswith("_Score")
        ):

            indicator_id = (
                column_name[:-6]
            )

            score = borrower_row[
                column
            ]

            try:

                score = float(
                    score
                )

            except Exception:

                continue

            records.append(
                {
                    "Rule_ID": indicator_id,
                    "Score": score
                }
            )

    return pd.DataFrame(
        records,
        columns=[
            "Rule_ID",
            "Score"
        ]
    )


# ============================================================
# BUILD FINAL PLAYBOOK TABLE
# ============================================================

def build_playbook_table(
    indicator_scores,
    playbook_df
):

    """
    Combines borrower-level scores with the functional
    logic playbook.

    Final table:

        Rule_ID
        Parameter
        Score
        What_it_signals
        Remedial_Action
        Primary_Owner
    """

    if indicator_scores.empty:

        return pd.DataFrame(
            columns=[
                "Rule_ID",
                "Parameter",
                "Score",
                "What_it_signals",
                "Remedial_Action",
                "Primary_Owner"
            ]
        )

    result = attach_playbook(
        indicator_scores,
        playbook_df
    )

    required_columns = [
        "Rule_ID",
        "Parameter",
        "Score",
        "What_it_signals",
        "Remedial_Action",
        "Primary_Owner"
    ]

    for col in required_columns:

        if col not in result.columns:
            result[col] = ""

    result = result[
        required_columns
    ].copy()

    result["Score"] = pd.to_numeric(
        result["Score"],
        errors="coerce"
    )

    result = result.sort_values(
        by="Score",
        ascending=False,
        na_position="last"
    )

    return result.reset_index(
        drop=True
    )


# ============================================================
# GET SELECTED CREDIT MONITORING ROW
# ============================================================

def get_selected_cm_row(
    cm_data,
    borrower_id
):

    if cm_data.empty:
        return None

    cm_id_col = find_column(
        cm_data,
        [
            "Borrower_ID",
            "Account_Number",
            "BorrowerID",
            "Account_Number_ID"
        ]
    )

    if not cm_id_col:
        return None

    matches = cm_data[
        cm_data[
            cm_id_col
        ]
        .astype(str)
        .str.strip()
        ==
        str(borrower_id).strip()
    ]

    if matches.empty:
        return None

    return matches.iloc[0]


# ============================================================
# LOAD SYNTHETIC DATA
# ============================================================

borrower_df = load_csv(
    BORROWER_FILE
)

ews_df = load_csv(
    EWS_FILE
)

ews_raw_df = load_csv(
    EWS_RAW_FILE
)

cm_df = load_csv(
    CM_FILE
)

cm_raw_df = load_csv(
    CM_RAW_FILE
)

alerts_df = load_csv(
    ALERT_FILE
)

trend_file_df = load_csv(
    TREND_FILE
)


# ============================================================
# LOAD FUNCTIONAL LOGIC PLAYBOOKS
# ============================================================

try:

    ews_playbook_df = (
        get_ews_playbook()
    )

except Exception as e:

    ews_playbook_df = pd.DataFrame()

    st.warning(
        "EWS functional logic playbook "
        f"could not be loaded: {e}"
    )


try:

    cm_playbook_df = (
        get_cm_playbook()
    )

except Exception as e:

    cm_playbook_df = pd.DataFrame()

    st.warning(
        "Credit Monitoring functional logic "
        f"could not be loaded: {e}"
    )


# ============================================================
# CHECK EWS DATA
# ============================================================

if ews_df.empty:

    st.error(
        "No EWS result data is available."
    )

    st.info(
        "Generate the synthetic dataset first by running:"
    )

    st.code(
        "python -m src.main"
    )

    st.stop()


# ============================================================
# IDENTIFY IMPORTANT COLUMNS
# ============================================================

borrower_id_col = find_column(
    ews_df,
    [
        "Borrower_ID",
        "Account_Number",
        "Account_Number_ID",
        "BorrowerID"
    ]
)


score_col = find_column(
    ews_df,
    [
        "Overall_Normalized_Score",
        "Overall_Risk_Score",
        "Overall_Score"
    ]
)


risk_band_col = find_column(
    ews_df,
    [
        "Risk_Band",
        "RiskBand"
    ]
)


status_col = find_column(
    ews_df,
    [
        "Final_Status",
        "Status"
    ]
)


critical_col = find_column(
    ews_df,
    [
        "Critical_Indicator_Override",
        "Critical_Override"
    ]
)


# ============================================================
# MERGE BORROWER MASTER + EWS RESULTS
# ============================================================

dashboard_df = ews_df.copy()


if (
    not borrower_df.empty
    and borrower_id_col
):

    master_id_col = find_column(
        borrower_df,
        [
            "Borrower_ID",
            "Account_Number",
            "BorrowerID"
        ]
    )

    if master_id_col:

        borrower_master_for_merge = (
            borrower_df.copy()
        )

        if (
            master_id_col
            != borrower_id_col
        ):

            borrower_master_for_merge = (
                borrower_master_for_merge
                .rename(
                    columns={
                        master_id_col:
                        borrower_id_col
                    }
                )
            )

        dashboard_df = (
            borrower_master_for_merge
            .merge(
                ews_df,
                on=borrower_id_col,
                how="left",
                suffixes=(
                    "",
                    "_EWS"
                )
            )
        )


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "⚙️ Dashboard Controls"
)

st.sidebar.markdown(
    "### Data Source"
)

st.sidebar.success(
    "Synthetic 200-Borrower Dataset"
)

st.sidebar.caption(
    "Generated using Faker + NumPy "
    "and scored using the EWS engine."
)


# ============================================================
# FILTER COLUMNS
# ============================================================

sector_col = find_column(
    dashboard_df,
    [
        "Sector",
        "Industry",
        "Business_Sector"
    ]
)


profile_col = find_column(
    dashboard_df,
    [
        "Risk_Profile",
        "Risk_Profile_Type",
        "Borrower_Risk_Profile"
    ]
)


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.markdown(
    "### Filters"
)


# Sector

if sector_col:

    sectors = sorted(
        dashboard_df[
            sector_col
        ]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    selected_sector = (
        st.sidebar.selectbox(
            "Sector",
            ["All"] + sectors
        )
    )

else:

    selected_sector = "All"


# EWS Risk Band

selected_band = (
    st.sidebar.selectbox(
        "EWS Risk Band",
        [
            "All",
            "Green",
            "Yellow",
            "Amber",
            "Red",
            "Critical"
        ]
    )
)


# Borrower Risk Profile

if profile_col:

    profiles = sorted(
        dashboard_df[
            profile_col
        ]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    selected_profile = (
        st.sidebar.selectbox(
            "Borrower Risk Profile",
            ["All"] + profiles
        )
    )

else:

    selected_profile = "All"


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df = (
    dashboard_df.copy()
)


if (
    sector_col
    and selected_sector != "All"
):

    filtered_df = filtered_df[
        filtered_df[
            sector_col
        ]
        .astype(str)
        ==
        str(selected_sector)
    ]


if (
    risk_band_col
    and selected_band != "All"
):

    filtered_df = filtered_df[
        filtered_df[
            risk_band_col
        ]
        .astype(str)
        ==
        str(selected_band)
    ]


if (
    profile_col
    and selected_profile != "All"
):

    filtered_df = filtered_df[
        filtered_df[
            profile_col
        ]
        .astype(str)
        ==
        str(selected_profile)
    ]


# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "📊 Risk Overview",
        "🔎 Evidence Pack",
        "📈 Trend & Peer Analytics",
        "✍️ Human Review",
        "📜 Governance & Audit Trail"
    ]
)


# ============================================================
# TAB 1 — RISK OVERVIEW
# ============================================================

with tab1:

    st.subheader(
        "Portfolio Risk Overview"
    )

    # --------------------------------------------------------
    # KPI CALCULATIONS
    # --------------------------------------------------------

    total_borrowers = len(
        filtered_df
    )

    if risk_band_col:

        critical_count = len(
            filtered_df[
                filtered_df[
                    risk_band_col
                ]
                .astype(str)
                == "Critical"
            ]
        )

        red_critical_count = len(
            filtered_df[
                filtered_df[
                    risk_band_col
                ]
                .astype(str)
                .isin(
                    [
                        "Red",
                        "Critical"
                    ]
                )
            ]
        )

    else:

        critical_count = 0
        red_critical_count = 0


    # --------------------------------------------------------
    # ALERT COUNT
    # --------------------------------------------------------

    if (
        not alerts_df.empty
        and borrower_id_col
        and borrower_id_col
        in alerts_df.columns
    ):

        active_alerts = len(
            alerts_df[
                alerts_df[
                    borrower_id_col
                ]
                .astype(str)
                .isin(
                    filtered_df[
                        borrower_id_col
                    ]
                    .astype(str)
                )
            ]
        )

    else:

        active_alerts = len(
            alerts_df
        )


    # --------------------------------------------------------
    # AVERAGE SCORE
    # --------------------------------------------------------

    if score_col:

        score_series = pd.to_numeric(
            filtered_df[
                score_col
            ],
            errors="coerce"
        )

        average_score = (
            score_series.mean()
            if score_series.notna().any()
            else 0
        )

    else:

        average_score = 0


    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    col1, col2, col3, col4, col5 = (
        st.columns(5)
    )

    with col1:

        st.metric(
            "Total Borrowers",
            total_borrowers
        )

    with col2:

        st.metric(
            "Critical",
            critical_count
        )

    with col3:

        st.metric(
            "Red + Critical",
            red_critical_count
        )

    with col4:

        st.metric(
            "Active Alerts",
            active_alerts
        )

    with col5:

        st.metric(
            "Average EWS Score",
            f"{average_score:.1f}"
        )


    st.divider()


    # --------------------------------------------------------
    # RISK DISTRIBUTION
    # --------------------------------------------------------

    col_left, col_right = (
        st.columns(2)
    )


    with col_left:

        st.subheader(
            "EWS Risk Band Distribution"
        )

        if risk_band_col:

            risk_distribution = (
                filtered_df[
                    risk_band_col
                ]
                .value_counts()
                .reindex(
                    [
                        "Green",
                        "Yellow",
                        "Amber",
                        "Red",
                        "Critical"
                    ],
                    fill_value=0
                )
            )

            st.bar_chart(
                risk_distribution
            )


    with col_right:

        st.subheader(
            "Borrower Risk Profile"
        )

        if profile_col:

            profile_distribution = (
                filtered_df[
                    profile_col
                ]
                .value_counts()
            )

            st.bar_chart(
                profile_distribution
            )


    st.divider()


    # --------------------------------------------------------
    # ACCOUNT LEVEL DATA
    # --------------------------------------------------------

    st.subheader(
        "Account-Level EWS Scores"
    )

    preferred_columns = [
        "Borrower_ID",
        "Borrower_Name",
        "Account_Number",
        "Sector",
        "City",
        "Risk_Profile",
        "External_Rating",
        "Annual_Turnover_Cr",
        "Total_Debt_Cr",
        "TNW_Cr",
        "Overall_Normalized_Score",
        "Overall_Risk_Score",
        "Risk_Band",
        "Final_Status"
    ]

    available_columns = [
        col
        for col in preferred_columns
        if col in filtered_df.columns
    ]

    if available_columns:

        st.dataframe(
            filtered_df[
                available_columns
            ],
            use_container_width=True,
            height=450,
            hide_index=True
        )

    else:

        st.dataframe(
            filtered_df,
            use_container_width=True,
            height=450,
            hide_index=True
        )


    # --------------------------------------------------------
    # DOWNLOAD
    # --------------------------------------------------------

    st.download_button(
        label="📥 Download Portfolio View",
        data=(
            filtered_df
            .to_csv(index=False)
            .encode("utf-8")
        ),
        file_name="EWS_Portfolio_View.csv",
        mime="text/csv"
    )


# ============================================================
# TAB 2 — EVIDENCE PACK
# ============================================================

with tab2:

    st.subheader(
        "🔎 Explainability & Evidence Pack"
    )

    if not borrower_id_col:

        st.error(
            "Borrower ID column could not be identified "
            "in the EWS results."
        )

    else:

        borrower_list = (
            filtered_df[
                borrower_id_col
            ]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        if not borrower_list:

            st.info(
                "No borrowers available for the selected filters."
            )

        else:

            selected_borrower = (
                st.selectbox(
                    "Select Borrower / Account",
                    borrower_list,
                    key="evidence_borrower"
                )
            )

            selected_data = filtered_df[
                filtered_df[
                    borrower_id_col
                ]
                .astype(str)
                ==
                str(selected_borrower)
            ]

            if not selected_data.empty:

                acc_info = (
                    selected_data.iloc[0]
                )


                # ====================================================
                # BORROWER INFORMATION
                # ====================================================

                st.markdown(
                    "### Borrower Information"
                )

                info1, info2, info3, info4 = (
                    st.columns(4)
                )

                name_col = find_column(
                    dashboard_df,
                    [
                        "Borrower_Name",
                        "Company_Name"
                    ]
                )

                with info1:

                    borrower_name = (
                        acc_info.get(
                            name_col,
                            "N/A"
                        )
                        if name_col
                        else "N/A"
                    )

                    st.metric(
                        "Borrower",
                        borrower_name
                    )

                with info2:

                    st.metric(
                        "Sector",
                        acc_info.get(
                            sector_col,
                            "N/A"
                        )
                        if sector_col
                        else "N/A"
                    )

                with info3:

                    st.metric(
                        "Rating",
                        acc_info.get(
                            "External_Rating",
                            "N/A"
                        )
                    )

                with info4:

                    st.metric(
                        "Risk Band",
                        acc_info.get(
                            risk_band_col,
                            "N/A"
                        )
                        if risk_band_col
                        else "N/A"
                    )


                st.divider()


                # ====================================================
                # EWS ASSESSMENT
                # ====================================================

                st.markdown(
                    "### EWS Assessment"
                )

                c1, c2, c3, c4 = (
                    st.columns(4)
                )

                with c1:

                    score_value = (
                        acc_info.get(
                            score_col,
                            "N/A"
                        )
                        if score_col
                        else "N/A"
                    )

                    try:

                        score_display = (
                            f"{float(score_value):.2f}"
                        )

                    except Exception:

                        score_display = str(
                            score_value
                        )

                    st.metric(
                        "Overall EWS Score",
                        score_display
                    )

                with c2:

                    st.metric(
                        "Risk Band",
                        acc_info.get(
                            risk_band_col,
                            "N/A"
                        )
                        if risk_band_col
                        else "N/A"
                    )

                with c3:

                    st.metric(
                        "Final Status",
                        acc_info.get(
                            status_col,
                            "N/A"
                        )
                        if status_col
                        else "N/A"
                    )

                with c4:

                    st.metric(
                        "Critical Override",
                        acc_info.get(
                            critical_col,
                            "N/A"
                        )
                        if critical_col
                        else "N/A"
                    )


                # ====================================================
                # EWS ACTIVE ALERTS
                # ====================================================

                st.markdown(
                    "### 🚨 Active EWS Alerts"
                )

                if (
                    not alerts_df.empty
                    and borrower_id_col
                    in alerts_df.columns
                ):

                    borrower_alerts = (
                        alerts_df[
                            alerts_df[
                                borrower_id_col
                            ]
                            .astype(str)
                            ==
                            str(selected_borrower)
                        ]
                        .copy()
                    )

                    if not borrower_alerts.empty:

                        sort_columns = [
                            col
                            for col in [
                                "Score",
                                "Normalized_Score"
                            ]
                            if col
                            in borrower_alerts.columns
                        ]

                        if sort_columns:

                            borrower_alerts = (
                                borrower_alerts
                                .sort_values(
                                    by=sort_columns[0],
                                    ascending=False
                                )
                            )

                        st.dataframe(
                            borrower_alerts,
                            use_container_width=True,
                            hide_index=True
                        )

                    else:

                        st.success(
                            "No active EWS alerts."
                        )

                else:

                    st.success(
                        "No active EWS alerts."
                    )


                # ====================================================
                # RAW EWS DATA
                # ====================================================

                st.markdown(
                    "### 📋 EWS Input Data"
                )

                if (
                    not ews_raw_df.empty
                    and borrower_id_col
                    in ews_raw_df.columns
                ):

                    raw_data = (
                        ews_raw_df[
                            ews_raw_df[
                                borrower_id_col
                            ]
                            .astype(str)
                            ==
                            str(selected_borrower)
                        ]
                    )

                    if not raw_data.empty:

                        st.dataframe(
                            raw_data,
                            use_container_width=True,
                            hide_index=True
                        )

                    else:

                        st.info(
                            "No raw EWS data available "
                            "for this borrower."
                        )

                else:

                    st.info(
                        "No raw EWS data available."
                    )


                # ====================================================
                # EWS SCORE BREAKDOWN
                # ====================================================

                st.markdown(
                    "### 📊 Indicator Score Breakdown"
                )

                score_columns = [
                    col
                    for col in ews_df.columns
                    if (
                        col.endswith("_Score")
                        or "normalized" in col.lower()
                    )
                ]

                if score_columns:

                    score_breakdown = (
                        selected_data[
                            [
                                col
                                for col in score_columns
                                if col
                                in selected_data.columns
                            ]
                        ]
                        .T
                    )

                    st.dataframe(
                        score_breakdown,
                        use_container_width=True
                    )

                else:

                    st.info(
                        "No indicator score columns found."
                    )


                # ====================================================
                # EWS RISK DRIVERS & REMEDIAL ACTION
                # ====================================================

                st.divider()

                st.markdown(
                    "## 🚨 EWS Risk Drivers & Remedial Action"
                )

                st.caption(
                    "The score is borrower-specific. "
                    "The parameter, signal, remedial action and "
                    "owner are sourced from the EWS functional logic."
                )

                borrower_ews_scores = (
                    extract_borrower_indicator_scores(
                        acc_info,
                        "EWS-"
                    )
                )

                borrower_ews_playbook = (
                    build_playbook_table(
                        borrower_ews_scores,
                        ews_playbook_df
                    )
                )

                if not borrower_ews_playbook.empty:

                    st.dataframe(
                        borrower_ews_playbook,
                        use_container_width=True,
                        hide_index=True,
                        column_config={

                            "Rule_ID":
                                st.column_config.TextColumn(
                                    "Rule ID",
                                    width="small"
                                ),

                            "Parameter":
                                st.column_config.TextColumn(
                                    "Parameter",
                                    width="medium"
                                ),

                            "Score":
                                st.column_config.NumberColumn(
                                    "Score",
                                    format="%.0f"
                                ),

                            "What_it_signals":
                                st.column_config.TextColumn(
                                    "What it signals & likely drivers",
                                    width="large"
                                ),

                            "Remedial_Action":
                                st.column_config.TextColumn(
                                    "Remedial action plan",
                                    width="large"
                                ),

                            "Primary_Owner":
                                st.column_config.TextColumn(
                                    "Primary owner",
                                    width="medium"
                                )
                        }
                    )

                else:

                    st.info(
                        "No EWS indicator-level score information "
                        "is available for this borrower."
                    )


                # ====================================================
                # CREDIT MONITORING
                # ====================================================

                st.divider()

                st.markdown(
                    "## 📋 Credit Monitoring Exceptions & Action Plan"
                )

                st.caption(
                    "The Credit Monitoring score is borrower-specific. "
                    "The parameter, signal, remedial action and owner "
                    "are sourced from the Credit Monitoring functional logic."
                )

                cm_row = get_selected_cm_row(
                    cm_df,
                    selected_borrower
                )

                borrower_cm_playbook = pd.DataFrame(
                    columns=[
                        "Rule_ID",
                        "Parameter",
                        "Score",
                        "What_it_signals",
                        "Remedial_Action",
                        "Primary_Owner"
                    ]
                )

                if cm_row is not None:

                    borrower_cm_scores = (
                        extract_borrower_indicator_scores(
                            cm_row,
                            "CM-"
                        )
                    )

                    borrower_cm_playbook = (
                        build_playbook_table(
                            borrower_cm_scores,
                            cm_playbook_df
                        )
                    )

                    if not borrower_cm_playbook.empty:

                        st.dataframe(
                            borrower_cm_playbook,
                            use_container_width=True,
                            hide_index=True,
                            column_config={

                                "Rule_ID":
                                    st.column_config.TextColumn(
                                        "Rule ID",
                                        width="small"
                                    ),

                                "Parameter":
                                    st.column_config.TextColumn(
                                        "Parameter",
                                        width="medium"
                                    ),

                                "Score":
                                    st.column_config.NumberColumn(
                                        "Score",
                                        format="%.0f"
                                    ),

                                "What_it_signals":
                                    st.column_config.TextColumn(
                                        "What it signals & likely drivers",
                                        width="large"
                                    ),

                                "Remedial_Action":
                                    st.column_config.TextColumn(
                                        "Remedial action plan",
                                        width="large"
                                    ),

                                "Primary_Owner":
                                    st.column_config.TextColumn(
                                        "Primary owner",
                                        width="medium"
                                    )
                            }
                        )

                    else:

                        st.info(
                            "No Credit Monitoring indicator-level "
                            "score information is available for "
                            "this borrower."
                        )

                else:

                    st.info(
                        "No Credit Monitoring record found "
                        "for this borrower."
                    )


                # ====================================================
                # DOWNLOAD BORROWER PLAYBOOK
                # ====================================================

                st.divider()

                st.markdown(
                    "### 📥 Download Borrower Action Plan"
                )

                ews_download = (
                    borrower_ews_playbook
                    .assign(
                        Module="EWS"
                    )
                )

                cm_download = (
                    borrower_cm_playbook
                    .assign(
                        Module="Credit Monitoring"
                    )
                )

                combined_action_plan = pd.concat(
                    [
                        ews_download,
                        cm_download
                    ],
                    ignore_index=True
                )

                st.download_button(
                    label="📥 Download EWS + Credit Monitoring Action Plan",

                    data=(
                        combined_action_plan
                        .to_csv(index=False)
                        .encode("utf-8")
                    ),

                    file_name=(
                        f"{selected_borrower}"
                        "_Risk_Action_Plan.csv"
                    ),

                    mime="text/csv",

                    key="download_action_plan"
                )


# ============================================================
# TAB 3 — TREND & PEER ANALYTICS
# ============================================================

with tab3:

    st.subheader(
        "📈 Trend & Peer Analytics"
    )


    # ========================================================
    # BORROWER SELECTION
    # ========================================================

    st.markdown(
        "### 👤 Borrower Selection"
    )

    trend_borrower_col = find_column(
        filtered_df,
        [
            "Borrower_ID",
            "Account_Number",
            "BorrowerID",
            "Account_Number_ID"
        ]
    )

    trend_borrower_name_col = find_column(
        filtered_df,
        [
            "Borrower_Name",
            "Company_Name"
        ]
    )


    if (
        trend_borrower_col
        and not filtered_df.empty
    ):

        trend_borrower_ids = (
            filtered_df[
                trend_borrower_col
            ]
            .dropna()
            .astype(str)
            .str.strip()
            .unique()
            .tolist()
        )

        trend_borrower_options = [
            "All Borrowers"
        ]

        for borrower_id in trend_borrower_ids:

            borrower_rows = filtered_df[
                filtered_df[
                    trend_borrower_col
                ]
                .astype(str)
                .str.strip()
                ==
                borrower_id
            ]

            if (
                trend_borrower_name_col
                and not borrower_rows.empty
            ):

                borrower_name = str(
                    borrower_rows.iloc[0].get(
                        trend_borrower_name_col,
                        ""
                    )
                ).strip()

                label = (
                    f"{borrower_id} | {borrower_name}"
                    if borrower_name
                    else borrower_id
                )

            else:

                label = borrower_id

            trend_borrower_options.append(
                label
            )


        selected_trend_label = st.selectbox(
            "Select Borrower / Account",
            trend_borrower_options,
            key="trend_peer_borrower"
        )


        if selected_trend_label == "All Borrowers":

            selected_trend_borrower_id = None

        else:

            selected_trend_borrower_id = (
                selected_trend_label
                .split(" | ", 1)[0]
            )

    else:

        selected_trend_borrower_id = None

        st.info(
            "No borrower selection is available "
            "for Trend & Peer Analytics."
        )


    # ========================================================
    # QUARTERLY METRIC DETERIORATION
    # ========================================================

    st.divider()

    st.markdown(
        "### 📉 Quarterly Metric Deterioration"
    )

    st.caption(
        "Quarter-on-quarter deterioration identified from "
        "the generated quarterly financial history. "
        "The table is linked to the selected borrower."
    )


    if not trend_file_df.empty:

        trend_display_df = (
            trend_file_df.copy()
        )

    else:

        trend_display_df = load_db_table(
            "trend_analytics_results"
        )


    if not trend_display_df.empty:

        trend_id_col = find_column(
            trend_display_df,
            [
                "Borrower_ID",
                "Account_Number",
                "BorrowerID",
                "Account_Number_ID"
            ]
        )


        if (
            selected_trend_borrower_id
            is not None
            and trend_id_col
        ):

            borrower_trend_df = (
                trend_display_df[
                    trend_display_df[
                        trend_id_col
                    ]
                    .astype(str)
                    .str.strip()
                    ==
                    str(
                        selected_trend_borrower_id
                    ).strip()
                ]
                .copy()
            )

        else:

            borrower_trend_df = (
                trend_display_df.copy()
            )


        # Numeric conversion

        for numeric_col in [
            "Previous_Value",
            "Current_Value",
            "QoQ_Change_pct"
        ]:

            if numeric_col in borrower_trend_df.columns:

                borrower_trend_df[
                    numeric_col
                ] = pd.to_numeric(
                    borrower_trend_df[
                        numeric_col
                    ],
                    errors="coerce"
                )


        deterioration_count = len(
            borrower_trend_df
        )


        if "Metric" in borrower_trend_df.columns:

            metric_count = (
                borrower_trend_df[
                    "Metric"
                ]
                .nunique()
            )

        else:

            metric_count = 0


        k1, k2 = st.columns(2)


        with k1:

            st.metric(
                "Deterioration Instances",
                deterioration_count
            )


        with k2:

            st.metric(
                "Metrics Showing Deterioration",
                metric_count
            )


        if not borrower_trend_df.empty:

            preferred_trend_columns = [
                "Borrower_ID",
                "Borrower_Name",
                "Previous_Quarter",
                "Current_Quarter",
                "Metric",
                "Previous_Value",
                "Current_Value",
                "QoQ_Change_pct",
                "Direction",
                "Deterioration"
            ]


            available_trend_columns = [
                col
                for col in preferred_trend_columns
                if col
                in borrower_trend_df.columns
            ]


            if not available_trend_columns:

                available_trend_columns = list(
                    borrower_trend_df.columns
                )


            st.dataframe(
                borrower_trend_df[
                    available_trend_columns
                ],
                use_container_width=True,
                height=400,
                hide_index=True,
                column_config={

                    "QoQ_Change_pct":
                        st.column_config.NumberColumn(
                            "QoQ Change (%)",
                            format="%.2f"
                        ),

                    "Previous_Value":
                        st.column_config.NumberColumn(
                            "Previous Value",
                            format="%.2f"
                        ),

                    "Current_Value":
                        st.column_config.NumberColumn(
                            "Current Value",
                            format="%.2f"
                        )
                }
            )


            st.download_button(
                label="📥 Download Quarterly Deterioration",

                data=(
                    borrower_trend_df
                    .to_csv(index=False)
                    .encode("utf-8")
                ),

                file_name=(
                    f"{selected_trend_borrower_id or 'portfolio'}_"
                    "Quarterly_Deterioration.csv"
                ),

                mime="text/csv",

                key="download_quarterly_deterioration"
            )


        else:

            st.success(
                "No quarterly metric deterioration was "
                "identified for the selected borrower."
            )


    else:

        st.info(
            "No quarterly metric deterioration data is available. "
            "Run generate_synthetic_data.py to create the "
            "quarterly history and deterioration output."
        )


    # ========================================================
    # PEER GROUP BENCHMARKING
    # ========================================================

    st.divider()

    st.markdown(
        "### 🏢 Peer Group Benchmarking"
    )

    st.caption(
        "Peer benchmark results for the selected borrower, "
        "generated using the borrower master and the "
        "peer benchmarking logic."
    )


    if selected_trend_borrower_id is not None:

        try:

            peer_benchmark_df = (
                generate_peer_benchmark(
                    selected_trend_borrower_id,
                    borrower_df
                )
            )


            if (
                peer_benchmark_df is not None
                and not peer_benchmark_df.empty
            ):

                # ------------------------------------------------
                # PEER SUMMARY
                # ------------------------------------------------

                peer_count = 0

                if (
                    "Peer_Count"
                    in peer_benchmark_df.columns
                ):

                    try:

                        peer_count = int(
                            peer_benchmark_df[
                                "Peer_Count"
                            ].iloc[0]
                        )

                    except Exception:

                        peer_count = 0


                peer_sector = ""

                if (
                    "Sector"
                    in peer_benchmark_df.columns
                ):

                    peer_sector = str(
                        peer_benchmark_df[
                            "Sector"
                        ].iloc[0]
                    )


                col_peer_1, col_peer_2 = (
                    st.columns(2)
                )


                with col_peer_1:

                    st.metric(
                        "Comparable Borrowers",
                        peer_count
                    )


                with col_peer_2:

                    st.metric(
                        "Peer Sector",
                        peer_sector
                        if peer_sector
                        else "N/A"
                    )


                # ------------------------------------------------
                # PREPARE DISPLAY TABLE
                # ------------------------------------------------

                peer_display_df = (
                    peer_benchmark_df.copy()
                )


                preferred_peer_columns = [
                    "Borrower_ID",
                    "Borrower_Name",
                    "Sector",
                    "Peer_Count",
                    "Metric",
                    "Borrower_Value",
                    "Peer_Median",
                    "Peer_Average",
                    "Variance_vs_Peer_Median_pct",
                    "Position"
                ]


                available_peer_columns = [
                    col
                    for col in preferred_peer_columns
                    if col
                    in peer_display_df.columns
                ]


                if available_peer_columns:

                    peer_display_df = (
                        peer_display_df[
                            available_peer_columns
                        ]
                    )


                # ------------------------------------------------
                # RENAME FOR DASHBOARD
                # ------------------------------------------------

                peer_display_df = (
                    peer_display_df.rename(
                        columns={

                            "Borrower_ID":
                                "Borrower ID",

                            "Borrower_Name":
                                "Borrower Name",

                            "Peer_Count":
                                "Peer Count",

                            "Borrower_Value":
                                "Borrower Value",

                            "Peer_Median":
                                "Peer Median",

                            "Peer_Average":
                                "Peer Average",

                            "Variance_vs_Peer_Median_pct":
                                "Variance vs Peer Median (%)",

                            "Position":
                                "Peer Position"
                        }
                    )
                )


                # ------------------------------------------------
                # NUMERIC FORMATTING
                # ------------------------------------------------

                numeric_peer_columns = [
                    "Borrower Value",
                    "Peer Median",
                    "Peer Average",
                    "Variance vs Peer Median (%)"
                ]


                for col in numeric_peer_columns:

                    if col in peer_display_df.columns:

                        peer_display_df[
                            col
                        ] = pd.to_numeric(
                            peer_display_df[
                                col
                            ],
                            errors="coerce"
                        )


                # ------------------------------------------------
                # DISPLAY
                # ------------------------------------------------

                st.dataframe(
                    peer_display_df,
                    use_container_width=True,
                    height=400,
                    hide_index=True,
                    column_config={

                        "Borrower Value":
                            st.column_config.NumberColumn(
                                "Borrower Value",
                                format="%.2f"
                            ),

                        "Peer Median":
                            st.column_config.NumberColumn(
                                "Peer Median",
                                format="%.2f"
                            ),

                        "Peer Average":
                            st.column_config.NumberColumn(
                                "Peer Average",
                                format="%.2f"
                            ),

                        "Variance vs Peer Median (%)":
                            st.column_config.NumberColumn(
                                "Variance vs Peer Median (%)",
                                format="%.2f"
                            )
                    }
                )


                # ------------------------------------------------
                # DOWNLOAD
                # ------------------------------------------------

                st.download_button(
                    label="📥 Download Peer Benchmark",

                    data=(
                        peer_benchmark_df
                        .to_csv(index=False)
                        .encode("utf-8")
                    ),

                    file_name=(
                        f"{selected_trend_borrower_id}_"
                        "Peer_Benchmark.csv"
                    ),

                    mime="text/csv",

                    key="download_peer_benchmark"
                )


            else:

                st.info(
                    "No comparable peer benchmark results "
                    "are available for the selected borrower."
                )


        except Exception as e:

            st.error(
                "Unable to generate peer benchmark."
            )

            st.exception(e)


    else:

        st.info(
            "Select a borrower above to generate "
            "peer group benchmarking."
        )


    # ========================================================
    # CREDIT MONITORING RESULTS
    # ========================================================

    st.divider()

    st.subheader(
        "📋 Credit Monitoring Results"
    )


    if not cm_df.empty:

        cm_display_df = (
            cm_df.copy()
        )


        cm_id_col = find_column(
            cm_display_df,
            [
                "Borrower_ID",
                "Account_Number",
                "BorrowerID",
                "Account_Number_ID"
            ]
        )


        if (
            selected_trend_borrower_id
            is not None
            and cm_id_col
        ):

            cm_display_df = (
                cm_display_df[
                    cm_display_df[
                        cm_id_col
                    ]
                    .astype(str)
                    .str.strip()
                    ==
                    str(
                        selected_trend_borrower_id
                    ).strip()
                ]
                .copy()
            )


        st.dataframe(
            cm_display_df,
            use_container_width=True,
            height=400,
            hide_index=True
        )


    else:

        st.info(
            "No Credit Monitoring results available."
        )


# ============================================================
# TAB 4 — HUMAN REVIEW
# ============================================================

with tab4:

    st.subheader(
        "✍️ Human Credit Review & Decisioning"
    )

    st.info(
        "The system provides risk signals and supporting "
        "evidence. Final credit decisions remain with the "
        "authorized Credit Officer."
    )


    if borrower_id_col:

        borrower_list = (
            filtered_df[
                borrower_id_col
            ]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )


        if borrower_list:

            acc_to_review = (
                st.selectbox(
                    "Select Borrower / Account",
                    borrower_list,
                    key="review_acc"
                )
            )


            review_row = (
                filtered_df[
                    filtered_df[
                        borrower_id_col
                    ]
                    .astype(str)
                    ==
                    str(acc_to_review)
                ]
            )


            if not review_row.empty:

                review_row = (
                    review_row.iloc[0]
                )


                r1, r2, r3 = (
                    st.columns(3)
                )


                with r1:

                    st.metric(
                        "Current EWS Score",
                        review_row.get(
                            score_col,
                            "N/A"
                        )
                        if score_col
                        else "N/A"
                    )


                with r2:

                    st.metric(
                        "Current Risk Band",
                        review_row.get(
                            risk_band_col,
                            "N/A"
                        )
                        if risk_band_col
                        else "N/A"
                    )


                with r3:

                    st.metric(
                        "Final Status",
                        review_row.get(
                            status_col,
                            "N/A"
                        )
                        if status_col
                        else "N/A"
                    )


            st.markdown(
                "### Credit Officer Action"
            )


            decision = st.radio(
                "Decision",
                [
                    "Accept Alert (Escalate to Remediation)",
                    "Override Risk Band",
                    "Close as False Positive"
                ]
            )


            rationale = st.text_area(
                "Mitigation Rationale / Comments",
                "",
                height=120
            )


            reviewer_id = st.text_input(
                "Reviewer ID",
                "CO_001"
            )


            if st.button(
                "Submit Decision",
                type="primary"
            ):

                if not rationale.strip():

                    st.error(
                        "Please provide a rationale "
                        "before submitting."
                    )

                else:

                    save_audit_action(
                        account_num=acc_to_review,
                        decision=decision,
                        rationale=rationale,
                        reviewer_id=reviewer_id
                    )

                    st.success(
                        f"Decision for {acc_to_review} "
                        "logged successfully."
                    )


# ============================================================
# TAB 5 — GOVERNANCE & AUDIT TRAIL
# ============================================================

with tab5:

    st.subheader(
        "📜 Governance & Audit Trail"
    )


    # --------------------------------------------------------
    # AUDIT HISTORY
    # --------------------------------------------------------

    st.markdown(
        "### Audit History"
    )


    audit_df = load_db_table(
        "audit_trail"
    )


    if not audit_df.empty:

        st.dataframe(
            audit_df,
            use_container_width=True,
            height=400,
            hide_index=True
        )


        st.download_button(
            label="📥 Download Audit History",

            data=(
                audit_df
                .to_csv(index=False)
                .encode("utf-8")
            ),

            file_name="EWS_Audit_Trail.csv",

            mime="text/csv"
        )


    else:

        st.info(
            "No audit logs recorded yet."
        )


    st.divider()


    # --------------------------------------------------------
    # DATASET INFORMATION
    # --------------------------------------------------------

    st.markdown(
        "### Dataset Information"
    )


    info1, info2, info3, info4 = (
        st.columns(4)
    )


    with info1:

        st.metric(
            "Synthetic Borrowers",
            (
                len(borrower_df)
                if not borrower_df.empty
                else 0
            )
        )


    with info2:

        st.metric(
            "EWS Records",
            len(ews_df)
        )


    with info3:

        st.metric(
            "Credit Monitoring Records",
            len(cm_df)
        )


    with info4:

        st.metric(
            "EWS Alerts",
            (
                len(alerts_df)
                if not alerts_df.empty
                else 0
            )
        )


    # --------------------------------------------------------
    # PLAYBOOK STATUS
    # --------------------------------------------------------

    st.markdown(
        "### Functional Logic Playbook Status"
    )


    playbook_status = pd.DataFrame(
        {
            "Playbook": [
                "EWS Functional Logic",
                "Credit Monitoring Functional Logic"
            ],

            "Records Loaded": [
                len(ews_playbook_df),
                len(cm_playbook_df)
            ],

            "Status": [
                (
                    "Available"
                    if not ews_playbook_df.empty
                    else "Not Loaded"
                ),

                (
                    "Available"
                    if not cm_playbook_df.empty
                    else "Not Loaded"
                )
            ]
        }
    )


    st.dataframe(
        playbook_status,
        use_container_width=True,
        hide_index=True
    )


    # --------------------------------------------------------
    # FILE STATUS
    # --------------------------------------------------------

    st.markdown(
        "### Data File Status"
    )


    file_status = pd.DataFrame(
        {
            "File": [

                "Borrower Master",

                "EWS Raw Inputs",

                "EWS Results",

                "Credit Monitoring Raw",

                "Credit Monitoring Results",

                "EWS Alerts",

                "Quarterly Metric Deterioration"
            ],

            "Status": [

                (
                    "Available"
                    if BORROWER_FILE.exists()
                    else "Missing"
                ),

                (
                    "Available"
                    if EWS_RAW_FILE.exists()
                    else "Missing"
                ),

                (
                    "Available"
                    if EWS_FILE.exists()
                    else "Missing"
                ),

                (
                    "Available"
                    if CM_RAW_FILE.exists()
                    else "Missing"
                ),

                (
                    "Available"
                    if CM_FILE.exists()
                    else "Missing"
                ),

                (
                    "Available"
                    if ALERT_FILE.exists()
                    else "Missing"
                ),

                (
                    "Available"
                    if TREND_FILE.exists()
                    else "Missing"
                )
            ]
        }
    )


    st.dataframe(
        file_status,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI EWS & Credit Monitoring System | "
    "Synthetic Corporate Borrower Dataset | "
    "Human-in-the-Loop Credit Decisioning"
)