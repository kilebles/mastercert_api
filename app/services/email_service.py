import os

from email.message import EmailMessage
from aiosmtplib import send

from app.core.config import config


async def send_contact_info_email(chat_id: str, messages: list[dict]):
    email_address = config.EMAIL_ADRESS
    
    msg = EmailMessage()
    msg["From"] = config.SMTP_USER
    msg["To"] = email_address
    msg["Subject"] = f"Новая контактная информация от пользователя ({chat_id})"

    history_text = "\n\n".join(
        f"{m['role'].capitalize()}: {m['content']}" for m in messages
    )

    msg.set_content(f"История чата:\n\n{history_text}")

    await send(
        msg,
        hostname="smtp.yandex.ru",
        port=587,
        username=os.getenv("SMTP_USER"),
        password=os.getenv("SMTP_PASS"),
        start_tls=True,
    )