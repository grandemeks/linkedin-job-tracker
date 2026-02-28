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
    requirements = "\n".join([f"  • {r}" for r in summary.get("key_requirements", [])])
    benefits = "\n".join([f"  • {b}" for b in summary.get("key_benefits", [])])

    message = f"""
🚀 *NOVA JOB POZICIJA*

💼 *{summary['title']}*
🏢 *Kompanija:* {summary['company']}
📍 *Tip rada:* {summary['work_type']}
{stars} *Ocjena:* {summary['rating']}/5

📋 *Summary:*
{summary['summary']}

🏢 *O kompaniji:*
{summary['company_info']}

✅ *Ključni zahtjevi:*
{requirements}

🎁 *Benefiti:*
{benefits}

💡 *Zašto ova ocjena:*
{summary['rating_reason']}

🔗 {summary['link']}
    """.strip()

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
```

Sada trebaš Twilio setup. Idi na [twilio.com](https://twilio.com), registruj se besplatno i:

1. Uzmi **Account SID** i **Auth Token** sa dashboarda
2. Idi na **Messaging → Try it out → Send a WhatsApp message**
3. Prati instrukcije — poslaćeš `join <kod>` na WhatsApp broj
4. Dodaj u `app/.env`:
```
TWILIO_ACCOUNT_SID=US8e53189c27acb6f2a4045c576339fc6a
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxx
WHATSAPP_FROM=whatsapp:+14155238886
WHATSAPP_TO=whatsapp:+TVOJ_BROJ_SA_POZIVNIM