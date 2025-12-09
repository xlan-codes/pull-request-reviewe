#!/usr/bin/env python3
"""
AI-Agentic Pull Request Reviewer

Main entry point for the application.
This is a comprehensive AI agent system that reviews Pull Requests and Merge Requests
from GitHub, GitLab, and Bitbucket using RAG.

Usage:
    # Start the web interface
    streamlit run src/frontend/app.py

    # Or run CLI demo
    python scripts/run_demo.py --url <PR_URL>

    # Or use programmatically
    from src.agents.crew_orchestrator import ReviewCrew
    crew = ReviewCrew()
    result = crew.review_pull_request(pr_url)
"""

import sys
from pathlib import Path


def print_welcome():
    """Print welcome message."""
    print("=" * 70)
    print("🤖 AI-Agentic Pull Request Reviewer".center(70))
    print("=" * 70)
    print()
    print("An intelligent system for automated code review using:")
    print("  ✅ Multi-agent reasoning (CrewAI)")
    print("  ✅ RAG pipeline (ChromaDB + OpenAI)")
    print("  ✅ Self-reflection and validation")
    print("  ✅ Multi-platform support (GitHub/GitLab/Bitbucket)")
    print()
    print("=" * 70)
    print()
    print("Getting Started:")
    print("  1. Setup: python scripts/setup_knowledge_base.py")
    print("  2. Web UI: streamlit run src/frontend/app.py")
    print("  3. CLI Demo: python scripts/run_demo.py --help")
    print()
    print("Documentation:")
    print("  README.md - Project overview and usage instructions")
    print("  architecture.md - Technical overview of the system architecture")
    print()
    print("=" * 70)


def check_setup():
    """Check if the system is properly configured."""
    issues = []

    # Check .env file
    env_file = Path(".env")
    if not env_file.exists():
        issues.append("⚠️  .env file not found. Copy .env.example to .env and configure.")

    # Check if dependencies are installed
    try:
        import crewai
        import langchain
        import chromadb
        import streamlit
    except ImportError as e:
        issues.append(f"⚠️  Missing dependency: {e.name}. Run: pip install -r requirements.txt")

    # Check knowledge base
    kb_path = Path("data/vector_db")
    if not kb_path.exists() or not list(kb_path.iterdir()):
        issues.append("⚠️  Knowledge base not initialized. Run: python scripts/setup_knowledge_base.py")

    return issues


def main():
    """Main entry point."""
    print_welcome()

    # Check setup
    issues = check_setup()

    if issues:
        print("⚙️  Setup Issues Detected:")
        print()
        for issue in issues:
            print(f"  {issue}")
        print()
        print("Please resolve these issues before running the application.")
        print()
        return 1
    else:
        print("✅ System is ready!")
        print()
        print("Launch the application with:")
        print("  streamlit run src/frontend/app.py")
        print()
        return 0


if __name__ == '__main__':
    sys.exit(main())
