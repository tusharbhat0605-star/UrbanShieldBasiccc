import smtplib
import os
from email.message import EmailMessage
from dotenv import load_dotenv
load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

def send_alert_email(snapshot_path, timestamp, source="RTSP"):

    msg = EmailMessage()
    msg["Subject"] = "🚨 UrbanShield AI Alert: Possible Accident Detected"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL

    body = f"""
UrbanShield AI has detected a possible accident.

Time: {timestamp}
Source: {source}

Please check the attached snapshot.
"""

    msg.set_content(body)

    # Attach snapshot
    with open(snapshot_path, "rb") as f:
        file_data = f.read()
        file_name = os.path.basename(snapshot_path)

    msg.add_attachment(
        file_data,
        maintype="image",
        subtype="jpeg",
        filename=file_name,
    )

    # Send email
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(SENDER_EMAIL, APP_PASSWORD)
        smtp.send_message(msg)