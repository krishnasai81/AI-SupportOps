from app.agents.escalation_agent import (
    detect_sensitive_action,
    evaluate_escalation
)


def make_state(
    subject="General question",
    description="I need help with my account.",
    priority="medium",
    confidence=0.95
):

    return {
        "subject": subject,
        "description": description,
        "priority": priority,
        "classification_confidence": confidence
    }


def test_refund_detection():

    result = detect_sensitive_action(
        "Please refund my payment."
    )

    assert result == "refund"


def test_account_modification_detection():

    result = detect_sensitive_action(
        "Please change my email address."
    )

    assert result == "account_modification"


def test_subscription_modification_detection():

    result = detect_sensitive_action(
        "I want to cancel my subscription."
    )

    assert result == "subscription_modification"


def test_security_concern_detection():

    result = detect_sensitive_action(
        "My account has been hacked."
    )

    assert result == "security_concern"


def test_critical_ticket_escalation():

    state = make_state(priority="critical")

    needs_review, reason = evaluate_escalation(state)

    assert needs_review is True
    assert "Critical-priority ticket" in reason


def test_low_confidence_escalation():

    state = make_state(confidence=0.30)

    needs_review, reason = evaluate_escalation(state)

    assert needs_review is True
    assert "Low classification confidence" in reason


def test_normal_ticket_no_escalation():

    state = make_state()

    needs_review, reason = evaluate_escalation(state)

    assert needs_review is False
    assert reason == ""