from pathlib import Path
import sys

import pandas as pd


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = Path(
    __file__
).resolve().parent.parent

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


# ============================================================
# CONFIGURATION
# ============================================================

NUMBER_OF_BORROWERS = 200


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
    print("Creating Excel workbook...")

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
    # 6. Save CSV files
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
    # 7. Export Excel workbook
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
    # 8. Summary
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