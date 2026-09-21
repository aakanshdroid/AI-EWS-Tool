import os
import resend

def get_secret(key_name, default_val=""):
    """Safely fetch secrets from Streamlit Cloud or fallback to local environment variables."""
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key_name in st.secrets:
            return st.secrets[key_name]
    except Exception:
        pass
    return os.getenv(key_name, default_val)

def send_critical_alert_email(account_number, borrower_name, risk_score, risk_band, override_flag):
    api_key = get_secret("RESEND_API_KEY", "")
    # Fallback to sender or placeholder if officer email is not defined
    credit_officer_email = get_secret("CREDIT_OFFICER_EMAIL", "onboarding@resend.dev")
    
    if not api_key:
        print(f"[Notifier Log] Alert triggered for {account_number} (Score: {risk_score}), but RESEND_API_KEY is missing.")
        return False

    resend.api_key = api_key

    subject = f"🚨 URGENT: Critical Credit Alert - Account {account_number}"
    
    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif;">
        <h2 style="color: #d9534f;">Critical Risk Triggered in EWS Pipeline</h2>
        <p>An automated scan detected high-risk indicators for the following borrower account:</p>
        <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; border-color: #ddd;">
          <tr style="background-color: #f2f2f2;"><td><b>Account Number</b></td><td>{account_number}</td></tr>
          <tr><td><b>Borrower Name</b></td><td>{borrower_name}</td></tr>
          <tr style="background-color: #f2f2f2;"><td><b>Overall Risk Score</b></td><td><b style="color: #d9534f;">{risk_score} / 100</b></td></tr>
          <tr><td><b>Risk Band</b></td><td>{risk_band}</td></tr>
          <tr style="background-color: #f2f2f2;"><td><b>Critical Override Flag</b></td><td><b>{override_flag}</b></td></tr>
        </table>
        <br>
        <p>Please log into the EWS Dashboard to review and action this borrower.</p>
        <p><i>Automated Notification Engine — EWS & Credit Monitoring System</i></p>
      </body>
    </html>
    """

    try:
        response = resend.Emails.send({
            "from": "EWS Alerts <onboarding@resend.dev>",
            "to": [credit_officer_email],
            "subject": subject,
            "html": html_content
        })
        print(f"[Notifier] API email alert sent successfully for {account_number} to {credit_officer_email}. ID: {response.get('id')}")
        return True
    except Exception as e:
        print(f"[Notifier Error] Failed to send API email alert: {e}")
        return False