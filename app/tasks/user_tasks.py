import smtplib
from email.message import EmailMessage

from loguru import logger

from app.core.celery_app import celery_app
from app.core.config import settings


def _build_message(email: str, full_name: str | None) -> EmailMessage:
    nome = full_name or email
    msg = EmailMessage()
    msg["Subject"] = "Bem-vindo(a)!"
    msg["From"] = settings.SMTP_FROM
    msg["To"] = email
    msg.set_content(f"Olá, {nome}!\n\nSua conta foi criada com sucesso.")
    return msg


@celery_app.task(name="send_welcome_email")
def send_welcome_email(user_id: int, email: str, full_name: str | None = None) -> str:
    logger.info(
        "Enviando email de boas-vindas user_id={user_id} email={email}",
        user_id=user_id,
        email=email,
    )
    msg = _build_message(email, full_name)
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as smtp:
        smtp.starttls()
        smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        smtp.send_message(msg)
    logger.info("Email de boas-vindas enviado user_id={user_id}", user_id=user_id)
    return f"email enviado para {email}"
