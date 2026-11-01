import re


SENSITIVE_PATTERNS = {
    "refund": [
        r"\brefund\b",
        r"\bmoney\s+back\b",
        r"\breverse\s+(?:the\s+)?payment\b",
        r"\bchargeback\b",
    ],
    "account_modification": [
        r"\bchange\s+(?:my\s+)?(?:email|password|phone|username)\b",
        r"\bupdate\s+(?:my\s+)?account\b",
        r"\bdelete\s+(?:my\s+)?account\b",
        r"\bmodify\s+(?:my\s+)?account\b",
    ],
    "subscription_modification": [
        r"\bcancel\s+(?:my\s+)?subscription\b",
        r"\bchange\s+(?:my\s+)?plan\b",
        r"\bupgrade\s+(?:my\s+)?plan\b",
        r"\bdowngrade\s+(?:my\s+)?plan\b",
    ],
    "security_concern": [
        r"\bunauthorized\s+access\b",
        r"\bhacked\b",
        r"\bsecurity\s+(?:breach|issue|concern|threat)\b",
        r"\bsuspicious\s+login\b",
        r"\baccount\s+compromised\b",
        r"\bstolen\s+account\b",
        r"\bdata\s+breach\b",
        r"\bphishing\b",
    ],
}


def detect_sensitive_action(text: str) -> str | None:

    if not text:
        return None

    text = text.lower()

    for action_type, patterns in SENSITIVE_PATTERNS.items():

        for pattern in patterns:

            if re.search(pattern, text):
                return action_type

    return None


def evaluate_escalation(state: dict) -> tuple[bool, str]:

    ticket = state.get("ticket", {})

    subject = state.get("subject") or ticket.get("subject", "")
    description = state.get("description") or ticket.get("description", "")

    combined_text = f"{subject} {description}"

    sensitive_action = detect_sensitive_action(combined_text)

    priority = str(
        state.get("priority") or ticket.get("priority", "")
    ).lower()

    confidence = state.get(
        "confidence",
        state.get("classification_confidence", 1.0)
    )

    reasons = []

    if sensitive_action:

        if sensitive_action == "refund":
            reasons.append("refund request requires human approval")
        else:
            reasons.append(
                f"{sensitive_action.replace('_', ' ')} requires human review"
            )

    if priority == "critical":
        reasons.append("Critical-priority ticket")

    try:

        if float(confidence) < 0.60:
            reasons.append("Low classification confidence")

    except (TypeError, ValueError):

        reasons.append(
            "Classification confidence could not be verified"
        )

    return bool(reasons), "; ".join(reasons)


def escalation_agent(state: dict) -> dict:
    """Escalation agent with previous approval awareness."""

    subject = state.get("subject", "")
    description = state.get("description", "")

    combined_text = f"{subject} {description}"

    sensitive_action = detect_sensitive_action(combined_text)

    previous_status = state.get("existing_approval_status", "")
    previous_action = state.get("existing_approval_action", "")

    # Check whether this exact action was already reviewed.
    already_reviewed = (
        sensitive_action is not None
        and sensitive_action == previous_action
        and previous_status in ("approved", "rejected")
    )

    if already_reviewed:

        if previous_status == "approved":

            response = (
                "Your request has passed human review. "
                "The requested action is authorized for a separately "
                "controlled manual process. No refund, account change, "
                "or subscription modification has been executed "
                "automatically. Our support team can proceed with "
                "the appropriate next step."
            )

            reason = "This action has already received human approval."

        else:

            response = (
                "Your request was reviewed by our support team, "
                "but the requested action was not approved. "
                "No refund, account change, or subscription "
                "modification has been performed. Our support team "
                "can assist with alternative options."
            )

            reason = "This action was previously rejected by human review."

        return {
            "needs_human_review": False,
            "escalation_reason": reason,
            "approval_action": sensitive_action,
            "escalation_response": response,
            "final_response": response,
        }

    # No previous decision for this action: use normal escalation.
    needs_review, reason = evaluate_escalation(state)

    response = state.get("final_response", "")

    if needs_review:

        response = (
            "Your request has been received and requires review by our "
            "support team. No account, billing, or subscription changes "
            "have been performed. Our team will review your request "
            "and follow up."
        )

    return {
        "needs_human_review": needs_review,
        "escalation_reason": reason,
        "approval_action": sensitive_action or "",
        "escalation_response": response if needs_review else "",
        "final_response": response,
    }