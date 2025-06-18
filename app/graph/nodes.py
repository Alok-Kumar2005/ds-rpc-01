
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model import Router
from state import AgentState
from utils.prompt import router_template
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from llm_config import gemini_model 
from dotenv import load_dotenv

load_dotenv()


def route_node(state: AgentState)-> AgentState:
    llm = ChatGoogleGenerativeAI(model = gemini_model, google_api_key = os.getenv('GOOGLE_API_KEY'))
    structured_llm = llm.with_structured_output(Router)
    prompt = PromptTemplate.from_template(router_template)
    chain = prompt | structured_llm
    result = chain.invoke({"question": state['user_question']})
    return {
        "post": result.post,
        "voice": result.voice
    }