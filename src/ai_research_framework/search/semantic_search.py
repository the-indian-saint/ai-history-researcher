"""Semantic search implementation using vector embeddings."""

from typing import List, Optional, Dict, Any, Tuple
import numpy as np
from datetime import datetime
import hashlib

from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.utils import embedding_functions

from ..storage.database import Document, get_database
from ..config import settings
from ..utils.logging import get_logger

logger = get_logger(__name__)


class EmbeddingGenerator:
    """Generate embeddings for text using sentence-transformers."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedding generator.
        
        Args:
            model_name: Name of the sentence-transformer model to use
        """
        try:
            self.model = SentenceTransformer(model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            logger.info(f"Loaded embedding model: {model_name} (dim={self.embedding_dim})")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            Embedding vector as list of floats
        """
        if not text:
            return [0.0] * self.embedding_dim
        
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return [0.0] * self.embedding_dim
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to generate embeddings for
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return [[0.0] * self.embedding_dim for _ in texts]


class TextChunker:
    """Split documents into chunks for embedding."""
    
    @staticmethod
    def chunk_text(
        text: str,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        separator: str = "\n\n"
    ) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to split
            chunk_size: Maximum size of each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
            separator: Separator to use for splitting (tries to split on this first)
            
        Returns:
            List of text chunks
        """
        if not text:
            return []
        
        # Try to split on separator first
        if separator and separator in text:
            paragraphs = text.split(separator)
            chunks = []
            current_chunk = ""
            
            for para in paragraphs:
                if len(current_chunk) + len(para) <= chunk_size:
                    current_chunk += para + separator
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = para + separator
            
            if current_chunk:
                chunks.append(current_chunk.strip())
        else:
            # Fall back to simple character-based chunking
            chunks = []
            start = 0
            while start < len(text):
                end = min(start + chunk_size, len(text))
                
                # Try to find a sentence boundary
                if end < len(text):
                    for sep in ['. ', '! ', '? ', '\n']:
                        last_sep = text[start:end].rfind(sep)
                        if last_sep != -1:
                            end = start + last_sep + len(sep)
                            break
                
                chunks.append(text[start:end].strip())
                start = end - chunk_overlap
        
        return chunks
    
    @staticmethod
    def create_chunk_metadata(
        document_id: str,
        chunk_index: int,
        chunk_text: str,
        document_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create metadata for a text chunk.
        
        Args:
            document_id: ID of the source document
            chunk_index: Index of this chunk in the document
            chunk_text: The chunk text
            document_metadata: Metadata from the source document
            
        Returns:
            Chunk metadata dictionary
        """
        # Create unique chunk ID
        chunk_id = hashlib.md5(f"{document_id}_{chunk_index}".encode()).hexdigest()
        
        return {
            "chunk_id": chunk_id,
            "document_id": document_id,
            "chunk_index": chunk_index,
            "chunk_size": len(chunk_text),
            "title": document_metadata.get("title", ""),
            "source_type": document_metadata.get("source_type", ""),
            "language": document_metadata.get("language", "english"),
            "author": document_metadata.get("author", ""),
            "created_at": document_metadata.get("created_at", ""),
        }


class SemanticSearch:
    """Semantic search using ChromaDB for vector storage."""
    
    def __init__(
        self,
        collection_name: str = None,
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize semantic search.
        
        Args:
            collection_name: Name of the ChromaDB collection
            embedding_model: Name of the embedding model to use
        """
        self.collection_name = collection_name or settings.chromadb_collection_name
        self.embedding_generator = EmbeddingGenerator(embedding_model)
        self.chunker = TextChunker()
        
        # Initialize ChromaDB client
        try:
            # Use the new ChromaDB API
            self.client = chromadb.PersistentClient(
                path="./data/chromadb"
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name=embedding_model
                )
            )
            
            logger.info(f"Initialized ChromaDB collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise
    
    async def index_document(
        self,
        document: Document,
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ) -> int:
        """
        Index a document for semantic search.
        
        Args:
            document: Document to index
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            
        Returns:
            Number of chunks indexed
        """
        try:
            # Get document text
            text = document.processed_text or document.raw_text or ""
            if not text:
                logger.warning(f"No text to index for document {document.id}")
                return 0
            
            # Split into chunks
            chunks = self.chunker.chunk_text(text, chunk_size, chunk_overlap)
            
            if not chunks:
                return 0
            
            # Prepare document metadata
            doc_metadata = {
                "title": document.title,
                "source_type": document.source_type,
                "language": document.language,
                "author": document.author,
                "created_at": document.created_at.isoformat() if document.created_at else "",
            }
            
            # Prepare data for ChromaDB
            ids = []
            documents = []
            metadatas = []
            
            for i, chunk in enumerate(chunks):
                chunk_metadata = self.chunker.create_chunk_metadata(
                    str(document.id),
                    i,
                    chunk,
                    doc_metadata
                )
                
                ids.append(chunk_metadata["chunk_id"])
                documents.append(chunk)
                metadatas.append(chunk_metadata)
            
            # Add to ChromaDB
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            
            logger.info(f"Indexed {len(chunks)} chunks for document {document.id}")
            return len(chunks)
            
        except Exception as e:
            logger.error(f"Error indexing document {document.id}: {e}")
            raise
    
    async def search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search.
        
        Args:
            query: Search query
            limit: Maximum number of results
            filters: Metadata filters to apply
            include_metadata: Whether to include metadata in results
            
        Returns:
            List of search results with scores and metadata
        """
        try:
            # Build where clause from filters
            where = {}
            if filters:
                if "source_type" in filters:
                    where["source_type"] = filters["source_type"]
                if "language" in filters:
                    where["language"] = filters["language"]
                if "author" in filters:
                    where["author"] = filters["author"]
            
            # Query ChromaDB
            results = self.collection.query(
                query_texts=[query],
                n_results=limit,
                where=where if where else None,
                include=["metadatas", "documents", "distances"] if include_metadata else ["distances"]
            )
            
            # Format results
            formatted_results = []
            if results["ids"] and results["ids"][0]:
                for i, chunk_id in enumerate(results["ids"][0]):
                    result = {
                        "chunk_id": chunk_id,
                        "score": 1.0 - results["distances"][0][i],  # Convert distance to similarity
                        "text": results["documents"][0][i] if "documents" in results else None,
                    }
                    
                    if include_metadata and "metadatas" in results:
                        result["metadata"] = results["metadatas"][0][i]
                        result["document_id"] = result["metadata"].get("document_id")
                    
                    formatted_results.append(result)
            
            logger.info(f"Semantic search for '{query}' returned {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Semantic search error: {e}")
            raise
    
    async def find_similar_documents(
        self,
        document_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find documents similar to a given document.
        
        Args:
            document_id: ID of the reference document
            limit: Maximum number of similar documents
            
        Returns:
            List of similar documents with scores
        """
        try:
            # Get embeddings for the reference document
            results = self.collection.get(
                where={"document_id": document_id},
                limit=1,
                include=["embeddings"]
            )
            
            if not results["ids"]:
                logger.warning(f"No embeddings found for document {document_id}")
                return []
            
            # Use the first embedding as reference
            reference_embedding = results["embeddings"][0]
            
            # Query for similar documents
            similar = self.collection.query(
                query_embeddings=[reference_embedding],
                n_results=limit + 1,  # +1 to exclude the reference document
                include=["metadatas", "distances"]
            )
            
            # Format and filter results
            formatted_results = []
            seen_docs = set()
            
            for i, chunk_id in enumerate(similar["ids"][0]):
                metadata = similar["metadatas"][0][i]
                doc_id = metadata.get("document_id")
                
                # Skip the reference document and duplicates
                if doc_id == document_id or doc_id in seen_docs:
                    continue
                
                seen_docs.add(doc_id)
                formatted_results.append({
                    "document_id": doc_id,
                    "title": metadata.get("title", ""),
                    "score": 1.0 - similar["distances"][0][i],
                    "source_type": metadata.get("source_type", "")
                })
                
                if len(formatted_results) >= limit:
                    break
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error finding similar documents: {e}")
            raise
    
    async def delete_document(self, document_id: str) -> int:
        """
        Delete all chunks for a document from the index.
        
        Args:
            document_id: ID of the document to delete
            
        Returns:
            Number of chunks deleted
        """
        try:
            # Get all chunk IDs for this document
            results = self.collection.get(
                where={"document_id": document_id},
                include=[]
            )
            
            if not results["ids"]:
                return 0
            
            # Delete chunks
            self.collection.delete(ids=results["ids"])
            
            logger.info(f"Deleted {len(results['ids'])} chunks for document {document_id}")
            return len(results["ids"])
            
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            raise
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector collection.
        
        Returns:
            Collection statistics
        """
        try:
            count = self.collection.count()
            
            return {
                "collection_name": self.collection_name,
                "total_chunks": count,
                "embedding_model": self.embedding_generator.model.get_sentence_embedding_dimension(),
                "embedding_dim": self.embedding_generator.embedding_dim
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {}
