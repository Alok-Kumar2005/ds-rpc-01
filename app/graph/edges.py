from state import AgentState
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
    

