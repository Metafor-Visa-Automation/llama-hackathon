"""
Document Indexer Service - NEW!
Bridges scraping and cover letter generation by indexing visa requirements
into visa_docs_rag collection for cover letter context.
"""

from typing import List, Dict, Any
from models.visa_models import ScrapedData, VisaRequirement
from services.qdrant_service import QdrantService
from utils import logger
from utils.exceptions import QdrantError
from config.settings import settings


class DocumentIndexer:
    """
    Index documents for RAG.
    
    KEY PURPOSE:
    - When visa requirements are scraped, index them in visa_docs_rag
    - Cover letter generator can then use these as context
    - Bridge between visa scraping and cover letter generation
    """
    
    def __init__(self, qdrant_service: QdrantService):
        """
        Initialize document indexer.
        
        Args:
            qdrant_service: Qdrant service for storage
        """
        self.qdrant_service = qdrant_service
        logger.info("DocumentIndexer initialized")
    
    async def index_visa_requirements_for_rag(
        self,
        scraped_data: ScrapedData
    ) -> bool:
        """
        Index scraped visa requirements into visa_docs_rag collection.
        
        This makes them available for cover letter generation RAG.
        
        Args:
            scraped_data: Scraped visa data
            
        Returns:
            True if successful
            
        Raises:
            QdrantError: If indexing fails
        """
        try:
            logger.info(
                f"Indexing {len(scraped_data.requirements)} requirements "
                f"for {scraped_data.country} {scraped_data.visa_type}"
            )
            
            # Prepare documents
            documents = []
            texts = []
            
            for req in scraped_data.requirements:
                # Create document with rich context
                doc = {
                    'country': scraped_data.country,
                    'visa_type': scraped_data.visa_type,
                    'requirement_id': req.requirement_id,
                    'title': req.title,
                    'description': req.description,
                    'category': req.category,
                    'mandatory': req.mandatory,
                    'notes': req.notes,
                    'applicable_to': req.applicable_to,
                    'text': self._create_search_text(req),
                    'source_url': scraped_data.source_url,
                    'scraped_at': scraped_data.scraped_at.isoformat()
                }
                documents.append(doc)
                texts.append(doc['text'])
            
            # Add application steps if available
            if scraped_data.application_steps:
                for idx, step in enumerate(scraped_data.application_steps):
                    doc = {
                        'country': scraped_data.country,
                        'visa_type': scraped_data.visa_type,
                        'requirement_id': f"step_{idx + 1}",
                        'title': f"Application Step {idx + 1}",
                        'description': step,
                        'category': 'application_process',
                        'mandatory': True,
                        'text': f"Application Step {idx + 1}: {step}",
                        'source_url': scraped_data.source_url,
                        'scraped_at': scraped_data.scraped_at.isoformat()
                    }
                    documents.append(doc)
                    texts.append(doc['text'])
            
            # Add processing time and fees as documents
            if scraped_data.processing_time:
                doc = {
                    'country': scraped_data.country,
                    'visa_type': scraped_data.visa_type,
                    'requirement_id': 'processing_time',
                    'title': 'Processing Time',
                    'description': scraped_data.processing_time,
                    'category': 'information',
                    'mandatory': False,
                    'text': f"Processing Time: {scraped_data.processing_time}",
                    'source_url': scraped_data.source_url
                }
                documents.append(doc)
                texts.append(doc['text'])
            
            if not documents:
                logger.warning("No documents to index")
                return False
            
            # Encode texts to vectors
            await self.qdrant_service.connect()
            vectors = self.qdrant_service.encode(texts)
            
            # Store in visa_docs_rag collection
            success = await self.qdrant_service.add_documents(
                collection_name=settings.COLLECTION_VISA_DOCS_RAG,
                documents=documents,
                vectors=vectors
            )
            
            if success:
                logger.info(
                    f"✓ Successfully indexed {len(documents)} documents "
                    f"in visa_docs_rag collection"
                )
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to index visa requirements: {str(e)}")
            raise QdrantError(
                "Document indexing failed",
                {"error": str(e), "country": scraped_data.country}
            )
    
    async def index_example_cover_letter(
        self,
        letter_id: str,
        content: str,
        country: str,
        visa_type: str,
        approved: bool = False,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Index an example cover letter into cover_letters collection.
        
        Args:
            letter_id: Unique letter ID
            content: Cover letter content
            country: Target country
            visa_type: Visa type
            approved: Whether this was approved
            metadata: Additional metadata
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"Indexing example cover letter: {letter_id}")
            
            # Prepare document
            doc = {
                'id': letter_id,
                'content': content,
                'country': country.lower(),
                'visa_type': visa_type,
                'approved': approved,
                'text': content  # Full content for search
            }
            
            if metadata:
                doc.update(metadata)
            
            # Encode
            await self.qdrant_service.connect()
            vector = self.qdrant_service.encode([content])[0]
            
            # Store in cover_letters collection
            success = await self.qdrant_service.add_documents(
                collection_name=settings.COLLECTION_COVER_LETTERS,
                documents=[doc],
                vectors=[vector]
            )
            
            if success:
                logger.info(f"✓ Indexed example cover letter: {letter_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to index cover letter: {str(e)}")
            return False
    
    async def bulk_index_example_letters(
        self,
        examples: List[Dict[str, Any]]
    ) -> int:
        """
        Bulk index multiple example cover letters.
        
        Args:
            examples: List of example letter dictionaries
            
        Returns:
            Number of successfully indexed letters
        """
        success_count = 0
        
        for example in examples:
            try:
                success = await self.index_example_cover_letter(
                    letter_id=example.get('id', f"example_{success_count}"),
                    content=example.get('content', ''),
                    country=example.get('country', ''),
                    visa_type=example.get('visa_type', ''),
                    approved=example.get('approved', False),
                    metadata=example.get('metadata')
                )
                
                if success:
                    success_count += 1
                    
            except Exception as e:
                logger.warning(f"Failed to index example: {str(e)}")
                continue
        
        logger.info(f"Bulk indexed {success_count}/{len(examples)} example letters")
        return success_count
    
    def _create_search_text(self, requirement: VisaRequirement) -> str:
        """
        Create rich search text from requirement.
        
        Args:
            requirement: Visa requirement
            
        Returns:
            Formatted search text
        """
        parts = [
            f"{requirement.title}.",
            requirement.description
        ]
        
        if requirement.notes:
            parts.append(f"Note: {requirement.notes}")
        
        if requirement.applicable_to:
            parts.append(f"Applies to: {', '.join(requirement.applicable_to)}")
        
        return " ".join(parts)
    
    async def close(self):
        """Close document indexer."""
        logger.info("✓ DocumentIndexer closed")


__all__ = ['DocumentIndexer']

