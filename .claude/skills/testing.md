---
name: testing
description: Padrão de testes — pytest + TestClient síncrono (não httpx.AsyncClient).
---

# testing

## Ferramentas

- `pytest` — runner
- `fastapi.testclient.TestClient` — cliente síncrono (compatível com SQLAlchemy síncrono)
- Banco: SQLite em memória para unit; MySQL containerizado para integração

Não usar `httpx.AsyncClient` nem `pytest-asyncio` — quebra a simetria com o código síncrono.

## Dependências

Em [requirements.txt](../../requirements.txt), seção dev/test:
```
pytest
pytest-cov
httpx
fakeredis
```

`fakeredis` substitui o Redis real nos testes — mesmo espírito do SQLite in-memory pro banco: zero infra externa na CI.

Estrutura:
```
tests/
├── __init__.py
├── conftest.py          # fixtures (client, db, cache)
├── test_auth.py
└── test_users.py
```

## `conftest.py` (real, ver [tests/conftest.py](../../tests/conftest.py))

```python
import fakeredis
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.api.deps import get_cache, get_db
from app.db.base_class import Base

_test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # garante que todas as conexões usam o mesmo BD in-memory
)
TestingSessionLocal = sessionmaker(bind=_test_engine)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=_test_engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=_test_engine)


@pytest.fixture
def cache():
    return fakeredis.FakeStrictRedis(decode_responses=True)


@pytest.fixture
def client(db, cache):
    # Suspende on_startup (conectaria ao MySQL) — tabelas já criadas pelo fixture db
    saved_startup = app.router.on_startup[:]
    app.router.on_startup.clear()

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_cache] = lambda: cache
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    app.router.on_startup.extend(saved_startup)
```

Endpoint que usa `Depends(get_cache)` (ver [database](database.md) pro equivalente com `get_db`) recebe o `fakeredis` automaticamente nos testes — nenhum teste precisa mockar `redis` na mão.

## Exemplo: teste de login

```python
def test_login_sucesso(client, db):
    # setup: cria user diretamente no DB de teste
    from app.models.user import User
    from app.core.security import get_password_hash
    db.add(User(email="t@t.com", hashed_password=get_password_hash("senha123")))
    db.commit()

    res = client.post("/api/v1/auth/login", json={"email": "t@t.com", "password": "senha123"})
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_senha_errada(client, db):
    res = client.post("/api/v1/auth/login", json={"email": "ninguem@t.com", "password": "x"})
    assert res.status_code == 400
```

## Rodando

Dentro do container (para ter o Python configurado):
```bash
docker compose exec backend pytest -v
```

Com cobertura:
```bash
docker compose exec backend pytest --cov=app --cov-report=term-missing
```

## Checklist do teste

- [ ] 1 teste por caminho feliz e 1 por erro esperado (400/401/404)
- [ ] Nunca mockar DB — testar contra SQLite/MySQL de verdade (mocks divergem de prod)
- [ ] Isolar: cada teste começa com tabela vazia (fixture `db` recria)
- [ ] Não depender de ordem de execução dos testes
- [ ] Nunca logar tokens/senhas dos testes nos asserts visíveis do terminal (mesmo em teste — vira hábito)
