import pandas as pd
import numpy as np

def calculate_multi_quarter_trends(historical_df):
    """
    Calculates quarterly deterioration trends across historical financial metrics.
    Flags accounts showing sequential margin compression or leverage escalation.
    """
    trends = []
    
    for account_id, group in historical_df.groupby("Account_Number"):
        group = group.sort_values("Quarter")
        
        # Calculate Quarter-over-Quarter (QoQ) changes
        group["DSCR_Change"] = group["DSCR"].diff()
        group["Leverage_Change"] = group["Debt_Equity_Ratio"].diff()
        group["Utilization_Trend"] = group["CC_OD_Utilization"].diff()
        
        latest = group.iloc[-1]
        
        # Trend Warning Triggers
        dscr_deterioration = bool((group["DSCR_Change"] < 0).sum() >= 2)  # Decreasing for 2 consecutive quarters
        leverage_escalation = bool((group["Leverage_Change"] > 0.2).sum() >= 1) # Rapid leverage rise
        utilization_spike = bool(latest["CC_OD_Utilization"] > 85 and latest["Utilization_Trend"] > 10)
        
        trends.append({
            "Account_Number": account_id,
            "Latest_Quarter": latest["Quarter"],
            "DSCR_Deteriorating": dscr_deterioration,
            "Leverage_Escalating": leverage_escalation,
            "Utilization_Spike": utilization_spike,
            "Trend_Risk_Flag": dscr_deterioration or leverage_escalation or utilization_spike
        })
        
    return pd.DataFrame(trends)


def calculate_peer_benchmarking(borrower_df, peer_benchmarks):
    """
    Compares borrower key financial metrics against sector peer benchmarks.
    """
    results = []
    
    for idx, row in borrower_df.iterrows():
        sector = row.get("Sector", "General Manufacturing")
        benchmark = peer_benchmarks.get(sector, {"Avg_DSCR": 1.5, "Avg_Leverage": 2.0, "Avg_Margin": 12.0})
        
        dscr_deviation = benchmark["Avg_DSCR"] - row.get("DSCR", 1.5)
        leverage_deviation = row.get("Debt_Equity_Ratio", 2.0) - benchmark["Avg_Leverage"]
        
        peer_flag = dscr_deviation > 0.3 or leverage_deviation > 0.8
        
        results.append({
            "Account_Number": row.get("Account_Number"),
            "Sector": sector,
            "Peer_DSCR_Benchmark": benchmark["Avg_DSCR"],
            "Observed_DSCR": row.get("DSCR"),
            "Peer_Deviation_Flag": peer_flag
        })
        
    return pd.DataFrame(results)