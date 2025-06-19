
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from model import Router
from state import AgentState
from utils.prompt import router_template
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.chains import RetrievalQA
from app.llm_config import gemini_model 
from app.logger import logging
from app.exception import CustomException
from app.Storage.Hybrid_ret import create_general_reranker,create_engineering_reranker,create_finance_summary_reranker,create_hr_reranker,create_marketing_reranker
from dotenv import load_dotenv

load_dotenv()
llm = ChatGoogleGenerativeAI(model = gemini_model, google_api_key = os.getenv('GOOGLE_API_KEY'))
parser = StrOutputParser()

def route_node(state: AgentState)-> AgentState:
    structured_llm = llm.with_structured_output(Router)
    prompt = PromptTemplate.from_template(router_template)
    chain = prompt | structured_llm
    result = chain.invoke({"question": state['user_question']})
    return {
        "post": result.post,
        "voice": result.voice
    }



def EngineeringNode(state: AgentState)->AgentState:
    try:
        logging.info("Enter Engineering Node")
        engineering_reranker = create_engineering_reranker()
        if engineering_reranker is None:
            raise CustomException("Failed to create engineering reranker", sys)
        
        eng_retrevial_chain = RetrievalQA.from_chain_type(
            llm = llm,
            chain_type = "stuff",
            retriever = engineering_reranker
        )
        result = eng_retrevial_chain.invoke({"query": state["user_question"]})
        
        return {
            "response": result["result"] 
        }
    except CustomException as e:
        logging.error(f"Error in Engineering Node : {str(e)}")
        raise CustomException(e, sys) from e
    
def FinanceNode(state: AgentState)->AgentState:
    try:
        logging.info("Enter Finance Node")
        finance_reranker = create_finance_summary_reranker()
        if finance_reranker is None:
            raise CustomException("Failed to create Finance reranker", sys)
        
        fin_retrevial_chain = RetrievalQA.from_chain_type(
            llm = llm,
            chain_type = "stuff",
            retriever = finance_reranker
        )
        result = fin_retrevial_chain.invoke({"query": state["user_question"]})
        
        return {
            "response": result["result"] 
        }
    except CustomException as e:
        logging.error(f"Error in Engineering Node : {str(e)}")
        raise CustomException(e, sys) from e
    
def GeneralNode(state: AgentState)->AgentState:
    try:
        logging.info("Enter General Node")
        general_reranker = create_general_reranker()
        if general_reranker is None:
            raise CustomException("Failed to create General reranker", sys)
        
        gen_retrevial_chain = RetrievalQA.from_chain_type(
            llm = llm,
            chain_type = "stuff",
            retriever = general_reranker
        )
        result = gen_retrevial_chain.invoke({"query": state["user_question"]})
        
        return {
            "response": result["result"] 
        }
    except CustomException as e:
        logging.error(f"Error in Engineering Node : {str(e)}")
        raise CustomException(e, sys) from e
    
def HRNode(state: AgentState)->AgentState:
    try:
        logging.info("Enter HR Node")
        hr_reranker = create_hr_reranker()
        if hr_reranker is None:
            raise CustomException("Failed to create HR reranker", sys)
        
        hr_retrevial_chain = RetrievalQA.from_chain_type(
            llm = llm,
            chain_type = "stuff",
            retriever = hr_reranker
        )
        result = hr_retrevial_chain.invoke({"query": state["user_question"]})
        
        return {
            "response": result["result"] 
        }
    except CustomException as e:
        logging.error(f"Error in Engineering Node : {str(e)}")
        raise CustomException(e, sys) from e
    
def MarketingNode(state: AgentState)->AgentState:
    try:
        logging.info("Enter Marketing Node")
        marketing_reranker = create_marketing_reranker()
        if marketing_reranker is None:
            raise CustomException("Failed to create Marketing reranker", sys)
        
        mar_retrevial_chain = RetrievalQA.from_chain_type(
            llm = llm,
            chain_type = "stuff",
            retriever = marketing_reranker
        )
        result = mar_retrevial_chain.invoke({"query": state["user_question"]})
        
        return {
            "response": result["result"] 
        }
    except CustomException as e:
        logging.error(f"Error in Engineering Node : {str(e)}")
        raise CustomException(e, sys) from e
    
