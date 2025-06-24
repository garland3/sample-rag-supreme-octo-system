"""
LLM client for making HTTP requests to OpenAI-compatible APIs.
"""
import requests
import json
import logging
from typing import List, Dict, Any, Optional
from .models import LLMRequest, LLMResponse, EvaluationResult, EvaluationAction, EvaluationMetrics
from .function_schema import pydantic_to_openai_tool, EvaluationParams


class LLMClient:
    """Client for making HTTP requests to LLM APIs."""
    
    def __init__(self, base_url: str, api_key: str, model: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.model = model
        self.logger = logging.getLogger(__name__)
    
    def call_llm(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 1000, tools: Optional[List[Dict]] = None) -> str:
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
            
            # Add tools if provided (for function calling)
            if tools:
                payload['tools'] = tools
                payload['tool_choice'] = 'auto'
            
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
                message = result['choices'][0]['message']
                
                # Handle function calling response
                if 'tool_calls' in message and message['tool_calls']:
                    tool_call = message['tool_calls'][0]
                    if tool_call['type'] == 'function':
                        return tool_call['function']['arguments']
                
                # Regular content response
                content = message.get('content', '')
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
    
    def generate_search_queries(self, question: str, num_queries: int = 3) -> List[str]:
        """Generate search queries for the given question."""
        messages = [
            {
                "role": "system",
                "content": f"You are a research assistant. Generate {num_queries} specific search queries to thoroughly research the given question. Return only the queries, one per line."
            },
            {
                "role": "user",
                "content": f"Question: {question}"
            }
        ]
        
        response = self.call_llm(messages, temperature=0.3)
        queries = [q.strip() for q in response.split('\n') if q.strip()]
        return queries[:num_queries]  # Limit to specified number of queries
    
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
    
    def evaluate_answer(self, question: str, answer: str, research_context: str) -> EvaluationResult:
        """Use LLM as a judge to evaluate the quality of an answer."""
        
        # Generate the function schema using Pydantic
        evaluation_tool = pydantic_to_openai_tool(EvaluationParams, "evaluate_answer")
        
        messages = [
            {
                "role": "system",
                "content": """You are an expert evaluator. Evaluate the quality of the provided answer based on the original question and research context.

Evaluation criteria:
- Accuracy (0-10): How factually correct is the information?
- Completeness (0-10): Does it fully address all aspects of the question?
- Relevance (0-10): How well does it directly answer what was asked?
- Clarity (0-10): Is it well-structured and easy to understand?
- Confidence (0-10): Overall quality and trustworthiness

Actions:
- sufficient_return: Answer is good enough (average score >= 7.0)
- redo_final_response: Answer needs improvement but research is sufficient (average score 5.0-6.9)
- research_again: More research needed (average score < 5.0 or missing key information)

Be honest and critical in your evaluation."""
            },
            {
                "role": "user",
                "content": f"""Original Question: {question}

Answer to Evaluate:
{answer}

Research Context:
{research_context}

Please evaluate this answer and provide your assessment."""
            }
        ]
        
        try:
            response = self.call_llm(messages, temperature=0.2, tools=[evaluation_tool])
            
            # Parse the function call response
            evaluation_data = json.loads(response)
            
            # Create metrics object
            metrics = EvaluationMetrics(
                accuracy=evaluation_data['accuracy'],
                completeness=evaluation_data['completeness'],
                relevance=evaluation_data['relevance'],
                clarity=evaluation_data['clarity'],
                confidence=evaluation_data['confidence']
            )
            
            # Calculate overall score
            overall_score = (metrics.accuracy + metrics.completeness + metrics.relevance + 
                           metrics.clarity + metrics.confidence) / 5
            
            # Create evaluation result
            return EvaluationResult(
                action=EvaluationAction(evaluation_data['action']),
                metrics=metrics,
                overall_score=overall_score,
                reasoning=evaluation_data['reasoning'],
                missing_topics=evaluation_data.get('missing_topics'),
                improvement_guidance=evaluation_data.get('improvement_guidance')
            )
            
        except (json.JSONDecodeError, KeyError) as e:
            self.logger.error(f"Failed to parse evaluation response: {e}")
            # Fallback evaluation if function calling fails
            return EvaluationResult(
                action=EvaluationAction.SUFFICIENT,
                metrics=EvaluationMetrics(accuracy=7.0, completeness=7.0, relevance=7.0, clarity=7.0, confidence=7.0),
                overall_score=7.0,
                reasoning="Evaluation parsing failed, defaulting to sufficient",
                missing_topics=None,
                improvement_guidance=None
            )
    
    def regenerate_answer_with_guidance(self, question: str, research_data: List[Dict[str, Any]], guidance: str) -> str:
        """Regenerate the final answer with specific improvement guidance."""
        research_text = "\n\n".join([
            f"Query: {step['query']}\nAnalysis: {step['analysis']}"
            for step in research_data
        ])
        
        messages = [
            {
                "role": "system",
                "content": f"""You are a research expert. Based on the research data provided, give a comprehensive answer to the user's question. 

IMPORTANT: Pay special attention to this improvement guidance: {guidance}

Cite relevant information and be factual. Ensure your answer addresses the specific areas for improvement mentioned in the guidance."""
            },
            {
                "role": "user",
                "content": f"Question: {question}\n\nResearch Data:\n{research_text}"
            }
        ]
        
        return self.call_llm(messages, temperature=0.6)
