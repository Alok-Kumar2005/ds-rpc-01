from typing import TypedDict, List, Dict, Optional
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    user_question: str
    voice: str
    post: str
    response: str
    audio: bytes
    user_email: str 
    conversation_history: Optional[List[Dict]] 
    messages: List[BaseMessage]