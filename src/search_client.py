"""
Search client for Tavily API integration.
"""
import requests
import logging
from typing import List, Dict, Any
from .models import SearchResult


class SearchClient:
    """Client for Tavily search API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.tavily.com"
        self.logger = logging.getLogger(__name__)
    
    def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """Search using Tavily API."""
        try:
            headers = {
                'Content-Type': 'application/json'
            }
            
            payload = {
                'api_key': self.api_key,
                'query': query,
                'search_depth': 'basic',
                'max_results': max_results,
                'include_raw_content': True
            }
            
            self.logger.info(f"Searching Tavily for: {query}")
            
            response = requests.post(
                f"{self.base_url}/search",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get('results', []):
                result = SearchResult(
                    title=item.get('title', 'No title'),
                    url=item.get('url', ''),
                    content=item.get('content', ''),
                    score=item.get('score')
                )
                results.append(result)
            
            self.logger.info(f"Found {len(results)} search results")
            return results
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Tavily search failed: {e}")
            raise Exception(f"Search request failed: {e}")
        except Exception as e:
            self.logger.error(f"Search error: {e}")
            raise
    
    def multi_search(self, queries: List[str], max_results_per_query: int = 3) -> Dict[str, List[SearchResult]]:
        """Perform multiple searches and return results grouped by query."""
        results = {}
        
        for query in queries:
            try:
                search_results = self.search(query, max_results_per_query)
                results[query] = search_results
            except Exception as e:
                self.logger.error(f"Failed to search for '{query}': {e}")
                results[query] = []
        
        return results
