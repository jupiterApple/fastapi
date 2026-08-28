from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "PDI Backend"
    SQLALCHEMY_DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Cache
    REDIS_URL: str = "redis://redis:6379/0"
    CACHE_TTL_SECONDS: int = 60

    # Filas (Celery) — broker é RabbitMQ (AMQP); result backend segue no Redis
    # (RabbitMQ não é indicado como result backend do Celery, só como broker)
    CELERY_BROKER_URL: str = "amqp://app:app@rabbitmq:5672//"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/1"

    # Email (SMTP — Ethereal em dev, nunca entrega de verdade)
    SMTP_HOST: str = "smtp.ethereal.email"
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_FROM: str = "PDI Backend <no-reply@pdi-backend.dev>"

    # IA (Claude API) — geração de bio via prompt engineering
    ANTHROPIC_API_KEY: str
    ANTHROPIC_MODEL: str = "claude-opus-5"

    # Seed do usuário inicial
    FIRST_SUPERUSER_EMAIL: str | None = None
    FIRST_SUPERUSER_PASSWORD: str | None = None
    FIRST_SUPERUSER_NAME: str = "Admin"

    # CORS
    BACKEND_CORS_ORIGINS: str = "http://localhost:8081,http://127.0.0.1:8081"

    class Config:
        env_file = ".env"


settings = Settings()
