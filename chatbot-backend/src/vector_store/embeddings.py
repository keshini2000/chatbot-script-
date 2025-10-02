from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings
import openai
import logging
from typing import List

try:
    from ..config.settings import settings
except ImportError:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from config.settings import settings

logger = logging.getLogger(__name__)

class EmbeddingManager:
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.embedding_model
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required for embeddings")
        
        # Set up OpenAI client
        openai.api_key = self.api_key
        
        # Initialize LlamaIndex embedding model
        self.embedding_model = OpenAIEmbedding(
            api_key=self.api_key,
            model=self.model
        )
        
        # Configure LlamaIndex global settings
        Settings.embed_model = self.embedding_model
        
        logger.info(f"Initialized embedding model: {self.model}")

    def get_text_embedding(self, text: str) -> List[float]:
        """Get embedding for a single text"""
        try:
            embedding = self.embedding_model.get_text_embedding(text)
            return embedding
        except Exception as e:
            logger.error(f"Error getting embedding for text: {e}")
            return []

    def get_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for a batch of texts"""
        try:
            embeddings = []
            for text in texts:
                embedding = self.get_text_embedding(text)
                embeddings.append(embedding)
            return embeddings
        except Exception as e:
            logger.error(f"Error getting batch embeddings: {e}")
            return []

    def test_embedding(self) -> bool:
        """Test if embeddings are working"""
        try:
            test_text = "This is a test sentence for embedding."
            embedding = self.get_text_embedding(test_text)
            
            if embedding and len(embedding) > 0:
                logger.info(f"Embedding test successful. Dimension: {len(embedding)}")
                return True
            else:
                logger.error("Embedding test failed: empty embedding returned")
                return False
                
        except Exception as e:
            logger.error(f"Embedding test failed: {e}")
            return False

if __name__ == "__main__":
    # Test embeddings
    try:
        embedding_manager = EmbeddingManager()
        success = embedding_manager.test_embedding()
        
        if success:
            print("✅ Embeddings are working correctly")
        else:
            print("❌ Embedding test failed")
            
    except Exception as e:
        print(f"❌ Failed to initialize embeddings: {e}")
        print("💡 Make sure to set your OpenAI API key in the .env file")