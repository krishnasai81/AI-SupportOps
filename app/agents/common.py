import json
import re

from app.llm import get_llm_provider


async def call_llm(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.1,
    max_tokens: int = 700
) -> str:

    llm = get_llm_provider()

    try:
        return await llm.generate(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )

    finally:
        await llm.close()


def parse_json_response(response: str) -> dict:

    try:
        return json.loads(response)

    except json.JSONDecodeError:
        pass

    match = re.search(
        r"\{.*\}",
        response,
        flags=re.DOTALL
    )

    if not match:
        raise ValueError("LLM did not return valid JSON.")

    return json.loads(match.group(0))