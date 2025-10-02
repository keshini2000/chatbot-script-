#!/usr/bin/env python3
"""
Production RAG server using OpenAI embeddings and GPT for intelligent responses
This is the full production version with vector database semantic search
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict, Any
import uvicorn
import openai
import os
import sys
import logging

# Add src to path for imports
sys.path.append('src')

try:
    from vector_store.chroma_store import ChromaVectorStore
    from config.settings import settings
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the chatbot-backend directory")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Data models
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class Citation(BaseModel):
    title: str
    url: str
    quote: str

class Action(BaseModel):
    type: str
    tool_name: Optional[str] = None
    fields: Optional[List[str]] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    sources: List[str] = []
    confidence_score: Optional[float] = None
    # New structured format fields
    structured_response: Optional[Dict[str, Any]] = None

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime
    vector_db_status: Dict[str, Any] = {}

# Create FastAPI app
app = FastAPI(
    title="Core DNA Chatbot API (Production RAG)",
    description="Production RAG chatbot using OpenAI embeddings and GPT",
    version="2.0.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
vector_store = None
openai_client = None

def initialize_openai():
    """Initialize OpenAI client"""
    global openai_client
    
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        logger.error("OPENAI_API_KEY not found in environment variables")
        return False
    
    try:
        openai_client = openai.OpenAI(api_key=openai_api_key)
        # Test the connection
        openai_client.embeddings.create(
            model="text-embedding-ada-002",
            input="test"
        )
        logger.info("✅ OpenAI client initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize OpenAI client: {e}")
        return False

def initialize_vector_store():
    """Initialize vector database"""
    global vector_store
    
    try:
        vector_store = ChromaVectorStore()
        info = vector_store.get_collection_info()
        logger.info(f"✅ Vector store initialized: {info['document_count']} documents")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize vector store: {e}")
        return False

def assemble_grounded_response(user_message: str, context_blocks: List[Dict[str, Any]], retrieval_confidence: float) -> dict:
    """
    Assemble a grounded answer per the Core DNA assistant guidelines.
    Returns STRICT JSON matching the declared OUTPUT FORMAT schema.
    
    Args:
        user_message: The user's question
        context_blocks: Array of {title, url, last_updated, excerpt}
        retrieval_confidence: Confidence score from retrieval (0-1)
    
    Returns:
        Strict JSON with: text, citations, confidence, actions
    """
    import re
    
    # Determine response behavior based on confidence thresholds
    if retrieval_confidence < 0.55:
        # Low confidence - ask clarifying question
        return {
            "text": "I don't have sufficient information about that topic in my Core DNA knowledge base. Could you be more specific about what aspect of Core DNA's platform you're interested in?",
            "citations": [],
            "confidence": retrieval_confidence,
            "actions": [{"type": "clarify"}]
        }
    
    if not context_blocks:
        return {
            "text": "I don't have specific information about that topic. Could you ask about Core DNA's e-commerce platform, content management features, or integrations?",
            "citations": [],
            "confidence": retrieval_confidence,
            "actions": [{"type": "clarify"}]
        }
    
    # Check for lead capture triggers
    lead_triggers = ['demo', 'quote', 'pricing', 'contact', 'sales', 'budget', 'timeline', 'implementation']
    user_lower = user_message.lower()
    if any(trigger in user_lower for trigger in lead_triggers):
        if retrieval_confidence >= 0.72:
            # Provide answer then collect lead
            top_context = context_blocks[0]
            response_text = f"Based on our documentation: {top_context['excerpt'][:200]}... To discuss your specific needs, I'd like to connect you with our team."
            citations = [{"title": top_context['title'], "url": top_context['url'], "quote": top_context['excerpt'][:100] + "..."}]
            return {
                "text": response_text,
                "citations": citations,
                "confidence": retrieval_confidence,
                "actions": [{"type": "collect_lead", "fields": ["name", "email", "company", "use_case"]}]
            }
    
    # Build response based on context
    top_context = context_blocks[0]
    citations = []
    
    # Create citations for referenced sources
    for i, block in enumerate(context_blocks[:3]):  # Use top 3 blocks
        citations.append({
            "title": block['title'],
            "url": block['url'],
            "quote": block['excerpt'][:150] + "..." if len(block['excerpt']) > 150 else block['excerpt']
        })
    
    # Generate response based on query intent and confidence
    if retrieval_confidence >= 0.72:
        # High confidence - full answer
        if any(word in user_lower for word in ['what is', 'what are', 'define', 'explain']):
            response_text = f"Based on Core DNA's documentation: {top_context['excerpt']}"
            if len(context_blocks) > 1:
                response_text += f" Additionally, {context_blocks[1]['excerpt'][:150]}..."
        elif any(word in user_lower for word in ['how', 'steps', 'process']):
            response_text = f"According to our documentation: {top_context['excerpt']}"
        elif any(word in user_lower for word in ['feature', 'capability', 'can']):
            response_text = f"Core DNA offers: {top_context['excerpt']}"
            if len(context_blocks) > 1:
                response_text += f" We also provide: {context_blocks[1]['excerpt'][:100]}..."
        else:
            response_text = f"From our documentation on {top_context['title']}: {top_context['excerpt']}"
        
        return {
            "text": response_text,
            "citations": citations,
            "confidence": retrieval_confidence,
            "actions": [{"type": "none"}]
        }
    
    else:  # 0.55-0.71 - brief answer + clarifying question
        brief_response = f"Based on our documentation: {top_context['excerpt'][:150]}... Would you like more specific information about any particular aspect?"
        
        return {
            "text": brief_response,
            "citations": citations[:1],  # Just top citation for brief response
            "confidence": retrieval_confidence,
            "actions": [{"type": "clarify"}]
        }

def generate_rag_response(query: str, context_chunks: List[Dict[str, Any]]) -> dict:
    """Generate intelligent response using OpenAI GPT with RAG context following Core DNA assistant guidelines"""
    
    if not openai_client:
        return {
            "text": "OpenAI client not available. Please check configuration.",
            "citations": [],
            "confidence": 0.1,
            "actions": [{"type": "handoff"}]
        }
    
    if not context_chunks:
        return {
            "text": "I don't have specific information about that topic in my Core DNA knowledge base. Could you be more specific about what aspect of Core DNA's platform you're interested in?",
            "citations": [],
            "confidence": 0.1,
            "actions": [{"type": "clarify"}]
        }
    
    # Calculate confidence based on context relevance
    avg_distance = sum(chunk['distance'] for chunk in context_chunks) / len(context_chunks)
    retrieval_confidence = max(0.1, 1.0 - (avg_distance / 2.0))
    
    # Build context from retrieved chunks
    context_blocks = []
    for chunk in context_chunks[:3]:
        context_blocks.append({
            "title": chunk['metadata'].get('title', 'Core DNA Documentation'),
            "url": chunk['metadata']['source_url'],
            "content": chunk['text']
        })
    
    context_text = "\n\n".join([
        f"Title: {block['title']}\nURL: {block['url']}\nContent: {block['content']}"
        for block in context_blocks
    ])
    
    # Core DNA assistant system prompt
    system_prompt = """You are Core DNA's assistant. Answer ONLY using the provided Context. 
If evidence is weak or missing, ask a concise clarifying question or offer a human handoff.
Never invent facts, policies, pricing, SLAs, or order/stock data.

STYLE
- Clear, compact, practical. ≤120 words unless the user explicitly asks for detail.
- Always include source attributions for any factual claim: [Title → URL].
- Quote exact lines for pricing/SLAs/security.

CITATIONS
- Cite only documents you actually used.
- Prefer the most recent, most specific source (product/docs/policy pages over blogs).
- If multiple snippets from the same page are used, cite once.

CONFIDENCE & ACTIONS
- You will receive a numeric confidence score from the retrieval step (0–1) as `retrieval_confidence`.
- Behavior:
  - ≥ 0.72 → Answer normally + citations.
  - 0.55–0.71 → Answer briefly + ask exactly ONE clarifying question + citations if applicable.
  - < 0.55 → Do NOT answer; ask ONE clarifying question or propose human handoff.
- Never mask uncertainty; say what you do and don't know based on Context.

ECOMMERCE ADD-ON (when user intent is shopping)
- Recommend up to 3 items + one accessory (optional).
- For each item: 1 line explaining "why this fits."
- If stock/ETA/order lookup is required, call the appropriate tool; otherwise say you can't access it.

LEAD / HANDOFF
- If the user requests a demo/quote or mentions budget/timeline/integrations, collect:
  name, work email, company, use case.
- Offer a human handoff path and confirm consent.

PRIVACY & SAFETY
- Do not expose raw emails, phone numbers, IDs from Context; redact in outputs unless explicitly part of a public policy page.
- Never output API keys, internal tokens, or credentials.
- If a request is out of scope (e.g., legal advice, personal data), decline and propose next steps.

OUTPUT FORMAT (STRICT)
Return a single JSON object matching this schema:
{
  "text": "final answer or clarifying question",
  "citations": [{"title":"...", "url":"...", "quote":"..."}],
  "confidence": <number 0..1>,
  "actions": [{"type":"none" | "clarify" | "handoff" | "collect_lead" | "use_tool", "tool_name":"optional", "fields":["optional"]}]
}

CONTEXT
{context_blocks}

USER
{user_message}

AIM
Provide the most accurate, sourced, minimal answer possible based solely on Context."""
    
    user_prompt = f"""retrieval_confidence: {retrieval_confidence}

Context:
{context_text}

User question: {query}"""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=800,
            temperature=0.3
        )
        
        answer = response.choices[0].message.content.strip()
        
        # Try to parse the JSON response
        try:
            import json
            parsed_response = json.loads(answer)
            # Ensure confidence matches retrieval confidence if not provided
            if 'confidence' not in parsed_response:
                parsed_response['confidence'] = retrieval_confidence
            return parsed_response
        except json.JSONDecodeError:
            # Fallback if GPT doesn't return proper JSON
            return {
                "text": answer,
                "citations": [{"title": block['title'], "url": block['url'], "quote": ""} for block in context_blocks],
                "confidence": retrieval_confidence,
                "actions": [{"type": "none"}]
            }
        
    except Exception as e:
        logger.error(f"Error generating OpenAI response: {e}")
        return {
            "text": "I encountered an error while processing your question. Please try again.",
            "citations": [],
            "confidence": 0.1,
            "actions": [{"type": "handoff"}]
        }

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("🚀 Starting Core DNA Production RAG Server")
    
    # Initialize OpenAI
    if not initialize_openai():
        logger.warning("⚠️  OpenAI initialization failed - running in limited mode")
    
    # Initialize vector store
    if not initialize_vector_store():
        logger.error("❌ Vector store initialization failed")
        raise RuntimeError("Cannot start server without vector database")

@app.get("/")
async def root():
    return {
        "message": "Core DNA Chatbot API (Production RAG)",
        "version": "2.0.0",
        "docs": "/docs",
        "features": [
            "OpenAI GPT-3.5 responses",
            "Vector database semantic search",
            "793 indexed documents",
            "Real-time embeddings"
        ],
        "documents_indexed": vector_store.get_collection_info()['document_count'] if vector_store else 0
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    vector_db_status = {}
    if vector_store:
        try:
            vector_db_status = vector_store.get_collection_info()
        except Exception as e:
            vector_db_status = {"error": str(e)}
    
    return HealthResponse(
        status="healthy" if vector_store and openai_client else "degraded",
        version="2.0.0",
        timestamp=datetime.now(),
        vector_db_status=vector_db_status
    )

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Production RAG chat endpoint"""
    try:
        if not vector_store:
            raise HTTPException(status_code=503, detail="Vector database not available")
        
        # Search for relevant content using semantic search
        search_results = vector_store.query(request.message, n_results=5)
        
        # Convert search results to context blocks format
        context_blocks = []
        for result in search_results[:3]:  # Use top 3 results
            context_blocks.append({
                'title': result['metadata'].get('title', 'Core DNA Documentation'),
                'url': result['metadata']['source_url'],
                'last_updated': result['metadata'].get('last_updated', ''),
                'excerpt': result['text']
            })
        
        # Calculate retrieval confidence
        avg_distance = sum(result['distance'] for result in search_results) / len(search_results) if search_results else 1.0
        retrieval_confidence = max(0.1, 1.0 - (avg_distance / 2.0))
        
        # Generate response using strict assembler
        rag_response = assemble_grounded_response(request.message, context_blocks, retrieval_confidence)
        
        # Extract sources from citations
        sources = [citation['url'] for citation in rag_response.get('citations', [])]
        if not sources:
            sources = [result['metadata']['source_url'] for result in search_results 
                      if result.get('metadata', {}).get('source_url')]
        
        conversation_id = request.conversation_id or f"rag_prod_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return ChatResponse(
            response=rag_response['text'],
            conversation_id=conversation_id,
            sources=sources[:3],  # Limit to top 3 sources
            confidence_score=rag_response['confidence'],
            structured_response=rag_response
        )
        
    except Exception as e:
        logger.error(f"Chat processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@app.get("/search")
async def search_endpoint(q: str, limit: int = 5):
    """Semantic search endpoint"""
    if not vector_store:
        raise HTTPException(status_code=503, detail="Vector database not available")
    
    try:
        results = vector_store.query(q, n_results=limit)
        
        return {
            "query": q,
            "results_count": len(results),
            "results": [{
                "text": r['text'],
                "source_url": r['metadata']['source_url'],
                "relevance_score": 1.0 - r['distance'],  # Convert distance to relevance
                "distance": r['distance']
            } for r in results]
        }
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/stats")
async def stats_endpoint():
    """Get comprehensive statistics"""
    if not vector_store:
        return {"error": "Vector database not available"}
    
    try:
        vector_info = vector_store.get_collection_info()
        
        return {
            "vector_database": vector_info,
            "openai_status": "connected" if openai_client else "disconnected",
            "server_version": "2.0.0",
            "features": [
                "Semantic search with OpenAI embeddings",
                "GPT-3.5 response generation",
                "Real-time RAG processing",
                "Source attribution"
            ]
        }
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    print("🚀 Starting Core DNA Production RAG Server")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("❤️  Health check: http://localhost:8000/health")
    print("💬 Chat endpoint: http://localhost:8000/chat")
    print("🔍 Search endpoint: http://localhost:8000/search")
    print("📊 Stats: http://localhost:8000/stats")
    print("🤖 Using OpenAI GPT-3.5 + Vector Database RAG")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)