---
name: fastapi-standard
description: Padrão obrigatório para endpoints FastAPI do projeto — router, responses, response_model, Depends, logging.
---

# fastapi-standard

Padrão para todos os endpoints do projeto. Baseado em [app/api/v1/users.py](../../app/api/v1/users.py) e [app/api/v1/auth.py](../../app/api/v1/auth.py).

## Estrutura do router

```python
from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserRead

router = APIRouter(prefix="/recurso", tags=["recurso"])

RESPONSES = {
    400: {"description": "Bad Request"},
    401: {"description": "Unauthorized"},
    404: {"description": "Not Found"},
    500: {"description": "Internal Server Error"},
}
```

## Obrigatórios em cada endpoint

- `response_model=SchemaRead` (ou `list[SchemaRead]`) — nunca retornar ORM direto.
- `responses=RESPONSES` — para aparecerem no Swagger.
- `status_code=status.HTTP_...` quando não for 200 (ex.: 201 no POST, 204 no DELETE).
- `Depends(get_db)` para sessão; `Depends(get_current_user)` para rotas protegidas.
- `logger.info(...)` na entrada (o que foi pedido, por quem).
- `logger.info(...)` no sucesso ou `logger.warning/exception(...)` no erro.

## Template de endpoint protegido

```python
@router.post(
    "/",
    response_model=RecursoRead,
    status_code=status.HTTP_201_CREATED,
    responses=RESPONSES,
)
def criar_recurso(
    payload: RecursoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logger.info(
        "Criar recurso solicitado por user_id={user_id}",
        user_id=current_user.id,
    )

    # validação
    existing = db.query(Recurso).filter(Recurso.chave == payload.chave).first()
    if existing:
        logger.warning("Criação falhou: recurso já existe chave={chave}", chave=payload.chave)
        raise HTTPException(status_code=400, detail="Recurso já existe")

    # mutação
    obj = Recurso(**payload.model_dump())
    db.add(obj)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Erro ao salvar recurso")
        raise HTTPException(status_code=500, detail="Falha ao criar recurso")
    db.refresh(obj)

    logger.info("Recurso criado id={id}", id=obj.id)
    return obj
```

## Códigos de status por verbo

| Verbo   | Sucesso | Quando usar                        |
|---------|---------|------------------------------------|
| GET     | 200     | padrão                             |
| POST    | 201     | criação de recurso                 |
| PUT     | 200     | atualização (retorna o recurso)    |
| PATCH   | 200     | atualização parcial                |
| DELETE  | 204     | remoção (sem body na resposta)     |

## Registrando router novo

Em [app/main.py](../../app/main.py):
```python
from app.api.v1.recurso import router as recurso_router
app.include_router(recurso_router, prefix="/api/v1")
```

## Anti-padrões (não fazer)

- ❌ `print(...)` — usar `logger`
- ❌ Retornar objeto SQLAlchemy sem `response_model`
- ❌ Omitir `responses={...}` (Swagger fica incompleto)
- ❌ Query complexa direto no router — delegar a service
- ❌ `try/except Exception` genérico silenciando o erro — sempre `.exception()` + `raise HTTPException`
- ❌ Esquecer `db.rollback()` antes de levantar erro
