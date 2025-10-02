from fastapi import APIRouter, HTTPException
from datetime import datetime
import os
import logging

try:
    from ...config.settings import settings
    from ..models.schemas import HealthResponse, IndexStatus
    from ...vector_store.chroma_store import ChromaVectorStore
except ImportError:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
    from config.settings import settings
    from api.models.schemas import HealthResponse, IndexStatus
    from vector_store.chroma_store import ChromaVectorStore

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=HealthResponse)
async def health_check():
    """Basic health check endpoint"""
    try:
        # Check if vector database directory exists
        db_status = "healthy" if os.path.exists(settings.chroma_db_path) else "missing"
        
        return HealthResponse(
            status="healthy",
            version="1.0.0",
            database_status=db_status,
            timestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/database", response_model=IndexStatus)
async def database_status():
    """Check vector database status"""
    try:
        vector_store = ChromaVectorStore()
        info = vector_store.get_collection_info()
        
        return IndexStatus(
            total_documents=info.get('document_count', 0),
            last_updated=None,  # We could add this to metadata
            is_ready=info.get('document_count', 0) > 0
        )
    except Exception as e:
        logger.error(f"Database status check failed: {e}")
        return IndexStatus(
            total_documents=0,
            last_updated=None,
            is_ready=False
        )

@router.get("/detailed")
async def detailed_health():
    """Detailed system health information"""
    try:
        # Check database
        db_healthy = False
        document_count = 0
        
        try:
            vector_store = ChromaVectorStore()
            info = vector_store.get_collection_info()
            document_count = info.get('document_count', 0)
            db_healthy = document_count > 0
        except Exception as e:
            logger.warning(f"Database check failed: {e}")
        
        # Check file system
        data_dir_exists = os.path.exists("data")
        processed_dir_exists = os.path.exists("data/processed")
        vector_db_dir_exists = os.path.exists(settings.chroma_db_path)
        
        # Check if scraped data exists
        scraped_data_exists = os.path.exists("data/raw/coredna_scraped_data.json")
        processed_data_exists = os.path.exists("data/processed/coredna_processed_data.json")
        chunks_exist = os.path.exists("data/processed/coredna_chunks.json")
        
        return {
            "status": "healthy" if db_healthy else "degraded",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "components": {
                "database": {
                    "status": "healthy" if db_healthy else "unhealthy",
                    "document_count": document_count,
                    "directory_exists": vector_db_dir_exists
                },
                "filesystem": {
                    "data_directory": data_dir_exists,
                    "processed_directory": processed_dir_exists,
                    "vector_db_directory": vector_db_dir_exists
                },
                "data_files": {
                    "scraped_data": scraped_data_exists,
                    "processed_data": processed_data_exists,
                    "text_chunks": chunks_exist
                }
            },
            "configuration": {
                "chroma_db_path": settings.chroma_db_path,
                "api_host": settings.api_host,
                "api_port": settings.api_port,
                "chunk_size": settings.chunk_size
            }
        }
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")