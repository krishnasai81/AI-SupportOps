from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "AI SupportOps"
    DATABASE_URL: str = "sqlite:///./supportops.db"

    # Authentication. The default key is for local development only.
    ENVIRONMENT: str = "development"
    JWT_SECRET_KEY: SecretStr = SecretStr("local-development-only-change-this-secret")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # LLM
    LLM_PROVIDER: str = "groq"
    GROQ_API_KEY: SecretStr | None = None
    GROQ_MODEL: str = "openai/gpt-oss-20b"
    OLLAMA_BASE_URL: str = "http://localhost:11434/v1"
    OLLAMA_MODEL: str = "llama3.2:3b"
    LLM_TIMEOUT_SECONDS: float = 60.0

    # RAG
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    EMBEDDING_DIMENSION: int = 384
    CHUNK_SIZE: int = 900
    CHUNK_OVERLAP: int = 150
    RETRIEVAL_TOP_K: int = 4

    MAX_UPLOAD_SIZE_MB: int = 10
    MAX_VISION_UPLOAD_MB: int = 8
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
