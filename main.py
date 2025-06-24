from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import asyncio
import json
from datetime import datetime
import uvicorn
import os
from dotenv import load_dotenv

from src.rag_system import RAGSystem

# Load environment variables
load_dotenv()

app = FastAPI(title="RAG Research System", description="A demo RAG system with Tavily search")

# Setup templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    rag_system = None
    
    try:
        while True:
            # Receive query from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "query":
                query = message["content"]
                
                # Create new RAG system instance for this session
                session_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                
                # Initialize RAG system with environment variables
                rag_system = RAGSystem(
                    tavily_api_key=os.getenv("TAVILY_API_KEY"),
                    llm_base_url=os.getenv("LLM_BASE_URL"),
                    llm_api_key=os.getenv("LLM_API_KEY"),
                    llm_model=os.getenv("LLM_MODEL", "gpt-3.5-turbo")
                )
                
                # Progress callback
                async def progress_callback(progress_update):
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "progress", 
                            "content": {
                                "step": progress_update.step_number,
                                "total": progress_update.total_steps,
                                "status": progress_update.status,
                                "message": progress_update.message
                            }
                        }),
                        websocket
                    )
                
                # Send initial status
                await manager.send_personal_message(
                    json.dumps({"type": "progress", "content": {"message": f"Starting research for: {query}"}}),
                    websocket
                )
                
                try:
                    # Process the query
                    result = await rag_system.research_question(query, session_id, progress_callback)
                    
                    # Send final result
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "result", 
                            "content": {
                                "answer": result.answer,
                                "session_id": result.session_id,
                                "total_steps": result.total_steps,
                                "research_steps": [
                                    {
                                        "step_number": step.step_number,
                                        "query": step.query,
                                        "analysis": step.analysis
                                    }
                                    for step in result.research_steps
                                ]
                            }
                        }),
                        websocket
                    )
                    
                except Exception as e:
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "error", 
                            "content": f"Error processing query: {str(e)}"
                        }),
                        websocket
                    )
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        if websocket in manager.active_connections:
            manager.disconnect(websocket)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
