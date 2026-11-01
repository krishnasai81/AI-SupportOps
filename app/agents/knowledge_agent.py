from app.rag.retrieval import retrieve_relevant_chunks


def knowledge_agent(state: dict, db) -> dict:

    context = retrieve_relevant_chunks(
        db=db,
        query=(
            state["subject"] + "\n" +
            state["description"]
        ),
        top_k=4
    )

    return {
        "knowledge_context": context,
        "knowledge_found": bool(context),
        "current_agent": "knowledge_agent",
        "agent_trace": state["agent_trace"] + [
            "knowledge_agent"
        ]
    }