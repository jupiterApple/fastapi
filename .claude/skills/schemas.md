---
name: schemas
description: Pydantic v2 — padrão Base/Create/Read/Update e serialização de ORM.
---

# schemas

## Padrão Base/Create/Read/Update

Cada recurso tem 4 schemas. Exemplo em [app/schemas/user.py](../../app/schemas/user.py):

```python
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = None
    password: str | None = None


class UserRead(UserBase):
    id: int

    class Config:
        from_attributes = True
```

### Quando usar cada um

| Schema       | Propósito                                              | Usado onde                            |
|--------------|--------------------------------------------------------|---------------------------------------|
| `XxxBase`    | Campos comuns entre Create e Read                      | herdado por Create e Read             |
| `XxxCreate`  | Payload de POST (inclui campos sensíveis como password) | `body: XxxCreate`                     |
| `XxxUpdate`  | PATCH parcial — **todos os campos opcionais**          | `body: XxxUpdate` em PUT              |
| `XxxRead`    | Resposta serializada — **com `from_attributes=True`**  | `response_model=XxxRead`              |

## Serializando ORM → response

Com `from_attributes = True` no `Config`, o FastAPI aceita objeto SQLAlchemy e serializa automaticamente segundo os campos do schema:

```python
@router.get("/{id}", response_model=UserRead)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    return user  # FastAPI serializa via UserRead — id, email, full_name
```

Campos do ORM que não estão no schema (ex.: `hashed_password`) ficam de fora — **é assim que evitamos vazar dado sensível**.

## Update parcial (PATCH-like em PUT)

No router, use `model_dump(exclude_unset=True)` para não sobrescrever campos que o cliente não mandou:

```python
data = user_in.model_dump(exclude_unset=True)
if "email" in data: user.email = data["email"]
if "full_name" in data: user.full_name = data["full_name"]
if data.get("password"): user.hashed_password = get_password_hash(data["password"])
```

Nunca `user.__dict__.update(data)` — perde controle e pode escrever em colunas inesperadas.

## Validações comuns

```python
from pydantic import Field, constr, EmailStr

class ProdutoCreate(BaseModel):
    nome: constr(min_length=1, max_length=100)
    preco: float = Field(gt=0)
    email_contato: EmailStr | None = None
```

## Anti-padrões

- ❌ Retornar dicionário montado na mão em vez de schema `Read`
- ❌ Usar o mesmo schema para Create e Read (expõe campos internos)
- ❌ `XxxUpdate` com campos obrigatórios (mata o semântico de PATCH parcial)
- ❌ Esquecer `from_attributes = True` (FastAPI falha em serializar o ORM)
- ❌ Colocar `password` em `XxxRead` ou `XxxBase`
