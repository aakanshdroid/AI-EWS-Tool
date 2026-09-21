import streamlit as st
import sqlite3
import pandas as pd
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "ews_cm_database.db")

st.set_page_config(page_title="AI EWS & Credit Monitoring", layout="wide")
st.title("🚨 Early Warning System & Credit Monitoring Engine")

@st.cache_data(ttl=30)
def load_db_table(table_name):
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        # Ensure object columns are strings for PyArrow stability
        for col in df.columns:
            if df[col].dtype == "object":
                df[col] = df[col].astype(str)
    except Exception:
        df = pd.DataFrame()
    finally:
        conn.close()
    return df

def save_audit_action(account_num, decision, rationale, reviewer_id="CO_001"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_trail (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_number TEXT,
            decision TEXT,
            rationale TEXT,
            reviewer_id TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute(
        "INSERT INTO audit_trail (account_number, decision, rationale, reviewer_id) VALUES (?, ?, ?, ?)",
        (account_num, decision, rationale, reviewer_id)
    )
    conn.commit()
    conn.close()
    st.cache_data.clear()

# Streamlit Tabs Definition
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Risk Overview", 
    "🔎 Evidence Pack", 
    "📈 Trend & Peer Analytics", 
    "✍️ Human Review", 
    "📜 Governance & Audit Trail"
])

ews_df = load_db_table("ews_results")

# --- TAB 1: OVERVIEW ---
with tab1:
    st.subheader("Account-Level EWS Scores")
    if not ews_df.empty:
        st.dataframe(ews_df, use_container_width=True)
    else:
        st.info("No EWS data available. Run 'python -m src.main' to populate results.")

# --- TAB 2: EVIDENCE PACK ---
with tab2:
    st.subheader("Explainability & Evidence Pack")
    if not ews_df.empty:
        selected_acc = st.selectbox("Select Account Number:", ews_df["Account_Number"])
        acc_info = ews_df[ews_df["Account_Number"] == selected_acc].iloc[0]
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Overall Score", acc_info.get("Overall_Risk_Score", "N/A"))
        col2.metric("Risk Band", acc_info.get("Risk_Band", "N/A"))
        col3.metric("Critical Override", acc_info.get("Critical_Override", "N/A"))

# --- TAB 3: TREND & PEER ANALYTICS ---
with tab3:
    st.subheader("Multi-Quarter Trend Deterioration & Sector Benchmarking")
    trend_data = load_db_table("trend_analytics_results")
    peer_data = load_db_table("peer_benchmark_results")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### 📉 Quarterly Metric Deterioration")
        if not trend_data.empty:
            st.dataframe(trend_data, use_container_width=True)
        else:
            st.info("No trend analytics generated yet.")
            
    with col_b:
        st.markdown("### 🏢 Peer Group Benchmarking")
        if not peer_data.empty:
            st.dataframe(peer_data, use_container_width=True)
        else:
            st.info("No peer benchmark results generated yet.")

# --- TAB 4: HUMAN REVIEW ---
with tab4:
    st.subheader("Human Credit Review & Decisioning")
    if not ews_df.empty:
        acc_to_review = st.selectbox("Select Account to Action:", ews_df["Account_Number"], key="review_acc")
        
        decision = st.radio(
            "Credit Officer Decision:",
            ["Accept Alert (Escalate to Remediation)", "Override Risk Band", "Close as False Positive"]
        )
        rationale = st.text_area("Mitigation Rationale / Comments:", "")
        
        if st.button("Submit Decision"):
            if not rationale.strip():
                st.error("Please provide a rationale before submitting.")
            else:
                save_audit_action(acc_to_review, decision, rationale)
                st.success(f"Decision for {acc_to_review} logged successfully!")

# --- TAB 5: AUDIT TRAIL ---
with tab5:
    st.subheader("Audit Trail & Governance Logs")
    audit_df = load_db_table("audit_trail")
    if not audit_df.empty:
        st.dataframe(audit_df, use_container_width=True)
        st.download_button(
            label="📥 Download Audit History (CSV)",
            data=audit_df.to_csv(index=False).encode("utf-8"),
            file_name="EWS_Audit_Trail.csv",
            mime="text/csv",
        )
    else:
        st.info("No audit logs recorded yet.")