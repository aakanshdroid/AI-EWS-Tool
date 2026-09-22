from faker import Faker
import numpy as np
import pandas as pd
import random


fake = Faker("en_IN")

SEED = 42

random.seed(SEED)
np.random.seed(SEED)
Faker.seed(SEED)


# ============================================================
# CORPORATE BORROWER GENERATOR
# ============================================================

class CorporateBorrowerGenerator:

    def __init__(self, n=200):

        self.n = n

        self.sectors = [
            "Manufacturing",
            "Steel",
            "Textiles",
            "Engineering",
            "Chemicals",
            "Pharmaceuticals",
            "Auto Components",
            "Food Processing",
            "Infrastructure",
            "Power",
            "Renewable Energy",
            "Construction",
            "Trading",
            "Logistics"
        ]

        self.cities = [
            "Mumbai",
            "Delhi",
            "Pune",
            "Bengaluru",
            "Chennai",
            "Hyderabad",
            "Ahmedabad",
            "Kolkata",
            "Coimbatore",
            "Jaipur",
            "Surat",
            "Vadodara",
            "Noida",
            "Gurugram"
        ]

        self.ratings = [
            "AAA",
            "AA+",
            "AA",
            "AA-",
            "A+",
            "A",
            "A-",
            "BBB+",
            "BBB",
            "BBB-",
            "BB",
            "B"
        ]

    # ========================================================
    # RISK PROFILE
    # ========================================================

    def generate_risk_profile(self):

        # Distribution intentionally creates
        # enough stressed observations for EWS testing.

       return random.choices(
    [
        "Healthy",
        "Watch",
        "Stressed",
        "Critical"
    ],
    weights=[
        60,
        25,
        12,
        3
    ],
    k=1
)[0]

    # ========================================================
    # BORROWER
    # ========================================================

    def generate_borrower(self, i):

        risk_profile = (
            self.generate_risk_profile()
        )

        sector = random.choice(
            self.sectors
        )

        turnover = np.random.lognormal(
            mean=5.2,
            sigma=1.0
        )

        turnover = max(
            50,
            min(turnover, 5000)
        )

        debt = turnover * random.uniform(
            0.15,
            0.75
        )

        tnw = turnover * random.uniform(
            0.15,
            0.50
        )

        sanctioned_limit = debt * random.uniform(
            0.8,
            1.3
        )

        if risk_profile == "Healthy":

            rating = random.choice(
                ["AAA", "AA+", "AA", "AA-",
                 "A+", "A"]
            )

        elif risk_profile == "Watch":

            rating = random.choice(
                ["A-", "BBB+", "BBB"]
            )

        elif risk_profile == "Stressed":

            rating = random.choice(
                ["BBB-", "BB"]
            )

        else:

            rating = random.choice(
                ["B", "BB"]
            )

        return {

            "Borrower_ID":
                f"BORR-{i:04d}",

            "Borrower_Name":
                fake.company(),

            "CIN":
                self.fake_cin(),

            "PAN":
                self.fake_pan(),

            "Sector":
                sector,

            "City":
                random.choice(self.cities),

            "Risk_Profile":
                risk_profile,

            "External_Rating":
                rating,

            "Sanctioned_Limit_Cr":
                round(sanctioned_limit, 2),

            "Annual_Turnover_Cr":
                round(turnover, 2),

            "Total_Debt_Cr":
                round(debt, 2),

            "TNW_Cr":
                round(tnw, 2),

            "Promoter_Holding_Pct":
                round(
                    random.uniform(35, 85),
                    2
                )
        }

    # ========================================================
    # CIN
    # ========================================================

    @staticmethod
    def fake_cin():

        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

        return (
            random.choice(letters)
            + random.choice(letters)
            + random.choice(letters)
            + random.choice(letters)
            + random.choice(letters)
            + random.choice(letters)
            + random.choice(letters)
            + random.choice(letters)
            + "L"
            + random.choice(letters)
            + random.choice(letters)
            + random.choice(letters)
            + random.choice(letters)
            + random.choice(letters)
            + random.choice(letters)
            + random.choice(letters)
            + random.choice(letters)
            + str(random.randint(100000, 999999))
        )

    # ========================================================
    # PAN
    # ========================================================

    @staticmethod
    def fake_pan():

        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

        return (
            "".join(
                random.choice(letters)
                for _ in range(5)
            )
            + str(
                random.randint(
                    1000,
                    9999
                )
            )
            + random.choice(letters)
        )

    # ========================================================
    # GENERATE MASTER
    # ========================================================

    def generate_master(self):

        records = []

        for i in range(
            1,
            self.n + 1
        ):

            records.append(
                self.generate_borrower(i)
            )

        return pd.DataFrame(records)

    # ========================================================
    # GENERATE EWS INPUTS
    # ========================================================

    def generate_ews(self, master):

        records = []

        for _, borrower in master.iterrows():

            profile = borrower[
                "Risk_Profile"
            ]

            values = self._ews_values(
                profile,
                borrower
            )

            values[
                "Borrower_ID"
            ] = borrower[
                "Borrower_ID"
            ]

            records.append(values)

        return pd.DataFrame(records)

    # ========================================================
    # EWS VALUES
    # ========================================================

    def _ews_values(
        self,
        profile,
        borrower
    ):

        if profile == "Healthy":

            severity = 0.15

        elif profile == "Watch":

            severity = 0.35

        elif profile == "Stressed":

            severity = 0.65

        else:

            severity = 0.90

        def pct(base, spread=10):

            value = (
                base
                + severity * spread
                + np.random.normal(
                    0,
                    spread / 4
                )
            )

            return round(
                max(0, value),
                2
            )

        return {

            # Liquidity
            "bank_utilization_pct":
                round(
                    min(
                        100,
                        45
                        + severity * 50
                        + np.random.normal(0, 5)
                    ),
                    2
                ),

            "adhoc_limit_requests":
                np.random.poisson(
                    severity * 3
                ),

            "credit_limit_reduction_pct":
                pct(0, 20),

            # Repayment
            "payment_defaults":
                np.random.poisson(
                    severity * 2
                ),

            "non_core_repayment_pct":
                pct(2, 35),

            # Operations
            "stock_variance_pct":
                pct(2, 20),

            "sales_change_pct":
                round(
                    -severity * 30
                    + np.random.normal(0, 7),
                    2
                ),

            "ebitda_margin_change_pct":
                round(
                    -severity * 8
                    + np.random.normal(0, 2),
                    2
                ),

            "debtor_days_change":
                round(
                    severity * 45
                    + np.random.normal(0, 8),
                    2
                ),

            "inventory_days_change":
                round(
                    severity * 35
                    + np.random.normal(0, 8),
                    2
                ),

            "creditor_days_change":
                round(
                    severity * 40
                    + np.random.normal(0, 8),
                    2
                ),

            "provision_change_pct":
                pct(2, 50),

            "cma_variance_pct":
                pct(3, 35),

            "unsecured_loan_change_pct":
                pct(2, 40),

            "finance_cost_growth_gap_pct":
                pct(2, 30),

            # Banking events
            "lc_events":
                np.random.poisson(
                    severity * 2
                ),

            "bg_events":
                np.random.poisson(
                    severity * 2
                ),

            "rating_downgrade_notches":
                np.random.poisson(
                    severity * 1.5
                ),

            "financial_performance_change_pct":
                round(
                    -severity * 25
                    + np.random.normal(0, 5),
                    2
                ),

            # Governance
            "auditor_change":
                random.random()
                < severity * 0.15,

            "management_change":
                random.random()
                < severity * 0.20,

            "promoter_pledge_pct":
                round(
                    severity * 60
                    + np.random.normal(0, 5),
                    2
                ),

            "promoter_holding_decline_pct":
                pct(1, 20),

            "related_party_change_pct":
                pct(3, 30),

            "group_stress":
                random.random()
                < severity * 0.30,

            # Compliance
            "statutory_delays":
                np.random.poisson(
                    severity * 2
                ),

            "regulatory_event":
                random.random()
                < severity * 0.12,

            "litigation_cases":
                np.random.poisson(
                    severity * 2
                ),

            "business_model_change":
                random.random()
                < severity * 0.15,

            # External
            "sector_growth_gap_pct":
                pct(2, 25),

            "news_severity":
                min(
                    5,
                    int(
                        np.random.poisson(
                            severity * 2
                        )
                    )
                ),

            "complaint_severity":
                min(
                    5,
                    int(
                        np.random.poisson(
                            severity * 2
                        )
                    )
                ),

            "workforce_disruption_days":
                int(
                    np.random.poisson(
                        severity * 8
                    )
                ),

            # Operations
            "capacity_utilization_pct":
                round(
                    90
                    - severity * 45
                    + np.random.normal(0, 5),
                    2
                ),

            "site_visit_severity":
                min(
                    5,
                    int(
                        np.random.poisson(
                            severity * 2
                        )
                    )
                ),

            "round_tripping":
                random.random()
                < severity * 0.08,

            # ESG
            "esg_severity":
                min(
                    5,
                    int(
                        np.random.poisson(
                            severity * 2
                        )
                    )
                ),

            "carbon_emission_change_pct":
                pct(2, 30),

            # Financial reporting
            "depreciation_change_pct":
                pct(2, 20),

            "inventory_valuation_change_pct":
                pct(2, 25),

            # Ratios
            "dscr":
                round(
                    max(
                        0.3,
                        2.2
                        - severity * 1.5
                        + np.random.normal(0, 0.2)
                    ),
                    2
                ),

            "debt_to_tnw":
                round(
                    1
                    + severity * 3
                    + np.random.normal(0, 0.3),
                    2
                ),

            "current_ratio":
                round(
                    max(
                        0.5,
                        2.0
                        - severity * 1.1
                        + np.random.normal(0, 0.15)
                    ),
                    2
                )
        }

    # ========================================================
    # CREDIT MONITORING
    # ========================================================

    def generate_cm(self, master):

        records = []

        for _, borrower in master.iterrows():

            profile = borrower[
                "Risk_Profile"
            ]

            if profile == "Healthy":
                severity = 0.15

            elif profile == "Watch":
                severity = 0.35

            elif profile == "Stressed":
                severity = 0.65

            else:
                severity = 0.90

            record = {

                "Borrower_ID":
                    borrower[
                        "Borrower_ID"
                    ],

                "dpd":
                    max(
                        0,
                        int(
                            np.random.poisson(
                                severity * 25
                            )
                        )
                    ),

                "excess_over_dp_pct":
                    round(
                        severity * 35
                        + np.random.normal(0, 5),
                        2
                    ),

                "gst_turnover_variance_pct":
                    round(
                        -severity * 30
                        + np.random.normal(0, 5),
                        2
                    ),

                "negative_cfo_periods":
                    int(
                        np.random.poisson(
                            severity * 2
                        )
                    ),

                "current_ratio":
                    round(
                        max(
                            0.5,
                            2
                            - severity * 1.2
                            + np.random.normal(0, .15)
                        ),
                        2
                    ),

                "audit_status":
                    min(
                        5,
                        int(
                            np.random.poisson(
                                severity * 1.5
                            )
                        )
                    ),

                "nclt_event":
                    random.random()
                    < severity * 0.04,

                "restructuring":
                    random.random()
                    < severity * 0.08,

                "security_cover_pct":
                    round(
                        max(
                            50,
                            180
                            - severity * 100
                            + np.random.normal(0, 10)
                        ),
                        2
                    ),

                "insurance_delay_days":
                    int(
                        np.random.poisson(
                            severity * 15
                        )
                    ),

                "customer_concentration_pct":
                    round(
                        25
                        + severity * 45
                        + np.random.normal(0, 5),
                        2
                    ),

                "supplier_concentration_pct":
                    round(
                        20
                        + severity * 35
                        + np.random.normal(0, 5),
                        2
                    ),

                "sector_stress":
                    min(
                        5,
                        int(
                            np.random.poisson(
                                severity * 2
                            )
                        )
                    ),

                "commodity_exposure_pct":
                    round(
                        20
                        + severity * 50,
                        2
                    ),

                "geopolitical_exposure_pct":
                    round(
                        severity * 50,
                        2
                    ),

                "project_delay_days":
                    int(
                        np.random.poisson(
                            severity * 30
                        )
                    ),

                "project_cost_overrun_pct":
                    round(
                        severity * 30
                        + np.random.normal(0, 5),
                        2
                    ),

                "plant_shutdown_days":
                    int(
                        np.random.poisson(
                            severity * 15
                        )
                    ),

                "cyber_severity":
                    min(
                        5,
                        int(
                            np.random.poisson(
                                severity
                            )
                        )
                    ),

                "end_use_deviation_pct":
                    round(
                        severity * 25,
                        2
                    ),

                "overdue_events":
                    int(
                        np.random.poisson(
                            severity * 2
                        )
                    )
            }

            records.append(record)

        return pd.DataFrame(records)


def generate_all_data(n=200):

    generator = CorporateBorrowerGenerator(n)

    master = generator.generate_master()

    ews = generator.generate_ews(
        master
    )

    cm = generator.generate_cm(
        master
    )

    return master, ews, cm