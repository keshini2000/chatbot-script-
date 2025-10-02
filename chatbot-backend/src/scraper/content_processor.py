import re
import json
import os
from typing import List, Dict, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ProcessedDocument:
    url: str
    title: str
    content: str
    metadata: Dict[str, Any]

class ContentProcessor:
    def __init__(self):
        self.processed_docs: List[ProcessedDocument] = []

    def clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
            
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.,\!\?\-\(\)\[\]\:\;\"\'\/]', '', text)
        
        # Remove repeated punctuation
        text = re.sub(r'[\.]{2,}', '.', text)
        text = re.sub(r'[\!\?]{2,}', '!', text)
        
        # Fix spacing around punctuation
        text = re.sub(r'\s+([,\.!?;:])', r'\1', text)
        text = re.sub(r'([,\.!?;:])\s*', r'\1 ', text)
        
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def extract_key_information(self, content: str, title: str, headers: List[str]) -> str:
        """Extract and organize key information from content"""
        processed_content = []
        
        # Add title as primary context
        if title:
            processed_content.append(f"Page Title: {self.clean_text(title)}")
            
        # Add headers for structure
        if headers:
            processed_content.append("\nKey Sections:")
            for header in headers[:10]:  # Limit to first 10 headers
                clean_header = self.clean_text(header)
                if clean_header and len(clean_header) > 3:
                    processed_content.append(f"- {clean_header}")
        
        # Add main content
        if content:
            clean_content = self.clean_text(content)
            if clean_content:
                processed_content.append(f"\nContent:\n{clean_content}")
        
        return '\n'.join(processed_content)

    def is_valuable_content(self, content: str, title: str) -> bool:
        """Determine if content is valuable enough to include"""
        # Skip if too short
        if len(content.strip()) < 100:
            return False
            
        # Skip if mostly navigation or boilerplate
        low_value_indicators = [
            'cookie policy', 'privacy policy', 'terms of service',
            'page not found', '404', 'error', 'maintenance',
            'coming soon', 'under construction'
        ]
        
        content_lower = content.lower()
        title_lower = title.lower() if title else ""
        
        for indicator in low_value_indicators:
            if indicator in content_lower or indicator in title_lower:
                return False
                
        # Check content-to-navigation ratio
        content_words = len(content.split())
        if content_words < 50:
            return False
            
        return True

    def process_scraped_data(self, input_file: str) -> List[ProcessedDocument]:
        """Process scraped data from JSON file"""
        logger.info(f"Processing scraped data from: {input_file}")
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                scraped_data = json.load(f)
        except Exception as e:
            logger.error(f"Error reading scraped data: {e}")
            return []

        processed_count = 0
        skipped_count = 0
        
        for page_data in scraped_data:
            url = page_data.get('url', '')
            title = page_data.get('title', '')
            content = page_data.get('content', '')
            meta_description = page_data.get('meta_description', '')
            headers = page_data.get('headers', [])
            timestamp = page_data.get('timestamp', '')
            
            # Skip if not valuable content
            if not self.is_valuable_content(content, title):
                skipped_count += 1
                logger.debug(f"Skipping low-value content: {url}")
                continue
            
            # Process and clean content
            processed_content = self.extract_key_information(content, title, headers)
            
            # Create metadata
            metadata = {
                'source_url': url,
                'scraped_timestamp': timestamp,
                'meta_description': self.clean_text(meta_description),
                'headers_count': len(headers),
                'content_length': len(processed_content),
                'original_title': title
            }
            
            # Create processed document
            processed_doc = ProcessedDocument(
                url=url,
                title=self.clean_text(title),
                content=processed_content,
                metadata=metadata
            )
            
            self.processed_docs.append(processed_doc)
            processed_count += 1
            
        logger.info(f"Processing complete. Processed: {processed_count}, Skipped: {skipped_count}")
        return self.processed_docs

    def save_processed_data(self, output_path: str = None) -> str:
        """Save processed documents to JSON file"""
        if not output_path:
            output_path = os.path.join("data", "processed", "coredna_processed_data.json")
            
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Convert to serializable format
        data_dict = []
        for doc in self.processed_docs:
            data_dict.append({
                'url': doc.url,
                'title': doc.title,
                'content': doc.content,
                'metadata': doc.metadata
            })
            
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data_dict, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Processed data saved to: {output_path}")
        return output_path

    def create_text_chunks(self, max_chunk_size: int = 1000, overlap: int = 200) -> List[Dict[str, Any]]:
        """Split processed documents into chunks for vector indexing"""
        chunks = []
        
        for doc in self.processed_docs:
            content = doc.content
            
            # If content is smaller than max_chunk_size, keep as single chunk
            if len(content) <= max_chunk_size:
                chunks.append({
                    'text': content,
                    'metadata': {
                        **doc.metadata,
                        'chunk_id': 0,
                        'total_chunks': 1,
                        'title': doc.title
                    }
                })
                continue
            
            # Split into overlapping chunks
            words = content.split()
            chunk_size_words = max_chunk_size // 5  # Rough estimate: 5 chars per word
            overlap_words = overlap // 5
            
            chunk_id = 0
            start_idx = 0
            
            while start_idx < len(words):
                end_idx = min(start_idx + chunk_size_words, len(words))
                chunk_words = words[start_idx:end_idx]
                chunk_text = ' '.join(chunk_words)
                
                chunks.append({
                    'text': chunk_text,
                    'metadata': {
                        **doc.metadata,
                        'chunk_id': chunk_id,
                        'title': doc.title,
                        'chunk_start': start_idx,
                        'chunk_end': end_idx
                    }
                })
                
                # Move start index with overlap
                start_idx = end_idx - overlap_words
                chunk_id += 1
                
                # Break if we've reached the end
                if end_idx >= len(words):
                    break
                    
        # Update total_chunks for each document
        url_chunk_counts = {}
        for chunk in chunks:
            url = chunk['metadata']['source_url']
            url_chunk_counts[url] = url_chunk_counts.get(url, 0) + 1
            
        for chunk in chunks:
            url = chunk['metadata']['source_url']
            chunk['metadata']['total_chunks'] = url_chunk_counts[url]
            
        logger.info(f"Created {len(chunks)} text chunks from {len(self.processed_docs)} documents")
        return chunks

if __name__ == "__main__":
    processor = ContentProcessor()
    
    # Process scraped data
    input_file = os.path.join("data", "raw", "coredna_scraped_data.json")
    if os.path.exists(input_file):
        processor.process_scraped_data(input_file)
        processor.save_processed_data()
        
        # Create chunks
        chunks = processor.create_text_chunks()
        chunks_output = os.path.join("data", "processed", "coredna_chunks.json")
        with open(chunks_output, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)
        logger.info(f"Text chunks saved to: {chunks_output}")
    else:
        logger.error(f"Input file not found: {input_file}")