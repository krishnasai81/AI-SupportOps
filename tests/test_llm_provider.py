from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.llm.openai_compatible import OpenAICompatibleProvider


@pytest.mark.asyncio
async def test_llm_generate_returns_response():

    provider = OpenAICompatibleProvider(
        api_key="test-key",
        base_url="https://example.com/v1",
        model="test-model"
    )

    fake_response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    content="Hello from AI SupportOps!"
                )
            )
        ]
    )

    provider.client.chat.completions.create = AsyncMock(
        return_value=fake_response
    )

    result = await provider.generate(
        messages=[
            {"role": "user", "content": "Say hello"}
        ]
    )

    assert result == "Hello from AI SupportOps!"

    await provider.close()