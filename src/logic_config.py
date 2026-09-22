# ============================================================
# AI EWS + CREDIT MONITORING
# LOGIC CONFIGURATION
# ============================================================

# ------------------------------------------------------------
# EWS INDICATOR MASTER
# ------------------------------------------------------------

EWS_INDICATORS = {

    "EWS-001": {
        "name": "High Bank Utilization",
        "category": "Liquidity",
        "type": "numeric",
        "field": "bank_utilization_pct",
        "max_score": 100,
        "critical": False
    },

    "EWS-002": {
        "name": "Adhoc / Temporary Limit Requests",
        "category": "Banking Behaviour",
        "type": "count",
        "field": "adhoc_limit_requests",
        "max_score": 100,
        "critical": False
    },

    "EWS-003": {
        "name": "Credit Facility Reduction / Decline",
        "category": "Banking Behaviour",
        "type": "percentage",
        "field": "credit_limit_reduction_pct",
        "max_score": 100,
        "critical": False
    },

    "EWS-004": {
        "name": "Payment Defaults",
        "category": "Repayment Behaviour",
        "type": "count",
        "field": "payment_defaults",
        "max_score": 100,
        "critical": True
    },

    "EWS-005": {
        "name": "Non-Core Repayment Source",
        "category": "Repayment Behaviour",
        "type": "percentage",
        "field": "non_core_repayment_pct",
        "max_score": 100,
        "critical": True
    },

    "EWS-006": {
        "name": "Stock / Inventory Variance",
        "category": "Operations",
        "type": "percentage",
        "field": "stock_variance_pct",
        "max_score": 100,
        "critical": False
    },

    "EWS-007": {
        "name": "Sales Decline",
        "category": "Financial Performance",
        "type": "percentage",
        "field": "sales_change_pct",
        "max_score": 100,
        "critical": False
    },

    "EWS-008": {
        "name": "EBITDA Margin Deterioration",
        "category": "Financial Performance",
        "type": "percentage",
        "field": "ebitda_margin_change_pct",
        "max_score": 100,
        "critical": False
    },

    "EWS-009": {
        "name": "Increase in Debtor Days",
        "category": "Working Capital",
        "type": "numeric",
        "field": "debtor_days_change",
        "max_score": 100,
        "critical": True
    },

    "EWS-010": {
        "name": "Increase in Inventory Days",
        "category": "Working Capital",
        "type": "numeric",
        "field": "inventory_days_change",
        "max_score": 100,
        "critical": False
    },

    "EWS-011": {
        "name": "Increase in Creditor Days",
        "category": "Working Capital",
        "type": "numeric",
        "field": "creditor_days_change",
        "max_score": 100,
        "critical": True
    },

    "EWS-012": {
        "name": "Increase in Provisions",
        "category": "Financial Performance",
        "type": "percentage",
        "field": "provision_change_pct",
        "max_score": 100,
        "critical": True
    },

    "EWS-013": {
        "name": "CMA / Projected vs Actual Variance",
        "category": "Financial Monitoring",
        "type": "percentage",
        "field": "cma_variance_pct",
        "max_score": 100,
        "critical": False
    },

    "EWS-014": {
        "name": "Increase in Unsecured Loans",
        "category": "Leverage",
        "type": "percentage",
        "field": "unsecured_loan_change_pct",
        "max_score": 100,
        "critical": True
    },

    "EWS-015": {
        "name": "Finance Cost Growth Gap",
        "category": "Financial Performance",
        "type": "percentage",
        "field": "finance_cost_growth_gap_pct",
        "max_score": 100,
        "critical": False
    },

    "EWS-016": {
        "name": "LC Events",
        "category": "Trade Finance",
        "type": "count",
        "field": "lc_events",
        "max_score": 100,
        "critical": False
    },

    "EWS-017": {
        "name": "BG Events",
        "category": "Trade Finance",
        "type": "count",
        "field": "bg_events",
        "max_score": 100,
        "critical": False
    },

    "EWS-018": {
        "name": "External Rating Downgrade",
        "category": "Rating",
        "type": "count",
        "field": "rating_downgrade_notches",
        "max_score": 100,
        "critical": True
    },

    "EWS-019": {
        "name": "Financial Year Change / Deterioration",
        "category": "Financial Performance",
        "type": "percentage",
        "field": "financial_performance_change_pct",
        "max_score": 100,
        "critical": False
    },

    "EWS-020": {
        "name": "Auditor Change",
        "category": "Governance",
        "type": "boolean",
        "field": "auditor_change",
        "max_score": 100,
        "critical": False
    },

    "EWS-021": {
        "name": "Management Change",
        "category": "Governance",
        "type": "boolean",
        "field": "management_change",
        "max_score": 100,
        "critical": False
    },

    "EWS-022": {
        "name": "Promoter Pledge",
        "category": "Promoter",
        "type": "percentage",
        "field": "promoter_pledge_pct",
        "max_score": 100,
        "critical": True
    },

    "EWS-023": {
        "name": "Promoter Holding Decline",
        "category": "Promoter",
        "type": "percentage",
        "field": "promoter_holding_decline_pct",
        "max_score": 100,
        "critical": False
    },

    "EWS-024": {
        "name": "Related Party Transaction Increase",
        "category": "Governance",
        "type": "percentage",
        "field": "related_party_change_pct",
        "max_score": 100,
        "critical": False
    },

    "EWS-025": {
        "name": "Group Company Stress",
        "category": "Group Risk",
        "type": "boolean",
        "field": "group_stress",
        "max_score": 100,
        "critical": False
    },

    "EWS-026": {
        "name": "Statutory Payment Delay",
        "category": "Compliance",
        "type": "count",
        "field": "statutory_delays",
        "max_score": 100,
        "critical": False
    },

    "EWS-027": {
        "name": "Regulatory Event",
        "category": "Compliance",
        "type": "boolean",
        "field": "regulatory_event",
        "max_score": 100,
        "critical": True
    },

    "EWS-028": {
        "name": "Litigation",
        "category": "Legal",
        "type": "count",
        "field": "litigation_cases",
        "max_score": 100,
        "critical": True
    },

    "EWS-029": {
        "name": "Business Model Change",
        "category": "Business Risk",
        "type": "boolean",
        "field": "business_model_change",
        "max_score": 100,
        "critical": False
    },

    "EWS-030": {
        "name": "Sector Growth Gap",
        "category": "Sector Risk",
        "type": "percentage",
        "field": "sector_growth_gap_pct",
        "max_score": 100,
        "critical": False
    },

    "EWS-031": {
        "name": "Adverse News",
        "category": "External Risk",
        "type": "severity",
        "field": "news_severity",
        "max_score": 100,
        "critical": False
    },

    "EWS-032": {
        "name": "Customer Complaint Severity",
        "category": "Operational Risk",
        "type": "severity",
        "field": "complaint_severity",
        "max_score": 100,
        "critical": False
    },

    "EWS-033": {
        "name": "Workforce Disruption",
        "category": "Operational Risk",
        "type": "count",
        "field": "workforce_disruption_days",
        "max_score": 100,
        "critical": False
    },

    "EWS-034": {
        "name": "Capacity Utilization",
        "category": "Operations",
        "type": "percentage",
        "field": "capacity_utilization_pct",
        "max_score": 100,
        "critical": False
    },

    "EWS-035": {
        "name": "Adverse Site Visit",
        "category": "Operations",
        "type": "severity",
        "field": "site_visit_severity",
        "max_score": 100,
        "critical": True
    },

    "EWS-036": {
        "name": "Round Tripping",
        "category": "Fraud Risk",
        "type": "boolean",
        "field": "round_tripping",
        "max_score": 100,
        "critical": True
    },

    "EWS-037": {
        "name": "ESG Action / Event",
        "category": "ESG",
        "type": "severity",
        "field": "esg_severity",
        "max_score": 100,
        "critical": False
    },

    "EWS-038": {
        "name": "Carbon Emission Increase",
        "category": "Climate Risk",
        "type": "percentage",
        "field": "carbon_emission_change_pct",
        "max_score": 100,
        "critical": False
    },

    "EWS-039": {
        "name": "Depreciation Change",
        "category": "Financial Performance",
        "type": "percentage",
        "field": "depreciation_change_pct",
        "max_score": 100,
        "critical": False
    },

    "EWS-040": {
        "name": "Inventory Valuation Change",
        "category": "Financial Reporting",
        "type": "percentage",
        "field": "inventory_valuation_change_pct",
        "max_score": 100,
        "critical": False
    },

    "EWS-041": {
        "name": "DSCR",
        "category": "Debt Servicing",
        "type": "ratio",
        "field": "dscr",
        "max_score": 100,
        "critical": True
    },

    "EWS-042": {
        "name": "Leverage",
        "category": "Leverage",
        "type": "ratio",
        "field": "debt_to_tnw",
        "max_score": 100,
        "critical": False
    },

    "EWS-043": {
        "name": "Current Ratio",
        "category": "Liquidity",
        "type": "ratio",
        "field": "current_ratio",
        "max_score": 100,
        "critical": False
    }
}


# ------------------------------------------------------------
# CREDIT MONITORING
# ------------------------------------------------------------

CM_INDICATORS = {

    "CM-001": {
        "name": "Days Past Due",
        "category": "Repayment",
        "field": "dpd",
        "type": "days"
    },

    "CM-002": {
        "name": "Excess Over Drawing Power",
        "category": "Banking",
        "field": "excess_over_dp_pct",
        "type": "percentage"
    },

    "CM-003": {
        "name": "GST Turnover Variance",
        "category": "Business Performance",
        "field": "gst_turnover_variance_pct",
        "type": "percentage"
    },

    "CM-004": {
        "name": "Negative CFO Periods",
        "category": "Cash Flow",
        "field": "negative_cfo_periods",
        "type": "count"
    },

    "CM-005": {
        "name": "Current Ratio",
        "category": "Liquidity",
        "field": "current_ratio",
        "type": "ratio"
    },

    "CM-006": {
        "name": "Audit Status",
        "category": "Governance",
        "field": "audit_status",
        "type": "severity"
    },

    "CM-007": {
        "name": "NCLT Event",
        "category": "Legal",
        "field": "nclt_event",
        "type": "boolean"
    },

    "CM-008": {
        "name": "Restructuring",
        "category": "Credit",
        "field": "restructuring",
        "type": "boolean"
    },

    "CM-009": {
        "name": "Security Cover",
        "category": "Security",
        "field": "security_cover_pct",
        "type": "percentage"
    },

    "CM-010": {
        "name": "Insurance Coverage Delay",
        "category": "Security",
        "field": "insurance_delay_days",
        "type": "days"
    },

    "CM-011": {
        "name": "Customer Concentration",
        "category": "Concentration",
        "field": "customer_concentration_pct",
        "type": "percentage"
    },

    "CM-012": {
        "name": "Supplier Concentration",
        "category": "Concentration",
        "field": "supplier_concentration_pct",
        "type": "percentage"
    },

    "CM-013": {
        "name": "Sector Stress",
        "category": "Sector Risk",
        "field": "sector_stress",
        "type": "severity"
    },

    "CM-014": {
        "name": "Commodity Exposure",
        "category": "Market Risk",
        "field": "commodity_exposure_pct",
        "type": "percentage"
    },

    "CM-015": {
        "name": "Geopolitical Exposure",
        "category": "External Risk",
        "field": "geopolitical_exposure_pct",
        "type": "percentage"
    },

    "CM-016": {
        "name": "Project Schedule Delay",
        "category": "Project Risk",
        "field": "project_delay_days",
        "type": "days"
    },

    "CM-017": {
        "name": "Project Cost Overrun",
        "category": "Project Risk",
        "field": "project_cost_overrun_pct",
        "type": "percentage"
    },

    "CM-018": {
        "name": "Plant Shutdown",
        "category": "Operations",
        "field": "plant_shutdown_days",
        "type": "days"
    },

    "CM-019": {
        "name": "Cyber Incident",
        "category": "Operational Risk",
        "field": "cyber_severity",
        "type": "severity"
    },

    "CM-020": {
        "name": "End Use Deviation",
        "category": "Monitoring",
        "field": "end_use_deviation_pct",
        "type": "percentage"
    },

    "CM-021": {
        "name": "Overdue Events",
        "category": "Repayment",
        "field": "overdue_events",
        "type": "count"
    }
}


# ------------------------------------------------------------
# RISK BANDS
# ------------------------------------------------------------

RISK_BANDS = [
    (0, 19, "Green"),
    (20, 39, "Yellow"),
    (40, 59, "Amber"),
    (60, 79, "Red"),
    (80, 100, "Critical")
]


# ------------------------------------------------------------
# CRITICAL COMBINATIONS
# ------------------------------------------------------------

CRITICAL_COMBINATIONS = [

    (
        "EWS-004",
        "EWS-011",
        "Payment defaults + stretched creditors"
    ),

    (
        "EWS-005",
        "EWS-014",
        "Non-core repayment source + rising unsecured loans"
    ),

    (
        "EWS-009",
        "EWS-012",
        "Stretched debtors + rising provisions"
    )
]