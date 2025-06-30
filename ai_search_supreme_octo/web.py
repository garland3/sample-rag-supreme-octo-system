"""
Web interface for AI Search Supreme Octo.
FastAPI application with WebSocket support for real-time progress updates.
"""
import os
from typing import Dict, Any
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import json
import asyncio
from datetime import datetime
import logging

from .rag_system import RAGSystem
from .models import ProgressUpdate

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")))
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Search Supreme Octo",
    description="A modern RAG system for research-backed AI answers",
    version="1.0.0"
)

# Get template and static directories relative to this file
template_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")

# Mount static files and templates
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

if os.path.exists(template_dir):
    templates = Jinja2Templates(directory=template_dir)
else:
    templates = None

# Initialize RAG system
rag_system = RAGSystem()

# Store active WebSocket connections
active_connections: Dict[str, WebSocket] = {}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main web interface."""
    if templates:
        return templates.TemplateResponse("index.html", {"request": request})
    else:
        # Fallback HTML if templates not available
        return HTMLResponse("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>AI Search Supreme Octo</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .container { max-width: 800px; margin: 0 auto; }
                input, textarea { width: 100%; padding: 10px; margin: 10px 0; }
                button { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }
                #result { margin-top: 20px; padding: 15px; border: 1px solid #ddd; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔍 AI Search Supreme Octo</h1>
                <p>A modern RAG system for research-backed AI answers</p>
                <input type="text" id="question" placeholder="Enter your research question...">
                <button onclick="startResearch()">Research</button>
                <div id="result"></div>
            </div>
            <script>
                async function startResearch() {
                    const question = document.getElementById('question').value;
                    if (!question) return;
                    
                    const resultDiv = document.getElementById('result');
                    resultDiv.innerHTML = 'Researching...';
                    
                    try {
                        const response = await fetch('/api/research', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({question: question})
                        });
                        const result = await response.json();
                        resultDiv.innerHTML = '<h3>Answer:</h3><p>' + result.answer + '</p>';
                    } catch (error) {
                        resultDiv.innerHTML = 'Error: ' + error.message;
                    }
                }
            </script>
        </body>
        </html>
        """)


@app.post("/api/research")
async def research_api(request: Request):
    """API endpoint for research questions."""
    data = await request.json()
    question = data.get("question", "")
    
    if not question:
        return {"error": "Question is required"}
    
    try:
        result = await rag_system.research_question(question)
        return {
            "answer": result.answer,
            "session_id": result.session_id,
            "research_steps": len(result.research_steps) if result.research_steps else 0
        }
    except Exception as e:
        logger.error(f"Research error: {str(e)}")
        return {"error": str(e)}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time research with progress updates."""
    await websocket.accept()
    connection_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    active_connections[connection_id] = websocket
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "query":
                question = message.get("content", "")
                max_search_queries = message.get("max_search_queries", 3)
                max_iterations = message.get("max_iterations", 3)
                
                if not question:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Question is required"
                    }))
                    continue
                
                # Progress callback function
                async def progress_callback(update: ProgressUpdate):
                    await websocket.send_text(json.dumps({
                        "type": "progress",
                        "step": update.step_number,
                        "total": update.total_steps,
                        "status": update.status,
                        "message": update.message
                    }))
                
                try:
                    # Perform research
                    result = await rag_system.research_question(
                        question=question,
                        max_search_queries=max_search_queries,
                        max_iterations=max_iterations,
                        progress_callback=progress_callback
                    )
                    
                    # Send final result
                    await websocket.send_text(json.dumps({
                        "type": "result",
                        "answer": result.answer,
                        "session_id": result.session_id,
                        "research_steps": [
                            {
                                "query": step.query,
                                "analysis": step.analysis,
                                "timestamp": step.timestamp.isoformat()
                            }
                            for step in (result.research_steps or [])
                        ],
                        "evaluation": ({
                            "overall_score": result.evaluation_result.overall_score,
                            "action": result.evaluation_result.action.value,
                            "reasoning": result.evaluation_result.reasoning,
                            "metrics": {
                                "accuracy": result.evaluation_result.metrics.accuracy,
                                "completeness": result.evaluation_result.metrics.completeness,
                                "relevance": result.evaluation_result.metrics.relevance,
                                "clarity": result.evaluation_result.metrics.clarity,
                                "confidence": result.evaluation_result.metrics.confidence
                            }
                        } if result.evaluation_result else None)
                    }))
                    
                except Exception as e:
                    logger.error(f"Research error: {str(e)}")
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": str(e)
                    }))
                    
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        # Clean up connection
        if connection_id in active_connections:
            del active_connections[connection_id]


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


def create_app():
    """Factory function to create the FastAPI app."""
    return app


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
