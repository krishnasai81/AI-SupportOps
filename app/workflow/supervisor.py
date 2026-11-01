def supervisor_agent(state: dict) -> dict:
    
    category = state["category"]

    if category == "technical":

        decision = "troubleshooting_agent"

    else:

        decision = "response_agent"

    return {
        "supervisor_decision": decision,
        "current_agent": "supervisor_agent",
        "agent_trace": state["agent_trace"] + [
            "supervisor_agent"
        ]
    }


def route_after_supervisor(state: dict) -> str:

    return state["supervisor_decision"]