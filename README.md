# Automated EWS & Credit Monitoring Engine

An end-to-end Python engine that replaces legacy Excel models for Early Warning Signals (EWS) and Credit Monitoring (CM). The tool ingests account-level metrics, applies dynamic threshold scoring rules, persists outputs to SQLite, and provides an interactive Streamlit risk dashboard.

## 📁 Repository Structure
```text
AI-EWS-Tool/
├── common/             # Configuration parsing & Scoring Engine
│   ├── config_loader.py
│   └── scoring_engine.py
├── ews/                # Account-level Early Warning Signal indicators
│   └── ews_calculator.py
├── credit_monitoring/ # Borrower-level Credit Monitoring indicators
│   └── cm_calculator.py
├── src/                # Pipeline orchestration & Database layer
│   ├── database.py
│   └── main.py
├── data/               # Input templates & SQLite database storage
├── docs/               # Excel functional specifications & threshold rules
├── app.py              # Interactive Streamlit dashboard
└── gitignore