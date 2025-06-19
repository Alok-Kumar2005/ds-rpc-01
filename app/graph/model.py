from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from langchain.prompts import PromptTemplate

class Router(BaseModel):
    """Router model for route through different nodes"""
    post: Literal["engineering", "finance", "general", "hr", "marketing"] = Field(..., description="Give the proper answer on the basis of understanding the user question and prompt")
    voice: Literal["Yes", "No"] = Field(..., description="if the user want the answer in the Voice format then return 'Yes' else return 'No'")



