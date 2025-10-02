from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime
import logging
import uuid
import os
from typing import List, Dict, Any

try:
    from ...config.settings import settings
    from ..models.schemas import ChatRequest, ChatResponse
    from ...vector_store.chroma_store import ChromaVectorStore
    from ...rag.retriever import DocumentRetriever
except ImportError:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
    from config.settings import settings
    from api.models.schemas import ChatRequest, ChatResponse
    from vector_store.chroma_store import ChromaVectorStore
    from rag.retriever import DocumentRetriever

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize retriever (without RAG engine for now due to OpenAI quota)
retriever = DocumentRetriever()

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint - processes user questions"""
    try:
        # Generate conversation ID if not provided
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        logger.info(f"Processing chat request: {request.message[:50]}...")
        
        # For now, let's create a fallback response system since OpenAI API has quota issues
        # This shows how the system would work once API access is restored
        
        # Get relevant documents from vector store
        try:
            relevant_docs = retriever.retrieve_relevant_docs(
                query=request.message,
                n_results=5,
                min_relevance_score=0.1
            )
            
            # Build context from retrieved documents
            context = retriever.get_document_context(
                query=request.message,
                max_context_length=2000
            )
            
            # Create response based on retrieved documents
            if relevant_docs:
                # Extract source URLs
                sources = []
                for doc in relevant_docs[:3]:  # Top 3 sources
                    metadata = doc.get('metadata', {})
                    source_url = metadata.get('source_url', '')
                    title = metadata.get('title', 'Unknown')
                    
                    if source_url:
                        sources.append(source_url)
                
                # For now, create a contextual response without OpenAI
                response_text = create_fallback_response(request.message, relevant_docs)
                
                return ChatResponse(
                    response=response_text,
                    conversation_id=conversation_id,
                    sources=sources,
                    confidence_score=0.8 if relevant_docs else 0.3
                )
            else:
                # No relevant documents found
                return ChatResponse(
                    response="I don't have specific information about that topic in my Core DNA knowledge base. Could you try rephrasing your question or ask about Core DNA's ecommerce platform, features, or services?",
                    conversation_id=conversation_id,
                    sources=[],
                    confidence_score=0.1
                )
                
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            # Fallback to basic response
            return ChatResponse(
                response="I'm having trouble accessing my knowledge base right now. Please try asking about Core DNA's ecommerce platform, content management, or integration capabilities.",
                conversation_id=conversation_id,
                sources=[],
                confidence_score=0.1
            )
            
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

def create_fallback_response(question: str, docs: List[Dict[str, Any]]) -> str:
    """Create a helpful response based on retrieved documents without OpenAI"""
    
    if not docs:
        return "I don't have specific information about that topic. Could you ask about Core DNA's platform features, ecommerce capabilities, or integration options?"
    
    # Analyze the question to determine response type
    question_lower = question.lower()
    
    # Extract key information from top documents
    doc_info = []
    for doc in docs[:3]:
        text = doc.get('text', '')
        metadata = doc.get('metadata', {})
        title = metadata.get('title', '')
        url = metadata.get('source_url', '')
        
        if text:
            # Get first 200 characters as summary
            summary = text[:200] + "..." if len(text) > 200 else text
            doc_info.append({
                'title': title,
                'summary': summary,
                'url': url
            })
    
    # Create contextual response based on question type
    if any(word in question_lower for word in ['what is', 'what are', 'define', 'explain']):
        # Definitional question
        if doc_info:
            response = f"Based on Core DNA's documentation:\n\n{doc_info[0]['summary']}"
            if len(doc_info) > 1:
                response += f"\n\nAdditionally: {doc_info[1]['summary']}"
        else:
            response = "I found some relevant information, but I'd need more context to provide a complete answer."
            
    elif any(word in question_lower for word in ['how to', 'how do', 'how can']):
        # How-to question
        response = "Here's what I found about that process:\n\n"
        for info in doc_info:
            if 'how' in info['summary'].lower() or 'step' in info['summary'].lower():
                response += f"• {info['summary']}\n"
        
        if response == "Here's what I found about that process:\n\n":
            response = f"I found relevant information: {doc_info[0]['summary'] if doc_info else 'Please check the Core DNA documentation for detailed steps.'}"
            
    elif any(word in question_lower for word in ['features', 'capabilities', 'functionality']):
        # Feature question
        response = "Core DNA offers these capabilities:\n\n"
        for info in doc_info:
            response += f"• {info['title']}: {info['summary'][:100]}...\n"
            
    elif any(word in question_lower for word in ['price', 'cost', 'pricing', 'plan']):
        # Pricing question
        response = "For pricing information, I'd recommend contacting Core DNA directly. "
        if doc_info:
            response += f"Here's some related information: {doc_info[0]['summary']}"
            
    else:
        # General question
        if doc_info:
            response = f"Here's what I found: {doc_info[0]['summary']}"
            if len(doc_info) > 1:
                response += f"\n\nRelated information: {doc_info[1]['summary']}"
        else:
            response = "I found some information related to your question, but I'd need more details to provide a specific answer."
    
    # Add helpful ending
    response += "\n\nFor more detailed information, you can check the specific Core DNA documentation pages I referenced."
    
    return response

@router.get("/status")
async def chat_status():
    """Get chat system status"""
    try:
        # Check if vector store is working
        vector_store = ChromaVectorStore()
        collection_info = vector_store.get_collection_info()
        
        # Check if we can retrieve documents
        test_results = retriever.retrieve_relevant_docs("test", n_results=1)
        
        return {
            "status": "operational",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "vector_store": {
                    "status": "healthy",
                    "document_count": collection_info.get('document_count', 0)
                },
                "retriever": {
                    "status": "healthy" if test_results else "degraded",
                    "test_query_results": len(test_results) if test_results else 0
                },
                "rag_engine": {
                    "status": "disabled",
                    "reason": "OpenAI API quota exceeded - using fallback responses"
                }
            }
        }
    except Exception as e:
        logger.error(f"Chat status check failed: {e}")
        return {
            "status": "degraded",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@router.get("/search")
async def search_documents(q: str, limit: int = 5):
    """Search documents in the knowledge base"""
    try:
        results = retriever.retrieve_relevant_docs(
            query=q,
            n_results=limit,
            min_relevance_score=0.1
        )
        
        # Format results for API response
        formatted_results = []
        for result in results:
            metadata = result.get('metadata', {})
            formatted_results.append({
                'text': result.get('text', '')[:300] + "...",  # Truncate for API
                'similarity_score': result.get('similarity_score', 0.0),
                'source_url': metadata.get('source_url', ''),
                'title': metadata.get('title', ''),
                'source_type': 'blog' if '/blogs/' in metadata.get('source_url', '') else 'feature'
            })
        
        return {
            "query": q,
            "results_count": len(formatted_results),
            "results": formatted_results
        }
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")