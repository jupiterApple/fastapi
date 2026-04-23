# APP_FC_26 — Backend FastAPI + JWT + CRUD de Users

Backend mínimo de estudo: autenticação JWT e CRUD completo de usuários.

---

## Stack

- Python 3.12
- FastAPI + Pydantic v2
- SQLAlchemy 2.x **síncrono**
- MySQL 8 (container)
- JWT HS256 (`python-jose`) + `passlib[pbkdf2_sha256]`
- Loguru (logging estruturado)
- Adminer (UI web do MySQL)

---

## Pré-requisitos

- Docker Desktop (Windows/Mac) ou Docker + Compose (Linux)
- Git

> Não precisa de Python no host — tudo roda no container.

---

## Quick Start

```bash
cd backend
docker compose up -d --build
```

| Serviço     | URL                                              |
|-------------|--------------------------------------------------|
| API         | http://localhost:8000                            |
| Swagger UI  | http://localhost:8000/docs                       |
| ReDoc       | http://localhost:8000/redoc                      |
| Adminer     | http://localhost:8080                            |
| MySQL       | `localhost:3307` (user/pass `app`/`app`, db `app`) |

**Credenciais iniciais** (via seed): `admin@local.dev` / `admin123` — definidas em [.env](.env).

---

## Variáveis de Ambiente

Arquivo: [.env](.env)

| Variável                      | Obrigatória | Descrição                                  |
|-------------------------------|-------------|--------------------------------------------|
| `SECRET_KEY`                  | sim         | Chave usada para assinar JWT               |
| `ALGORITHM`                   | não         | Algoritmo JWT (default `HS256`)            |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | não         | Validade do token (default 30)             |
| `SQLALCHEMY_DATABASE_URL`     | sim         | URL do banco                               |
| `FIRST_SUPERUSER_EMAIL`       | não         | Email do seed inicial                      |
| `FIRST_SUPERUSER_PASSWORD`    | não         | Senha do seed (apenas dev)                 |
| `FIRST_SUPERUSER_NAME`        | não         | Nome do seed                               |
| `BACKEND_CORS_ORIGINS`        | não         | Origens permitidas, separadas por vírgula  |

---

## Comandos úteis

```bash
docker compose up -d --build     # sobe
docker compose logs -f backend   # logs em tempo real
docker compose down              # derruba
docker compose down -v           # derruba + apaga volume do banco
```

Alterações em `app/**` recarregam automaticamente (uvicorn `--reload`).

---

## Endpoints

Todos sob o prefixo `/api/v1`. Swagger completo: http://localhost:8000/docs

### Autenticação

| Método | Rota            | Auth | Descrição                |
|--------|-----------------|------|--------------------------|
| POST   | `/auth/login`   | ❌   | Login, retorna JWT       |

### Usuários (CRUD)

| Método | Rota              | Auth | Descrição                      |
|--------|-------------------|------|--------------------------------|
| GET    | `/users/me`       | ✅   | Usuário autenticado atual      |
| GET    | `/users/`         | ✅   | Lista usuários (skip/limit)    |
| GET    | `/users/{id}`     | ✅   | Busca usuário por ID           |
| POST   | `/users/`         | ✅   | Cria usuário                   |
| PUT    | `/users/{id}`     | ✅   | Atualiza usuário (parcial)     |
| DELETE | `/users/{id}`     | ✅   | Remove usuário                 |

---

## Exemplos rápidos (cURL)

```bash
# 1) Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@local.dev","password":"admin123"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# 2) Usuário atual
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN"

# 3) Listar
curl "http://localhost:8000/api/v1/users/?skip=0&limit=10" \
  -H "Authorization: Bearer $TOKEN"

# 4) Criar
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email":"novo@ex.com","full_name":"Novo","password":"123456"}'

# 5) Atualizar
curl -X PUT http://localhost:8000/api/v1/users/2 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Nome Atualizado"}'

# 6) Deletar
curl -X DELETE http://localhost:8000/api/v1/users/2 \
  -H "Authorization: Bearer $TOKEN"
```

Collection Postman pronta: [API_Collection.postman_collection.json](API_Collection.postman_collection.json)

---

## Estrutura

```
backend/
├── app/
│   ├── api/
│   │   ├── deps.py              # get_db, get_current_user
│   │   └── v1/
│   │       ├── auth.py          # POST /auth/login
│   │       └── users.py         # CRUD /users
│   ├── core/
│   │   ├── config.py            # Settings (pydantic-settings)
│   │   ├── logging.py           # Loguru
│   │   └── security.py          # JWT + hashing
│   ├── db/
│   │   ├── base.py              # registra modelos pro create_all
│   │   ├── base_class.py        # DeclarativeBase
│   │   ├── seed.py              # superusuário inicial
│   │   └── session.py           # engine + SessionLocal
│   ├── models/
│   │   └── user.py
│   ├── schemas/
│   │   ├── auth.py              # LoginInput, Token
│   │   └── user.py              # UserCreate/Read/Update
│   └── main.py
├── .env
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── API_Collection.postman_collection.json
```

