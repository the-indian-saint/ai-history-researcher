"""ChromaDB vector storage connection and management."""

from typing import Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings

from ..config import settings

# ChromaDB client
chroma_client = None
collection = None


async def init_vector_storage() -> None:
    """Initialize ChromaDB connection."""
    global chroma_client, collection
    
    # Use the correct HttpClient initialization for ChromaDB 1.0.x
    chroma_client = chromadb.HttpClient(
        host=settings.chromadb_host,
        port=settings.chromadb_port
    )
    
    # Get or create collection
    try:
        collection = chroma_client.get_collection(settings.chromadb_collection_name)
    except Exception:
        collection = chroma_client.create_collection(
            name=settings.chromadb_collection_name,
            metadata={"description": "AI Research Framework document collection"}
        )


async def get_vector_storage():
    """Get ChromaDB collection."""
    if not collection:
        raise RuntimeError("Vector storage not initialized")
    return collection


async def check_vector_storage_health() -> Dict[str, Any]:
    """Check vector storage health."""
    try:
        if not chroma_client:
            return {"healthy": False, "error": "Client not initialized"}
        
        # Try to get collection info
        collections = chroma_client.list_collections()
        collection_names = [col.name for col in collections]
        
        return {
            "healthy": True,
            "collections": collection_names,
            "target_collection": settings.chromadb_collection_name,
            "collection_exists": settings.chromadb_collection_name in collection_names,
        }
    except Exception as e:
        return {
            "healthy": False,
            "error": str(e)
        }

