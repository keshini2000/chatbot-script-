#!/usr/bin/env python3
"""
Setup and initialize the vector database with Core DNA content
"""

import sys
import os
import logging
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from vector_store.chroma_store import ChromaVectorStore, index_coredna_documents
from vector_store.embeddings import EmbeddingManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'database_setup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def test_embeddings() -> bool:
    """Test if OpenAI embeddings are working"""
    logger.info("Testing OpenAI embeddings...")
    
    try:
        embedding_manager = EmbeddingManager()
        success = embedding_manager.test_embedding()
        
        if success:
            logger.info("✅ Embeddings test passed")
            return True
        else:
            logger.error("❌ Embeddings test failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Failed to initialize embeddings: {e}")
        logger.error("💡 Make sure to set your OpenAI API key in the .env file")
        return False

def setup_vector_database() -> bool:
    """Setup and populate the vector database"""
    logger.info("=" * 60)
    logger.info("Setting up Core DNA vector database")
    logger.info("=" * 60)
    
    # Check if processed chunks exist
    chunks_file = os.path.join("data", "processed", "coredna_chunks.json")
    if not os.path.exists(chunks_file):
        logger.error(f"Processed chunks file not found: {chunks_file}")
        logger.error("Run the scraping pipeline first: python scripts/scrape_and_index.py")
        return False
    
    # Test embeddings first
    if not test_embeddings():
        return False
    
    # Index documents
    logger.info("Indexing Core DNA documents into vector database...")
    success = index_coredna_documents(chunks_file)
    
    if success:
        # Test query
        logger.info("Testing vector database with sample query...")
        vector_store = ChromaVectorStore()
        
        test_queries = [
            "ecommerce platform features",
            "content management system",
            "API integration capabilities"
        ]
        
        for query in test_queries:
            results = vector_store.query(query, n_results=3)
            logger.info(f"Query: '{query}' returned {len(results)} results")
            
            if results:
                best_result = results[0]
                logger.info(f"  Best match (distance: {best_result['distance']:.3f}): {best_result['text'][:100]}...")
        
        # Get collection info
        info = vector_store.get_collection_info()
        
        logger.info("=" * 60)
        logger.info("DATABASE SETUP COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        logger.info(f"📊 Collection: {info.get('name', 'N/A')}")
        logger.info(f"📄 Documents indexed: {info.get('document_count', 'N/A')}")
        logger.info(f"📁 Database location: {info.get('persist_directory', 'N/A')}")
        logger.info("=" * 60)
        logger.info("Vector database is ready for RAG queries!")
        
        return True
    else:
        logger.error("Failed to index documents")
        return False

def reset_database() -> bool:
    """Reset the vector database"""
    logger.info("Resetting vector database...")
    
    try:
        vector_store = ChromaVectorStore()
        success = vector_store.reset_collection()
        
        if success:
            logger.info("✅ Database reset successfully")
            return True
        else:
            logger.error("❌ Failed to reset database")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error resetting database: {e}")
        return False

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup Core DNA vector database")
    parser.add_argument("--reset", action="store_true", help="Reset the database before setup")
    parser.add_argument("--test-only", action="store_true", help="Only test embeddings, don't setup database")
    
    args = parser.parse_args()
    
    if args.test_only:
        success = test_embeddings()
        sys.exit(0 if success else 1)
    
    if args.reset:
        if not reset_database():
            sys.exit(1)
    
    success = setup_vector_database()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()