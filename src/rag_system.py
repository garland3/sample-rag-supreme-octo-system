"""
RAG (Retrieval-Augmented Generation) System for web search and analysis.
"""
import os
import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable

from .models import SearchResult, ResearchStep, RAGRequest, RAGResponse, ProgressUpdate
from .llm_client import LLMClient
from .search_client import SearchClient


class RAGSystem:
    """Main RAG system for research and question answering."""
    
    def __init__(self, 
                 tavily_api_key: str,
                 llm_base_url: str,
                 llm_api_key: str,
                 llm_model: str,
                 logs_dir: str = "logs"):
        """Initialize the RAG system with API keys and configuration."""
        self.logs_dir = logs_dir
        
        # Create logs directory if it doesn't exist
        os.makedirs(logs_dir, exist_ok=True)
        
        # Initialize clients
        self.llm_client = LLMClient(llm_base_url, llm_api_key, llm_model)
        self.search_client = SearchClient(tavily_api_key)
        
        # Setup logging
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logger for the RAG system."""
        logger = logging.getLogger("rag_system")
        logger.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        return logger
    
    def _setup_session_logger(self, session_id: str) -> logging.Logger:
        """Setup a session-specific logger that writes to a file."""
        session_logger = logging.getLogger(f"session_{session_id}")
        session_logger.setLevel(logging.INFO)
        
        # Remove existing handlers
        for handler in session_logger.handlers[:]:
            session_logger.removeHandler(handler)
        
        # Create file handler for this session
        log_file = os.path.join(self.logs_dir, f"{session_id}.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        session_logger.addHandler(file_handler)
        session_logger.propagate = False
        
        return session_logger
    
    def _send_progress_update(self, 
                            session_id: str, 
                            step_number: int, 
                            total_steps: int, 
                            status: str, 
                            message: str,
                            progress_callback: Optional[Callable] = None):
        """Send progress update via callback if provided."""
        if progress_callback:
            update = ProgressUpdate(
                session_id=session_id,
                step_number=step_number,
                total_steps=total_steps,
                status=status,
                message=message,
                timestamp=datetime.now()
            )
            progress_callback(update)
    
    async def research_question(self, 
                              question: str, 
                              session_id: Optional[str] = None,
                              progress_callback: Optional[Callable] = None) -> RAGResponse:
        """Main method to research a question using the RAG pipeline."""
        
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Setup session logger
        session_logger = self._setup_session_logger(session_id)
        session_logger.info(f"Starting research session: {session_id}")
        session_logger.info(f"Question: {question}")
        
        research_steps = []
        
        try:
            # Step 1: Generate search queries
            self._send_progress_update(session_id, 1, 4, "generating_queries", 
                                     "Generating search queries...", progress_callback)
            session_logger.info("Generating search queries")
            
            queries = self.llm_client.generate_search_queries(question)
            session_logger.info(f"Generated {len(queries)} queries: {queries}")
            
            # Step 2: Perform searches
            self._send_progress_update(session_id, 2, 4, "searching", 
                                     "Performing web searches...", progress_callback)
            session_logger.info("Performing searches")
            
            search_results_by_query = self.search_client.multi_search(queries, max_results_per_query=3)
            
            # Step 3: Analyze results for each query
            self._send_progress_update(session_id, 3, 4, "analyzing", 
                                     "Analyzing search results...", progress_callback)
            session_logger.info("Analyzing search results")
            
            for i, (query, search_results) in enumerate(search_results_by_query.items()):
                session_logger.info(f"Analyzing results for query: {query}")
                
                # Convert SearchResult objects to dict for LLM analysis
                results_data = [
                    {
                        "title": result.title,
                        "url": result.url,
                        "content": result.content
                    }
                    for result in search_results
                ]
                
                analysis = self.llm_client.analyze_search_results(query, results_data)
                
                research_step = ResearchStep(
                    step_number=i + 1,
                    query=query,
                    search_results=search_results,
                    analysis=analysis,
                    timestamp=datetime.now()
                )
                
                research_steps.append(research_step)
                session_logger.info(f"Completed analysis for step {i + 1}")
            
            # Step 4: Synthesize final answer
            self._send_progress_update(session_id, 4, 4, "synthesizing", 
                                     "Synthesizing final answer...", progress_callback)
            session_logger.info("Synthesizing final answer")
            
            # Prepare research data for synthesis
            research_data = [
                {
                    "query": step.query,
                    "analysis": step.analysis
                }
                for step in research_steps
            ]
            
            final_answer = self.llm_client.synthesize_final_answer(question, research_data)
            session_logger.info("Research completed successfully")
            
            # Create response
            response = RAGResponse(
                answer=final_answer,
                research_steps=research_steps,
                session_id=session_id,
                total_steps=len(research_steps),
                timestamp=datetime.now()
            )
            
            self._send_progress_update(session_id, 4, 4, "completed", 
                                     "Research completed!", progress_callback)
            
            return response
            
        except Exception as e:
            session_logger.error(f"Research failed: {e}")
            self._send_progress_update(session_id, 0, 4, "error", 
                                     f"Research failed: {str(e)}", progress_callback)
            raise
    
    def get_session_logs(self, session_id: str) -> Optional[str]:
        """Get the logs for a specific session."""
        log_file = os.path.join(self.logs_dir, f"{session_id}.log")
        
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                return f.read()
        
        return None
