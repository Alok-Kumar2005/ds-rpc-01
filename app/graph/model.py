from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from langchain.prompts import PromptTemplate

class Router(BaseModel):
    """Router model for route through different nodes"""
    post: Literal["engineering", "finance", "general", "hr", "marketing"] = Field(..., description="Give the proper answer on the basis of understanding the user question and prompt")
    voice: Literal["Yes", "No"] = Field(..., description="if the user want the answer in the Voice format then return 'Yes' else return 'No'")





# from langchain_google_genai import ChatGoogleGenerativeAI 

# llm = ChatGoogleGenerativeAI(model = "gemini-1.5-flash") 

# # Fix: Add input_variables and use {question} placeholder
# prompt = PromptTemplate( 
#     input_variables=["question"],
#     template="""You are an helpful assistant that help to generalize the user problem in correct category 
#     1. engineering: return when question is for engineering department 
#     2. finance: return when question for finance department 
#     3. general: when general question are asked 
#     4. hr: when question for hr 
#     5. marketing: when question for marketing team 
    
#     User question: {question}
#     """ 
# ) 

# structured_llm = llm.with_structured_output(Router) 

# chain = prompt | structured_llm 

# result = chain.invoke({"question": "can you tell me about the engineering requirement in voice note"})

# print(result.post)
# print(result.voice)