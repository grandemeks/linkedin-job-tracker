import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
WHATSAPP_FROM = os.getenv("WHATSAPP_FROM")
WHATSAPP_TO = os.getenv("WHATSAPP_TO")


def format_message(summary: dict) -> str:
    """Formatira WhatsApp poruku od AI summary."""
    stars = "⭐" * summary.get("rating", 0)
    requirements = "\n".join([f"  - {r}" for r in summary.get("key_requirements", [])])
    benefits = "\n".join([f"  - {b}" for b in summary.get("key_benefits", [])])

    message = (
        f"NOVA JOB POZICIJA\n\n"
        f"Title: {summary['title']}\n"
        f"Kompanija: {summary['company']}\n"
        f"Tip rada: {summary['work_type']}\n"
        f"Ocjena: {stars} {summary['rating']}/5\n\n"
        f"Summary:\n{summary['summary']}\n\n"
        f"O kompaniji:\n{summary['company_info']}\n\n"
        f"Kljucni zahtjevi:\n{requirements}\n\n"
        f"Benefiti:\n{benefits}\n\n"
        f"Zasto ova ocjena:\n{summary['rating_reason']}\n\n"
        f"Link: {summary['link']}"
    )
    return message


def send_whatsapp_message(message: str) -> bool:
    """Salje WhatsApp poruku putem Twilio."""
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        msg = client.messages.create(
            body=message,
            from_=WHATSAPP_FROM,
            to=WHATSAPP_TO,
        )
        print(f"[Notifier] Message sent! SID: {msg.sid}")
        return True
    except Exception as e:
        print(f"[Notifier] Error sending message: {e}")
        return False


def notify_new_job(summary: dict) -> bool:
    """Formatira i salje notifikaciju za novi job."""
    message = format_message(summary)
    print(f"[Notifier] Sending notification for: {summary['title']} @ {summary['company']}")
    return send_whatsapp_message(message)
