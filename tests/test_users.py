from unittest.mock import patch

from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserBioGenerated


def _create_user_and_login(client, db, email="owner@test.com", password="senha123"):
    db.add(User(email=email, hashed_password=get_password_hash(password), full_name="Owner"))
    db.commit()
    res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_get_user_serve_do_cache_apos_primeira_chamada(client, db):
    headers = _create_user_and_login(client, db)
    target = db.query(User).filter(User.email == "owner@test.com").first()

    first = client.get(f"/api/v1/users/{target.id}", headers=headers)
    assert first.status_code == 200
    assert first.json()["full_name"] == "Owner"

    # muda o banco por fora da API — cache não sabe disso
    target.full_name = "Mudou Direto No Banco"
    db.commit()

    second = client.get(f"/api/v1/users/{target.id}", headers=headers)
    assert second.json()["full_name"] == "Owner"


def test_list_users_serve_do_cache_apos_primeira_chamada(client, db):
    headers = _create_user_and_login(client, db)

    first = client.get("/api/v1/users/", headers=headers)
    total_antes = len(first.json())

    db.add(User(email="fora_da_api@test.com", hashed_password=get_password_hash("x")))
    db.commit()

    second = client.get("/api/v1/users/", headers=headers)
    assert len(second.json()) == total_antes


def test_create_user_invalida_cache_da_listagem(client, db):
    headers = _create_user_and_login(client, db)
    client.get("/api/v1/users/", headers=headers)  # popula cache

    res = client.post(
        "/api/v1/users/",
        headers=headers,
        json={"email": "novo@test.com", "full_name": "Novo", "password": "123456"},
    )
    assert res.status_code == 201

    listagem = client.get("/api/v1/users/", headers=headers)
    emails = [u["email"] for u in listagem.json()]
    assert "novo@test.com" in emails


def test_create_user_dispara_task_de_email_de_boas_vindas(client, db):
    headers = _create_user_and_login(client, db)

    with patch("app.api.v1.users.send_welcome_email.delay") as mock_delay:
        res = client.post(
            "/api/v1/users/",
            headers=headers,
            json={"email": "boasvindas@test.com", "full_name": "Novo", "password": "123456"},
        )
    assert res.status_code == 201

    novo_id = res.json()["id"]
    mock_delay.assert_called_once_with(novo_id, "boasvindas@test.com", "Novo")


def test_update_user_invalida_cache_do_usuario(client, db):
    headers = _create_user_and_login(client, db)
    target = db.query(User).filter(User.email == "owner@test.com").first()
    client.get(f"/api/v1/users/{target.id}", headers=headers)  # popula cache

    res = client.put(
        f"/api/v1/users/{target.id}",
        headers=headers,
        json={"full_name": "Nome Atualizado"},
    )
    assert res.status_code == 200

    depois = client.get(f"/api/v1/users/{target.id}", headers=headers)
    assert depois.json()["full_name"] == "Nome Atualizado"


def test_delete_user_invalida_cache_do_usuario(client, db):
    headers = _create_user_and_login(client, db)
    outro = User(email="apagar@test.com", hashed_password=get_password_hash("x"))
    db.add(outro)
    db.commit()
    db.refresh(outro)

    client.get(f"/api/v1/users/{outro.id}", headers=headers)  # popula cache

    res = client.delete(f"/api/v1/users/{outro.id}", headers=headers)
    assert res.status_code == 204

    depois = client.get(f"/api/v1/users/{outro.id}", headers=headers)
    assert depois.status_code == 404


def test_get_user_nao_encontrado(client, db):
    headers = _create_user_and_login(client, db)
    res = client.get("/api/v1/users/999999", headers=headers)
    assert res.status_code == 404


def test_generate_bio_retorna_estrutura_esperada(client, db):
    headers = _create_user_and_login(client, db)
    target = db.query(User).filter(User.email == "owner@test.com").first()

    fake_bio = UserBioGenerated(headline="Dev backend", bio="Owner integra a base de estudo.", tone="formal")
    with patch("app.api.v1.users.generate_user_bio", return_value=fake_bio):
        res = client.post(f"/api/v1/users/{target.id}/bio", headers=headers)

    assert res.status_code == 200
    assert res.json() == {
        "user_id": target.id,
        "headline": "Dev backend",
        "bio": "Owner integra a base de estudo.",
        "tone": "formal",
    }


def test_generate_bio_usuario_nao_encontrado(client, db):
    headers = _create_user_and_login(client, db)
    res = client.post("/api/v1/users/999999/bio", headers=headers)
    assert res.status_code == 404
