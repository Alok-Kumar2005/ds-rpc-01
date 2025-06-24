import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import base64
import tempfile
import io
from cartesia import Cartesia
from graph.model import Router
from graph.state import AgentState
from graph.utils.prompt import router_template, engineering_prompt, finance_prompt, general_prompt, hr_prompt, marketing_prompt
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
        prompt = PromptTemplate.from_template(engineering_prompt)
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
    

cartesia_client = None
try:
    cartesia_api_key = os.getenv('CARTESIA_API_KEY')
    if cartesia_api_key:
        cartesia_client = Cartesia(api_key=cartesia_api_key)
except Exception as e:
    logging.error(f"Failed to initialize Cartesia client: {str(e)}")

def VoiceNode(state: AgentState) -> AgentState:
    try:
        logging.info("Enter Voice Node")
        response_text = state.get("response", "")
        
        if not response_text:
            return {"audio": ""}
        
        if not cartesia_client:
            logging.error("Cartesia client not initialized")
            return {"audio": ""}
        
        # voice_id = os.getenv('CARTESIA_VOICE_ID')
        voice_id = "ef8390dc-0fc0-473b-bbc0-7277503793f7"
        
        # Generate audio using the new API
        audio_generator = cartesia_client.tts.bytes(
            model_id="sonic",
            transcript=response_text,
            voice={
                "mode": "id",
                "id": voice_id
            },
            language="en",
            output_format={
                "container": "raw",
                "sample_rate": 16000,
                "encoding": "pcm_f32le"
            }
        )
        
        # Collect all audio chunks
        audio_chunks = []
        for chunk in audio_generator:
            audio_chunks.append(chunk)
        
        # Combine all chunks into a single bytes object
        audio_data = b''.join(audio_chunks)
        
        # Convert raw PCM to WAV format for browser compatibility
        import wave
        import struct
        
        # Create WAV file in memory
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1) 
            wav_file.setsampwidth(4)  
            wav_file.setframerate(16000)
            wav_file.writeframes(audio_data)
        
        wav_buffer.seek(0)
        wav_bytes = wav_buffer.read()
        
        # Convert to base64 for JSON serialization
        audio_base64 = base64.b64encode(wav_bytes).decode('utf-8')
        
        return {
            "audio": audio_base64
        }
        
    except Exception as e:
        logging.error(f"Error in Voice Node: {str(e)}")
        return {"audio": ""}