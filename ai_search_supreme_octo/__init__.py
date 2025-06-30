"""
AI Search Supreme Octo - A modern RAG system for research-backed AI answers.

This package provides a comprehensive Retrieval-Augmented Generation system that combines
web search with AI-powered analysis to provide comprehensive, research-backed answers.

Features:
- Web search integration via Tavily API  
- OpenAI-compatible LLM support
- Modern web UI with real-time progress tracking
- Command-line interface for terminal usage
- Structured research pipeline with detailed logging
- Modular architecture for easy customization

Usage:
    # Programmatic usage
    from ai_search_supreme_octo import research_question
    
    result = await research_question("What are the benefits of renewable energy?")
    print(result.final_answer)
    
    # Or use the RAGSystem directly
    from ai_search_supreme_octo import RAGSystem
    
    rag = RAGSystem()
    result = await rag.research_question("Your question here")
"""

__version__ = "1.0.0"
__author__ = "AI Search Supreme Octo Team"
__email__ = "contact@example.com"

from .rag_system import RAGSystem
from .models import RAGResponse, ProgressUpdate, SearchResult, ResearchStep
from .cli import main as cli_main

# Convenience function for direct usage
async def research_question(
    question: str,
    max_search_queries: int = 3,
    max_iterations: int = 3,
    progress_callback=None
) -> 'RAGResponse':
    """
    Research a question using the RAG system.
    
    Args:
        question: The question to research
        max_search_queries: Number of search queries to generate (1-10)
        max_iterations: Maximum answer improvement iterations (1-5)
        progress_callback: Optional callback for progress updates
        
    Returns:
        RAGResponse containing the final answer and research details
    """
    rag = RAGSystem()
    return await rag.research_question(
        question=question,
        progress_callback=progress_callback,
        num_searches=max_search_queries,
        num_rewordings=max_iterations
    )

__all__ = [
    'RAGSystem',
    'RAGResponse', 
    'ProgressUpdate',
    'SearchResult',
    'ResearchStep',
    'research_question',
    'cli_main'
]
