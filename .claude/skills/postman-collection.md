---
name: postman-collection
description: Manter a collection Postman (API_Collection.postman_collection.json) sincronizada com os endpoints da API — atualizar sempre que um endpoint for criado, alterado ou removido, e testar antes de reportar pronto.
---

# postman-collection

A collection em [API_Collection.postman_collection.json](../../API_Collection.postman_collection.json) é a forma de testar a API manualmente (Postman/Newman) fora do Swagger. Ela precisa refletir exatamente os endpoints que existem — não é opcional nem "depois eu atualizo".

## Quando atualizar

- Endpoint novo criado em qualquer `app/api/v1/*.py` → adicionar request novo na collection.
- Endpoint existente mudou (rota, método, body, auth) → atualizar o request correspondente.
- Endpoint removido → remover o request correspondente.

Isso faz parte de "terminar" a tarefa, no mesmo nível que rodar os testes — não um passo separado que pode ficar pendente.

## Estrutura da collection

- Um `item` de nível superior por *recurso* (ex.: "Autenticação", "Usuários (CRUD)") — agrupa os requests daquele router. Endpoint de router novo sem grupo existente → criar um grupo novo.
- Dentro de cada grupo, um `item` por endpoint, seguindo os já existentes como modelo (`Get User by ID`, `Create User`, etc.).
- Auth: rotas protegidas usam `{ "key": "Authorization", "value": "Bearer {{auth_token}}", "type": "text" }` no header — a variável `auth_token` é preenchida automaticamente pelo script de teste do request "Login". Não duplicar lógica de login em outros requests.
- `description` de cada request documenta: o que o endpoint faz, se precisa de auth (🔒), body esperado (se houver) e a tabela de status codes — mesmo formato dos requests existentes.
- Toda URL usa `{{base_url}}` (variável, nunca `localhost:8000` hardcoded), com `path` quebrado em array de segmentos.

## Template de request novo

```json
{
  "name": "Nome Descritivo Da Ação",
  "request": {
    "method": "POST",
    "header": [
      { "key": "Content-Type", "value": "application/json" },
      { "key": "Authorization", "value": "Bearer {{auth_token}}", "type": "text" }
    ],
    "body": {
      "mode": "raw",
      "raw": "{\n  \"campo\": \"valor\"\n}"
    },
    "url": {
      "raw": "{{base_url}}/api/v1/recurso/1/acao",
      "host": ["{{base_url}}"],
      "path": ["api", "v1", "recurso", "1", "acao"]
    },
    "description": "O que o endpoint faz.\n\n🔒 **Requer Autenticação**: Sim\n\n**Status Codes:**\n- `200` - Sucesso\n- `401` - Token inválido/expirado\n- `404` - Não encontrado"
  },
  "response": []
}
```

Omitir `header`/`body` quando o endpoint não usa (GET/DELETE sem `Content-Type`).

## Depois de atualizar: testar de verdade

Atualizar o JSON não é suficiente — confirmar que o request funciona contra a API rodando (`docker compose up -d --build` já feito):

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@local.dev","password":"admin123"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

curl -X POST http://localhost:8000/api/v1/recurso/1/acao \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"campo": "valor"}'
```

Exceção: endpoint que depende de credencial paga/externa que não deve ser gasta sem confirmação explícita do usuário (ex.: Claude API) — aí só validar a forma da requisição (Swagger reconhece a rota, schema correto) e deixar o teste com chamada real documentado como passo manual separado, sem executá-lo sozinho.

## Anti-padrões (não fazer)

- ❌ Criar o endpoint e deixar a collection defasada "pra depois"
- ❌ Hardcodar `localhost:8000` em vez de `{{base_url}}`
- ❌ Duplicar o script de captura de token em requests que não são o login
- ❌ Adicionar o request sem `description` (a collection também é documentação)
- ❌ Marcar a tarefa como pronta sem ter testado o request contra a API rodando (ou documentado por que não foi testado)
