from app.agents.escalation_agent import evaluate_escalation
from app.workflow.supervisor import (
    supervisor_agent,
    route_after_supervisor
)


def make_state(
    category="general",
    priority="medium",
    confidence=0.95,
    subject="General question",
    description="I need some information."
):

    return {
        "ticket_id": 1,
        "customer_id": 1,
        "customer_email": "test@example.com",
        "subject": subject,
        "description": description,
        "category": category,
        "priority": priority,
        "classification_confidence": confidence,
        "supervisor_decision": "",
        "knowledge_context": [],
        "knowledge_found": False,
        "troubleshooting_steps": [],
        "draft_response": "",
        "final_response": "",
        "needs_human_review": False,
        "escalation_reason": "",
        "current_agent": "",
        "agent_trace": [],
        "error": ""
    }


def test_technical_ticket_routes_to_troubleshooting():

    state = make_state(category="technical")

    result = supervisor_agent(state)

    assert route_after_supervisor(result) == (
        "troubleshooting_agent"
    )


def test_billing_ticket_routes_to_response():

    state = make_state(category="billing")

    result = supervisor_agent(state)

    assert route_after_supervisor(result) == (
        "response_agent"
    )


def test_refund_request_requires_human_review():

    state = make_state(
        category="billing",
        subject="Refund request",
        description="Please refund my payment."
    )

    needs_review, reason = evaluate_escalation(state)

    assert needs_review is True
    assert "refund request" in reason


def test_critical_ticket_requires_human_review():

    state = make_state(priority="critical")

    needs_review, reason = evaluate_escalation(state)

    assert needs_review is True
    assert "Critical-priority ticket" in reason


def test_low_confidence_requires_human_review():

    state = make_state(confidence=0.30)

    needs_review, reason = evaluate_escalation(state)

    assert needs_review is True
    assert "Low classification confidence" in reason


def test_normal_ticket_does_not_require_review():

    state = make_state()

    needs_review, reason = evaluate_escalation(state)

    assert needs_review is False
    assert reason == ""