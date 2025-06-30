#!/usr/bin/env python3
"""
CLI version of the RAG Research System.
A simple command-line interface for the RAG system that provides research-backed answers.
"""
import asyncio
import os
import sys
import argparse
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

from .rag_system import RAGSystem
from .models import ProgressUpdate


class CLIProgressHandler:
    """Simple progress handler for CLI output."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.last_step = 0
    
    async def handle_progress(self, update: ProgressUpdate):
        """Handle progress updates and display them to the user."""
        if self.verbose:
            timestamp = update.timestamp.strftime("%H:%M:%S")
            print(f"[{timestamp}] Step {update.step_number}/{update.total_steps}: {update.message}")
        else:
            # Simple progress indicator
            if update.step_number != self.last_step:
                print(f"Step {update.step_number}/{update.total_steps}: {update.status}")
                self.last_step = update.step_number


def print_banner():
    """Print a simple banner for the CLI."""
    print("=" * 60)
    print("🔍 RAG Research System - CLI Version")
    print("=" * 60)


def print_result(result, verbose: bool = False):
    """Print the research result in a formatted way."""
    print("\n" + "=" * 60)
    print("📊 RESEARCH RESULTS")
    print("=" * 60)
    
    print(f"\n🎯 ANSWER:")
    print("-" * 40)
    print(result.answer)
    
    if verbose and result.research_steps:
        print(f"\n🔍 RESEARCH STEPS ({len(result.research_steps)} steps):")
        print("-" * 40)
        for i, step in enumerate(result.research_steps, 1):
            print(f"\nStep {i}: {step.query}")
            print(f"Analysis: {step.analysis[:200]}{'...' if len(step.analysis) > 200 else ''}")
    
    if result.evaluation_result:
        print(f"\n📈 EVALUATION:")
        print("-" * 40)
        print(f"Overall Score: {result.evaluation_result.overall_score:.1f}/10")
        print(f"Action: {result.evaluation_result.action.value}")
        if result.evaluation_result.reasoning:
            print(f"Reasoning: {result.evaluation_result.reasoning}")
    
    print(f"\n📝 Session ID: {result.session_id}")
    print(f"⏱️  Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


def save_result_to_file(result, question: str, output_dir: str = "output") -> str:
    """Save the research result to a timestamped text file."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"rag_result_{timestamp}.txt"
    filepath = os.path.join(output_dir, filename)
    
    # Prepare content to save
    content_lines = []
    content_lines.append("=" * 80)
    content_lines.append("RAG RESEARCH SYSTEM - RESULTS")
    content_lines.append("=" * 80)
    content_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    content_lines.append(f"Session ID: {result.session_id}")
    content_lines.append("")
    
    content_lines.append("QUESTION:")
    content_lines.append("-" * 40)
    content_lines.append(question)
    content_lines.append("")
    
    content_lines.append("ANSWER:")
    content_lines.append("-" * 40)
    content_lines.append(result.answer)
    content_lines.append("")
    
    if result.research_steps:
        content_lines.append(f"RESEARCH STEPS ({len(result.research_steps)} steps):")
        content_lines.append("-" * 40)
        for i, step in enumerate(result.research_steps, 1):
            content_lines.append(f"\nStep {i}: {step.query}")
            content_lines.append(f"Timestamp: {step.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            content_lines.append(f"Analysis:")
            content_lines.append(step.analysis)
            content_lines.append("-" * 40)
    
    if result.evaluation_result:
        content_lines.append("")
        content_lines.append("EVALUATION RESULTS:")
        content_lines.append("-" * 40)
        content_lines.append(f"Overall Score: {result.evaluation_result.overall_score:.1f}/10")
        content_lines.append(f"Action: {result.evaluation_result.action.value}")
        if result.evaluation_result.reasoning:
            content_lines.append(f"Reasoning: {result.evaluation_result.reasoning}")
        
        content_lines.append("")
        content_lines.append("Detailed Metrics:")
        metrics = result.evaluation_result.metrics
        content_lines.append(f"  Accuracy: {metrics.accuracy:.1f}/10")
        content_lines.append(f"  Completeness: {metrics.completeness:.1f}/10")
        content_lines.append(f"  Relevance: {metrics.relevance:.1f}/10")
        content_lines.append(f"  Clarity: {metrics.clarity:.1f}/10")
        content_lines.append(f"  Confidence: {metrics.confidence:.1f}/10")
    
    content_lines.append("")
    content_lines.append("=" * 80)
    content_lines.append("End of Results")
    content_lines.append("=" * 80)
    
    # Write to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content_lines))
    
    return filepath


async def run_research(question: str, 
                      num_searches: int = 3, 
                      num_rewordings: int = 3, 
                      verbose: bool = False,
                      output_dir: str = "output"):
    """Run the research process with the given parameters."""
    
    # Load environment variables
    load_dotenv()
    
    # Check for required environment variables
    required_vars = ["TAVILY_API_KEY", "LLM_BASE_URL", "LLM_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file or environment.")
        return 1
    
    # Initialize RAG system
    rag_system = RAGSystem()
    
    # Setup progress handler
    progress_handler = CLIProgressHandler(verbose)
    
    print(f"\n🚀 Starting research for: {question}")
    print(f"📊 Search queries: {num_searches}, Max rewordings: {num_rewordings}")
    print("-" * 60)
    
    try:
        # Run the research
        result = await rag_system.research_question(
            question=question,
            max_search_queries=num_searches,
            max_iterations=num_rewordings,
            progress_callback=progress_handler.handle_progress
        )
        
        # Print results to console
        print_result(result, verbose)
        
        # Save results to file
        try:
            output_file = save_result_to_file(result, question, output_dir)
            print(f"\n💾 Results saved to: {output_file}")
        except Exception as e:
            print(f"\n⚠️  Warning: Could not save results to file: {str(e)}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during research: {str(e)}")
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="RAG Research System - CLI Version",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ai-search-supreme-octo "What are the benefits of renewable energy?"
  ai-search-supreme-octo "How does machine learning work?" --searches 5 --verbose
  ai-search-supreme-octo "Latest AI developments" --searches 4 --rewordings 2
  ai-search-supreme-octo "AI ethics" --output-dir ./my_results --verbose
        """
    )
    
    parser.add_argument(
        "question",
        help="The research question to investigate"
    )
    
    parser.add_argument(
        "--searches", "-s",
        type=int,
        default=3,
        help="Number of search queries to generate (default: 3)"
    )
    
    parser.add_argument(
        "--rewordings", "-r",
        type=int,
        default=3,
        help="Maximum number of answer rewordings/improvements (default: 3)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed progress information"
    )
    
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        default="output",
        help="Directory to save result files (default: output)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="AI Search Supreme Octo v1.0.0"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Run the research
    exit_code = asyncio.run(run_research(
        question=args.question,
        num_searches=args.searches,
        num_rewordings=args.rewordings,
        verbose=args.verbose,
        output_dir=args.output_dir
    ))
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
