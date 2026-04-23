# Instruções para o Claude Code — Backend APP_FC_26

## Sobre

Backend FastAPI de estudo com autenticação JWT e CRUD de usuários. MySQL via Docker, SQLAlchemy 2.x síncrono, Loguru. Ver [README.md](README.md) para setup e endpoints.

## Stack

- Python 3.12
- FastAPI + Pydantic v2
- SQLAlchemy 2.x **síncrono** (não async — é proposital, não "migre para async" sem pedido)
- MySQL 8 via Docker Compose
- JWT HS256 (`python-jose`) + `passlib[pbkdf2_sha256]`
- Loguru para logging

## Skills disponíveis em `.claude/skills/`

Sempre consulte a skill relevante antes de gerar código:

| Skill              | Quando usar                                                      |
|--------------------|------------------------------------------------------------------|
| `fastapi-standard` | padrão de router, `responses`, `response_model`, `Depends`       |
| `auth-jwt`         | login, geração/validação de token, proteção de rotas             |
| `database`         | modelos SQLAlchemy 2.x, queries, sessão                          |
| `schemas`          | Pydantic v2 Base/Create/Read/Update                              |
| `logging`          | Loguru — níveis, contexto, o que NÃO logar                       |
| `testing`          | pytest + TestClient síncrono                                     |
| `docker`           | compose, portas, hot reload, healthcheck                         |

## Regras rígidas

1. **Nunca** `print()` — sempre `logger` (Loguru).
2. Todo endpoint tem `responses={...}` e `response_model`.
3. Sessão sempre via `Depends(get_db)`.
4. Router não executa lógica complexa — delega a service/repository quando crescer.
5. Nunca retorne ORM direto — serialize via schema `Read`.
6. Nunca logue senhas, hashes ou tokens.
7. Segredos só via `.env` + `pydantic-settings` — nada hardcoded.
8. Não migrar SQLAlchemy para async sem pedido explícito.
9. Código e mensagens de commit em **português**.
10. Commits descrevem **o estado atual** (o que o código é), não a transformação ("enxugar/remover/limpar" são banidos do título).

## Antes de editar

- Se for mexer em endpoint/schema/modelo existente, leia o arquivo primeiro — não invente estrutura.
- Ao adicionar modelo novo, importar em [app/db/base.py](app/db/base.py) para o `create_all` pegar.
- Ao adicionar router novo, incluir em [app/main.py](app/main.py) via `app.include_router(..., prefix="/api/v1")`.

## Antes de reportar "pronto"

- Endpoint roda localmente? (`docker compose up -d --build`)
- Swagger em http://localhost:8000/docs reconhece a rota com `responses` documentados?
- Se houve mudança de schema do banco, o container foi reiniciado? Volume apagado se for breaking change (`docker compose down -v`)?
- Credencial seed (`admin@local.dev` / `admin123`) ainda autentica?
