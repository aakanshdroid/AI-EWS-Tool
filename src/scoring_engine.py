import pandas as pd
import numpy as np

from src.logic_config import (
    EWS_INDICATORS,
    CM_INDICATORS,
    RISK_BANDS,
    CRITICAL_COMBINATIONS
)


# ============================================================
# GENERIC RISK SCORE
# ============================================================

def score_numeric(
    value,
    thresholds
):

    """
    thresholds:
        [
            (upper_limit, score),
            ...
        ]
    """

    if value is None:
        return 0

    for upper, score in thresholds:

        if value <= upper:
            return score

    return 100


# ============================================================
# EWS SCORING
# ============================================================

def calculate_ews_indicator_score(
    indicator,
    value
):

    # --------------------------------------------------------
    # Percentage indicators
    # --------------------------------------------------------

    percentage_rules = {

        "EWS-001": [
            (50, 0),
            (70, 25),
            (85, 50),
            (95, 75),
            (100, 100)
        ],

        "EWS-003": [
            (5, 0),
            (10, 25),
            (20, 50),
            (30, 75),
            (float("inf"), 100)
        ],

        "EWS-005": [
            (5, 0),
            (15, 25),
            (30, 50),
            (50, 75),
            (float("inf"), 100)
        ],

        "EWS-006": [
            (5, 0),
            (10, 25),
            (20, 50),
            (30, 75),
            (float("inf"), 100)
        ],

        "EWS-008": [
            (0, 0),
            (2, 25),
            (5, 50),
            (8, 75),
            (float("inf"), 100)
        ],

        "EWS-012": [
            (5, 0),
            (15, 25),
            (30, 50),
            (50, 75),
            (float("inf"), 100)
        ],

        "EWS-014": [
            (5, 0),
            (15, 25),
            (30, 50),
            (50, 75),
            (float("inf"), 100)
        ],

        "EWS-015": [
            (5, 0),
            (10, 25),
            (20, 50),
            (30, 75),
            (float("inf"), 100)
        ],

        "EWS-022": [
            (5, 0),
            (15, 25),
            (30, 50),
            (50, 75),
            (float("inf"), 100)
        ],

        "EWS-023": [
            (5, 0),
            (10, 25),
            (20, 50),
            (30, 75),
            (float("inf"), 100)
        ],

        "EWS-024": [
            (5, 0),
            (15, 25),
            (30, 50),
            (50, 75),
            (float("inf"), 100)
        ],

        "EWS-030": [
            (5, 0),
            (10, 25),
            (20, 50),
            (30, 75),
            (float("inf"), 100)
        ],

        "EWS-038": [
            (5, 0),
            (10, 25),
            (20, 50),
            (30, 75),
            (float("inf"), 100)
        ],

        "EWS-039": [
            (5, 0),
            (10, 25),
            (20, 50),
            (30, 75),
            (float("inf"), 100)
        ],

        "EWS-040": [
            (5, 0),
            (10, 25),
            (20, 50),
            (30, 75),
            (float("inf"), 100)
        ]
    }

    if indicator in percentage_rules:

        return score_numeric(
            abs(float(value)),
            percentage_rules[indicator]
        )

    # --------------------------------------------------------
    # Count indicators
    # --------------------------------------------------------

    count_rules = {

        "EWS-002": [
            (0, 0),
            (1, 25),
            (2, 50),
            (3, 75),
            (float("inf"), 100)
        ],

        "EWS-004": [
            (0, 0),
            (1, 50),
            (2, 75),
            (float("inf"), 100)
        ],

        "EWS-016": [
            (0, 0),
            (2, 25),
            (4, 50),
            (6, 75),
            (float("inf"), 100)
        ],

        "EWS-017": [
            (0, 0),
            (2, 25),
            (4, 50),
            (6, 75),
            (float("inf"), 100)
        ],

        "EWS-026": [
            (0, 0),
            (1, 25),
            (2, 50),
            (3, 75),
            (float("inf"), 100)
        ],

        "EWS-028": [
            (0, 0),
            (1, 50),
            (2, 75),
            (float("inf"), 100)
        ],

        "EWS-033": [
            (0, 0),
            (5, 25),
            (15, 50),
            (30, 75),
            (float("inf"), 100)
        ]
    }

    if indicator in count_rules:

        return score_numeric(
            float(value),
            count_rules[indicator]
        )

    # --------------------------------------------------------
    # Day-change indicators
    # --------------------------------------------------------

    day_rules = {

        "EWS-009": [
            (5, 0),
            (15, 25),
            (30, 50),
            (45, 75),
            (float("inf"), 100)
        ],

        "EWS-010": [
            (5, 0),
            (15, 25),
            (30, 50),
            (45, 75),
            (float("inf"), 100)
        ],

        "EWS-011": [
            (5, 0),
            (15, 25),
            (30, 50),
            (45, 75),
            (float("inf"), 100)
        ]
    }

    if indicator in day_rules:

        return score_numeric(
            float(value),
            day_rules[indicator]
        )

    # --------------------------------------------------------
    # Ratio indicators
    # --------------------------------------------------------

    if indicator == "EWS-041":

        # DSCR: lower is worse
        value = float(value)

        if value >= 2:
            return 0
        elif value >= 1.5:
            return 25
        elif value >= 1.2:
            return 50
        elif value >= 1:
            return 75
        else:
            return 100

    if indicator == "EWS-042":

        # Debt / TNW: higher is worse
        value = float(value)

        if value <= 1:
            return 0
        elif value <= 2:
            return 25
        elif value <= 3:
            return 50
        elif value <= 4:
            return 75
        else:
            return 100

    if indicator == "EWS-043":

        # Current ratio: lower is worse
        value = float(value)

        if value >= 2:
            return 0
        elif value >= 1.5:
            return 25
        elif value >= 1.2:
            return 50
        elif value >= 1:
            return 75
        else:
            return 100

    # --------------------------------------------------------
    # Boolean
    # --------------------------------------------------------

    if indicator in [
        "EWS-020",
        "EWS-021",
        "EWS-025",
        "EWS-027",
        "EWS-029",
        "EWS-036"
    ]:

        return 100 if bool(value) else 0

    # --------------------------------------------------------
    # Severity 0–5
    # --------------------------------------------------------

    if indicator in [
        "EWS-031",
        "EWS-032",
        "EWS-035",
        "EWS-037"
    ]:

        value = float(value)

        return min(
            100,
            value * 20
        )

    # --------------------------------------------------------
    # Rating downgrade
    # --------------------------------------------------------

    if indicator == "EWS-018":

        return min(
            100,
            float(value) * 25
        )

    # --------------------------------------------------------
    # Default
    # --------------------------------------------------------

    return 0


# ============================================================
# EWS DATASET SCORING
# ============================================================

def score_ews_dataset(
    raw_data
):

    result = raw_data[
        ["Borrower_ID"]
    ].copy()

    normalized_columns = []

    critical_columns = []

    for uid, config in EWS_INDICATORS.items():

        field = config["field"]

        raw_values = []
        scores = []
        criticals = []

        for value in raw_data[field]:

            score = calculate_ews_indicator_score(
                uid,
                value
            )

            raw_values.append(value)
            scores.append(score)

            criticals.append(
                config["critical"]
                and score >= 100
            )

        result[
            f"{uid}_Value"
        ] = raw_values

        result[
            f"{uid}_Score"
        ] = scores

        result[
            f"{uid}_Critical"
        ] = criticals

        normalized_columns.append(
            f"{uid}_Score"
        )

        critical_columns.append(
            f"{uid}_Critical"
        )

    # --------------------------------------------------------
    # Overall score
    # --------------------------------------------------------

    result[
        "Overall_Normalized_Score"
    ] = result[
        normalized_columns
    ].mean(axis=1)

    # --------------------------------------------------------
    # Critical override
    # --------------------------------------------------------

    result[
        "Critical_Indicator_Override"
    ] = result[
        critical_columns
    ].any(axis=1)

    # --------------------------------------------------------
    # Critical combinations
    # --------------------------------------------------------

    result[
        "Critical_Combination_Override"
    ] = False

    result[
        "Critical_Combination"
    ] = ""

    for uid1, uid2, description in CRITICAL_COMBINATIONS:

        score1 = result[
            f"{uid1}_Score"
        ]

        score2 = result[
            f"{uid2}_Score"
        ]

        trigger = (
            (score1 >= 20)
            &
            (score2 >= 20)
        )

        result.loc[
            trigger,
            "Critical_Combination_Override"
        ] = True

        result.loc[
            trigger,
            "Critical_Combination"
        ] = description

    # --------------------------------------------------------
    # Risk band
    # --------------------------------------------------------

    result["Risk_Band"] = result[
        "Overall_Normalized_Score"
    ].apply(
        assign_risk_band
    )

    # --------------------------------------------------------
    # Final status
    # --------------------------------------------------------

    result["Final_Status"] = result[
        "Risk_Band"
    ]

    critical = (
        result[
            "Critical_Indicator_Override"
        ]
        |
        result[
            "Critical_Combination_Override"
        ]
    )

    result.loc[
        critical,
        "Final_Status"
    ] = "Critical"

    return result


# ============================================================
# CREDIT MONITORING SCORING
# ============================================================

def calculate_cm_score(
    indicator,
    value
):

    value = float(value)

    if indicator == "CM-001":

        if value <= 0:
            return 0
        elif value <= 30:
            return 25
        elif value <= 60:
            return 50
        elif value <= 90:
            return 75
        else:
            return 100

    if indicator == "CM-002":

        return score_numeric(
            value,
            [
                (5, 0),
                (10, 25),
                (20, 50),
                (30, 75),
                (float("inf"), 100)
            ]
        )

    if indicator == "CM-003":

        return score_numeric(
            abs(value),
            [
                (5, 0),
                (10, 25),
                (20, 50),
                (30, 75),
                (float("inf"), 100)
            ]
        )

    if indicator == "CM-004":

        return score_numeric(
            value,
            [
                (0, 0),
                (1, 25),
                (2, 50),
                (3, 75),
                (float("inf"), 100)
            ]
        )

    if indicator == "CM-005":

        if value >= 2:
            return 0
        elif value >= 1.5:
            return 25
        elif value >= 1.2:
            return 50
        elif value >= 1:
            return 75
        return 100

    if indicator in [
        "CM-006",
        "CM-013",
        "CM-019"
    ]:

        return min(
            100,
            value * 20
        )

    if indicator in [
        "CM-007",
        "CM-008"
    ]:

        return 100 if bool(value) else 0

    if indicator == "CM-009":

        if value >= 150:
            return 0
        elif value >= 125:
            return 25
        elif value >= 100:
            return 50
        elif value >= 75:
            return 75
        return 100

    if indicator == "CM-010":

        return score_numeric(
            value,
            [
                (0, 0),
                (7, 25),
                (15, 50),
                (30, 75),
                (float("inf"), 100)
            ]
        )

    if indicator in [
        "CM-011",
        "CM-012",
        "CM-014",
        "CM-015",
        "CM-017",
        "CM-020"
    ]:

        return score_numeric(
            value,
            [
                (20, 0),
                (40, 25),
                (60, 50),
                (80, 75),
                (float("inf"), 100)
            ]
        )

    if indicator in [
        "CM-016",
        "CM-018",
        "CM-021"
    ]:

        return score_numeric(
            value,
            [
                (0, 0),
                (7, 25),
                (15, 50),
                (30, 75),
                (float("inf"), 100)
            ]
        )

    return 0


# ============================================================
# CM DATASET
# ============================================================

def score_cm_dataset(
    raw_data
):

    result = raw_data[
        ["Borrower_ID"]
    ].copy()

    score_columns = []

    for uid, config in CM_INDICATORS.items():

        field = config["field"]

        scores = []

        for value in raw_data[field]:

            score = calculate_cm_score(
                uid,
                value
            )

            scores.append(score)

        result[
            f"{uid}_Score"
        ] = scores

        score_columns.append(
            f"{uid}_Score"
        )

    result[
        "Overall_Normalized_Score"
    ] = result[
        score_columns
    ].mean(axis=1)

    result[
        "Risk_Band"
    ] = result[
        "Overall_Normalized_Score"
    ].apply(
        assign_risk_band
    )

    result[
        "Final_Status"
    ] = result[
        "Risk_Band"
    ]

    return result


# ============================================================
# RISK BAND
# ============================================================

def assign_risk_band(score):

    score = float(score)

    for lower, upper, band in RISK_BANDS:

        if lower <= score <= upper:

            return band

    return "Critical"


# ============================================================
# ALERT GENERATION
# ============================================================

def generate_alerts(
    ews_results
):

    alerts = []

    for _, row in ews_results.iterrows():

        borrower_id = row[
            "Borrower_ID"
        ]

        for uid, config in EWS_INDICATORS.items():

            score = row[
                f"{uid}_Score"
            ]

            if score < 40:
                continue

            if score >= 80:
                severity = "Critical"

            elif score >= 60:
                severity = "High"

            elif score >= 40:
                severity = "Medium"

            else:
                severity = "Low"

            alerts.append({

                "Borrower_ID":
                    borrower_id,

                "Indicator_ID":
                    uid,

                "Indicator_Name":
                    config["name"],

                "Category":
                    config["category"],

                "Score":
                    score,

                "Severity":
                    severity,

                "Critical_Indicator":
                    config["critical"],

                "Final_Status":
                    row[
                        "Final_Status"
                    ]
            })

        combination = row[
            "Critical_Combination"
        ]

        if combination:

            alerts.append({

                "Borrower_ID":
                    borrower_id,

                "Indicator_ID":
                    "CRITICAL-COMBO",

                "Indicator_Name":
                    combination,

                "Category":
                    "Critical Combination",

                "Score":
                    100,

                "Severity":
                    "Critical",

                "Critical_Indicator":
                    True,

                "Final_Status":
                    "Critical"
            })

    return pd.DataFrame(alerts)