from typing import TypedDict

class AgentState(TypedDict):
    user_question: str
    voice: str
    post: str
    response: str