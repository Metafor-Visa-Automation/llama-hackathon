#!/usr/bin/env python
"""
Recreate Qdrant collections with new vector size.
Run this when changing embedding model or vector dimensions.
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from config.settings import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def recreate_collections():
    """Recreate all Qdrant collections with new settings."""
    
    # Connect to Qdrant
    client = QdrantClient(
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT
    )
    
    collections = [
        settings.COLLECTION_VISA_REQUIREMENTS,
        settings.COLLECTION_COVER_LETTERS,
        settings.COLLECTION_VISA_DOCS_RAG
    ]
    
    for collection_name in collections:
        try:
            # Delete existing collection if it exists
            try:
                client.delete_collection(collection_name)
                logger.info(f"Deleted existing collection: {collection_name}")
            except:
                logger.info(f"Collection {collection_name} doesn't exist, creating new")
            
            # Create new collection with updated vector size
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=settings.QDRANT_VECTOR_SIZE,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"✓ Created collection: {collection_name} with vector size {settings.QDRANT_VECTOR_SIZE}")
            
        except Exception as e:
            logger.error(f"Failed to recreate {collection_name}: {str(e)}")
            return False
    
    logger.info(f"\n✅ Successfully recreated all collections with new vector size: {settings.QDRANT_VECTOR_SIZE}")
    logger.info(f"   Using embedding model: {settings.EMBEDDING_MODEL}")
    logger.info(f"   Top-K results: {settings.QDRANT_TOP_K}")
    logger.info(f"   Min similarity score: {settings.QDRANT_MIN_SCORE}")
    return True

if __name__ == "__main__":
    recreate_collections()