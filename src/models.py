"""
Pydantic models for the RAG system.
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class SearchResult(BaseModel):
    """Model for search results from Tavily."""
    title: str
    url: str
    content: str
    score: Optional[float] = None


class LLMRequest(BaseModel):
    """Model for LLM API requests."""
    model: str
    messages: List[Dict[str, str]]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000


class LLMResponse(BaseModel):
    """Model for LLM API responses."""
    content: str
    usage: Optional[Dict[str, Any]] = None


class ResearchStep(BaseModel):
    """Model for individual research steps."""
    step_number: int
    query: str
    search_results: List[SearchResult]
    analysis: str
    timestamp: datetime


class RAGRequest(BaseModel):
    """Model for RAG system requests."""
    question: str
    session_id: Optional[str] = None


class RAGResponse(BaseModel):
    """Model for RAG system responses."""
    answer: str
    research_steps: List[ResearchStep]
    session_id: str
    total_steps: int
    timestamp: datetime


class ProgressUpdate(BaseModel):
    """Model for WebSocket progress updates."""
    session_id: str
    step_number: int
    total_steps: int
    status: str
    message: str
    timestamp: datetime
