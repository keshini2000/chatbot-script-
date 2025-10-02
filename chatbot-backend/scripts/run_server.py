#!/usr/bin/env python3
"""
Run the Core DNA Chatbot API server
"""

import sys
import os
import logging
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import uvicorn
from api.main import 
app
from config.settings import settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'api_server_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Run the API server"""
    logger.info("=" * 60)
    logger.info("Starting Core DNA Chatbot API Server")
    logger.info("=" * 60)
    
    try:
        # Check if data exists
        data_files = [
            "data/raw/coredna_scraped_data.json",
            "data/processed/coredna_processed_data.json", 
            "data/processed/coredna_chunks.json"
        ]
        
        missing_files = []
        for file_path in data_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if missing_files:
            logger.warning("⚠️  Some data files are missing:")
            for file in missing_files:
                logger.warning(f"   - {file}")
            logger.warning("   Run the scraping pipeline first: python scripts/scrape_and_index.py")
        else:
            logger.info("✅ All data files present")
        
        # Check if vector database exists
        if os.path.exists(settings.chroma_db_path):
            logger.info("✅ Vector database found")
        else:
            logger.warning("⚠️  Vector database not found. Run: python scripts/setup_database.py")
        
        logger.info(f"🚀 Starting server on {settings.api_host}:{settings.api_port}")
        logger.info(f"📖 API Documentation: http://{settings.api_host}:{settings.api_port}/docs")
        logger.info(f"🔍 Alternative docs: http://{settings.api_host}:{settings.api_port}/redoc")
        logger.info(f"❤️  Health check: http://{settings.api_host}:{settings.api_port}/health")
        
        # Run the server
        uvicorn.run(
            app,
            host=settings.api_host,
            port=settings.api_port,
            reload=True,
            log_level="info",
            access_log=True
        )
        
    except KeyboardInterrupt:
        logger.info("👋 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server failed to start: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()