from app.agents.common import (
    call_llm,
    parse_json_response
)


async def troubleshooting_agent(state: dict) -> dict:

    context = "\n".join(
        item["content"]
        for item in state["knowledge_context"]
    )

    system_prompt = """
You are the Technical Troubleshooting Agent for CloudDesk.

Analyze technical support problems and recommend safe diagnostic steps.

Rules:
1. Prefer the supplied knowledge base.
2. Never invent company-specific procedures.
3. Never ask for passwords, OTPs, API keys or secret tokens.
4. Never claim that a problem has been fixed.
5. If there is insufficient information, request clarification.
6. Return valid JSON only.

Format:

{
  "steps": [
    "Step one",
    "Step two"
  ]
}
"""

    user_prompt = f"""
Ticket:
{state['description']}

Retrieved knowledge:
{context if context else "No relevant knowledge base content found."}

Provide up to five safe diagnostic steps.
If the knowledge is insufficient, say so in the steps.
"""

    try:

        response = await call_llm(
            system_prompt,
            user_prompt,
            max_tokens=500
        )

        result = parse_json_response(response)

        steps = result.get("steps", [])

        if not isinstance(steps, list):
            steps = []

        steps = [
            str(step)[:500]
            for step in steps[:5]
            if isinstance(step, str) and step.strip()
        ]

    except Exception:

        steps = [
            "We need additional information to diagnose this issue.",
            "Please provide the exact error message without sharing passwords or security codes."
        ]

    return {
        "troubleshooting_steps": steps,
        "current_agent": "troubleshooting_agent",
        "agent_trace": state["agent_trace"] + [
            "troubleshooting_agent"
        ]
    }