---
name: logging
description: Loguru — como logar, níveis, contexto estruturado e o que NUNCA logar.
---

# logging

## Import padrão

```python
from loguru import logger
```

**Nunca `print(...)`.** A configuração está em [app/core/logging.py](../../app/core/logging.py) — formato colorido com timestamp, módulo e nível.

## Níveis e quando usar

| Nível         | Uso                                                            |
|---------------|----------------------------------------------------------------|
| `logger.debug`   | investigação profunda (desabilitado em INFO)                |
| `logger.info`    | fluxo normal — entrada/saída de endpoint, operações bem-sucedidas |
| `logger.warning` | fluxo de erro **previsível** — tentativa inválida, dado duplicado, 401/404 que a API retorna ao cliente |
| `logger.error`   | erro real mas sem stack trace (caso raro)                   |
| `logger.exception` | dentro de `except` — inclui stack trace automaticamente   |

## Contexto estruturado

Usar placeholders nomeados em vez de f-string — Loguru serializa os kwargs:

```python
# ✅ bom
logger.info("User criado user_id={user_id} email={email}", user_id=user.id, email=user.email)

# ❌ evitar (f-string perde a estrutura)
logger.info(f"User criado user_id={user.id} email={user.email}")
```

## Padrão em endpoints

Entrada:
```python
logger.info(
    "Criar recurso solicitado por user_id={user_id}",
    user_id=current_user.id,
)
```

Sucesso:
```python
logger.info("Recurso criado id={id}", id=obj.id)
```

Fluxo de erro previsível (cliente errou):
```python
logger.warning("Criação falhou: email já registrado {email}", email=payload.email)
raise HTTPException(status_code=400, ...)
```

Erro interno (bug, DB indisponível, etc):
```python
except Exception:
    db.rollback()
    logger.exception("Erro ao salvar recurso")
    raise HTTPException(status_code=500, ...)
```

## O que NUNCA logar

- 🚫 Senha em texto (`payload.password`)
- 🚫 Hash de senha (`user.hashed_password`)
- 🚫 Tokens JWT inteiros (`access_token`, `Authorization` header)
- 🚫 Chaves de API, `SECRET_KEY`, segredos do `.env`
- 🚫 Dados pessoais sensíveis (CPF, número de cartão, etc) em texto

## O que PODE logar

- ✅ `user_id`, email (email ok; senha não)
- ✅ IDs de recursos (`post_id`, `recurso_id`)
- ✅ Ação tomada (`"user criado"`, `"tentativa de login"`)
- ✅ Contexto de falha sem vazar segredo (`"login falhou para email=..."` — mas nunca `"password=..."`)

## Ver logs em dev

```bash
docker compose logs -f backend
```
