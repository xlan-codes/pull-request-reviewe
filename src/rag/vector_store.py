"""
Vector store management using ChromaDB.
"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path

from src.config.settings import settings as app_settings

logger = logging.getLogger(__name__)


class VectorStore:
    """Manages the ChromaDB vector store for code review knowledge."""

    def __init__(self, persist_directory: Optional[str] = None):
        """
        Initialize the vector store.

        Args:
            persist_directory: Directory to persist the database
        """
        self.persist_directory = persist_directory or app_settings.chroma_persist_directory
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        logger.info(f"Initialized vector store at {self.persist_directory}")

    def get_or_create_collection(self, name: str) -> chromadb.Collection:
        """
        Get or create a collection.

        Args:
            name: Collection name

        Returns:
            ChromaDB collection
        """
        try:
            collection = self.client.get_or_create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Using collection: {name}")
            return collection
        except Exception as e:
            logger.error(f"Error getting/creating collection: {e}")
            raise

    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ) -> bool:
        """
        Add documents to a collection.

        Args:
            collection_name: Name of the collection
            documents: List of document texts
            metadatas: List of metadata dictionaries
            ids: List of unique IDs

        Returns:
            True if successful
        """
        try:
            collection = self.get_or_create_collection(collection_name)
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(documents)} documents to {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            return False

    def query(
        self,
        collection_name: str,
        query_texts: List[str],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query the vector store.

        Args:
            collection_name: Name of the collection
            query_texts: List of query texts
            n_results: Number of results to return
            where: Optional metadata filter

        Returns:
            Query results
        """
        try:
            collection = self.get_or_create_collection(collection_name)
            results = collection.query(
                query_texts=query_texts,
                n_results=n_results,
                where=where
            )
            logger.debug(f"Query returned {len(results.get('documents', [[]])[0])} results")
            return results
        except Exception as e:
            logger.error(f"Error querying collection: {e}")
            return {"documents": [], "metadatas": [], "distances": []}

    def delete_collection(self, name: str) -> bool:
        """Delete a collection."""
        try:
            self.client.delete_collection(name)
            logger.info(f"Deleted collection: {name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            return False

    def list_collections(self) -> List[str]:
        """List all collections."""
        try:
            collections = self.client.list_collections()
            return [col.name for col in collections]
        except Exception as e:
            logger.error(f"Error listing collections: {e}")
            return []

    def count_documents(self, collection_name: str) -> int:
        """Count documents in a collection."""
        try:
            collection = self.get_or_create_collection(collection_name)
            return collection.count()
        except Exception as e:
            logger.error(f"Error counting documents: {e}")
            return 0

