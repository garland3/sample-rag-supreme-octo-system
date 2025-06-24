"""
Simple Pydantic-based schema generation for OpenAI tool calling.
Converts Pydantic models to OpenAI tool call JSON schemas.
"""
import json
from pydantic import BaseModel, Field
from typing import Optional, List


class EvaluationParams(BaseModel):
    """Evaluate the quality of an answer based on multiple metrics."""
    action: str = Field(description="Action to take: sufficient_return, redo_final_response, or research_again")
    accuracy: float = Field(ge=0, le=10, description="How factually accurate is the response (0-10)")
    completeness: float = Field(ge=0, le=10, description="How complete is the response (0-10)")
    relevance: float = Field(ge=0, le=10, description="How relevant is the response to the question (0-10)")
    clarity: float = Field(ge=0, le=10, description="How clear and well-structured is the response (0-10)")
    confidence: float = Field(ge=0, le=10, description="Overall confidence in the response quality (0-10)")
    reasoning: str = Field(description="Explanation for the evaluation decision")
    missing_topics: Optional[List[str]] = Field(default=None, description="Topics that need more research")
    improvement_guidance: Optional[str] = Field(default=None, description="Specific guidance for improving the answer")


def pydantic_to_openai_tool(model_class: BaseModel, function_name: str) -> dict:
    """Convert Pydantic model to OpenAI tool schema."""
    schema = model_class.model_json_schema()
    
    return {
        "type": "function",
        "function": {
            "name": function_name,
            "description": model_class.__doc__ or f"Call {function_name}",
            "parameters": schema
        }
    }


# Example usage and testing
if __name__ == "__main__":
    # Test the schema generation
    tool_schema = pydantic_to_openai_tool(EvaluationParams, "evaluate_answer")
    print("Generated Schema:")
    print(json.dumps(tool_schema, indent=2))
