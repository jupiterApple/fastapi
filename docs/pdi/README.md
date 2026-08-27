# POCs de Estudo

Base: FastAPI + JWT + CRUD de users (branch `main`).

| #  | Tema                                             | Complexidade | Branch | Doc | Status     |
|----|---------------------------------------------------|--------------|--------|-----|------------|
| 1  | CI/CD                                              | —            | `poc/01-cicd`  | [01-cicd.md](01-cicd.md)   | ✅ concluído |
| 2  | Redis                                              | —            | `poc/02-redis` | [02-redis.md](02-redis.md) | ✅ concluído |
| 3  | Filas (Celery)                                     | —            | `poc/03-filas` | [03-filas.md](03-filas.md) | ✅ concluído |
| 4  | RabbitMQ como broker alternativo                   | Baixa        | `poc/04-rabbitmq` | [04-rabbitmq.md](04-rabbitmq.md) | ✅ concluído |
| 5  | Engenharia de prompt                               | Baixa-média  | —      | —   | ⏳ pendente |
| 6  | BFF                                                 | Baixa-média  | —      | —   | ⏳ pendente |
| 7  | AI Skills                                          | Média        | —      | —   | ⏳ pendente |
| 8  | AI Output Verification                             | Média        | —      | —   | ⏳ pendente |
| 9  | AI-Assisted Code Review                            | Média        | —      | —   | ⏳ pendente |
| 10 | AI-Assisted Debugging e Root Cause Analysis        | Média        | —      | —   | ⏳ pendente |
| 11 | AI-Assisted Test Design & Test Generation          | Média        | —      | —   | ⏳ pendente |
| 12 | AI-Based Failure Analysis (Pipeline Failures)      | Média-alta   | —      | —   | ⏳ pendente |
| 13 | Kubernetes                                         | Média-alta   | —      | —   | ⏳ pendente |
| 14 | Arquitetura e decomposição de solução com AI       | Alta         | —      | —   | ⏳ pendente |
| 15 | Clean Architecture (service/repository layer)      | Baixa-média  | —      | —   | ⏳ pendente |
| 16 | Diagramas UML                                      | Baixa        | —      | —   | ⏳ pendente |
| 17 | Criptografia de Dados                              | Média        | —      | —   | ⏳ pendente |
| 18 | OWASP Top 10 aplicado à API                        | Média        | —      | —   | ⏳ pendente |
| 19 | Observability - Tracing                            | Média        | —      | —   | ⏳ pendente |
| 20 | Bancos NoSQL (MongoDB)                             | Média        | —      | —   | ⏳ pendente |
| 21 | ElasticSearch                                      | Média-alta   | —      | —   | ⏳ pendente |
| 22 | Event-driven architecture                          | Média-alta   | —      | —   | ⏳ pendente |
| 23 | Agentes de IA (fundamentos)                        | Alta         | —      | —   | ⏳ pendente |
| 24 | Bases vetoriais                                    | Alta         | —      | —   | ⏳ pendente |
| 25 | RAG (Retrieval Augmented Generation)               | Alta         | —      | —   | ⏳ pendente |
| 26 | MCP (Model Context Protocol)                       | Alta         | —      | —   | ⏳ pendente |
| 27 | Orquestradores (LangChain/CrewAI)                  | Alta         | —      | —   | ⏳ pendente |
| 28 | Arquitetura multi-agente de IA                     | Alta         | —      | —   | ⏳ pendente |
| 29 | Guardrails                                         | Alta         | —      | —   | ⏳ pendente |
| 30 | Amazon Bedrock                                     | Alta         | —      | —   | ⏳ pendente |
| 31 | Deployment de LLMs e SLMs                          | Alta         | —      | —   | ⏳ pendente |
| 32 | Microservices Architecture                         | Altíssima    | —      | —   | ⏳ pendente |

Itens 5-14 vêm da lista **"Gap (10)"** do PDI real — skills marcadas como `Core` pro seu papel, com lacuna confirmada. Entram logo após o RabbitMQ por serem prioridade de papel, não por ordem de complexidade (por isso a complexidade oscila dentro desse bloco). "Engenharia de prompt" saiu do item que antes chamava "Agentes de IA (fundamentos + prompt engineering)" — agora é entrada própria, já que a matriz trata como skill Core separada; "Agentes de IA" (item 23) ficou só com os fundamentos de agente.

Itens 15-32 seguem a matriz mais ampla de skills ("Crescer"), ordenados por complexidade crescente e por dependência entre eles (ex.: RAG depende de Bases vetoriais; Guardrails/Orquestradores/Multi-agente dependem de já existir uma feature de IA rodando).

### Já praticado na base do projeto (sem POC numerado)

Estes itens da matriz já são exercidos desde a base do projeto, não por uma branch dedicada:

| Skill                                | Onde já aparece |
|----------------------------------------|------------------|
| Autenticação e Autorização              | JWT HS256 + rotas protegidas — [app/core/security.py](../../app/core/security.py), [app/api/deps.py](../../app/api/deps.py) |
| REST API — Padrões de autenticação      | Mesmo ponto acima (Bearer token via `OAuth2PasswordBearer`) |
| Observability - Logging                 | Loguru obrigatório em toda a aplicação (regra do `CLAUDE.md`) — parcial: sem correlation ID nem agregação centralizada |

### Fora do escopo deste repositório

- **Akka** — stack JVM/Scala, incompatível com o stack Python/FastAPI deste projeto.
- **Micro front-ends** — repositório é backend-only, sem frontend.
- **Low-code para experimentação** — não é uma técnica de engenharia de backend aplicável aqui.
- **Visão estratégica** — soft skill de gestão, não é um POC técnico de código.
- **Modelagem de dados** — já exercida continuamente em qualquer POC que mexa em modelo, não justifica branch dedicada.
