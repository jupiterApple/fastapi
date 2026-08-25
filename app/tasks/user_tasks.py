import time

from loguru import logger

from app.core.celery_app import celery_app


@celery_app.task(name="send_welcome_email")
def send_welcome_email(user_id: int, email: str) -> str:
    logger.info(
        "Enviando email de boas-vindas user_id={user_id} email={email}",
        user_id=user_id,
        email=email,
    )
    time.sleep(2)  # simula latência de um provedor de email real
    logger.info("Email de boas-vindas enviado user_id={user_id}", user_id=user_id)
    return f"email enviado para {email}"
