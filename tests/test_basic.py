"""
Simple test to verify the system is working.
"""
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))


def test_imports():
    """Test that all modules can be imported."""
    try:
        from src.config.settings import settings
        from src.rag.vector_store import VectorStore
        from src.rag.embeddings import EmbeddingModel
        from src.data_preparation.github_adapter import GitHubAdapter
        from src.agents.crew_orchestrator import ReviewCrew

        print("✅ All imports successful!")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_settings():
    """Test settings configuration."""
    try:
        from src.config.settings import settings

        print(f"OpenAI Model: {settings.openai_model}")
        print(f"Review Mode: {settings.review_mode}")
        print(f"Log Level: {settings.log_level}")

        if settings.openai_api_key and settings.openai_api_key != "your_openai_api_key_here":
            print("✅ OpenAI API key is configured")
        else:
            print("⚠️  OpenAI API key not configured")

        return True
    except Exception as e:
        print(f"❌ Settings test failed: {e}")
        return False


def test_vector_store():
    """Test vector store initialization."""
    try:
        from src.rag.vector_store import VectorStore

        vs = VectorStore()
        collections = vs.list_collections()

        print(f"✅ Vector store initialized")
        print(f"Collections: {collections}")

        return True
    except Exception as e:
        print(f"❌ Vector store test failed: {e}")
        return False


if __name__ == "__main__":
    print("="*60)
    print("Running System Tests")
    print("="*60)

    results = []

    print("\n1. Testing imports...")
    results.append(test_imports())

    print("\n2. Testing settings...")
    results.append(test_settings())

    print("\n3. Testing vector store...")
    results.append(test_vector_store())

    print("\n" + "="*60)
    if all(results):
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)

