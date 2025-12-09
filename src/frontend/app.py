"""
Streamlit frontend for PR Reviewer.
"""
import streamlit as st
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(src_path))

from src.agents.crew_orchestrator import ReviewCrew
from src.evaluation.metrics import MetricsTracker, ReviewMetrics
from src.rag.indexer import KnowledgeBaseIndexer
from src.config.settings import settings
from datetime import datetime
import time
import json


# Page config
st.set_page_config(
    page_title="AI PR Reviewer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .issue-critical {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .issue-warning {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .issue-suggestion {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 1rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'metrics_tracker' not in st.session_state:
    st.session_state.metrics_tracker = MetricsTracker()

if 'review_history' not in st.session_state:
    st.session_state.review_history = []


def main():
    """Main application."""

    # Header
    st.markdown('<div class="main-header">🤖 AI-Agentic PR Reviewer</div>', unsafe_allow_html=True)
    st.markdown("---")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Platform selection
        platform = st.selectbox(
            "Platform",
            ["Auto-detect", "GitHub", "GitLab", "Bitbucket"],
            help="Select the platform or let the system auto-detect"
        )

        # Review mode
        review_mode = st.selectbox(
            "Review Mode",
            ["Standard", "Quick", "Deep"],
            help="Standard: Balanced analysis\nQuick: Surface issues only\nDeep: Comprehensive review"
        )

        # Enable self-reflection
        enable_reflection = st.checkbox(
            "Enable Self-Reflection",
            value=True,
            help="Use critic agent to validate suggestions"
        )

        st.markdown("---")

        # System status
        st.subheader("📊 System Status")

        try:
            # Check if settings are configured
            if settings.openai_api_key and settings.openai_api_key != "your_openai_api_key_here":
                st.success("✅ OpenAI API Key configured")
            else:
                st.error("❌ OpenAI API Key not configured")
                st.info("Please set OPENAI_API_KEY in your .env file")
        except Exception as e:
            st.error(f"Configuration error: {e}")

        # Quick stats
        total_reviews = len(st.session_state.review_history)
        st.metric("Total Reviews", total_reviews)

        st.markdown("---")

        # Knowledge base management
        st.subheader("📚 Knowledge Base")
        if st.button("🔄 Initialize Knowledge Base"):
            with st.spinner("Indexing knowledge base..."):
                try:
                    indexer = KnowledgeBaseIndexer()
                    indexer.index_all()
                    st.success("Knowledge base initialized!")
                except Exception as e:
                    st.error(f"Error: {e}")

    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Review PR", "📊 Metrics", "🎮 Demo", "ℹ️ About"])

    with tab1:
        review_tab()

    with tab2:
        metrics_tab()

    with tab3:
        demo_tab()

    with tab4:
        about_tab()


def review_tab():
    """PR review tab."""
    st.header("Review Pull Request")

    col1, col2 = st.columns([3, 1])

    with col1:
        pr_url = st.text_input(
            "Enter PR/MR URL",
            placeholder="https://github.com/owner/repo/pull/123",
            help="Enter the full URL of the GitHub, GitLab, or Bitbucket PR/MR"
        )

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        review_button = st.button("🚀 Review PR", type="primary", use_container_width=True)

    if review_button and pr_url:
        perform_review(pr_url)

    # Show review history
    if st.session_state.review_history:
        st.markdown("---")
        st.subheader("📜 Recent Reviews")

        for i, review in enumerate(reversed(st.session_state.review_history[-5:])):
            with st.expander(f"Review #{len(st.session_state.review_history) - i}: {review.get('pr_info', {}).get('title', 'Unknown')}"):
                display_review_result(review)


def perform_review(pr_url: str):
    """Perform PR review."""
    try:
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()

        start_time = time.time()

        status_text.text("🔍 Initializing review crew...")
        progress_bar.progress(10)

        # Initialize crew
        crew = ReviewCrew()

        status_text.text("📥 Fetching PR data...")
        progress_bar.progress(30)

        # Perform review
        status_text.text("🤖 Agents analyzing code...")
        progress_bar.progress(50)

        result = crew.review_pull_request(pr_url)

        status_text.text("✅ Review complete!")
        progress_bar.progress(100)

        end_time = time.time()

        # Store in history
        result['review_time'] = end_time - start_time
        result['timestamp'] = datetime.now()
        st.session_state.review_history.append(result)

        # Display result
        time.sleep(0.5)
        progress_bar.empty()
        status_text.empty()

        if result.get('success'):
            st.success(f"Review completed in {result['review_time']:.2f} seconds!")
            display_review_result(result)
        else:
            st.error(f"Review failed: {result.get('error', 'Unknown error')}")

    except Exception as e:
        st.error(f"Error during review: {str(e)}")


def display_review_result(result: dict):
    """Display review results."""
    if not result.get('success'):
        st.error(f"Review failed: {result.get('error')}")
        return

    # PR Info
    pr_info = result.get('pr_info', {})

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Files Changed", pr_info.get('files_changed', 0))
    with col2:
        st.metric("Additions", pr_info.get('additions', 0))
    with col3:
        st.metric("Deletions", pr_info.get('deletions', 0))
    with col4:
        st.metric("Platform", pr_info.get('platform', 'Unknown').title())

    # Review content
    st.markdown("### 📋 Review Feedback")
    review_text = result.get('review', '')

    # Display using Streamlit's native markdown for better readability
    st.markdown("---")

    # Use a container with custom styling
    with st.container():
        st.markdown("""
        <style>
        .review-container {
            background-color: #f0f2f6;
            padding: 1.5rem;
            border-radius: 0.5rem;
            border-left: 4px solid #1f77b4;
            color: #262730;
            margin: 1rem 0;
        }
        .review-text {
            color: #262730 !important;
            font-size: 1rem;
            line-height: 1.6;
        }
        </style>
        """, unsafe_allow_html=True)

        # Display review text with proper formatting
        st.markdown(f'<div class="review-container review-text">', unsafe_allow_html=True)
        st.markdown(review_text)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Download review with unique key based on timestamp
    download_key = f"download_{hash(pr_info.get('title', 'pr') + str(time.time()))}"
    st.download_button(
        label="📥 Download Review",
        data=review_text,
        file_name=f"review_{pr_info.get('title', 'pr').replace(' ', '_')}.md",
        mime="text/markdown",
        key=download_key
    )


def metrics_tab():
    """Metrics and analytics tab."""
    st.header("📊 Review Metrics")

    if not st.session_state.review_history:
        st.info("No reviews yet. Review a PR to see metrics!")
        return

    # Summary stats
    total_reviews = len(st.session_state.review_history)
    avg_time = sum(r.get('review_time', 0) for r in st.session_state.review_history) / total_reviews

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Reviews", total_reviews)
    with col2:
        st.metric("Avg Review Time", f"{avg_time:.2f}s")
    with col3:
        successful = sum(1 for r in st.session_state.review_history if r.get('success'))
        st.metric("Success Rate", f"{(successful/total_reviews)*100:.1f}%")

    # Platform distribution
    st.subheader("Platform Distribution")
    platforms = {}
    for review in st.session_state.review_history:
        platform = review.get('platform', 'Unknown')
        platforms[platform] = platforms.get(platform, 0) + 1

    st.bar_chart(platforms)

    # Recent reviews table
    st.subheader("Recent Reviews")

    table_data = []
    for review in reversed(st.session_state.review_history[-10:]):
        table_data.append({
            "PR Title": review.get('pr_info', {}).get('title', 'Unknown')[:50],
            "Platform": review.get('platform', 'Unknown').title(),
            "Time (s)": f"{review.get('review_time', 0):.2f}",
            "Status": "✅" if review.get('success') else "❌"
        })

    st.table(table_data)


def demo_tab():
    """Demo tab with example PRs."""
    st.header("🎮 Demo Mode")

    st.markdown("""
    Try the PR reviewer with these example public pull requests:
    """)

    examples = [
        {
            "title": "Python: Security Fix",
            "url": "https://github.com/pallets/flask/pull/5200",
            "description": "Example of a security-related PR"
        },
        {
            "title": "JavaScript: Performance Improvement",
            "url": "https://github.com/facebook/react/pull/27200",
            "description": "Example of a performance optimization PR"
        },
        {
            "title": "Python: Bug Fix",
            "url": "https://github.com/django/django/pull/17000",
            "description": "Example of a bug fix PR"
        }
    ]

    for example in examples:
        with st.expander(f"📌 {example['title']}"):
            st.markdown(f"**URL:** `{example['url']}`")
            st.markdown(f"**Description:** {example['description']}")

            if st.button(f"Review this PR", key=example['url']):
                perform_review(example['url'])


def about_tab():
    """About tab with project information."""
    st.header("ℹ️ About")

    st.markdown("""
    ## 🤖 AI-Agentic Pull Request Reviewer
    
    An intelligent, autonomous AI agent system that reviews Pull Requests and Merge Requests 
    from GitHub, GitLab, and Bitbucket using RAG, self-reflection, and multi-agent reasoning.
    
    ### 🎯 Key Features
    
    - **Multi-Platform Support**: Reviews PRs/MRs from GitHub, GitLab, and Bitbucket
    - **RAG Pipeline**: Retrieves relevant coding standards and best practices
    - **Multi-Agent System**: Specialized agents for analysis, retrieval, criticism, and synthesis
    - **Self-Reflection**: Built-in quality validation and false positive detection
    - **Tool Integration**: Static analysis and complexity metrics
    - **Comprehensive Metrics**: Track review quality and performance
    
    ### 🏗️ Architecture
    
    The system uses a multi-agent architecture with four specialized agents:
    
    1. **Analyzer Agent**: Identifies code issues and improvements
    2. **Retriever Agent**: Fetches relevant context from RAG knowledge base
    3. **Critic Agent**: Validates suggestions and filters false positives
    4. **Synthesizer Agent**: Creates actionable, structured feedback
    
    ### 🛠️ Technology Stack
    
    - **Framework**: CrewAI for multi-agent orchestration
    - **LLM**: OpenAI GPT-4
    - **RAG**: ChromaDB with OpenAI embeddings
    - **Frontend**: Streamlit
    - **Platform APIs**: PyGithub, python-gitlab, atlassian-python-api
    
    ### 📚 Knowledge Base
    
    The system uses a RAG pipeline with curated knowledge including:
    - Python, JavaScript, and other language best practices
    - Security patterns and anti-patterns
    - Performance optimization techniques
    - Code review examples
    
    ### 🎓 Project Context
    
    This project was developed as part of the AI Academy Engineering Track final assignment,
    demonstrating a complete AI-Agentic system with data preparation, RAG, reasoning,
    tool-calling, and evaluation components.
    
    ### 📖 Getting Started
    
    1. Configure your `.env` file with API keys
    2. Initialize the knowledge base (sidebar)
    3. Enter a PR/MR URL and click Review
    4. View structured, actionable feedback
    
    ### 🔗 Links
    
    - [GitHub Repository](#)
    - [Documentation](old_README.md)
    
    ---
    
    Made with ❤️ using AI-Agentic principles
    """)


if __name__ == "__main__":
    main()

