from app.models.user import User
from app.core.security import get_password_hash


def test_login_sucesso(client, db):
    db.add(User(email="test@test.com", hashed_password=get_password_hash("senha123")))
    db.commit()

    res = client.post("/api/v1/auth/login", json={"email": "test@test.com", "password": "senha123"})
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_senha_errada(client, db):
    db.add(User(email="test@test.com", hashed_password=get_password_hash("correta")))
    db.commit()

    res = client.post("/api/v1/auth/login", json={"email": "test@test.com", "password": "errada"})
    assert res.status_code == 400


def test_login_usuario_inexistente(client, db):
    res = client.post("/api/v1/auth/login", json={"email": "ninguem@test.com", "password": "qualquer"})
    assert res.status_code == 400
