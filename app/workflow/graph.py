from langgraph.graph import StateGraph, START, END

from app.workflow.state import SupportState
from app.workflow.supervisor import (
    supervisor_agent,
    route_after_supervisor
)

from app.agents.classification_agent import classification_agent
from app.agents.knowledge_agent import knowledge_agent
from app.agents.troubleshooting_agent import troubleshooting_agent
from app.agents.response_agent import response_agent
from app.agents.escalation_agent import escalation_agent


def build_support_graph(db):

    graph = StateGraph(SupportState)

    # Register agents.

    graph.add_node(
        "classification_agent",
        classification_agent
    )

    graph.add_node(
        "knowledge_agent",
        lambda state: knowledge_agent(state, db)
    )

    graph.add_node(
        "supervisor_agent",
        supervisor_agent
    )

    graph.add_node(
        "troubleshooting_agent",
        troubleshooting_agent
    )

    graph.add_node(
        "response_agent",
        response_agent
    )

    graph.add_node(
        "escalation_agent",
        escalation_agent
    )

    # Workflow connections.

    graph.add_edge(
        START,
        "classification_agent"
    )

    graph.add_edge(
        "classification_agent",
        "knowledge_agent"
    )

    graph.add_edge(
        "knowledge_agent",
        "supervisor_agent"
    )

    # Supervisor decides the next agent.

    graph.add_conditional_edges(
        "supervisor_agent",
        route_after_supervisor,
        {
            "troubleshooting_agent": "troubleshooting_agent",
            "response_agent": "response_agent"
        }
    )

    graph.add_edge(
        "troubleshooting_agent",
        "response_agent"
    )

    graph.add_edge(
        "response_agent",
        "escalation_agent"
    )

    graph.add_edge(
        "escalation_agent",
        END
    )

    return graph.compile()