from llama_index.core import VectorStoreIndex, ServiceContext
from llama_index.core.llms import ChatMessage
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.storage.storage_context import StorageContext
from llama_index.core import Settings
import chromadb
import openai
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

try:
    from ..config.settings import settings
    from ..vector_store.chroma_store import ChromaVectorStore as CustomChromaStore
except ImportError:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from config.settings import settings
    from vector_store.chroma_store import ChromaVectorStore as CustomChromaStore

logger = logging.getLogger(__name__)

class CoreDNARAGEngine:
    def __init__(self, api_key: str = None, collection_name: str = "coredna_docs"):
        self.api_key = api_key or settings.openai_api_key
        self.collection_name = collection_name
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        # Set up OpenAI
        openai.api_key = self.api_key
        
        # Initialize LLM
        self.llm = OpenAI(
            api_key=self.api_key,
            model=settings.llm_model,
            temperature=0.7
        )
        
        # Initialize embedding model
        self.embed_model = OpenAIEmbedding(
            api_key=self.api_key,
            model=settings.embedding_model
        )
        
        # Configure global settings
        Settings.llm = self.llm
        Settings.embed_model = self.embed_model
        Settings.chunk_size = settings.chunk_size
        Settings.chunk_overlap = settings.chunk_overlap
        
        # Initialize components
        self.index = None
        self.query_engine = None
        
        logger.info("Initialized Core DNA RAG Engine")

    def setup_vector_store(self) -> bool:
        """Setup connection to ChromaDB vector store"""
        try:
            # Connect to ChromaDB
            chroma_client = chromadb.PersistentClient(path=settings.chroma_db_path)
            chroma_collection = chroma_client.get_collection(name=self.collection_name)
            
            # Create LlamaIndex ChromaVectorStore
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            
            # Create storage context
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            
            # Create index from existing vector store
            self.index = VectorStoreIndex.from_vector_store(
                vector_store=vector_store,
                storage_context=storage_context
            )
            
            logger.info("Successfully connected to vector store")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup vector store: {e}")
            return False

    def create_query_engine(self, similarity_top_k: int = 5) -> bool:
        """Create the RAG query engine"""
        try:
            if not self.index:
                logger.error("Vector store index not initialized")
                return False
            
            # Create query engine with customized prompt
            self.query_engine = self.index.as_query_engine(
                similarity_top_k=similarity_top_k,
                response_mode="compact"
            )
            
            logger.info(f"Created query engine with top_k={similarity_top_k}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create query engine: {e}")
            return False

    def query(self, question: str, include_sources: bool = True) -> Dict[str, Any]:
        """Query the RAG system"""
        try:
            if not self.query_engine:
                logger.error("Query engine not initialized")
                return {
                    "answer": "Sorry, the system is not ready to answer questions.",
                    "sources": [],
                    "error": "Query engine not initialized"
                }
            
            # Add system context to make responses more helpful
            contextualized_question = f"""
            You are a helpful assistant for Core DNA, an e-commerce and digital experience platform company. 
            Answer the following question based on the provided context about Core DNA's products, services, and capabilities.
            Be specific, accurate, and helpful. If you don't know something, say so.
            
            Question: {question}
            """
            
            # Execute query
            response = self.query_engine.query(contextualized_question)
            
            # Extract sources if available
            sources = []
            if include_sources and hasattr(response, 'source_nodes'):
                for node in response.source_nodes:
                    if hasattr(node, 'metadata') and node.metadata:
                        source_url = node.metadata.get('source_url', 'Unknown')
                        title = node.metadata.get('title', 'Unknown')
                        sources.append({
                            'url': source_url,
                            'title': title,
                            'score': getattr(node, 'score', 0.0)
                        })
            
            result = {
                "answer": str(response),
                "sources": sources,
                "timestamp": datetime.now().isoformat(),
                "question": question
            }
            
            logger.info(f"Successfully answered question: {question[:50]}...")
            return result
            
        except Exception as e:
            logger.error(f"Error querying RAG system: {e}")
            return {
                "answer": "Sorry, I encountered an error while processing your question.",
                "sources": [],
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "question": question
            }

    def test_query(self) -> bool:
        """Test the RAG system with sample queries"""
        test_questions = [
            "What is Core DNA?",
            "What ecommerce features does Core DNA provide?",
            "How does Core DNA's content management work?"
        ]
        
        logger.info("Testing RAG system with sample queries...")
        
        for question in test_questions:
            try:
                result = self.query(question)
                
                if "error" in result:
                    logger.error(f"Test failed for question: {question}")
                    logger.error(f"Error: {result['error']}")
                    return False
                
                logger.info(f"✅ Test passed for: {question}")
                logger.info(f"Answer length: {len(result['answer'])} chars")
                logger.info(f"Sources found: {len(result['sources'])}")
                
            except Exception as e:
                logger.error(f"Test failed with exception: {e}")
                return False
        
        logger.info("✅ All RAG system tests passed")
        return True

    def initialize(self) -> bool:
        """Initialize the complete RAG system"""
        logger.info("Initializing Core DNA RAG system...")
        
        # Setup vector store
        if not self.setup_vector_store():
            logger.error("Failed to setup vector store")
            return False
        
        # Create query engine
        if not self.create_query_engine():
            logger.error("Failed to create query engine")
            return False
        
        # Test the system
        if not self.test_query():
            logger.error("RAG system tests failed")
            return False
        
        logger.info("✅ Core DNA RAG system initialized successfully")
        return True

def create_rag_engine() -> Optional[CoreDNARAGEngine]:
    """Factory function to create and initialize RAG engine"""
    try:
        rag_engine = CoreDNARAGEngine()
        
        if rag_engine.initialize():
            return rag_engine
        else:
            logger.error("Failed to initialize RAG engine")
            return None
            
    except Exception as e:
        logger.error(f"Error creating RAG engine: {e}")
        return None

if __name__ == "__main__":
    # Test the RAG engine
    rag_engine = create_rag_engine()
    
    if rag_engine:
        print("✅ RAG engine created successfully!")
        
        # Interactive testing
        while True:
            question = input("\nAsk a question about Core DNA (or 'quit' to exit): ")
            if question.lower() in ['quit', 'exit', 'q']:
                break
                
            result = rag_engine.query(question)
            print(f"\n🤖 Answer: {result['answer']}")
            
            if result['sources']:
                print(f"\n📚 Sources ({len(result['sources'])}):")
                for i, source in enumerate(result['sources'][:3]):
                    print(f"  {i+1}. {source['title']} - {source['url']}")
    else:
        print("❌ Failed to create RAG engine")
        print("💡 Make sure to:")
        print("   1. Set your OpenAI API key in .env")
        print("   2. Run the scraping pipeline first")
        print("   3. Setup the vector database")