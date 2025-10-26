"""
Enhanced Qdrant service with multi-collection support.
Supports 3 collections:
1. visa_requirements - For checklist generation RAG
2. cover_letter_examples - Example cover letters
3. visa_documents_rag - Visa requirements for cover letter context
"""

from typing import List, Dict, Any, Optional
try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
    from sentence_transformers import SentenceTransformer
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    QdrantClient = None
    Distance = None
    VectorParams = None
    PointStruct = None
    Filter = None
    FieldCondition = None
    MatchValue = None
    SentenceTransformer = None

from utils import logger
from utils.exceptions import QdrantError, ConfigurationError
from config.settings import settings


class QdrantService:
    """
    Enhanced Qdrant service with multi-collection support.
    Manages 3 separate collections for different RAG purposes.
    """
    
    def __init__(self):
        """Initialize Qdrant service."""
        if not QDRANT_AVAILABLE:
            raise ImportError(
                "Qdrant client or sentence-transformers not installed. "
                "Install with: pip install qdrant-client sentence-transformers"
            )
        self._client: Optional[QdrantClient] = None
        self._encoder: Optional[SentenceTransformer] = None
        self._initialized = False
        
        # Collection names from settings
        self.collections = {
            'visa_requirements': settings.COLLECTION_VISA_REQUIREMENTS,
            'cover_letters': settings.COLLECTION_COVER_LETTERS,
            'visa_docs_rag': settings.COLLECTION_VISA_DOCS_RAG
        }
    
    async def connect(self) -> None:
        """Establish connection to Qdrant and initialize all collections."""
        if self._initialized:
            logger.info("Qdrant already connected")
            return
        
        try:
            # Initialize Qdrant client
            if settings.QDRANT_API_KEY:
                self._client = QdrantClient(
                    host=settings.QDRANT_HOST,
                    port=settings.QDRANT_PORT,
                    api_key=settings.QDRANT_API_KEY
                )
            else:
                self._client = QdrantClient(
                    host=settings.QDRANT_HOST,
                    port=settings.QDRANT_PORT
                )
            
            # Initialize embedding model
            logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
            self._encoder = SentenceTransformer(settings.EMBEDDING_MODEL)
            
            # Verify or create all collections
            for collection_key, collection_name in self.collections.items():
                try:
                    self._client.get_collection(collection_name)
                    logger.info(f"Connected to collection: {collection_name}")
                except Exception:
                    await self._create_collection(collection_name)
            
            self._initialized = True
            logger.info("Qdrant connection established successfully with all collections")
            
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {str(e)}")
            raise QdrantError(
                "Qdrant connection failed",
                {"error": str(e)}
            )
    
    async def _create_collection(self, collection_name: str) -> None:
        """Create Qdrant collection if it doesn't exist."""
        try:
            self._client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=settings.QDRANT_VECTOR_SIZE,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Created Qdrant collection: {collection_name}")
        except Exception as e:
            logger.error(f"Failed to create collection {collection_name}: {str(e)}")
            raise QdrantError(
                f"Failed to create Qdrant collection: {collection_name}",
                {"error": str(e)}
            )
    
    def encode(self, texts: List[str]) -> List[List[float]]:
        """
        Encode texts into vectors.
        
        Args:
            texts: List of texts to encode
            
        Returns:
            List of embedding vectors
        """
        if not self._encoder:
            raise QdrantError("Encoder not initialized", {})
        
        embeddings = self._encoder.encode(texts, show_progress_bar=False)
        return embeddings.tolist()
    
    async def search(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents in specific collection.
        
        Args:
            collection_name: Name of collection to search
            query_vector: Query embedding vector
            limit: Maximum number of results
            filters: Optional filters (e.g., country, visa_type)
            
        Returns:
            List of similar documents with scores
        """
        if not self._initialized:
            await self.connect()
        
        try:
            # Build filter conditions
            query_filter = None
            if filters:
                conditions = []
                for key, value in filters.items():
                    conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value)
                        )
                    )
                if conditions:
                    query_filter = Filter(must=conditions)
            
            # Perform search
            search_results = self._client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                query_filter=query_filter,
                limit=limit
            )
            
            # Format results and apply score filtering
            results = []
            min_score = settings.QDRANT_MIN_SCORE
            
            for result in search_results:
                # Filter by minimum score
                if result.score >= min_score:
                    results.append({
                        "id": str(result.id),
                        "score": result.score,
                        "payload": result.payload
                    })
            
            logger.info(f"Found {len(results)} results in {collection_name} (filtered by min_score={min_score})")
            return results
            
        except Exception as e:
            logger.error(f"Qdrant search failed in {collection_name}: {str(e)}")
            raise QdrantError(
                f"Vector search failed in {collection_name}",
                {"error": str(e)}
            )
    
    async def add_documents(
        self,
        collection_name: str,
        documents: List[Dict[str, Any]],
        vectors: List[List[float]]
    ) -> bool:
        """
        Add documents to specific collection.
        
        Args:
            collection_name: Target collection
            documents: List of documents
            vectors: Corresponding embedding vectors
            
        Returns:
            True if successful
        """
        if not self._initialized:
            await self.connect()
        
        if len(documents) != len(vectors):
            raise QdrantError(
                "Mismatch between documents and vectors count",
                {"documents": len(documents), "vectors": len(vectors)}
            )
        
        try:
            # Get current max ID to avoid conflicts
            try:
                collection_info = self._client.get_collection(collection_name)
                start_id = collection_info.points_count
            except:
                start_id = 0
            
            # Create points for insertion
            points = []
            for idx, (doc, vector) in enumerate(zip(documents, vectors)):
                points.append(
                    PointStruct(
                        id=start_id + idx,
                        vector=vector,
                        payload=doc
                    )
                )
            
            # Insert into Qdrant
            self._client.upsert(
                collection_name=collection_name,
                points=points
            )
            
            logger.info(f"Added {len(documents)} documents to {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add documents to {collection_name}: {str(e)}")
            raise QdrantError(
                f"Failed to add documents to {collection_name}",
                {"error": str(e)}
            )
    
    async def search_visa_requirements(
        self,
        query_text: str,
        country: Optional[str] = None,
        visa_type: Optional[str] = None,
        limit: int = None
    ) -> List[Dict[str, Any]]:
        """
        Search visa_requirements collection for checklist generation.
        
        Args:
            query_text: Query text describing the profile
            country: Filter by country
            visa_type: Filter by visa type
            limit: Maximum results
            
        Returns:
            List of similar visa requirements
        """
        query_vector = self.encode([query_text])[0]
        
        filters = {}
        if country:
            filters['country'] = country.lower()
        if visa_type:
            filters['visa_type'] = visa_type
        
        limit = limit or settings.QDRANT_TOP_K
        
        return await self.search(
            collection_name=self.collections['visa_requirements'],
            query_vector=query_vector,
            limit=limit,
            filters=filters if filters else None
        )
    
    async def search_cover_letter_examples(
        self,
        query_text: str,
        country: Optional[str] = None,
        visa_type: Optional[str] = None,
        limit: int = None
    ) -> List[Dict[str, Any]]:
        """
        Search cover_letters collection for example letters.
        
        Args:
            query_text: Query text
            country: Filter by country
            visa_type: Filter by visa type
            limit: Maximum results
            
        Returns:
            List of example cover letters
        """
        query_vector = self.encode([query_text])[0]
        
        filters = {}
        if country:
            filters['country'] = country.lower()
        if visa_type:
            filters['visa_type'] = visa_type
        
        limit = limit or settings.QDRANT_TOP_K
        
        return await self.search(
            collection_name=self.collections['cover_letters'],
            query_vector=query_vector,
            limit=limit,
            filters=filters if filters else None
        )
    
    async def search_visa_docs_for_cover_letter(
        self,
        query_text: str,
        country: Optional[str] = None,
        visa_type: Optional[str] = None,
        limit: int = None
    ) -> List[Dict[str, Any]]:
        """
        Search visa_documents_rag collection for visa requirements context.
        Used during cover letter generation to include actual requirements.
        
        Args:
            query_text: Query text
            country: Filter by country
            visa_type: Filter by visa type
            limit: Maximum results
            
        Returns:
            List of visa requirements for context
        """
        query_vector = self.encode([query_text])[0]
        
        filters = {}
        if country:
            filters['country'] = country.lower()
        if visa_type:
            filters['visa_type'] = visa_type
        
        limit = limit or settings.QDRANT_TOP_K
        
        return await self.search(
            collection_name=self.collections['visa_docs_rag'],
            query_vector=query_vector,
            limit=limit,
            filters=filters if filters else None
        )
    
    async def close(self) -> None:
        """Close Qdrant client (if needed)."""
        self._initialized = False
        logger.info("Qdrant service closed")


__all__ = ['QdrantService']

