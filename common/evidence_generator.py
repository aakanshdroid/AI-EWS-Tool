import pandas as pd

# Remedial Playbook & Rule Explanations
EVIDENCE_DICTIONARY = {
    "EWS-001": {
        "name": "CC/OD Utilization %",
        "formula": "(Outstanding Amount / Sanctioned Limit) * 100",
        "threshold": "> 85%",
        "category": "Liquidity Risk",
        "recommended_action": "Request updated stock/receivables statements and review quarterly cash flow projections."
    },
    "EWS-003": {
        "name": "DP / Excess Over Sanction",
        "formula": "Days Continuous Overdraw / Excess",
        "threshold": "> 30 Days",
        "category": "Default / Breach",
        "recommended_action": "Issue immediate breach advisory to Borrower and escalate to Credit Committee."
    },
    "EWS-007": {
        "name": "Cheque Bounce / NACH Failure Count",
        "formula": "Total Inward/Outward Bounces in 30 Days",
        "threshold": ">= 3 Bounces",
        "category": "Operational Cash Flow",
        "recommended_action": "Verify bank statement details and audit short-term working capital shortfall."
    }
}

def generate_evidence_pack(borrower_id, triggered_indicators):
    """
    Generates an Evidence Pack and AI Advisory recommendation for a specific borrower.
    """
    evidence_items = []
    
    for ind_id, observed_val in triggered_indicators.items():
        meta = EVIDENCE_DICTIONARY.get(ind_id, {
            "name": ind_id,
            "formula": "Standard Metric Calculation",
            "threshold": "Configured Threshold",
            "category": "General Risk",
            "recommended_action": "Review borrower financial disclosures and schedule credit assessment."
        })
        
        evidence_items.append({
            "Indicator Code": ind_id,
            "Indicator Name": meta["name"],
            "Category": meta["category"],
            "Observed Value": f"{observed_val}%" if isinstance(observed_val, (int, float)) else str(observed_val),
            "Threshold Criteria": meta["threshold"],
            "Calculation Formula": meta["formula"],
            "AI Recommended Action": meta["recommended_action"]
        })
        
    return pd.DataFrame(evidence_items)