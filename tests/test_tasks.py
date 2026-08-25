from app.tasks.user_tasks import send_welcome_email


def test_send_welcome_email_envia_via_smtp_e_retorna_confirmacao(mock_smtp):
    result = send_welcome_email.delay(1, "test@test.com", "Fulano")

    assert result.get() == "email enviado para test@test.com"
    mock_smtp.starttls.assert_called_once()
    mock_smtp.login.assert_called_once()
    mock_smtp.send_message.assert_called_once()


def test_send_welcome_email_sem_full_name_usa_email_no_corpo(mock_smtp):
    send_welcome_email.delay(1, "sem-nome@test.com").get()

    enviado = mock_smtp.send_message.call_args.args[0]
    assert "sem-nome@test.com" in enviado.get_content()
