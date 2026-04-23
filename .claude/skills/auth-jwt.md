---
name: auth-jwt
description: Como o login e a proteção de rotas funcionam — JWT HS256, oauth2_scheme, get_current_user, hash de senhas.
---

# auth-jwt

## Fluxo de login

1. Cliente envia `POST /api/v1/auth/login` com `{email, password}`.
2. [app/api/v1/auth.py](../../app/api/v1/auth.py) busca user por email, valida senha com `verify_password` (pbkdf2_sha256).
3. Em sucesso, chama `create_access_token(subject=user.id)` e retorna `{access_token, token_type: "bearer"}`.
4. Cliente envia `Authorization: Bearer <token>` nas próximas requisições.

## Componentes

### `app/core/security.py`
- `pwd_context` = `CryptContext(schemes=["pbkdf2_sha256"])`
- `verify_password(plain, hashed)` e `get_password_hash(plain)`
- `create_access_token(subject)` — payload: `{sub: str(subject), exp: <tz-aware>}`, assinado com `SECRET_KEY` via `HS256`.
- `oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")` — obrigatório para o Swagger ter o botão "Authorize".

### `app/api/deps.py`
- `get_db()` — generator com `SessionLocal()`, `try/yield/finally db.close()`.
- `get_current_user(db, token)` — decodifica JWT, extrai `sub`, busca user. Lança `401 Unauthorized` com header `WWW-Authenticate: Bearer` em qualquer falha (token inválido, expirado, sub ausente, user não existe).

## Proteger um endpoint

```python
from fastapi import Depends
from app.api.deps import get_current_user
from app.models.user import User

@router.get("/recurso")
def listar(current_user: User = Depends(get_current_user)):
    ...
```

Isso basta — o próprio `Depends` devolve 401 quando o token for ruim.

## Configurações (`.env`)

```
SECRET_KEY=...         # chave HS256, obrigatório em produção trocar
ALGORITHM=HS256        # default já no config
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Seed de usuário inicial

Se `FIRST_SUPERUSER_EMAIL` + `FIRST_SUPERUSER_PASSWORD` estiverem no `.env`, o [seed.py](../../app/db/seed.py) cria o user no startup. Default dev: `admin@local.dev` / `admin123`.

## Regras

- ✅ Senha **só** é armazenada como hash — nunca em texto claro, nunca logada.
- ✅ Token **nunca** aparece em log (`logger.info` pode citar `user_id`, nunca `access_token`).
- ✅ `sub` é sempre `str(user.id)` no payload — `get_current_user` faz `int(sub)` de volta.
- ✅ Trocar `SECRET_KEY` invalida todos os tokens emitidos (é uma forma de "logout global" brutal).

## Anti-padrões

- ❌ Gravar password em texto ou logar `credentials.password`
- ❌ Usar `HTTPBearer` em vez de `OAuth2PasswordBearer` (quebra o "Authorize" do Swagger)
- ❌ Confundir `sub` (string) com `user_id` (int) — sempre converter explicitamente
- ❌ Criar novo endpoint de refresh sem pedido — não existe ainda, o token expira em 30min e pronto
