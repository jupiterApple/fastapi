from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "APP_FC_26"
    SQLALCHEMY_DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Cache
    REDIS_URL: str = "redis://redis:6379/0"
    CACHE_TTL_SECONDS: int = 60

    # Seed do usuário inicial
    FIRST_SUPERUSER_EMAIL: str | None = None
    FIRST_SUPERUSER_PASSWORD: str | None = None
    FIRST_SUPERUSER_NAME: str = "Admin"

    # CORS
    BACKEND_CORS_ORIGINS: str = "http://localhost:8081,http://127.0.0.1:8081"

    class Config:
        env_file = ".env"


settings = Settings()
