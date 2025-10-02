from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

try:
    from ..vector_store.chroma_store import ChromaVectorStore
    from ..config.settings import settings
except ImportError:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from vector_store.chroma_store import ChromaVectorStore
    from config.settings import settings

logger = logging.getLogger(__name__)

class DocumentRetriever:
    def __init__(self, collection_name: str = "coredna_docs"):
        self.collection_name = collection_name
        self.vector_store = ChromaVectorStore(collection_name=collection_name)
        
    def retrieve_relevant_docs(self, query: str, n_results: int = 5, 
                             min_relevance_score: float = 0.0) -> List[Dict[str, Any]]:
        """Retrieve relevant documents for a query"""
        try:
            # Query the vector store
            results = self.vector_store.query(
                query_text=query,
                n_results=n_results,
                include_metadata=True
            )
            
            # Filter by relevance score if specified
            filtered_results = []
            for result in results:
                # ChromaDB returns distance (lower is better), convert to similarity score
                similarity_score = 1.0 - result['distance']
                
                if similarity_score >= min_relevance_score:
                    result['similarity_score'] = similarity_score
                    filtered_results.append(result)
            
            logger.info(f"Retrieved {len(filtered_results)} relevant documents for query: {query[:50]}...")
            return filtered_results
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []

    def get_document_context(self, query: str, max_context_length: int = 4000) -> str:
        """Get concatenated context from relevant documents"""
        try:
            # Retrieve relevant documents
            docs = self.retrieve_relevant_docs(query, n_results=10)
            
            if not docs:
                return ""
            
            # Build context string
            context_parts = []
            current_length = 0
            
            for doc in docs:
                text = doc['text']
                metadata = doc.get('metadata', {})
                
                # Add source information
                source_url = metadata.get('source_url', 'Unknown')
                title = metadata.get('title', 'Unknown')
                
                # Format the document with source info
                doc_text = f"[Source: {title} - {source_url}]\n{text}\n"
                
                # Check if adding this document would exceed max length
                if current_length + len(doc_text) > max_context_length:
                    break
                
                context_parts.append(doc_text)
                current_length += len(doc_text)
            
            context = "\n---\n".join(context_parts)
            
            logger.info(f"Built context with {len(context_parts)} documents, {current_length} characters")
            return context
            
        except Exception as e:
            logger.error(f"Error building document context: {e}")
            return ""

    def find_similar_questions(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Find documents that might contain answers to similar questions"""
        try:
            # Enhance query to find FAQ-like content
            enhanced_query = f"question answer FAQ help guide how to {query}"
            
            docs = self.retrieve_relevant_docs(enhanced_query, n_results=n_results)
            
            # Filter for documents that seem to contain Q&A content
            qa_docs = []
            for doc in docs:
                text = doc['text'].lower()
                if any(keyword in text for keyword in ['how to', 'what is', 'why', 'when', 'where', 'question', 'answer', 'faq']):
                    qa_docs.append(doc)
            
            return qa_docs
            
        except Exception as e:
            logger.error(f"Error finding similar questions: {e}")
            return []

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the document collection"""
        try:
            info = self.vector_store.get_collection_info()
            
            # Get a sample of documents to analyze
            sample_docs = self.vector_store.query("Core DNA platform", n_results=50)
            
            if sample_docs:
                # Analyze content types
                content_types = {}
                total_length = 0
                
                for doc in sample_docs:
                    metadata = doc.get('metadata', {})
                    url = metadata.get('source_url', '')
                    
                    # Categorize by URL pattern
                    if '/blogs/' in url:
                        content_types['blog'] = content_types.get('blog', 0) + 1
                    elif '/all-features/' in url:
                        content_types['features'] = content_types.get('features', 0) + 1
                    elif '/customers/' in url:
                        content_types['case_studies'] = content_types.get('case_studies', 0) + 1
                    elif '/guides/' in url:
                        content_types['guides'] = content_types.get('guides', 0) + 1
                    else:
                        content_types['other'] = content_types.get('other', 0) + 1
                    
                    total_length += len(doc['text'])
                
                avg_length = total_length / len(sample_docs) if sample_docs else 0
                
                stats = {
                    **info,
                    'content_types': content_types,
                    'avg_document_length': avg_length,
                    'sample_size': len(sample_docs)
                }
            else:
                stats = info
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {}

    def search_by_category(self, query: str, category: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for documents in a specific category"""
        try:
            # Map categories to URL patterns
            category_patterns = {
                'blog': '/blogs/',
                'features': '/all-features/',
                'case_studies': '/customers/',
                'guides': '/guides/',
                'integrations': '/integrations/',
                'ecommerce': '/ecommerce/',
                'content': '/content/'
            }
            
            if category not in category_patterns:
                logger.warning(f"Unknown category: {category}")
                return self.retrieve_relevant_docs(query, n_results)
            
            # Get all relevant docs first
            all_docs = self.retrieve_relevant_docs(query, n_results=n_results * 3)
            
            # Filter by category
            pattern = category_patterns[category]
            category_docs = []
            
            for doc in all_docs:
                metadata = doc.get('metadata', {})
                url = metadata.get('source_url', '')
                
                if pattern in url:
                    category_docs.append(doc)
                    
                if len(category_docs) >= n_results:
                    break
            
            logger.info(f"Found {len(category_docs)} documents in category '{category}' for query: {query[:50]}...")
            return category_docs
            
        except Exception as e:
            logger.error(f"Error searching by category: {e}")
            return []

if __name__ == "__main__":
    # Test the retriever
    retriever = DocumentRetriever()
    
    # Get collection stats
    stats = retriever.get_collection_stats()
    print("📊 Collection Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Test retrieval
    test_query = "ecommerce platform features"
    print(f"\n🔍 Testing retrieval for: '{test_query}'")
    
    docs = retriever.retrieve_relevant_docs(test_query, n_results=3)
    for i, doc in enumerate(docs):
        print(f"\n{i+1}. Similarity: {doc.get('similarity_score', 0.0):.3f}")
        print(f"   Text: {doc['text'][:100]}...")
        if 'metadata' in doc:
            print(f"   Source: {doc['metadata'].get('source_url', 'N/A')}")
    
    # Test context building
    print(f"\n📄 Testing context building...")
    context = retriever.get_document_context(test_query, max_context_length=1000)
    print(f"Context length: {len(context)} characters")
    print(f"Context preview: {context[:200]}...")