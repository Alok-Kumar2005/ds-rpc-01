from fastapi import FastAPI
from pydantic import BaseModel
from graph.graph import Graph
from langchain_core.messages import HumanMessage
import uuid

app = FastAPI()

class QuestionRequest(BaseModel):
    user_question: str
    user_email: str  # Added to track user for memory

@app.get("/")
async def root():
    return {"status": "ok", "message": "Agent Chatbot API is running"}

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    state = {
        "user_question": request.user_question,
        "user_email": request.user_email,  # Pass user email for memory
        "voice": "",
        "post": "",
        "response": "",
        "audio": b"",
        "conversation_history": [],
        "messages": [HumanMessage(content=request.user_question)]
    }
    
    # If using checkpointing, uncomment the following lines:
    # thread_id = str(uuid.uuid4())
    # config = {"configurable": {"thread_id": thread_id}}
    # result = Graph.invoke(state, config=config)
    
    # For no checkpointing (simpler approach):
    result = Graph.invoke(state)
    
    response_data = {
        "response": result.get("response", ""),
        "audio": result.get("audio", ""),
        # "thread_id": thread_id  # Uncomment if using checkpointing
    }
    
    return response_data

@app.get("/history/{user_email}")
async def get_user_history(user_email: str, limit: int = 10):
    """Get user's conversation history from long-term memory"""
    from app.memory.longterm_memory import longterm_memory
    
    try:
        history = longterm_memory.get_user_history(user_email, limit)
        return {"history": history}
    except Exception as e:
        return {"error": str(e), "history": []}

@app.post("/search/{user_email}")
async def search_user_conversations(user_email: str, query: str, limit: int = 5):
    """Search user's past conversations"""
    from app.memory.longterm_memory import longterm_memory
    
    try:
        results = longterm_memory.search_user_conversations(user_email, query, limit)
        return {"results": results}
    except Exception as e:
        return {"error": str(e), "results": []}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)