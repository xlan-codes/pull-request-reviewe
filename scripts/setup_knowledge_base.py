#!/usr/bin/env python3
"""
Setup script to initialize the knowledge base.
"""
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from src.rag.indexer import KnowledgeBaseIndexer
from src.utils.logging_config import logger


def main():
    """Initialize the knowledge base."""
    logger.info("=== Knowledge Base Setup ===")
    logger.info("This will index all knowledge base documents into the vector store.")

    try:
        # Create indexer
        indexer = KnowledgeBaseIndexer()

        # Index all documents
        logger.info("Starting indexing process...")
        indexer.index_all()

        logger.info("\n=== Setup Complete ===")
        logger.info("Knowledge base has been successfully initialized!")
        logger.info("\nYou can now run the application:")
        logger.info("  streamlit run src/frontend/app.py")

        return 0

    except Exception as e:
        logger.error(f"Setup failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

