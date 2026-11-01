from openai import AsyncOpenAI, APIError

from app.llm.base import BaseLLMProvider


class LLMProviderError(Exception):
    """Raised when an LLM provider request fails."""
    pass


class OpenAICompatibleProvider(BaseLLMProvider):

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        timeout: float = 60.0
    ):
        self.model = model

        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=2
        )

    async def generate(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 512
    ) -> str:

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            content = response.choices[0].message.content

            if not content:
                raise LLMProviderError(
                    "The LLM returned an empty response."
                )

            return content.strip()

        except APIError as exc:
            raise LLMProviderError(
                f"LLM API request failed: {exc.__class__.__name__}"
            ) from exc

    async def close(self):
        await self.client.close()