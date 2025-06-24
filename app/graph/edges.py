from langgraph.graph import END
from graph.state import AgentState
from typing import Literal

def select_workflow(state: AgentState) -> Literal[
    "EngineeringNode",
    "FinanceNode", 
    "MarketingNode",
    "HRNode",
    "GeneralNode"
]:
    workflow = state["post"]
    if workflow == "engineering":
        return "EngineeringNode"
    elif workflow == "finance":
        return "FinanceNode"
    elif workflow == "marketing":
        return "MarketingNode"
    elif workflow == "general":
        return "GeneralNode"
    else:
        return "HRNode" 
    
def eng_conditional_edge(state: AgentState):
    workflow = state["voice"]
    if workflow == "No": 
        return END
    else:
        return "VoiceNode"
    
def fin_conditional_edge(state: AgentState):
    workflow = state["voice"]
    if workflow == "No":
        return END
    else:
        return "VoiceNode"
    
def mar_conditional_edge(state: AgentState):
    workflow = state["voice"]
    if workflow == "No": 
        return END
    else:
        return "VoiceNode"
    
def gen_conditional_edge(state: AgentState):
    workflow = state["voice"]
    if workflow == "No": 
        return END
    else:
        return "VoiceNode"
    
def hr_conditional_edge(state: AgentState):
    workflow = state["voice"]
    if workflow == "No":  
        return END
    else:
        return "VoiceNode"