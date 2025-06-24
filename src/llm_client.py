"""
LLM client for making HTTP requests to OpenAI-compatible APIs.
"""
import requests
import json
import logging
from typing import List, Dict, Any
from .models import LLMRequest, LLMResponse


class LLMClient:
    """Client for making HTTP requests to LLM APIs."""
    
    def __init__(self, base_url: str, api_key: str, model: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.model = model
        self.logger = logging.getLogger(__name__)
    
    def call_llm(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """Make HTTP request to LLM API."""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': self.model,
                'messages': messages,
                'temperature': temperature,
                'max_tokens': max_tokens
            }
            
            self.logger.info(f"Making LLM request to {self.base_url}/chat/completions")
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            response.raise_for_status()
            result = response.json()
            
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                self.logger.info("LLM request successful")
                return content
            else:
                raise Exception("No choices returned from LLM")
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"HTTP request failed: {e}")
            raise Exception(f"LLM request failed: {e}")
        except Exception as e:
            self.logger.error(f"LLM call failed: {e}")
            raise
    
    def generate_search_queries(self, question: str) -> List[str]:
        """Generate search queries for the given question."""
        messages = [
            {
                "role": "system",
                "content": "You are a research assistant. Generate 3-5 specific search queries to thoroughly research the given question. Return only the queries, one per line."
            },
            {
                "role": "user",
                "content": f"Question: {question}"
            }
        ]
        
        response = self.call_llm(messages, temperature=0.3)
        queries = [q.strip() for q in response.split('\n') if q.strip()]
        return queries[:5]  # Limit to 5 queries
    
    def analyze_search_results(self, query: str, search_results: List[Dict[str, Any]]) -> str:
        """Analyze search results and extract key information."""
        results_text = "\n\n".join([
            f"Title: {result.get('title', 'N/A')}\nURL: {result.get('url', 'N/A')}\nContent: {result.get('content', 'N/A')}"
            for result in search_results
        ])
        
        messages = [
            {
                "role": "system",
                "content": "You are a research analyst. Analyze the search results and extract the most relevant information for the query. Be concise but comprehensive."
            },
            {
                "role": "user",
                "content": f"Query: {query}\n\nSearch Results:\n{results_text}"
            }
        ]
        
        return self.call_llm(messages, temperature=0.5)
    
    def synthesize_final_answer(self, question: str, research_data: List[Dict[str, Any]]) -> str:
        """Synthesize the final answer from all research data."""
        research_text = "\n\n".join([
            f"Query: {step['query']}\nAnalysis: {step['analysis']}"
            for step in research_data
        ])
        
        messages = [
            {
                "role": "system",
                "content": "You are a research expert. Based on the research data provided, give a comprehensive answer to the user's question. Cite relevant information and be factual."
            },
            {
                "role": "user",
                "content": f"Question: {question}\n\nResearch Data:\n{research_text}"
            }
        ]
        
        return self.call_llm(messages, temperature=0.6)
