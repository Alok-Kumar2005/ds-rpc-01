
from graph.state import AgentState
from graph.nodes import route_node, EngineeringNode, FinanceNode, MarketingNode, HRNode, GeneralNode, VoiceNode
from langgraph.graph import END, START, StateGraph
from graph.edges import select_workflow, eng_conditional_edge, fin_conditional_edge, gen_conditional_edge, hr_conditional_edge, mar_conditional_edge



def create_workflow():
    graph_builder = StateGraph(AgentState)

    # Addding nodes
    graph_builder.add_node("route_node", route_node)
    graph_builder.add_node("EngineeringNode", EngineeringNode)
    graph_builder.add_node("FinanceNode", FinanceNode)
    graph_builder.add_node("MarketingNode", MarketingNode)
    graph_builder.add_node("HRNode", HRNode)
    graph_builder.add_node("GeneralNode", GeneralNode)
    graph_builder.add_node("VoiceNode", VoiceNode)

    # Adding edges
    graph_builder.add_edge(START, "route_node")
    graph_builder.add_conditional_edges("route_node", select_workflow)
    graph_builder.add_conditional_edges("EngineeringNode", eng_conditional_edge)
    graph_builder.add_conditional_edges("FinanceNode", fin_conditional_edge) 
    graph_builder.add_conditional_edges("MarketingNode", mar_conditional_edge) 
    graph_builder.add_conditional_edges("HRNode", hr_conditional_edge) 
    graph_builder.add_conditional_edges("GeneralNode", gen_conditional_edge) 
    
    # Add END edges after each workflow node
    graph_builder.add_edge("VoiceNode", END)


    return graph_builder

Graph = create_workflow().compile()

# Test state
# test_state = {
#     "user_question": "What is microservices in Engineering",
#     "voice": "",
#     "post": "",
#     "response": ""
#     "audio": b""
# }

# print(Graph.invoke(test_state))