from state import AgentState
from nodes import route_node
from langgraph.graph import END, START, StateGraph


def create_workflow():
    graph_builder = StateGraph(AgentState)

    graph_builder.add_node("route_node", route_node)

    graph_builder.add_edge(START, "route_node")

    graph_builder.add_edge("route_node", END)

    return graph_builder


graph = create_workflow().compile()

# Fixed: Pass a proper state dictionary instead of separate parameters
test_state = {
    "user_question": "can you tell me about the engineering requirement in voice note",
    "voice": "",
    "post": "",
    "response": "",
    "audio_buffer": b""
}

print(graph.invoke(test_state))