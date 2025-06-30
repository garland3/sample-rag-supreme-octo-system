#!/usr/bin/env python3
"""
Example usage of the ai-search-supreme-octo package.

This script demonstrates how to use the package programmatically.
"""

import asyncio
import os
from ai_search_supreme_octo import research_question, RAGSystem


async def simple_example():
    """Simple example using the convenience function."""
    print("=== Simple Example ===")
    
    # Make sure you have your API keys set in environment variables or .env file
    question = "What are the latest developments in renewable energy technology?"
    
    try:
        result = await research_question(
            question=question,
            max_search_queries=2,
            max_iterations=1
        )
        
        print(f"Question: {question}")
        print(f"Answer: {result.answer}")
        print(f"Research steps: {len(result.research_steps)}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have set your API keys in environment variables or .env file")


async def advanced_example():
    """Advanced example using RAGSystem directly with progress tracking."""
    print("\n=== Advanced Example with Progress Tracking ===")
    
    def progress_callback(update):
        print(f"Progress: {update.step} - {update.message}")
    
    question = "What are the environmental benefits of electric vehicles?"
    
    try:
        rag = RAGSystem()
        result = await rag.research_question(
            question=question,
            max_search_queries=3,
            max_iterations=2,
            progress_callback=progress_callback
        )
        
        print(f"\nQuestion: {question}")
        print(f"Answer: {result.answer}")
        print(f"\nResearch Steps:")
        for i, step in enumerate(result.research_steps, 1):
            print(f"{i}. Query: {step.query}")
            print(f"   Found {len(step.search_results)} sources")
            for source in step.search_results[:2]:  # Show first 2 sources per step
                print(f"   - {source.title}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have set your API keys in environment variables or .env file")


if __name__ == "__main__":
    # Check if .env file exists for configuration
    if not os.path.exists(".env"):
        print("Warning: No .env file found. Make sure to set the following environment variables:")
        print("- LLM_API_KEY (OpenAI API key)")
        print("- TAVILY_API_KEY (Tavily search API key)")
        print("- LLM_BASE_URL (optional, defaults to OpenAI)")
        print("- LLM_MODEL (optional, defaults to gpt-3.5-turbo)")
        print()
    
    # Run examples
    asyncio.run(simple_example())
    asyncio.run(advanced_example())
