import anthropic
from loguru import logger

from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserBioGenerated

anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """Você escreve bios curtas e profissionais para perfis de usuário de um backend de estudo.

Regras:
- headline: até 60 caracteres, sem ponto final.
- bio: 2 a 3 frases, terceira pessoa, sem inventar cargo ou empresa que não foram informados.
- tone: escolha "formal", "casual" ou "tecnico" conforme o nome/email sugerir.

Exemplo:
Entrada: Nome: Ana Souza / Email: ana.souza@empresa.com
Saída: headline="Ana Souza", bio="Ana integra a base de usuários da plataforma, com foco em manter o cadastro sempre atualizado.", tone="formal"
"""


def generate_user_bio(user: User) -> UserBioGenerated:
    logger.info("Gerando bio via Claude API user_id={user_id}", user_id=user.id)
    response = anthropic_client.messages.parse(
        model=settings.ANTHROPIC_MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Nome: {user.full_name or user.email}\nEmail: {user.email}",
            }
        ],
        output_format=UserBioGenerated,
    )
    logger.info("Bio gerada user_id={user_id}", user_id=user.id)
    return response.parsed_output
