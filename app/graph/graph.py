from graph.state import AgentState
from graph.nodes import route_node, EngineeringNode, FinanceNode, MarketingNode, HRNode, GeneralNode, VoiceNode, MemoryNode
from langgraph.graph import END, START, StateGraph
from graph.edges import select_workflow, eng_conditional_edge, fin_conditional_edge, gen_conditional_edge, hr_conditional_edge, mar_conditional_edge

def create_workflow():
    graph_builder = StateGraph(AgentState)
    
    # Adding nodes
    graph_builder.add_node("route_node", route_node)
    graph_builder.add_node("EngineeringNode", EngineeringNode)
    graph_builder.add_node("FinanceNode", FinanceNode)
    graph_builder.add_node("MarketingNode", MarketingNode)
    graph_builder.add_node("HRNode", HRNode)
    graph_builder.add_node("GeneralNode", GeneralNode)
    graph_builder.add_node("VoiceNode", VoiceNode)
    graph_builder.add_node("MemoryNode", MemoryNode)
    
    # Adding edges
    graph_builder.add_edge(START, "route_node")
    graph_builder.add_conditional_edges("route_node", select_workflow)
    
    # All workflow nodes now go to MemoryNode first, then check for voice
    graph_builder.add_edge("EngineeringNode", "MemoryNode")
    graph_builder.add_edge("FinanceNode", "MemoryNode")
    graph_builder.add_edge("MarketingNode", "MemoryNode")
    graph_builder.add_edge("HRNode", "MemoryNode")
    graph_builder.add_edge("GeneralNode", "MemoryNode")
    
    # From MemoryNode, check if voice response is needed
    graph_builder.add_conditional_edges("MemoryNode", lambda state: "VoiceNode" if state["voice"] == "Yes" else END)
    graph_builder.add_edge("VoiceNode", END)
    
    # Compile without checkpointer for simplicity
    return graph_builder.compile()

Graph = create_workflow()