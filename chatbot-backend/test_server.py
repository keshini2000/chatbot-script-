#!/usr/bin/env python3
"""
Simple test server to demonstrate the API without requiring full setup
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import uvicorn

# Simple data models
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    sources: List[str] = []
    confidence_score: Optional[float] = None

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime

# Create FastAPI app
app = FastAPI(
    title="Core DNA Chatbot API (Demo)",
    description="Demo version of the RAG-powered chatbot API",
    version="1.0.0"
)

# Add CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock Core DNA data for demonstration
MOCK_RESPONSES = {
    "features": "Core DNA offers comprehensive ecommerce platform features including product management, order processing, payment integration, inventory management, and multi-store capabilities.",
    "ecommerce": "Core DNA's ecommerce platform provides B2B and B2C solutions with advanced features like reverse auctions, subscription management, and flexible pricing models.",
    "content": "Core DNA includes a powerful content management system with headless CMS capabilities, WYSIWYG editor, and content-as-a-service functionality.",
    "integration": "Core DNA supports extensive integrations including Salesforce, PayPal, various payment gateways, shipping carriers, and ERP systems.",
    "platform": "Core DNA is a comprehensive digital experience platform that combines ecommerce, content management, and automation capabilities in a single solution."
}

@app.get("/")
async def root():
    """Welcome endpoint"""
    return {
        "message": "Core DNA Chatbot API (Demo Mode)",
        "version": "1.0.0",
        "docs": "/docs",
        "note": "This is a demo version without full vector database integration"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now()
    )

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Demo chat endpoint"""
    try:
        message_lower = request.message.lower()
        
        # Simple keyword matching for demo
        response_text = "I can help you with questions about Core DNA's platform. "
        sources = ["https://www.coredna.com"]
        confidence = 0.5
        
        # Find relevant response
        for keyword, response in MOCK_RESPONSES.items():
            if keyword in message_lower:
                response_text = response
                sources = [f"https://www.coredna.com/{keyword}"]
                confidence = 0.8
                break
        
        if "what is" in message_lower or "tell me about" in message_lower:
            if "core dna" in message_lower or "coredna" in message_lower:
                response_text = "Core DNA is a comprehensive digital experience platform that provides ecommerce, content management, and automation solutions for businesses looking to create powerful online experiences."
                confidence = 0.9
        
        conversation_id = request.conversation_id or f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return ChatResponse(
            response=response_text,
            conversation_id=conversation_id,
            sources=sources,
            confidence_score=confidence
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@app.get("/search")
async def search_demo(q: str):
    """Demo search endpoint"""
    return {
        "query": q,
        "message": "Search functionality will be available once the full vector database is set up",
        "demo_keywords": list(MOCK_RESPONSES.keys())
    }

if __name__ == "__main__":
    print("🚀 Starting Core DNA Chatbot API Demo Server")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("❤️  Health check: http://localhost:8000/health")
    print("💬 Chat endpoint: http://localhost:8000/chat")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)