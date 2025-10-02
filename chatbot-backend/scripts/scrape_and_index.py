#!/usr/bin/env python3
"""
Complete pipeline to scrape Core DNA website and prepare data for indexing
"""

import sys
import os
import logging
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from scraper.web_scraper import CoreDNAScraper
from scraper.content_processor import ContentProcessor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'scraping_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Run the complete scraping and processing pipeline"""
    logger.info("=" * 60)
    logger.info("Starting Core DNA website scraping and processing pipeline")
    logger.info("=" * 60)
    
    try:
        # Step 1: Scrape the website
        logger.info("Step 1: Scraping Core DNA website...")
        scraper = CoreDNAScraper()
        scraped_pages = scraper.scrape_all_pages()
        
        if not scraped_pages:
            logger.error("No pages were scraped. Exiting.")
            return False
            
        # Save scraped data
        raw_data_path = scraper.save_to_json()
        logger.info(f"Scraped {len(scraped_pages)} pages and saved to {raw_data_path}")
        
        # Step 2: Process the scraped content
        logger.info("Step 2: Processing scraped content...")
        processor = ContentProcessor()
        processed_docs = processor.process_scraped_data(raw_data_path)
        
        if not processed_docs:
            logger.error("No documents were processed. Exiting.")
            return False
            
        # Save processed data
        processed_data_path = processor.save_processed_data()
        logger.info(f"Processed {len(processed_docs)} documents and saved to {processed_data_path}")
        
        # Step 3: Create text chunks for vector indexing
        logger.info("Step 3: Creating text chunks for vector indexing...")
        chunks = processor.create_text_chunks()
        
        # Save chunks
        chunks_output = os.path.join("data", "processed", "coredna_chunks.json")
        os.makedirs(os.path.dirname(chunks_output), exist_ok=True)
        
        import json
        with open(chunks_output, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Created {len(chunks)} text chunks and saved to {chunks_output}")
        
        # Summary
        logger.info("=" * 60)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        logger.info(f"📄 Pages scraped: {len(scraped_pages)}")
        logger.info(f"📝 Documents processed: {len(processed_docs)}")
        logger.info(f"🧩 Text chunks created: {len(chunks)}")
        logger.info(f"📁 Raw data: {raw_data_path}")
        logger.info(f"📁 Processed data: {processed_data_path}")
        logger.info(f"📁 Text chunks: {chunks_output}")
        logger.info("=" * 60)
        logger.info("Next step: Run vector database indexing")
        
        return True
        
    except Exception as e:
        logger.error(f"Pipeline failed with error: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)