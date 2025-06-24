from fastapi import FastAPI
from pydantic import BaseModel
from graph.graph import Graph

app = FastAPI()

class QuestionRequest(BaseModel):
    user_question: str

@app.get("/")
async def root():
    return {"status": "ok", "message": "Agent Chatbot API is running"}

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    state = {
        "user_question": request.user_question,
        "voice": "",
        "post": "",
        "response": "",
        "audio": b""
    }
    
    result = Graph.invoke(state)
    
    response_data = {
        "response": result.get("response", ""),
        "audio": result.get("audio", "")  
    }
    
    return response_data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)