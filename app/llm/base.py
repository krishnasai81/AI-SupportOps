from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):

    @abstractmethod
    async def generate(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 512
    ) -> str:
        """Generate a response from the LLM."""
        pass