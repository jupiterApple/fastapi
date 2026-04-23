---
name: docker
description: Comandos Docker Compose do projeto, portas, hot reload, healthcheck.
---

# docker

## Serviços

Definidos em [docker-compose.yml](../../docker-compose.yml):

| Serviço  | Imagem             | Porta host | Função                                   |
|----------|--------------------|------------|------------------------------------------|
| backend  | build local        | 8000       | API FastAPI                              |
| db       | `mysql:8`          | 3307       | MySQL (user/pass `app`/`app`, db `app`)  |
| adminer  | `adminer`          | 8080       | UI web para inspecionar o MySQL          |

## Comandos do dia-a-dia

```bash
docker compose up -d --build          # sobe com rebuild
docker compose up -d                  # sobe sem rebuild (após mudança em .py)
docker compose logs -f backend        # acompanha logs do backend
docker compose logs -f db             # logs do MySQL
docker compose ps                     # status dos containers
docker compose down                   # derruba (preserva volumes)
docker compose down -v                # derruba + apaga volume do DB (reset total)
docker compose restart backend        # só reinicia o backend
docker compose exec backend bash      # shell dentro do container
```

## Hot reload

O [Dockerfile](../../Dockerfile) usa `uvicorn --reload` e o compose monta `./app:/app/app`. Qualquer mudança em `app/**` recarrega automaticamente — não precisa rebuild nem restart.

Rebuild **só** é necessário quando:
- Mudou o `requirements.txt`
- Mudou o `Dockerfile`

## Healthcheck do MySQL

Usa o user `app` (não root):
```yaml
test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-uapp", "-papp"]
```

Testar com root (`-uroot -proot`) dá falso positivo: o MySQL responde ao ping antes de terminar de criar o user da aplicação, e o backend quebra no startup com `Connection refused`. Usar o user da app garante que ele já está pronto.

## Debugging de problemas comuns

| Sintoma                                    | Investigação                                      |
|--------------------------------------------|---------------------------------------------------|
| Backend crashando no startup               | `docker compose logs backend` — normalmente é falha de conexão com DB ou erro de import |
| `Connection refused` pro MySQL             | esperar o `db` virar `healthy` (~20s primeira vez); ou derrubar com `-v` e subir de novo |
| Mudou schema do modelo e não refletiu      | `docker compose down -v && docker compose up -d --build` (não há Alembic) |
| Porta 8000 ocupada                         | outro processo usando; `docker compose down` ou mudar `ports:` no compose |
| `pip install` lento no build               | já está cacheado na layer `COPY requirements.txt`; só invalida quando o arquivo muda |

## Reset total do banco

```bash
docker compose down -v && docker compose up -d --build
```

Útil para:
- Testar o seed inicial
- Limpar dados de teste
- Aplicar breaking change em schema

## Dockerfile

Python 3.12-slim, deps instaladas em layer própria (cache-friendly), sem venv (container é isolado por si só):
```dockerfile
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000","--reload"]
```
