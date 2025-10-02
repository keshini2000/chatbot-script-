from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[datetime] = None

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    sources: List[str] = []
    confidence_score: Optional[float] = None

class HealthResponse(BaseModel):
    status: str
    version: str
    database_status: str
    timestamp: datetime

class IndexStatus(BaseModel):
    total_documents: int
    last_updated: Optional[datetime] = None
    is_ready: bool