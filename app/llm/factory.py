from app.config import settings
from app.llm.openai_compatible import OpenAICompatibleProvider


def get_llm_provider():

    provider = settings.LLM_PROVIDER.lower()

    if provider == "groq":

        if not settings.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is missing. Add it to your .env file."
            )

        return OpenAICompatibleProvider(
            api_key=settings.GROQ_API_KEY.get_secret_value(),
            base_url="https://api.groq.com/openai/v1",
            model=settings.GROQ_MODEL,
            timeout=settings.LLM_TIMEOUT_SECONDS
        )

    elif provider == "ollama":

        return OpenAICompatibleProvider(
            api_key="ollama",
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
            timeout=settings.LLM_TIMEOUT_SECONDS
        )

    else:
        raise ValueError(
            f"Unsupported LLM provider: {provider}"
        )