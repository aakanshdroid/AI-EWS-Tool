import os
import resend


def get_secret(key_name, default_val=""):
    """
    Get secret from Streamlit Cloud.
    If unavailable, use local environment variable.
    """
    try:
        import streamlit as st

        if key_name in st.secrets:
            return st.secrets[key_name]

    except Exception:
        pass

    return os.getenv(key_name, default_val)


def send_critical_alert_email(
    account_number,
    borrower_name,
    risk_score,
    risk_band,
    override_flag
):
    """
    Send Critical EWS email alert using Resend.
    """

    # Get configuration
    api_key = get_secret("RESEND_API_KEY")
    from_email = get_secret("RESEND_FROM_EMAIL")
    credit_officer_email = get_secret("CREDIT_OFFICER_EMAIL")

    # Check configuration
    if not api_key:
        print("[Notifier Error] RESEND_API_KEY is missing.")
        return False

    if not from_email:
        print("[Notifier Error] RESEND_FROM_EMAIL is missing.")
        return False

    if not credit_officer_email:
        print("[Notifier Error] CREDIT_OFFICER_EMAIL is missing.")
        return False

    # Configure Resend
    resend.api_key = api_key

    # Email subject
    subject = (
        f"🚨 Critical Credit Alert - Account {account_number}"
    )

    # Email content
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">

        <h2 style="color: #d9534f;">
            Critical Risk Triggered in EWS Pipeline
        </h2>

        <p>
            The Early Warning System detected high-risk
            indicators for the following borrower.
        </p>

        <table
            border="1"
            cellpadding="8"
            cellspacing="0"
            style="border-collapse: collapse;"
        >

            <tr>
                <td><b>Account Number</b></td>
                <td>{account_number}</td>
            </tr>

            <tr>
                <td><b>Borrower Name</b></td>
                <td>{borrower_name}</td>
            </tr>

            <tr>
                <td><b>Overall Risk Score</b></td>
                <td>{risk_score} / 100</td>
            </tr>

            <tr>
                <td><b>Risk Band</b></td>
                <td>{risk_band}</td>
            </tr>

            <tr>
                <td><b>Critical Override</b></td>
                <td>{override_flag}</td>
            </tr>

        </table>

        <br>

        <p>
            Please log into the EWS Dashboard to review
            and action this borrower.
        </p>

        <p>
            <i>
                Automated Notification Engine —
                EWS & Credit Monitoring System
            </i>
        </p>

    </body>
    </html>
    """

    # Send email
    try:

        response = resend.Emails.send({
            "from": from_email,
            "to": [credit_officer_email],
            "subject": subject,
            "html": html_content
        })

        print(
            f"[Notifier] Email successfully sent "
            f"for {account_number}"
        )

        print(response)

        return True

    except Exception as e:

        print(
            f"[Notifier Error] "
            f"Failed to send email: {e}"
        )

        return False