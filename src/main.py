from pathlib import Path
import sys

import pandas as pd


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent.parent
)

# Make project root available for common/ imports
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


OUTPUT_DIR = (
    BASE_DIR
    / "output"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# IMPORT PROJECT MODULES
# ============================================================

from src.synthetic_generator import (
    generate_all_data
)

from src.scoring_engine import (
    score_ews_dataset,
    score_cm_dataset,
    generate_alerts
)

# Resend notification
from common.notifier import (
    send_critical_alert_email
)

from common.notification_tracker import (
    should_send_critical_alert,
    record_critical_notification,
    record_critical_baseline,
    notification_history_exists,
    mark_non_critical
)


# ============================================================
# CONFIGURATION
# ============================================================

NUMBER_OF_BORROWERS = 200


# ============================================================
# CRITICAL EMAIL NOTIFICATION
# ============================================================

def send_critical_notifications(ews_final):
    """
    Send Resend email notifications only for NEW Critical EWS events.

    Duplicate Critical notifications are suppressed using the
    SQLite notification history table.
    """

    print()
    print("Checking for Critical EWS triggers...")

    required_columns = [
        "Borrower_ID",
        "Overall_Normalized_Score",
        "Risk_Band",
        "Final_Status"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in ews_final.columns
    ]

    if missing_columns:
        print("⚠ Critical notification skipped.")
        print("Missing columns:", missing_columns)
        return

    # --------------------------------------------------------
    # Identify current Critical borrowers
    # --------------------------------------------------------

    critical_mask = (
        ews_final["Final_Status"]
        .astype(str)
        .str.strip()
        .str.lower()
        .eq("critical")
    )

    critical_borrowers = ews_final.loc[critical_mask]

    # --------------------------------------------------------
    # Mark borrowers who are no longer Critical as inactive
    # --------------------------------------------------------

    current_critical_ids = (
        critical_borrowers["Borrower_ID"]
        .dropna()
        .astype(str)
        .tolist()
    )

    mark_non_critical(current_critical_ids)

    # --------------------------------------------------------
    # No Critical trigger
    # --------------------------------------------------------

    if critical_borrowers.empty:
        print("✓ No Critical EWS triggers detected.")
        return

    # --------------------------------------------------------
    # FIRST-RUN BASELINE
    # --------------------------------------------------------
    # The first run after notification tracking is enabled is
    # treated as the baseline. Existing Critical borrowers are
    # recorded without sending emails. This prevents a bulk
    # email on the first run.

    if not notification_history_exists():

        print()
        print("No notification history found.")
        print("Creating initial Critical EWS baseline...")

        for _, row in critical_borrowers.iterrows():

            borrower_id = row.get(
                "Borrower_ID",
                "Unknown"
            )

            risk_score = row.get(
                "Overall_Normalized_Score",
                0
            )

            if pd.isna(risk_score):
                risk_score = 0

            risk_score = round(
                float(risk_score),
                2
            )

            risk_band = row.get(
                "Risk_Band",
                "Critical"
            )

            if pd.isna(risk_band):
                risk_band = "Critical"

            record_critical_baseline(
                borrower_id=borrower_id,
                risk_score=risk_score,
                risk_band=risk_band,
                override_flag="Baseline"
            )

        print(
            f"✓ Baseline created for "
            f"{len(critical_borrowers)} Critical borrowers."
        )

        print("✓ No emails sent during baseline creation.")

        return

    print(
        f"⚠ Critical EWS triggers detected: "
        f"{len(critical_borrowers)}"
    )

    emails_sent = 0
    emails_suppressed = 0
    emails_failed = 0

    # --------------------------------------------------------
    # Process Critical borrowers
    # --------------------------------------------------------

    for _, row in critical_borrowers.iterrows():

        borrower_id = row.get(
            "Borrower_ID",
            "Unknown"
        )

        borrower_id = str(borrower_id)

        # ----------------------------------------------------
        # Check duplicate notification
        # ----------------------------------------------------

        risk_score = row.get(
            "Overall_Normalized_Score",
            0
        )

        if pd.isna(risk_score):
            risk_score = 0

        risk_score = round(
            float(risk_score),
            2
        )

        risk_band = row.get(
            "Risk_Band",
            "Critical"
        )

        if pd.isna(risk_band):
            risk_band = "Critical"

        # ----------------------------------------------------
        # Determine override type
        # ----------------------------------------------------

        indicator_override = bool(
            row.get(
                "Critical_Indicator_Override",
                False
            )
        )

        combination_override = bool(
            row.get(
                "Critical_Combination_Override",
                False
            )
        )

        if (
            indicator_override
            and combination_override
        ):
            override_flag = (
                "Critical Indicator Override + "
                "Critical Combination Override"
            )

        elif indicator_override:
            override_flag = (
                "Critical Indicator Override"
            )

        elif combination_override:
            override_flag = (
                "Critical Combination Override"
            )

        else:
            override_flag = (
                "Critical Final Status"
            )

        # ----------------------------------------------------
        # Check notification history
        # ----------------------------------------------------

        should_send = should_send_critical_alert(
            borrower_id=borrower_id,
            risk_score=risk_score,
            risk_band=risk_band,
            override_flag=override_flag
        )

        if not should_send:

            emails_suppressed += 1

            print(
                f"↳ Duplicate Critical alert suppressed "
                f"for {borrower_id}"
            )

            continue

        # ----------------------------------------------------
        # Borrower name
        # ----------------------------------------------------

        borrower_name = row.get(
            "Borrower_Name",
            borrower_id
        )

        if pd.isna(borrower_name):
            borrower_name = borrower_id

        # ----------------------------------------------------
        # Account number
        # ----------------------------------------------------

        account_number = None

        possible_account_columns = [
            "Account_Number",
            "Account_No",
            "AccountNo",
            "Account"
        ]

        for column in possible_account_columns:

            if column in row.index:

                value = row[column]

                if pd.notna(value):

                    account_number = value
                    break

        if account_number is None:
            account_number = borrower_id

        # ----------------------------------------------------
        # Send email
        # ----------------------------------------------------

        print()
        print(
            f"Sending NEW Critical Alert for "
            f"{borrower_name} "
            f"({borrower_id})..."
        )

        success = send_critical_alert_email(
            account_number=account_number,
            borrower_name=borrower_name,
            risk_score=risk_score,
            risk_band=risk_band,
            override_flag=override_flag
        )

        if success:

            # Record only after successful email
            record_critical_notification(
                borrower_id=borrower_id,
                risk_score=risk_score,
                risk_band=risk_band,
                override_flag=override_flag
            )

            emails_sent += 1

            print(
                f"✓ Critical email sent and recorded "
                f"for {borrower_name}"
            )

        else:

            emails_failed += 1

            print(
                f"✗ Critical email failed "
                f"for {borrower_name}"
            )

    # --------------------------------------------------------
    # Notification summary
    # --------------------------------------------------------

    print()
    print(
        "Critical Email Notification Summary"
    )

    print(
        f"Critical borrowers : "
        f"{len(critical_borrowers)}"
    )

    print(
        f"Emails sent        : "
        f"{emails_sent}"
    )

    print(
        f"Duplicates blocked : "
        f"{emails_suppressed}"
    )

    print(
        f"Emails failed      : "
        f"{emails_failed}"
    )

# ============================================================
# EXPORT SYNTHETIC DATA TO EXCEL
# ============================================================

def export_to_excel(
    borrower_master,
    ews_raw,
    ews_results,
    cm_raw,
    cm_results,
    alerts
):

    excel_path = (
        OUTPUT_DIR
        / "AI_EWS_Synthetic_Data_200.xlsx"
    )

    print()
    print(
        "Creating Excel workbook..."
    )

    with pd.ExcelWriter(
        excel_path,
        engine="openpyxl"
    ) as writer:

        # ----------------------------------------------------
        # Sheet 1 - Borrower Master
        # ----------------------------------------------------

        borrower_master.to_excel(
            writer,
            sheet_name="Borrower_Master",
            index=False
        )

        # ----------------------------------------------------
        # Sheet 2 - EWS Raw Data
        # ----------------------------------------------------

        ews_raw.to_excel(
            writer,
            sheet_name="EWS_Raw_Data",
            index=False
        )

        # ----------------------------------------------------
        # Sheet 3 - EWS Results
        # ----------------------------------------------------

        ews_results.to_excel(
            writer,
            sheet_name="EWS_Results",
            index=False
        )

        # ----------------------------------------------------
        # Sheet 4 - Credit Monitoring Raw
        # ----------------------------------------------------

        cm_raw.to_excel(
            writer,
            sheet_name="CM_Raw_Data",
            index=False
        )

        # ----------------------------------------------------
        # Sheet 5 - Credit Monitoring Results
        # ----------------------------------------------------

        cm_results.to_excel(
            writer,
            sheet_name="CM_Results",
            index=False
        )

        # ----------------------------------------------------
        # Sheet 6 - Alerts
        # ----------------------------------------------------

        alerts.to_excel(
            writer,
            sheet_name="EWS_Alerts",
            index=False
        )

        # ----------------------------------------------------
        # Formatting
        # ----------------------------------------------------

        workbook = writer.book

        for worksheet in workbook.worksheets:

            # Freeze first row
            worksheet.freeze_panes = "A2"

            # Auto filter
            worksheet.auto_filter.ref = (
                worksheet.dimensions
            )

            # Set column widths
            for column in worksheet.columns:

                max_length = 0

                column_letter = (
                    column[0].column_letter
                )

                for cell in column:

                    try:

                        cell_length = len(
                            str(cell.value)
                        )

                        if cell_length > max_length:
                            max_length = cell_length

                    except Exception:
                        pass

                worksheet.column_dimensions[
                    column_letter
                ].width = min(
                    max(max_length + 2, 10),
                    35
                )

    print(
        f"✓ Excel workbook created:\n"
        f"{excel_path}"
    )

    return excel_path


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 75)

    print(
        "AI EWS + CREDIT MONITORING"
    )

    print(
        "STRUCTURED SYNTHETIC CORPORATE BORROWER GENERATOR"
    )

    print("=" * 75)

    print()

    print(
        f"Generating {NUMBER_OF_BORROWERS} "
        "corporate borrowers..."
    )

    # --------------------------------------------------------
    # 1. Generate structured borrower data
    # --------------------------------------------------------

    (
        borrower_master,
        ews_raw,
        cm_raw
    ) = generate_all_data(
        n=NUMBER_OF_BORROWERS
    )

    print(
        "✓ Borrower master generated"
    )

    print(
        "✓ EWS indicators generated"
    )

    print(
        "✓ Credit monitoring indicators generated"
    )

    # --------------------------------------------------------
    # 2. Score EWS
    # --------------------------------------------------------

    print()

    print(
        "Calculating EWS scores..."
    )

    ews_results = score_ews_dataset(
        ews_raw
    )

    print(
        "✓ EWS scoring completed"
    )

    # --------------------------------------------------------
    # 3. Score Credit Monitoring
    # --------------------------------------------------------

    print(
        "Calculating Credit Monitoring scores..."
    )

    cm_results = score_cm_dataset(
        cm_raw
    )

    print(
        "✓ Credit Monitoring scoring completed"
    )

    # --------------------------------------------------------
    # 4. Generate alerts
    # --------------------------------------------------------

    print(
        "Generating alerts..."
    )

    alerts = generate_alerts(
        ews_results
    )

    print(
        "✓ Alert generation completed"
    )

    # --------------------------------------------------------
    # 5. Merge master information
    # --------------------------------------------------------

    ews_final = borrower_master.merge(
        ews_results,
        on="Borrower_ID",
        how="left"
    )

    cm_final = borrower_master.merge(
        cm_results,
        on="Borrower_ID",
        how="left"
    )

    # --------------------------------------------------------
    # 6. SEND CRITICAL EMAIL NOTIFICATIONS
    # --------------------------------------------------------

    send_critical_notifications(
        ews_final
    )

    # --------------------------------------------------------
    # 7. Save CSV files
    # --------------------------------------------------------

    borrower_master.to_csv(
        OUTPUT_DIR
        / "borrower_master_200.csv",
        index=False
    )

    ews_raw.to_csv(
        OUTPUT_DIR
        / "ews_raw_inputs_200.csv",
        index=False
    )

    cm_raw.to_csv(
        OUTPUT_DIR
        / "credit_monitoring_raw_inputs_200.csv",
        index=False
    )

    ews_final.to_csv(
        OUTPUT_DIR
        / "ews_results_200.csv",
        index=False
    )

    cm_final.to_csv(
        OUTPUT_DIR
        / "credit_monitoring_results_200.csv",
        index=False
    )

    alerts.to_csv(
        OUTPUT_DIR
        / "ews_alerts.csv",
        index=False
    )

    # --------------------------------------------------------
    # 8. Export Excel workbook
    # --------------------------------------------------------

    export_to_excel(
        borrower_master=borrower_master,
        ews_raw=ews_raw,
        ews_results=ews_final,
        cm_raw=cm_raw,
        cm_results=cm_final,
        alerts=alerts
    )

    # --------------------------------------------------------
    # 9. Summary
    # --------------------------------------------------------

    print()

    print("=" * 75)
    print("GENERATION COMPLETE")
    print("=" * 75)

    print()

    print(
        "Borrowers:",
        len(borrower_master)
    )

    print()

    print(
        "EWS Risk Distribution:"
    )

    print(
        ews_final[
            "Final_Status"
        ]
        .value_counts()
        .to_string()
    )

    print()

    print(
        "Credit Monitoring Distribution:"
    )

    print(
        cm_final[
            "Final_Status"
        ]
        .value_counts()
        .to_string()
    )

    print()

    print(
        "Total alerts:",
        len(alerts)
    )

    print()

    print(
        "Output location:"
    )

    print(
        OUTPUT_DIR
    )

    print()

    print("=" * 75)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()