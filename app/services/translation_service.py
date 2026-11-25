from app.agents.common import call_llm


SUPPORTED_LANGUAGE_HINT = """
Identify the customer's language. Preserve names, product names, IDs, amounts,
dates and technical error codes exactly. Do not add facts or change intent.
"""


async def normalize_ticket(subject: str, description: str, preferred_language: str | None = None) -> dict:
    prompt = f"""
{SUPPORTED_LANGUAGE_HINT}
Return only JSON with keys detected_language, normalized_subject and normalized_description.
Translate the following customer message into clear English for internal processing.
If it is already English, keep its meaning and wording.

Preferred customer response language hint: {preferred_language or "auto-detect"}
Subject: {subject}
Description: {description}
"""
    response = await call_llm(
        "You are a careful multilingual customer-support translation service. Return valid JSON only.",
        prompt,
        temperature=0.0,
        max_tokens=700,
    )
    from app.agents.common import parse_json_response
    data = parse_json_response(response)
    return {
        "detected_language": str(data.get("detected_language") or preferred_language or "en"),
        "normalized_subject": str(data.get("normalized_subject") or subject),
        "normalized_description": str(data.get("normalized_description") or description),
    }


async def localize_response(text: str, language: str) -> str:
    if not language or language.lower().startswith("en"):
        return text
    prompt = f"""
Translate the customer-facing support response into language code/name: {language}.
Keep ticket IDs, URLs, error codes and amounts unchanged. Do not add information.
Text:
{text}
"""
    try:
        return await call_llm(
            "You are a precise customer-support translator. Preserve meaning and tone.",
            prompt,
            temperature=0.0,
            max_tokens=700,
        )
    except Exception:
        return text
