import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")
CREDIT_OFFICER_EMAIL = os.getenv("CREDIT_OFFICER_EMAIL", "")

def send_critical_alert_email(account_number, borrower_name, risk_score, risk_band, override_flag):
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print(f"[Notifier Log] Alert triggered for {account_number} (Score: {risk_score}), but email credentials are not set.")
        return False

    subject = f"🚨 URGENT: Critical Credit Alert - Account {account_number}"
    
    body = f"""
    <html>
      <body>
        <h2 style="color: #d9534f;">Critical Risk Triggered in EWS Pipeline</h2>
        <p>An automated scan detected high-risk indicators for the following account:</p>
        <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse;">
          <tr><td><b>Account Number</b></td><td>{account_number}</td></tr>
          <tr><td><b>Borrower Name</b></td><td>{borrower_name}</td></tr>
          <tr><td><b>Overall Risk Score</b></td><td><b style="color: #d9534f;">{risk_score} / 100</b></td></tr>
          <tr><td><b>Risk Band</b></td><td>{risk_band}</td></tr>
          <tr><td><b>Critical Override Flag</b></td><td><b>{override_flag}</b></td></tr>
        </table>
        <br>
        <p>Please log into the dashboard to review and complete human review.</p>
      </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = CREDIT_OFFICER_EMAIL
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, CREDIT_OFFICER_EMAIL, msg.as_string())
        print(f"[Notifier] Email alert sent successfully for {account_number}.")
        return True
    except Exception as e:
        print(f"[Notifier Error] Failed to send email alert: {e}")
        return False