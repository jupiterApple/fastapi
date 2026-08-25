import smtplib
from email.message import EmailMessage

from loguru import logger

from app.core.celery_app import celery_app
from app.core.config import settings

_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html>
  <body style="margin:0; padding:32px 0; background-color:#f4f4f7; font-family: -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
      <tr>
        <td align="center">
          <table role="presentation" width="480" cellpadding="0" cellspacing="0" style="background-color:#ffffff; border-radius:8px; overflow:hidden; box-shadow:0 1px 3px rgba(0,0,0,0.12);">
            <tr>
              <td style="background-color:#4f46e5; padding:24px 32px;">
                <span style="color:#ffffff; font-size:20px; font-weight:600;">APP_FC_26</span>
              </td>
            </tr>
            <tr>
              <td style="padding:32px;">
                <h1 style="margin:0 0 16px; font-size:22px; color:#111827;">Bem-vindo(a), {nome}! 🎉</h1>
                <p style="margin:0 0 16px; font-size:15px; line-height:1.6; color:#374151;">
                  Sua conta foi criada com sucesso. Agora você já pode fazer login e explorar a API.
                </p>
                <p style="margin:24px 0 0; font-size:13px; color:#9ca3af; border-top:1px solid #e5e7eb; padding-top:16px;">
                  Este é um email automático de um projeto de estudo, enviado via Ethereal — não chega numa caixa real.
                </p>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
"""


def _build_message(email: str, full_name: str | None) -> EmailMessage:
    nome = full_name or email
    msg = EmailMessage()
    msg["Subject"] = "Bem-vindo(a)!"
    msg["From"] = settings.SMTP_FROM
    msg["To"] = email
    msg.set_content(f"Olá, {nome}!\n\nSua conta foi criada com sucesso.")
    msg.add_alternative(_HTML_TEMPLATE.format(nome=nome), subtype="html")
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
