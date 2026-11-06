import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")


def send_realtime_alert(subject_title, message_body):
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print("Skipping email alert: Credentials missing in .env")
        return

    clean_subject = str(subject_title).replace('\n', ' ').replace('\r', '').strip()

    msg = EmailMessage()
    msg['Subject'] = f"🚨 File Observer: {clean_subject}"
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL

    msg.set_content(message_body)

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
            print(f"📧 Real-time notification email sent for: {clean_subject}")
    except Exception as e:
        print(f"❌ Failed to send email alert: {e}")