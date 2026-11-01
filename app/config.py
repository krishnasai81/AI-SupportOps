from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    APP_NAME: str = "AI SupportOps"
    DATABASE_URL: str = "sqlite:///./supportops.db"

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
    APPROVAL_API_KEY: SecretStr | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()