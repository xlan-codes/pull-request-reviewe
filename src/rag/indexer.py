"""
Indexer for populating the knowledge base.
"""
import os
from pathlib import Path
from typing import List, Dict, Any
import logging
import hashlib

from src.rag.vector_store import VectorStore
from src.rag.embeddings import EmbeddingModel

logger = logging.getLogger(__name__)


class KnowledgeBaseIndexer:
    """Index knowledge base documents into vector store."""

    def __init__(self):
        """Initialize the indexer."""
        self.vector_store = VectorStore()
        self.embedding_model = EmbeddingModel()
        self.knowledge_base_path = Path(__file__).parent / "knowledge_base"

    def _generate_doc_id(self, content: str, metadata: Dict[str, Any]) -> str:
        """Generate unique ID for a document."""
        unique_str = f"{content}{metadata.get('source', '')}"
        return hashlib.md5(unique_str.encode()).hexdigest()

    def _chunk_document(self, content: str, chunk_size: int = 1000) -> List[str]:
        """
        Chunk a document into smaller pieces.

        Args:
            content: Document content
            chunk_size: Maximum chunk size in characters

        Returns:
            List of chunks
        """
        # Simple chunking by paragraphs
        paragraphs = content.split('\n\n')
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            if len(current_chunk) + len(para) > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = para
            else:
                current_chunk += "\n\n" + para if current_chunk else para

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def index_markdown_files(self, directory: Path, collection_name: str, metadata: Dict[str, Any] = None):
        """
        Index all markdown files in a directory.

        Args:
            directory: Directory containing markdown files
            collection_name: Name of the collection
            metadata: Additional metadata for all documents
        """
        if not directory.exists():
            logger.warning(f"Directory not found: {directory}")
            return

        documents = []
        metadatas = []
        ids = []

        for md_file in directory.glob("*.md"):
            try:
                content = md_file.read_text()
                chunks = self._chunk_document(content)

                for i, chunk in enumerate(chunks):
                    doc_metadata = {
                        "source": str(md_file.name),
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        **(metadata or {})
                    }

                    documents.append(chunk)
                    metadatas.append(doc_metadata)
                    ids.append(self._generate_doc_id(chunk, doc_metadata) + f"_{i}")

                logger.info(f"Indexed {md_file.name} into {len(chunks)} chunks")

            except Exception as e:
                logger.error(f"Error indexing {md_file}: {e}")

        if documents:
            self.vector_store.add_documents(
                collection_name=collection_name,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(documents)} documents to {collection_name}")

    def index_best_practices(self):
        """Index best practices documents."""
        logger.info("Indexing best practices...")
        best_practices_dir = self.knowledge_base_path / "best_practices"

        self.index_markdown_files(
            directory=best_practices_dir,
            collection_name="best_practices",
            metadata={"type": "best_practice"}
        )

    def index_code_patterns(self):
        """Index code patterns documents."""
        logger.info("Indexing code patterns...")
        patterns_dir = self.knowledge_base_path / "code_patterns"

        self.index_markdown_files(
            directory=patterns_dir,
            collection_name="code_patterns",
            metadata={"type": "code_pattern"}
        )

    def index_review_examples(self):
        """Index review examples documents."""
        logger.info("Indexing review examples...")
        examples_dir = self.knowledge_base_path / "review_examples"

        self.index_markdown_files(
            directory=examples_dir,
            collection_name="review_examples",
            metadata={"type": "review_example"}
        )

    def index_all(self):
        """Index all knowledge base content."""
        logger.info("Starting full knowledge base indexing...")

        self.index_best_practices()
        self.index_code_patterns()
        self.index_review_examples()

        logger.info("Knowledge base indexing complete!")

        # Print statistics
        for collection in ["best_practices", "code_patterns", "review_examples"]:
            count = self.vector_store.count_documents(collection)
            logger.info(f"{collection}: {count} documents")

    def reset_and_reindex(self):
        """Delete all collections and reindex."""
        logger.info("Resetting knowledge base...")

        for collection in ["best_practices", "code_patterns", "review_examples"]:
            self.vector_store.delete_collection(collection)

        self.index_all()

