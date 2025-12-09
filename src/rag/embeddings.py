"""
Embedding model wrapper for consistent embedding generation.
"""
from typing import List, Union
from openai import OpenAI
import logging

from src.config.settings import settings

logger = logging.getLogger(__name__)


class EmbeddingModel:
    """Wrapper for embedding models."""

    def __init__(self, model_name: str = None):
        """
        Initialize the embedding model.

        Args:
            model_name: Name of the embedding model
        """
        self.model_name = model_name or settings.embedding_model
        self.client = OpenAI(api_key=settings.openai_api_key)
        logger.info(f"Initialized embedding model: {self.model_name}")

    def embed_text(self, text: Union[str, List[str]]) -> List[List[float]]:
        """
        Generate embeddings for text(s).

        Args:
            text: Single text or list of texts

        Returns:
            List of embedding vectors
        """
        try:
            # Ensure text is a list
            texts = [text] if isinstance(text, str) else text

            # Filter out empty texts
            texts = [t for t in texts if t.strip()]

            if not texts:
                return []

            # Generate embeddings
            response = self.client.embeddings.create(
                input=texts,
                model=self.model_name
            )

            embeddings = [item.embedding for item in response.data]
            logger.debug(f"Generated {len(embeddings)} embeddings")

            return embeddings

        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple documents.

        Args:
            documents: List of document texts

        Returns:
            List of embedding vectors
        """
        return self.embed_text(documents)

    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a query.

        Args:
            query: Query text

        Returns:
            Embedding vector
        """
        embeddings = self.embed_text(query)
        return embeddings[0] if embeddings else []

