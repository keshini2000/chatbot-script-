from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API Keys
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # Database
    chroma_db_path: str = os.getenv("CHROMA_DB_PATH", "./data/vector_db")
    
    # API Configuration
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    
    # Scraping Configuration
    coredna_base_url: str = os.getenv("COREDNA_BASE_URL", "https://www.coredna.com")
    max_pages: int = int(os.getenv("MAX_PAGES", "200"))
    scraping_delay: float = float(os.getenv("SCRAPING_DELAY", "1"))
    
    # LlamaIndex Configuration
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "1000"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    
    class Config:
        env_file = ".env"

settings = Settings()