# Redis — Cache de Leitura

## Conceito

**Cache-aside** (lazy loading) é o padrão mais comum de cache: a aplicação primeiro consulta o cache; em caso de miss, busca no banco e grava o resultado no cache antes de responder. Escritas invalidam as chaves afetadas em vez de atualizá-las diretamente — mais simples e menos propenso a inconsistência do que manter cache e banco sincronizados em toda mutação.

O objetivo é reduzir carga no MySQL em rotas de leitura frequente, ao custo de aceitar dados potencialmente desatualizados por até `CACHE_TTL_SECONDS` (ou até a próxima escrita, que invalida na hora).

## O que foi implementado

Cache-aside em `GET /users/` e `GET /users/{id}`:

```
GET /users/{id}
  ├── cache hit  → retorna do Redis (não toca o MySQL)
  └── cache miss → consulta MySQL → grava no Redis (TTL) → retorna

POST /users/, PUT /users/{id}, DELETE /users/{id}
  └── invalida a(s) chave(s) afetada(s) no Redis antes de responder
```

Componentes:
- [app/core/cache.py](../../app/core/cache.py) — client Redis (`redis.from_url`), mesmo padrão do `engine`/`SessionLocal` em `app/db/session.py`.
- [app/api/deps.py](../../app/api/deps.py) — `get_cache()`, dependency análoga ao `get_db()`.
- [app/api/v1/users.py](../../app/api/v1/users.py) — chaves `cache:user:{id}` e `cache:users:list:{skip}:{limit}`; invalidação via `cache.delete` (chave única) e `cache.scan_iter` (padrão da listagem, já que paginação gera N chaves).

## Diagrama

```mermaid
sequenceDiagram
    participant C as Cliente
    participant A as API
    participant R as Redis
    participant M as MySQL

    C->>A: GET /users/5
    A->>R: GET cache:user:5
    alt cache hit
        R-->>A: JSON
        A-->>C: 200 (do cache)
    else cache miss
        R-->>A: nil
        A->>M: SELECT * FROM users WHERE id=5
        M-->>A: linha
        A->>R: SET cache:user:5 (TTL)
        A-->>C: 200 (do banco)
    end

    C->>A: PUT /users/5
    A->>M: UPDATE users SET ...
    A->>R: DEL cache:user:5
    A->>R: DEL cache:users:list:*
    A-->>C: 200
```

## Decisões

| Decisão | Alternativa descartada | Motivo |
|---------|------------------------|--------|
| Cache-aside com invalidação | Write-through (atualizar cache na escrita) | Invalidar é mais simples e não duplica a lógica de serialização no fluxo de mutação |
| `fakeredis` nos testes | Redis real via `services:` no GitHub Actions | Mesma decisão já tomada pro banco (SQLite in-memory) — reduz complexidade do workflow, [01-cicd.md](01-cicd.md) |
| TTL curto (60s default) | TTL longo ou sem expiração | POC de estudo — TTL curto deixa o comportamento observável manualmente sem esperar muito |
| Invalidar toda a listagem (`scan_iter` + `DEL`) em qualquer mutação | Cachear só `skip=0&limit=100` (uma chave fixa) | A rota aceita paginação arbitrária; cachear por combinação de `skip/limit` é mais realista, mas exige varrer o padrão pra invalidar todas as páginas |
| `GET /users/me` fora do cache | Cachear também | `get_current_user` já consulta o banco pra autenticar o token — cachear não evitaria a query, só adicionaria complexidade |

## O que aprendi

- Dependency injection do FastAPI serve tão bem pra um client Redis quanto pra sessão do SQLAlchemy — `get_cache()` é praticamente um `get_db()` com outro backend, e isso também torna o cache trivialmente substituível por `fakeredis` nos testes via `app.dependency_overrides`.
- `response_model` do FastAPI valida a resposta independente da origem — retornar um `dict` vindo do Redis (`json.loads`) ou um objeto ORM vindo do SQLAlchemy passam pelo mesmo `UserRead`, então o cache não abre brecha pra vazar campo que o schema não expõe (ex.: `hashed_password`).
- `SCAN` (via `scan_iter`) é a forma correta de buscar chaves por padrão em produção — `KEYS *` bloqueia o Redis inteiro enquanto varre, `SCAN` itera em lotes sem travar outros comandos.
- Cache errado (não invalidado) é pior que sem cache: por isso toda mutação (`POST`/`PUT`/`DELETE`) precisa invalidar antes de responder, não só o TTL — o teste `test_list_users_serve_do_cache_apos_primeira_chamada` propositalmente muda o banco "por fora" da API pra provar que o cache é servido sem re-consultar, e os testes de `create`/`update`/`delete` prova o oposto: que a invalidação realmente acontece.

## Referências

- [Redis — Caching documentation](https://redis.io/docs/latest/develop/use/patterns/)
- [redis-py — Documentação oficial](https://redis.readthedocs.io/)
- [fakeredis — PyPI](https://pypi.org/project/fakeredis/)
- [AWS — Caching patterns (cache-aside)](https://aws.amazon.com/caching/best-practices/)
