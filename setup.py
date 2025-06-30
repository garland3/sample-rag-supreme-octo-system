#!/usr/bin/env python3
"""Setup script for ai-search-supreme-octo package."""

from setuptools import setup, find_packages
import os

# Read the contents of your README file
def read_long_description():
    """Read the long description from README.md."""
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return "A modern RAG (Retrieval-Augmented Generation) system for research-backed AI answers."

# Read requirements from requirements.txt
def read_requirements():
    """Read requirements from requirements.txt."""
    try:
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            return [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        return [
            "fastapi>=0.104.1",
            "uvicorn>=0.24.0",
            "websockets>=12.0",
            "python-dotenv>=1.0.0",
            "requests>=2.31.0",
            "pydantic>=2.5.0",
            "aiofiles>=23.2.1",
            "jinja2>=3.1.2",
        ]

setup(
    name="ai-search-supreme-octo",
    version="1.0.0",
    author="AI Search Supreme Octo",
    author_email="contact@example.com",
    description="A modern RAG system that combines web search with AI-powered analysis",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/ai-search-supreme-octo",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0",
            "flake8>=6.0",
            "mypy>=1.0",
        ],
        "cohere": [
            "cohere>=4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ai-search-supreme-octo=ai_search_supreme_octo.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "ai_search_supreme_octo": [
            "templates/*.html",
            "static/css/*.css",
            "static/js/*.js",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/your-username/ai-search-supreme-octo/issues",
        "Source": "https://github.com/your-username/ai-search-supreme-octo",
        "Documentation": "https://github.com/your-username/ai-search-supreme-octo#readme",
    },
    keywords="rag, ai, search, research, llm, retrieval, augmented, generation, tavily, openai",
)
