import asyncio

from app.llm import get_llm_provider


async def main():

    llm = get_llm_provider()

    try:
        response = await llm.generate(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful customer support assistant."
                },
                {
                    "role": "user",
                    "content": "Explain what a failed payment means in two sentences."
                }
            ]
        )

        print("\nLLM RESPONSE:")
        print(response)

    finally:
        await llm.close()


if __name__ == "__main__":
    asyncio.run(main())