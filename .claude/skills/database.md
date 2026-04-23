---
name: database
description: SQLAlchemy 2.x síncrono — modelos, sessão, queries, como adicionar tabela nova.
---

# database

## Por que síncrono

SQLAlchemy 2.x é usado **síncrono** por decisão de projeto. Não migrar para async sem pedido explícito — a escolha prioriza simplicidade sobre throughput máximo.

## Componentes

### `app/db/base_class.py`
```python
from sqlalchemy.orm import DeclarativeBase
class Base(DeclarativeBase): pass
```

### `app/db/session.py`
```python
engine = create_engine(settings.SQLALCHEMY_DATABASE_URL, future=True, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

### `app/db/base.py`
Importa **todos os modelos** para o `Base.metadata` enxergá-los no `create_all`. Sempre que criar um modelo novo, adicionar o import aqui.

### `app/api/deps.py`
```python
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## Criando um modelo novo (passo a passo)

1. Criar `app/models/recurso.py`:
```python
from sqlalchemy import Column, Integer, String
from app.db.base_class import Base

class Recurso(Base):
    __tablename__ = "recursos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False, index=True)
    descricao = Column(String(500), nullable=True)
```

2. Importar em `app/db/base.py`:
```python
from app.models.recurso import Recurso  # noqa: F401
```

3. Reiniciar o container — o `on_startup` chama `Base.metadata.create_all(bind=engine)` e a tabela aparece.

4. Breaking change (ex.: remover coluna)? `docker compose down -v` apaga o volume e recria do zero. **Não existe Alembic ainda** — migrações manuais/destrutivas só em dev.

## Queries no router (simples)

```python
# Get por id
obj = db.query(Recurso).filter(Recurso.id == recurso_id).first()
if not obj:
    raise HTTPException(status_code=404, detail="Recurso not found")

# List com paginação
items = db.query(Recurso).offset(skip).limit(limit).all()

# Exists
existing = db.query(Recurso).filter(Recurso.nome == nome).first()
if existing:
    raise HTTPException(status_code=400, detail="Nome já usado")
```

## Mutação + commit

```python
obj = Recurso(**payload.model_dump())
db.add(obj)
try:
    db.commit()
except Exception:
    db.rollback()
    logger.exception("Erro ao salvar recurso")
    raise HTTPException(status_code=500, detail="Falha ao criar")
db.refresh(obj)
```

Sempre `rollback()` antes de lançar `HTTPException(500)`.

## Quando delegar a um service/repository

Regra: se o endpoint precisa de mais de 1 query ou lógica não-trivial (agregação, regra de negócio, transação com múltiplos modelos), criar `app/services/recurso_service.py` ou `app/repositories/recurso_repository.py`.

## Anti-padrões

- ❌ Instanciar `SessionLocal()` no router — usar `Depends(get_db)`
- ❌ `db.commit()` sem `try/except` em fluxo de mutação
- ❌ Esquecer de registrar modelo novo em `app/db/base.py`
- ❌ `session.add()` seguido de acesso a `.id` sem `refresh()` (pode não estar populado)
