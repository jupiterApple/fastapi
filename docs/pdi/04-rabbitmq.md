# RabbitMQ — Broker Dedicado do Celery

## Conceito

### O que é o RabbitMQ

RabbitMQ é um **message broker** dedicado, que implementa o protocolo AMQP (Advanced Message Queuing Protocol) 0-9-1. Diferente do Redis — que serve como broker "emprestando" sua estrutura de `List` (`LPUSH`/`BRPOP`) — o RabbitMQ foi desenhado desde a origem só pra mensageria: entende `exchange` (roteia mensagem pra fila certa), `queue` (armazena até ser consumida) e `ack`/`nack` (confirmação explícita de que o consumidor processou a mensagem, com re-entrega automática se ele cair no meio do processamento).

| Conceito AMQP | Papel |
|----------------|-------|
| **Producer** | quem publica a mensagem (aqui, a API, via `.delay()`) |
| **Exchange** | recebe a mensagem do producer e decide pra qual(is) fila(s) rotear — o Celery usa por padrão um exchange direto por fila |
| **Queue** | onde a mensagem fica até um consumer processar |
| **Consumer** | quem processa a mensagem (aqui, o worker do Celery) |
| **Ack/Nack** | confirmação explícita — sem ack, a mensagem volta pra fila (não se perde se o worker cair no meio do processamento) |

### RabbitMQ vs Redis como broker (comparação conceitual)

Um broker de fila pode ser um serviço dedicado a mensageria (RabbitMQ) ou uma estrutura de dados genérica reaproveitada pra esse fim (a `List` do Redis). Nenhum dos dois exige mudar código de task — a diferença é só de infraestrutura:

| | Redis como broker | RabbitMQ como broker |
|---|---|---|
| Modelo | Lista (`LPUSH`/`BRPOP`), reaproveitando uma estrutura de dados genérica | AMQP nativo — protocolo desenhado pra mensageria |
| Confirmação de entrega | Sem ack nativo — se o worker morre com a mensagem já retirada da lista, ela se perde | Ack explícito — mensagem não confirmada volta pra fila |
| Observabilidade dedicada | Nenhuma (via `redis-cli MONITOR`, genérico) | Management UI própria, com métricas de fila, taxa de entrega, consumidores conectados |

## O que foi implementado

O broker do Celery é o RabbitMQ (AMQP). O *result backend* (onde o Celery guarda o retorno da task pra `.get()` funcionar) fica no Redis — RabbitMQ não é recomendado como result backend, só como broker de mensagens.

```
POST /users/
  ├── cria o user no MySQL (síncrono, como sempre)
  ├── invalida cache da listagem
  ├── send_welcome_email.delay(user.id, user.email, user.full_name)  ← publica numa fila no RabbitMQ
  └── responde 201

worker (processo separado, celery -A app.core.celery_app worker)
  └── consome a fila no RabbitMQ → conecta no Ethereal via SMTP → envia → loga sucesso → grava resultado no Redis (result backend)
```

Componentes:
- [docker-compose.yml](../../docker-compose.yml) — serviço `rabbitmq` (imagem `rabbitmq:3-management-alpine`), com usuário próprio (`app`/`app`) em vez do `guest` padrão. `worker`, `flower` e `backend` dependem do `rabbitmq` saudável.
- [app/core/config.py](../../app/core/config.py) — `CELERY_BROKER_URL` aponta pro RabbitMQ (`amqp://app:app@rabbitmq:5672//`); `CELERY_RESULT_BACKEND` aponta pro Redis.
- [app/core/celery_app.py](../../app/core/celery_app.py) — instância `Celery()` genérica: lê broker e result backend de `settings`, sem nenhuma lógica específica de RabbitMQ.
- [app/tasks/user_tasks.py](../../app/tasks/user_tasks.py) — task `send_welcome_email`, sem nenhuma dependência do broker usado.

## Observabilidade

- **RabbitMQ Management UI** (`http://localhost:15672`, login `app`/`app`) — painel oficial do RabbitMQ: filas, taxa de mensagens publicadas/entregues/confirmadas, consumidores conectados, exchanges. Equivalente ao Flower, só que na camada do broker em vez da camada do Celery.
- **Flower** (`http://localhost:5555`) — é agnóstico ao broker, só fala com a API do Celery.
- **`docker compose logs -f worker`** — ciclo de vida da task no log (`received` → log da própria função → `succeeded in Xs`).

## Diagrama

```mermaid
sequenceDiagram
    participant C as Cliente
    participant A as API (backend)
    participant M as MySQL
    participant Q as RabbitMQ (broker)
    participant W as Worker (Celery)
    participant R as Redis (result backend)
    participant E as Ethereal (SMTP)

    C->>A: POST /users
    A->>M: INSERT INTO users
    A->>Q: publica send_welcome_email(id, email, nome)
    A-->>C: 201 (não espera o email)

    Q->>W: entrega a mensagem (com ack pendente)
    W->>E: STARTTLS + login + envia mensagem
    E-->>W: 250 OK
    W->>Q: ack (confirma processamento, mensagem sai da fila)
    W->>R: grava resultado da task
    Note over W: log "email enviado"
```

## Decisões

| Decisão | Alternativa descartada | Motivo |
|---------|------------------------|--------|
| RabbitMQ como broker | Redis como broker (reaproveitando a mesma instância do [cache](02-redis.md)) | Praticar gestão de filas com um broker dedicado de verdade — ack explícito, Management UI própria, modelo AMQP — em vez de reaproveitar a estrutura de lista de um banco genérico |
| Result backend no Redis | Usar RabbitMQ também como result backend (`rpc://`) | RabbitMQ não é indicado como result backend do Celery — o `rpc://` cria uma fila de resposta por cliente e não persiste resultado, diferente do Redis que guarda com TTL e sobrevive a reconexão |
| Usuário próprio (`app`/`app`) em vez de `guest` | Usar as credenciais padrão (`guest`/`guest`) da imagem | O usuário `guest` só autentica via `localhost` por padrão (`loopback_users`) — como `worker`/`backend`/`flower` conectam pela rede do Compose (não é loopback do container do RabbitMQ), a conexão seria recusada (`ACCESS_REFUSED`). Criar um usuário via `RABBITMQ_DEFAULT_USER`/`RABBITMQ_DEFAULT_PASS` evita a restrição, no mesmo padrão que o projeto já usa pro MySQL (`MYSQL_USER`/`MYSQL_PASSWORD`) |
| Imagem `rabbitmq:3-management-alpine` | Imagem `rabbitmq:3-alpine` (sem management) | A variante `management` já vem com o plugin de UI habilitado, sem passo extra — mesmo espírito do Flower e do Adminer: observabilidade sempre disponível em `docker compose up -d` |

## O que aprendi

- Escolher o broker do Celery é 100% configuração de URL — `celery_app = Celery("app", broker=settings.CELERY_BROKER_URL, ...)` não sabe (nem precisa saber) qual broker está por trás, então nenhuma task ou endpoint precisa de lógica específica de RabbitMQ.
- O usuário `guest` do RabbitMQ tem uma trava de segurança pouco óbvia: só autentica de `localhost`. Em qualquer topologia com containers separados (Docker Compose, Kubernetes) isso derruba a conexão com `ACCESS_REFUSED (403)` mesmo com senha correta — o erro engana porque parece autenticação errada, mas é restrição de origem.
- RabbitMQ não guarda resultado de task de forma persistente como result backend — por isso a arquitetura recomendada do Celery é **broker especializado (RabbitMQ) + result backend especializado (Redis/DB)**, cada um focado no que faz bem, em vez de um serviço só fazendo os dois papéis.
- A imagem `rabbitmq:3-management-alpine` expõe duas portas: `5672` (protocolo AMQP, é o que o Celery usa) e `15672` (HTTP, a Management UI) — confundir as duas é um erro comum ao configurar `CELERY_BROKER_URL` (que deve sempre apontar pra `5672`).
- `rabbitmq-diagnostics -q ping` é o healthcheck oficial recomendado pela imagem — mais confiável que checar só se a porta está aberta, porque verifica se o broker Erlang interno já terminou de subir (RabbitMQ demora mais que Redis pra ficar pronto, daí o `start_period: 20s`).

## Referências

- [RabbitMQ — AMQP 0-9-1 Model Explained](https://www.rabbitmq.com/tutorials/amqp-concepts.html)
- [Celery — RabbitMQ as broker](https://docs.celeryq.dev/en/stable/getting-started/backends-and-brokers/rabbitmq.html)
- [RabbitMQ — Access Control (guest user loopback restriction)](https://www.rabbitmq.com/access-control.html)
- [RabbitMQ — Docker Hub official image](https://hub.docker.com/_/rabbitmq)
- [Celery — Result Backends](https://docs.celeryq.dev/en/stable/userguide/configuration.html#task-result-backend-settings)
