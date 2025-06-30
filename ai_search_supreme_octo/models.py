"""
Pydantic models for the RAG system.
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


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
    evaluation_result: Optional['EvaluationResult'] = None


class ProgressUpdate(BaseModel):
    """Model for WebSocket progress updates."""
    session_id: str
    step_number: int
    total_steps: int
    status: str
    message: str
    timestamp: datetime


class EvaluationAction(str, Enum):
    """Possible actions from LLM judge evaluation."""
    SUFFICIENT = "sufficient_return"
    REDO_FINAL_RESPONSE = "redo_final_response" 
    RESEARCH_AGAIN = "research_again"


class EvaluationMetrics(BaseModel):
    """Individual evaluation metrics scores."""
    accuracy: float  # 0-10: How factually accurate is the response
    completeness: float  # 0-10: How complete is the response 
    relevance: float  # 0-10: How relevant is the response to the question
    clarity: float  # 0-10: How clear and well-structured is the response
    confidence: float  # 0-10: Overall confidence in the response quality


class EvaluationResult(BaseModel):
    """Result from LLM judge evaluation."""
    action: EvaluationAction
    metrics: EvaluationMetrics
    overall_score: float  # Average of all metrics
    reasoning: str  # Explanation for the decision
    missing_topics: Optional[List[str]] = None  # Topics to research more if action is RESEARCH_MORE
    improvement_guidance: Optional[str] = None  # Guidance for regeneration if action is REGENERATE


class EvaluationStep(BaseModel):
    """Model for evaluation step in research process."""
    attempt_number: int
    evaluation_result: EvaluationResult
    timestamp: datetime
