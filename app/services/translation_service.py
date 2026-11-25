from app.agents.common import call_llm, parse_json_response

LANGUAGE_NAMES = {
    "en": "English", "hi": "Hindi", "te": "Telugu", "ta": "Tamil",
    "kn": "Kannada", "ml": "Malayalam", "bn": "Bengali", "mr": "Marathi",
    "gu": "Gujarati", "ur": "Urdu", "pa": "Punjabi",
}


async def normalize_ticket(subject: str, description: str, preferred_language: str = "auto") -> dict:
    prompt = f"""
Detect the language of this customer support ticket. Translate its subject and
description into clear English for internal support processing.
Return valid JSON only with keys: detected_language (BCP-47 or short language code),
normalized_subject, normalized_description.
Preserve names, product names, ticket IDs, URLs, amounts, dates and technical
error codes. Do not invent details. Use the language the customer actually wrote
in; the selected language is only a hint.
Selected language hint: {preferred_language}
Subject: {subject}
Description: {description}
"""
    try:
        raw = await call_llm(
            "You are a precise multilingual support-ticket translation service. Return JSON only.",
            prompt,
            temperature=0.0,
            max_tokens=700,
        )
        data = parse_json_response(raw)
        return {
            "detected_language": str(data.get("detected_language") or preferred_language or "und").strip().lower(),
            "normalized_subject": str(data.get("normalized_subject") or subject),
            "normalized_description": str(data.get("normalized_description") or description),
        }
    except Exception:
        # Preserve the original text if translation is unavailable.
        language = "und" if preferred_language == "auto" else preferred_language
        return {
            "detected_language": language,
            "normalized_subject": subject,
            "normalized_description": description,
        }


async def localize_response(text: str, language: str) -> str:
    language = (language or "en").lower()
    if language in {"en", "und", "auto"}:
        return text
    language_name = LANGUAGE_NAMES.get(language, language)
    try:
        return await call_llm(
            "You are a precise customer-support translator. Preserve meaning, tone, IDs, URLs, amounts and technical codes. Return only the translation.",
            f"Translate this support response into {language_name} ({language}):\n\n{text}",
            temperature=0.0,
            max_tokens=700,
        )
    except Exception:
        return text
