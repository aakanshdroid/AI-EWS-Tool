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
        st.error(f"Database not found at '{DB_PATH}'. Run 'python -m src.main' first.")
        return pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        # Convert object columns to string to ensure PyArrow compatibility
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
    st.cache_data.clear()  # Refresh cached tables

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Risk Overview", 
    "🔎 Evidence Pack", 
    "✍️ Human Review", 
    "📜 Governance & Audit Trail"
])

ews_df = load_db_table("ews_results")

# --- TAB 1: OVERVIEW ---
with tab1:
    st.subheader("Account-Level EWS Scores")
    if not ews_df.empty:
        st.dataframe(ews_df, use_container_width=True)

# --- TAB 2: EVIDENCE PACK ---
with tab2:
    st.subheader("Explainability & Evidence Pack (Steps 10–12)")
    if not ews_df.empty:
        selected_acc = st.selectbox("Select Account Number:", ews_df["Account_Number"])
        acc_info = ews_df[ews_df["Account_Number"] == selected_acc].iloc[0]
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Overall Score", acc_info.get("Overall_Risk_Score", "N/A"))
        col2.metric("Risk Band", acc_info.get("Risk_Band", "N/A"))
        col3.metric("Critical Override", acc_info.get("Critical_Override", "N/A"))

# --- TAB 3: HUMAN REVIEW ---
with tab3:
    st.subheader("Human Credit Review & Decisioning (Steps 13–14)")
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

# --- TAB 4: AUDIT TRAIL ---
with tab4:
    st.subheader("Audit Trail & Feedback Logs (Step 15)")
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
        st.info("No human review actions logged yet. Submit a decision in the 'Human Review' tab to see it recorded here.")