from app.agents.common import (
    call_llm,
    parse_json_response
)


VALID_CATEGORIES = {
    "billing",
    "technical",
    "account",
    "subscription",
    "general"
}

VALID_PRIORITIES = {
    "low",
    "medium",
    "high",
    "critical"
}


async def classification_agent(state: dict) -> dict:

    system_prompt = """
You are the Ticket Classification Agent for CloudDesk.

Classify customer support tickets.

Categories:
- billing
- technical
- account
- subscription
- general

Priorities:
- low
- medium
- high
- critical

Priority guidelines:
- low: General information requests.
- medium: Normal support issues.
- high: Significant service disruption or payment issue.
- critical: Severe outage, security incident, or urgent risk.

Return ONLY valid JSON:

{
  "category": "billing",
  "priority": "medium",
  "confidence": 0.95
}

Confidence must be between 0 and 1.
Do not invent information.
"""

    user_prompt = f"""
Ticket Subject: {state['subject']}

Ticket Description:
{state['description']}
"""

    try:

        response = await call_llm(
            system_prompt,
            user_prompt
        )

        result = parse_json_response(response)

        category = str(
            result.get("category", "general")
        ).lower()

        priority = str(
            result.get("priority", "medium")
        ).lower()

        confidence = float(
            result.get("confidence", 0.0)
        )

        if category not in VALID_CATEGORIES:
            category = "general"
            confidence = 0.0

        if priority not in VALID_PRIORITIES:
            priority = "medium"
            confidence = 0.0

        if not 0 <= confidence <= 1:
            confidence = 0.0

    except Exception:

        category = "general"
        priority = "medium"
        confidence = 0.0

    return {
        "category": category,
        "priority": priority,
        "classification_confidence": confidence,
        "current_agent": "classification_agent",
        "agent_trace": state["agent_trace"] + [
            "classification_agent"
        ]
    }