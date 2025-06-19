from state import AgentState
from nodes import route_node, EngineeringNode, FinanceNode, MarketingNode, HRNode, GeneralNode
from langgraph.graph import END, START, StateGraph
from edges import select_workflow

def create_workflow():
    graph_builder = StateGraph(AgentState)

    # Addding nodes
    graph_builder.add_node("route_node", route_node)
    graph_builder.add_node("EngineeringNode", EngineeringNode)
    graph_builder.add_node("FinanceNode", FinanceNode)
    graph_builder.add_node("MarketingNode", MarketingNode)
    graph_builder.add_node("HRNode", HRNode)
    graph_builder.add_node("GeneralNode", GeneralNode)

    # Adding edges
    graph_builder.add_edge(START, "route_node")
    graph_builder.add_conditional_edges("route_node", select_workflow)
    
    # Add END edges after each workflow node
    graph_builder.add_edge("EngineeringNode", END)
    graph_builder.add_edge("FinanceNode", END)
    graph_builder.add_edge("MarketingNode", END)
    graph_builder.add_edge("HRNode", END)
    graph_builder.add_edge("GeneralNode", END)

    return graph_builder

graph = create_workflow().compile()

# Test state
test_state = {
    "user_question": "What is Quarterly Expense Breakdown in finance",
    "voice": "",
    "post": "",
    "response": "",
    "audio_buffer": b""
}

print(graph.invoke(test_state))