from app.tasks.user_tasks import send_welcome_email


def test_send_welcome_email_executa_e_retorna_confirmacao():
    result = send_welcome_email.delay(1, "test@test.com")
    assert result.get() == "email enviado para test@test.com"
