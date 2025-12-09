"""
Document retrieval from vector store.
"""
from typing import List, Dict, Any, Optional
import logging

from src.rag.vector_store import VectorStore
from src.config.settings import settings

logger = logging.getLogger(__name__)


class Retriever:
    """Retrieve relevant documents from vector store."""

    def __init__(self, vector_store: Optional[VectorStore] = None):
        """
        Initialize the retriever.

        Args:
            vector_store: VectorStore instance
        """
        self.vector_store = vector_store or VectorStore()
        self.k = settings.retrieval_k

    def retrieve(
        self,
        query: str,
        collection_name: str = "code_reviews",
        k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents.

        Args:
            query: Search query
            collection_name: Collection to search
            k: Number of results to return
            filters: Optional metadata filters

        Returns:
            List of documents with metadata and scores
        """
        k = k or self.k

        try:
            results = self.vector_store.query(
                collection_name=collection_name,
                query_texts=[query],
                n_results=k,
                where=filters
            )

            # Format results
            documents = []
            if results and results.get('documents'):
                docs = results['documents'][0]
                metadatas = results.get('metadatas', [[]])[0]
                distances = results.get('distances', [[]])[0]

                for i, doc in enumerate(docs):
                    documents.append({
                        'content': doc,
                        'metadata': metadatas[i] if i < len(metadatas) else {},
                        'distance': distances[i] if i < len(distances) else 1.0,
                        'relevance_score': 1.0 - (distances[i] if i < len(distances) else 1.0)
                    })

            logger.info(f"Retrieved {len(documents)} documents for query")
            return documents

        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []

    def retrieve_by_language(
        self,
        query: str,
        language: str,
        k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve documents filtered by programming language.

        Args:
            query: Search query
            language: Programming language
            k: Number of results

        Returns:
            List of relevant documents
        """
        filters = {"language": language}
        return self.retrieve(query, k=k, filters=filters)

    def retrieve_by_category(
        self,
        query: str,
        category: str,
        k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve documents filtered by category.

        Args:
            query: Search query
            category: Category (e.g., "security", "performance")
            k: Number of results

        Returns:
            List of relevant documents
        """
        filters = {"category": category}
        return self.retrieve(query, k=k, filters=filters)

    def retrieve_best_practices(
        self,
        query: str,
        language: Optional[str] = None,
        k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve best practices.

        Args:
            query: Search query
            language: Optional language filter
            k: Number of results

        Returns:
            List of best practice documents
        """
        filters = {"type": "best_practice"}
        if language:
            filters["language"] = language

        return self.retrieve(
            query,
            collection_name="best_practices",
            k=k,
            filters=filters
        )

    def retrieve_code_patterns(
        self,
        query: str,
        pattern_type: Optional[str] = None,
        k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve code patterns.

        Args:
            query: Search query
            pattern_type: Type of pattern (e.g., "anti-pattern", "design-pattern")
            k: Number of results

        Returns:
            List of code pattern documents
        """
        filters = {}
        if pattern_type:
            filters["pattern_type"] = pattern_type

        return self.retrieve(
            query,
            collection_name="code_patterns",
            k=k,
            filters=filters
        )

    def retrieve_review_examples(
        self,
        query: str,
        issue_type: Optional[str] = None,
        k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve similar review examples.

        Args:
            query: Search query (code or description)
            issue_type: Type of issue (e.g., "security", "bug")
            k: Number of results

        Returns:
            List of review example documents
        """
        filters = {}
        if issue_type:
            filters["issue_type"] = issue_type

        return self.retrieve(
            query,
            collection_name="review_examples",
            k=k,
            filters=filters
        )

