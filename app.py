import streamlit as st
import sqlite3
import pandas as pd
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "ews_cm_database.db")

st.set_page_config(page_title="AI EWS & Credit Monitoring Dashboard", layout="wide")

st.title("🚨 Early Warning System & Credit Monitoring Dashboard")
st.markdown("Automated Early Warning Signals & Borrower Risk Scoring Engine")

def load_data(table_name):
    if not os.path.exists(DB_PATH):
        st.error("Database file not found. Please run 'python -m src.main' first.")
        return pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df

tab1, tab2 = st.tabs(["📊 Early Warning Signals (EWS)", "🏢 Credit Monitoring (CM)"])

with tab1:
    st.header("Account-Level EWS Metrics & Mapped Scores")
    ews_df = load_data("ews_results")
    if not ews_df.empty:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.dataframe(ews_df, width="stretch")
        with col2:
            st.subheader("EWS Indicator Summary")
            st.bar_chart(ews_df.set_index("Account_Number")[["EWS_01", "EWS_02"]])
            
        # Download Button for EWS
        st.download_button(
            label="📥 Download EWS Report (CSV)",
            data=ews_df.to_csv(index=False).encode('utf-8'),
            file_name='EWS_Risk_Report.csv',
            mime='text/csv',
        )

        st.subheader("Filter Accounts")
        account_search = st.text_input("Search by Account Number:", "")
        if account_search:
            filtered_df = ews_df[ews_df["Account_Number"].str.contains(account_search, case=False)]
            st.write(filtered_df)

with tab2:
    st.header("Borrower-Level Credit Monitoring")
    cm_df = load_data("cm_results")
    if not cm_df.empty:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.dataframe(cm_df, width="stretch")
        with col2:
            st.subheader("CM Metrics Breakdown")
            st.bar_chart(cm_df.set_index("Borrower_ID")[["CM_01", "CM_02"]])

        # Download Button for CM
        st.download_button(
            label="📥 Download CM Report (CSV)",
            data=cm_df.to_csv(index=False).encode('utf-8'),
            file_name='CM_Risk_Report.csv',
            mime='text/csv',
        )

        st.subheader("Filter Borrowers")
        borrower_search = st.text_input("Search by Borrower ID:", "")
        if borrower_search:
            filtered_cm = cm_df[cm_df["Borrower_ID"].str.contains(borrower_search, case=False)]
            st.write(filtered_cm)