"""
RAG (Retrieval-Augmented Generation) System for web search and analysis.
"""
import os
import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable

from .models import SearchResult, ResearchStep, RAGRequest, RAGResponse, ProgressUpdate, EvaluationResult, EvaluationAction
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
    
    async def _send_progress_update(self, 
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
            await progress_callback(update)
    
    async def research_question(self, 
                              question: str, 
                              session_id: Optional[str] = None,
                              progress_callback: Optional[Callable] = None,
                              num_searches: int = 3,
                              num_rewordings: int = 3) -> RAGResponse:
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
            await self._send_progress_update(session_id, 1, 6, "generating_queries", 
                                     "🤖 Analyzing your question and generating search queries...", progress_callback)
            session_logger.info("Generating search queries")
            
            queries = self.llm_client.generate_search_queries(question, num_queries=num_searches)
            session_logger.info(f"Generated {len(queries)} queries: {queries}")
            
            await self._send_progress_update(session_id, 1, 6, "queries_generated", 
                                     f"✅ Generated {len(queries)} targeted search queries", progress_callback)
            
            # Step 2: Perform searches
            search_results_by_query = {}
            total_queries = len(queries)
            
            for i, query in enumerate(queries, 1):
                await self._send_progress_update(session_id, 2, 6, "searching", 
                                       f"🔍 Searching for: \"{query[:60]}{'...' if len(query) > 60 else ''}\" ({i}/{total_queries})", progress_callback)
                session_logger.info(f"Searching for query {i}/{total_queries}: {query}")
                
                search_results = self.search_client.search(query, max_results=3)
                search_results_by_query[query] = search_results
                
                await self._send_progress_update(session_id, 2, 6, "search_complete", 
                                       f"📄 Found {len(search_results)} results for search {i}/{total_queries}", progress_callback)
            
            await self._send_progress_update(session_id, 3, 6, "searches_complete", 
                                     f"✅ Completed all {total_queries} web searches", progress_callback)
            
            # Step 3: Analyze results for each query
            await self._send_progress_update(session_id, 4, 6, "analyzing", 
                                     "🧠 Starting analysis of search results...", progress_callback)
            session_logger.info("Analyzing search results")
            
            for i, (query, search_results) in enumerate(search_results_by_query.items(), 1):
                await self._send_progress_update(session_id, 4, 6, "analyzing_query", 
                                       f"🔬 Analyzing results for: \"{query[:50]}{'...' if len(query) > 50 else ''}\" ({i}/{len(search_results_by_query)})", progress_callback)
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
                
                await self._send_progress_update(session_id, 4, 6, "processing_sources", 
                                       f"📊 Processing {len(results_data)} sources for analysis {i}/{len(search_results_by_query)}", progress_callback)
                
                analysis = self.llm_client.analyze_search_results(query, results_data)
                
                research_step = ResearchStep(
                    step_number=i,
                    query=query,
                    search_results=search_results,
                    analysis=analysis,
                    timestamp=datetime.now()
                )
                
                research_steps.append(research_step)
                session_logger.info(f"Completed analysis for step {i}")
                
                await self._send_progress_update(session_id, 4, 6, "analysis_complete", 
                                       f"✅ Completed analysis {i}/{len(search_results_by_query)}", progress_callback)
            
            await self._send_progress_update(session_id, 5, 6, "all_analysis_complete", 
                                     "✅ All search result analysis completed", progress_callback)
            
            # Step 5: Synthesize and evaluate answers with LLM judge
            await self._send_progress_update(session_id, 6, 6, "synthesizing", 
                                     "🔗 Synthesizing answer and evaluating quality...", progress_callback)
            session_logger.info("Starting synthesis and evaluation loop")
            
            # Prepare research data for synthesis
            research_data = [
                {
                    "query": step.query,
                    "analysis": step.analysis
                }
                for step in research_steps
            ]
            
            # Prepare research context for evaluation
            research_context = "\n\n".join([
                f"Query: {step.query}\nAnalysis: {step.analysis}"
                for step in research_steps
            ])
            
            # Main evaluation loop - max iterations to prevent infinite loops
            max_iterations = num_rewordings
            current_iteration = 0
            final_answer = None
            evaluation_result = None
            
            while current_iteration < max_iterations:
                current_iteration += 1
                iteration_msg = f" (attempt {current_iteration}/{max_iterations})" if current_iteration > 1 else ""
                
                await self._send_progress_update(session_id, 6, 6, "synthesizing", 
                                       f"📝 Generating comprehensive answer{iteration_msg}...", progress_callback)
                
                # Generate answer based on iteration type
                if current_iteration == 1:
                    # First attempt - normal synthesis
                    final_answer = self.llm_client.synthesize_final_answer(question, research_data)
                    session_logger.info(f"Generated initial answer (iteration {current_iteration})")
                elif evaluation_result and evaluation_result.action == EvaluationAction.REDO_FINAL_RESPONSE:
                    # Redo with guidance from previous evaluation
                    final_answer = self.llm_client.regenerate_answer_with_guidance(
                        question, research_data, evaluation_result.improvement_guidance or "Improve clarity and completeness"
                    )
                    session_logger.info(f"Regenerated answer with guidance (iteration {current_iteration})")
                elif evaluation_result and evaluation_result.action == EvaluationAction.RESEARCH_AGAIN:
                    # Research additional topics as suggested by evaluation
                    await self._send_progress_update(session_id, 6, 6, "additional_research", 
                                           f"🔍 Conducting additional research{iteration_msg}...", progress_callback)
                    
                    if evaluation_result.missing_topics:
                        additional_research = await self._conduct_additional_research(
                            evaluation_result.missing_topics, session_id, progress_callback, session_logger
                        )
                        # Add new research to existing data
                        research_data.extend(additional_research)
                        # Update research context
                        research_context = "\n\n".join([
                            f"Query: {item['query']}\nAnalysis: {item['analysis']}"
                            for item in research_data
                        ])
                    
                    # Now synthesize with enhanced research
                    final_answer = self.llm_client.synthesize_final_answer(question, research_data)
                    session_logger.info(f"Generated answer with additional research (iteration {current_iteration})")
                
                # Evaluate the answer using LLM as judge
                await self._send_progress_update(session_id, 6, 6, "evaluating", 
                                       f"⚖️ Evaluating answer quality{iteration_msg}...", progress_callback)
                
                evaluation_result = self.llm_client.evaluate_answer(question, final_answer, research_context)
                
                session_logger.info(f"Evaluation result (iteration {current_iteration}): "
                                  f"Action={evaluation_result.action.value}, "
                                  f"Score={evaluation_result.overall_score:.1f}, "
                                  f"Reasoning={evaluation_result.reasoning}")
                
                # Check if we should return the answer
                if evaluation_result.action == EvaluationAction.SUFFICIENT:
                    await self._send_progress_update(session_id, 6, 6, "evaluation_passed", 
                                           f"✅ Answer quality approved (score: {evaluation_result.overall_score:.1f}/10)", progress_callback)
                    break
                elif current_iteration >= max_iterations:
                    await self._send_progress_update(session_id, 6, 6, "max_iterations", 
                                           f"⚠️ Reached maximum iterations - using best available answer", progress_callback)
                    session_logger.warning(f"Reached maximum evaluation iterations ({max_iterations})")
                    break
                else:
                    action_msg = {
                        EvaluationAction.REDO_FINAL_RESPONSE: "improving answer structure",
                        EvaluationAction.RESEARCH_AGAIN: "conducting additional research"
                    }.get(evaluation_result.action, "refining answer")
                    
                    await self._send_progress_update(session_id, 6, 6, "improvement_needed", 
                                           f"🔄 Score {evaluation_result.overall_score:.1f}/10 - {action_msg}...", progress_callback)
            
            session_logger.info("Research and evaluation completed successfully")
            
            await self._send_progress_update(session_id, 6, 6, "finalizing", 
                                     "✨ Finalizing comprehensive research report...", progress_callback)
            
            # Create response with evaluation metrics
            response = RAGResponse(
                answer=final_answer,
                research_steps=research_steps,
                session_id=session_id,
                total_steps=len(research_steps),
                timestamp=datetime.now(),
                evaluation_result=evaluation_result
            )
            
            await self._send_progress_update(session_id, 6, 6, "completed", 
                                     f"🎉 Research completed! Quality score: {evaluation_result.overall_score:.1f}/10", progress_callback)
            
            return response
            
        except Exception as e:
            session_logger.error(f"Research failed: {e}")
            await self._send_progress_update(session_id, 0, 4, "error", 
                                     f"Research failed: {str(e)}", progress_callback)
            raise
    
    async def _conduct_additional_research(self, 
                                          missing_topics: List[str], 
                                          session_id: str,
                                          progress_callback: Optional[Callable],
                                          session_logger: logging.Logger) -> List[Dict[str, Any]]:
        """Conduct additional research on missing topics."""
        additional_research = []
        
        for i, topic in enumerate(missing_topics, 1):
            await self._send_progress_update(session_id, 6, 6, "additional_search", 
                                   f"🔍 Researching additional topic: \"{topic[:50]}{'...' if len(topic) > 50 else ''}\" ({i}/{len(missing_topics)})", progress_callback)
            
            session_logger.info(f"Conducting additional research on: {topic}")
            
            # Search for the missing topic
            search_results = self.search_client.search(topic, max_results=2)
            
            # Convert SearchResult objects to dict for analysis
            results_data = [
                {
                    "title": result.title,
                    "url": result.url,
                    "content": result.content
                }
                for result in search_results
            ]
            
            # Analyze the additional research
            analysis = self.llm_client.analyze_search_results(topic, results_data)
            
            additional_research.append({
                "query": topic,
                "analysis": analysis
            })
            
            session_logger.info(f"Completed additional research for: {topic}")
        
        return additional_research
    
    def get_session_logs(self, session_id: str) -> Optional[str]:
        """Get the logs for a specific session."""
        log_file = os.path.join(self.logs_dir, f"{session_id}.log")
        
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                return f.read()
        
        return None
