import chromadb
from chromadb.config import Settings
import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    from ..config.settings import settings
except ImportError:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from config.settings import settings

logger = logging.getLogger(__name__)

class ChromaVectorStore:
    def __init__(self, collection_name: str = "coredna_docs", persist_directory: str = None):
        self.collection_name = collection_name
        self.persist_directory = persist_directory or settings.chroma_db_path
        
        # Ensure directory exists
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"Loaded existing collection: {self.collection_name}")
        except Exception:
            # Collection doesn't exist, create it
            try:
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "Core DNA website content for RAG"}
                )
                logger.info(f"Created new collection: {self.collection_name}")
            except Exception as e:
                logger.error(f"Failed to create collection: {e}")
                raise

    def add_documents(self, chunks: List[Dict[str, Any]]) -> bool:
        """Add document chunks to the vector store"""
        try:
            documents = []
            metadatas = []
            ids = []
            
            for i, chunk in enumerate(chunks):
                # Create unique ID for each chunk
                url = chunk['metadata']['source_url']
                chunk_id = chunk['metadata'].get('chunk_id', 0)
                doc_id = f"{hash(url)}_{chunk_id}"
                
                documents.append(chunk['text'])
                metadatas.append(chunk['metadata'])
                ids.append(doc_id)
            
            # Add to collection in batches to avoid memory issues
            batch_size = 100
            total_added = 0
            
            for i in range(0, len(documents), batch_size):
                end_idx = min(i + batch_size, len(documents))
                batch_docs = documents[i:end_idx]
                batch_metadata = metadatas[i:end_idx]
                batch_ids = ids[i:end_idx]
                
                self.collection.add(
                    documents=batch_docs,
                    metadatas=batch_metadata,
                    ids=batch_ids
                )
                
                total_added += len(batch_docs)
                logger.info(f"Added batch {i//batch_size + 1}: {total_added}/{len(documents)} documents")
            
            logger.info(f"Successfully added {total_added} documents to vector store")
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            return False

    def query(self, query_text: str, n_results: int = 5, 
              include_metadata: bool = True) -> List[Dict[str, Any]]:
        """Query the vector store for relevant documents"""
        try:
            include_fields = ["documents", "distances"]
            if include_metadata:
                include_fields.append("metadatas")
            
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                include=include_fields
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results['documents'][0])):
                result = {
                    'text': results['documents'][0][i],
                    'distance': results['distances'][0][i],
                }
                
                if include_metadata and 'metadatas' in results:
                    result['metadata'] = results['metadatas'][0][i]
                
                formatted_results.append(result)
            
            logger.info(f"Query returned {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error querying vector store: {e}")
            return []

    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection"""
        try:
            count = self.collection.count()
            return {
                'name': self.collection_name,
                'document_count': count,
                'persist_directory': self.persist_directory,
                'created_at': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {}

    def delete_collection(self) -> bool:
        """Delete the entire collection"""
        try:
            self.client.delete_collection(name=self.collection_name)
            logger.info(f"Deleted collection: {self.collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            return False

    def reset_collection(self) -> bool:
        """Reset the collection by deleting and recreating it"""
        try:
            # Delete existing collection
            try:
                self.client.delete_collection(name=self.collection_name)
            except ValueError:
                pass  # Collection doesn't exist
            
            # Create new collection
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Core DNA website content for RAG"}
            )
            
            logger.info(f"Reset collection: {self.collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting collection: {e}")
            return False

def index_coredna_documents(chunks_file: str = None) -> bool:
    """Index Core DNA documents from processed chunks file"""
    if not chunks_file:
        chunks_file = os.path.join("data", "processed", "coredna_chunks.json")
    
    if not os.path.exists(chunks_file):
        logger.error(f"Chunks file not found: {chunks_file}")
        return False
    
    try:
        # Load chunks
        with open(chunks_file, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        
        logger.info(f"Loaded {len(chunks)} chunks from {chunks_file}")
        
        # Initialize vector store
        vector_store = ChromaVectorStore()
        
        # Reset collection to start fresh
        vector_store.reset_collection()
        
        # Add documents
        success = vector_store.add_documents(chunks)
        
        if success:
            info = vector_store.get_collection_info()
            logger.info(f"Indexing completed. Collection info: {info}")
        
        return success
        
    except Exception as e:
        logger.error(f"Error indexing documents: {e}")
        return False

if __name__ == "__main__":
    # Test the vector store
    success = index_coredna_documents()
    if success:
        # Test query
        vector_store = ChromaVectorStore()
        results = vector_store.query("ecommerce platform features", n_results=3)
        
        print("\nTest query results:")
        for i, result in enumerate(results):
            print(f"{i+1}. Distance: {result['distance']:.3f}")
            print(f"   Text: {result['text'][:100]}...")
            if 'metadata' in result:
                print(f"   URL: {result['metadata'].get('source_url', 'N/A')}")
            print()