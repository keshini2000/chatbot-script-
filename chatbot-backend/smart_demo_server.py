#!/usr/bin/env python3
"""
Advanced demo server that uses the actual scraped data without requiring OpenAI API
This shows the full system architecture working with real Core DNA content
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict, Any
import uvicorn
import json
import os
import re
from collections import defaultdict

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

# Create FastAPI app
app = FastAPI(
    title="Core DNA Chatbot API (Demo Mode)",
    description="Core DNA assistant operating in demo mode without LLM inference using keyword/lexical matches",
    version="1.0.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variable to store scraped data
scraped_data = []
indexed_content = defaultdict(list)

def load_scraped_data():
    """Load the actual scraped Core DNA data"""
    global scraped_data, indexed_content
    
    # Try to load the processed data first, then raw data
    data_files = [
        "data/processed/coredna_processed_data.json",
        "data/raw/coredna_scraped_data.json"
    ]
    
    for file_path in data_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    scraped_data = json.load(f)
                print(f"✅ Loaded {len(scraped_data)} documents from {file_path}")
                
                # Create simple keyword index
                create_keyword_index()
                return True
            except Exception as e:
                print(f"❌ Error loading {file_path}: {e}")
                continue
    
    print("❌ No scraped data found. Using fallback responses.")
    return False

def create_keyword_index():
    """Create a simple keyword index from scraped content"""
    global indexed_content
    
    for doc in scraped_data:
        url = doc.get('url', '')
        title = doc.get('title', '')
        content = doc.get('content', '')
        
        # Combine title and content for indexing
        full_text = f"{title} {content}".lower()
        
        # Extract keywords
        words = re.findall(r'\b\w+\b', full_text)
        
        # Index by keywords
        for word in words:
            if len(word) > 3:  # Only index meaningful words
                indexed_content[word].append({
                    'url': url,
                    'title': title,
                    'content': content[:500],  # First 500 chars
                    'score': 1.0
                })

def search_content(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Simple content search using keyword matching"""
    if not scraped_data:
        return []
    
    query_words = re.findall(r'\b\w+\b', query.lower())
    if not query_words:
        return []
    
    # Score documents based on keyword matches
    doc_scores = defaultdict(float)
    doc_info = {}
    
    for word in query_words:
        if word in indexed_content:
            for doc in indexed_content[word]:
                doc_id = doc['url']
                doc_scores[doc_id] += 1.0
                doc_info[doc_id] = doc
    
    # Sort by score and return top results
    sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
    
    results = []
    for doc_id, score in sorted_docs[:max_results]:
        if doc_id in doc_info:
            result = doc_info[doc_id].copy()
            result['relevance_score'] = score / len(query_words)  # Normalize score
            results.append(result)
    
    return results

def clean_content(content: str) -> str:
    """Clean up scraped content to make it more readable"""
    import re
    
    if not content:
        return ""
    
    # Remove metadata sections completely
    content = re.sub(r'Page Title:.*?\n\n', '', content, flags=re.DOTALL)
    content = re.sub(r'Key Sections:.*?\n\n', '', content, flags=re.DOTALL)
    content = re.sub(r'Content:\s*', '', content, flags=re.MULTILINE)
    content = re.sub(r'On this page:.*?\n', '', content, flags=re.MULTILINE)
    
    # Remove bullet points and structural markers
    content = re.sub(r'^\s*[-•]\s*', '', content, flags=re.MULTILINE)
    content = re.sub(r'^\s*\d+\.\s*', '', content, flags=re.MULTILINE)
    
    # Remove "Core dna" section headers and repetitive elements
    content = re.sub(r'Core dna[^\n]*\n', '', content, flags=re.IGNORECASE)
    content = re.sub(r'Implementation Example.*$', '', content, flags=re.DOTALL)
    content = re.sub(r'Practical Use Case:.*?(?=\n[A-Z]|\n\n|$)', '', content, flags=re.DOTALL)
    
    # Clean up excessive whitespace
    content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
    content = re.sub(r'\s+', ' ', content)
    
    # Split into sentences and find the most informative ones
    sentences = re.split(r'[.!?]+', content)
    useful_sentences = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        # Keep sentences that are informative and substantial
        if (len(sentence) > 30 and 
            not sentence.startswith(('Page Title', 'Key Sections', 'On this page', 'Implementation Example', 'No FAQ')) and
            not re.match(r'^[A-Z\s]+$', sentence) and  # Skip all-caps headers
            not sentence.endswith('Core dna') and  # Skip repetitive endings
            any(word in sentence.lower() for word in ['provides', 'offers', 'enables', 'helps', 'allows', 'supports', 'platform', 'solution', 'business', 'customer', 'ecommerce', 'commerce', 'management', 'integration', 'feature'])):
            useful_sentences.append(sentence.strip())
    
    if useful_sentences:
        # Take the 2-3 most informative sentences
        result = '. '.join(useful_sentences[:3])
        if not result.endswith('.'):
            result += '.'
        return result
    
    # Fallback: try to extract description sections
    description_match = re.search(r'Description\s+(.*?)(?=\n[A-Z]|\n\n|$)', content, re.DOTALL | re.IGNORECASE)
    if description_match:
        desc = description_match.group(1).strip()
        return desc[:300] + ('...' if len(desc) > 300 else '')
    
    # Final fallback: return first paragraph
    paragraphs = [p.strip() for p in content.split('\n\n') if len(p.strip()) > 50]
    if paragraphs:
        return paragraphs[0][:300] + ('...' if len(paragraphs[0]) > 300 else '')
    
    return content[:200] + '...' if len(content) > 200 else content

def assemble_grounded_response(user_message: str, context_blocks: List[Dict[str, Any]], match_score: float) -> dict:
    """
    Assemble a grounded answer per the Core DNA assistant guidelines for demo mode.
    Returns STRICT JSON matching the declared OUTPUT FORMAT schema.
    
    Args:
        user_message: The user's question
        context_blocks: Array of {title, url, last_updated, excerpt}
        match_score: Match score from keyword search (0-1)
    
    Returns:
        Strict JSON with: text, citations, confidence, actions
    """
    
    # Handle basic greetings and conversational queries
    user_lower = user_message.lower().strip()
    if user_lower in ['hello', 'hi', 'hey', 'how are you', 'how are you?', 'good morning', 'good afternoon']:
        return {
            "text": "Hello! I'm the Core DNA assistant. I can help you learn about Core DNA's comprehensive digital commerce platform, including e-commerce features, content management, integrations, pricing, and more. What would you like to know about Core DNA?",
            "citations": [],
            "confidence": 1.0,
            "actions": [{"type": "none"}]
        }
    
    # Handle very general Core DNA questions
    if 'what is core dna' in user_lower or 'what is coredna' in user_lower:
        return {
            "text": "Core DNA is a comprehensive digital commerce platform that enables businesses to create exceptional customer experiences. The platform combines e-commerce capabilities, content management, customer engagement tools, and seamless integrations to help businesses grow their online presence and sales. Core DNA serves businesses of all sizes with flexible, scalable solutions for modern digital commerce.",
            "citations": [],
            "confidence": 1.0,
            "actions": [{"type": "none"}]
        }
    
    # Handle feature questions with better fallbacks
    if any(word in user_lower for word in ['feature', 'capability', 'function', 'what does', 'what can']):
        return {
            "text": "Core DNA offers a comprehensive suite of digital commerce features including: e-commerce platform with advanced shopping cart functionality, content management system, customer engagement tools, payment gateway integrations, inventory management, order processing, analytics and reporting, multi-channel selling capabilities, and seamless third-party integrations. The platform is designed to help businesses of all sizes create exceptional online customer experiences.",
            "citations": [],
            "confidence": 0.9,
            "actions": [{"type": "none"}]
        }
    
    # Handle pricing questions with better information
    if any(word in user_lower for word in ['price', 'cost', 'pricing', 'plan', 'subscription']):
        return {
            "text": "Core DNA offers flexible pricing plans designed to accommodate businesses of all sizes. The platform provides scalable solutions with various pricing tiers based on your specific needs, transaction volume, and required features. For detailed pricing information and to get a custom quote tailored to your business requirements, I recommend contacting Core DNA's sales team directly. They can provide accurate pricing based on your specific use case.",
            "citations": [],
            "confidence": 0.9,
            "actions": [{"type": "collect_lead", "fields": ["name", "email", "company", "use_case"]}]
        }
    
    # Handle ecommerce questions
    if any(word in user_lower for word in ['ecommerce', 'e-commerce', 'online store', 'shop', 'selling']):
        return {
            "text": "Core DNA provides a powerful e-commerce platform that includes advanced shopping cart functionality, secure payment processing, inventory management, order tracking, customer account management, and multi-channel selling capabilities. The platform supports various payment gateways, offers flexible product catalog management, and provides comprehensive analytics to help businesses optimize their online sales performance.",
            "citations": [],
            "confidence": 0.9,
            "actions": [{"type": "none"}]
        }
    
    # Handle integration questions
    if any(word in user_lower for word in ['integration', 'connect', 'api', 'third party']):
        return {
            "text": "Core DNA offers extensive integration capabilities with over 100+ third-party applications and services. The platform provides APIs for custom integrations and supports connections with popular CRM systems, marketing tools, payment gateways, shipping providers, analytics platforms, and accounting software. This allows businesses to create a seamless ecosystem that connects all their essential business tools.",
            "citations": [],
            "confidence": 0.9,
            "actions": [{"type": "none"}]
        }
    
    # Determine response behavior based on confidence thresholds
    if match_score < 0.55 and not context_blocks:
        return {
            "text": "I don't have specific information about that topic in my Core DNA knowledge base. Could you ask about Core DNA's e-commerce platform, content management features, pricing plans, or integrations?",
            "citations": [],
            "confidence": match_score,
            "actions": [{"type": "clarify"}]
        }
    
    if not context_blocks:
        return {
            "text": "Let me help you learn about Core DNA. You can ask me about e-commerce features, content management, pricing plans, integrations, or specific platform capabilities. What interests you most?",
            "citations": [],
            "confidence": 0.7,
            "actions": [{"type": "clarify"}]
        }
    
    # Check for lead capture triggers
    lead_triggers = ['demo', 'quote', 'pricing', 'contact', 'sales', 'budget', 'timeline', 'implementation']
    if any(trigger in user_lower for trigger in lead_triggers):
        if match_score >= 0.72:
            top_context = context_blocks[0]
            cleaned_content = clean_content(top_context['excerpt'])
            response_text = f"Regarding {user_message.lower()}: {cleaned_content[:200]}... Demo mode cannot access live tools. To discuss pricing and get a demo, please contact Core DNA directly."
            clean_quote = clean_content(top_context['excerpt'])
            citations = [{"title": top_context['title'].replace('Core dna', 'Core DNA'), "url": top_context['url'], "quote": clean_quote[:100] + "..."}]
            return {
                "text": response_text,
                "citations": citations,
                "confidence": match_score,
                "actions": [{"type": "collect_lead", "fields": ["name", "email", "company", "use_case"]}]
            }
    
    # Build response based on context
    top_context = context_blocks[0]
    citations = []
    
    # Clean and prepare content
    cleaned_content = clean_content(top_context['excerpt'])
    
    # Create citations for referenced sources  
    for block in context_blocks[:3]:  # Use top 3 blocks
        clean_quote = clean_content(block['excerpt'])
        citations.append({
            "title": block['title'].replace('Core dna', 'Core DNA'),
            "url": block['url'],
            "quote": clean_quote[:100] + "..." if len(clean_quote) > 100 else clean_quote
        })
    
    # Generate response based on query intent and confidence
    if match_score >= 0.72:
        # High confidence - full answer
        if any(word in user_lower for word in ['what is', 'what are', 'define', 'explain']):
            response_text = f"Based on Core DNA's documentation: {cleaned_content}"
            if len(context_blocks) > 1 and len(cleaned_content) < 200:
                additional_content = clean_content(context_blocks[1]['excerpt'])
                response_text += f" Additionally, {additional_content[:150]}..."
                
        elif any(word in user_lower for word in ['how', 'steps', 'process', 'setup', 'configure']):
            response_text = f"According to Core DNA's documentation: {cleaned_content}"
            
        elif any(word in user_lower for word in ['feature', 'capability', 'function', 'can', 'does']):
            response_text = f"Core DNA provides: {cleaned_content}"
            if len(context_blocks) > 1 and len(cleaned_content) < 200:
                additional_content = clean_content(context_blocks[1]['excerpt'])
                response_text += f" The platform also offers: {additional_content[:150]}..."
                
        elif any(word in user_lower for word in ['price', 'cost', 'pricing', 'plan']):
            response_text = f"Regarding Core DNA pricing: {cleaned_content}"
            if 'contact' not in response_text.lower():
                response_text += " For detailed pricing information and custom quotes, I recommend contacting Core DNA's sales team directly."
                
        else:
            # General query
            response_text = f"From Core DNA's documentation: {cleaned_content}"
        
        return {
            "text": response_text,
            "citations": citations,
            "confidence": match_score,
            "actions": [{"type": "none"}]
        }
    
    else:  # 0.55-0.71 - brief answer + clarifying question
        brief_response = f"Based on Core DNA's documentation: {cleaned_content[:200]}... Would you like more specific information about any particular aspect?"
        
        return {
            "text": brief_response,
            "citations": citations[:1],  # Just top citation for brief response
            "confidence": match_score,
            "actions": [{"type": "clarify"}]
        }

def generate_intelligent_response(query: str, search_results: List[Dict[str, Any]]) -> dict:
    """Generate an intelligent response based on search results using demo mode guidelines"""
    
    if not search_results:
        return {
            "text": "I don't have specific information about that topic in my Core DNA knowledge base. Could you be more specific about what aspect of Core DNA's platform you're interested in?",
            "citations": [],
            "confidence": 0.1,
            "actions": [{"type": "clarify"}]
        }
    
    # Calculate match score based on relevance scores
    avg_relevance = sum(result.get('relevance_score', 0.5) for result in search_results) / len(search_results)
    match_score = min(1.0, avg_relevance)
    
    # Extract the most relevant content
    top_result = search_results[0]
    content = top_result.get('content', '')
    title = top_result.get('title', 'Core DNA Documentation')
    url = top_result.get('url', '')
    
    # Build citations
    citations = []
    for result in search_results[:3]:  # Top 3 results
        if result.get('url') and result.get('title'):
            citations.append({
                "title": result['title'],
                "url": result['url'],
                "quote": result.get('content', '')[:100] + "..." if len(result.get('content', '')) > 100 else result.get('content', '')
            })
    
    # Confidence-based response logic
    if match_score < 0.55:
        return {
            "text": "I couldn't find sufficient information about that topic in my Core DNA knowledge base. Could you rephrase your question or ask about a specific Core DNA feature?",
            "citations": [],
            "confidence": match_score,
            "actions": [{"type": "clarify"}]
        }
    
    query_lower = query.lower()
    
    # Generate response based on query intent
    if any(word in query_lower for word in ['what is', 'what are', 'define', 'explain']):
        if 'core dna' in query_lower or 'coredna' in query_lower:
            response = f"Based on Core DNA's documentation: {content[:200]}..."
            if len(search_results) > 1:
                response += f" Additional details: {search_results[1]['content'][:100]}..."
        else:
            response = f"According to [{title} → {url}]: {content[:250]}..."
            
    elif any(word in query_lower for word in ['how', 'steps', 'process', 'setup']):
        response = f"From Core DNA's documentation on {title.lower()}: {content[:300]}..."
        
    elif any(word in query_lower for word in ['feature', 'capability', 'function', 'can']):
        response = f"Core DNA offers these capabilities: **{title}**: {content[:200]}..."
        if len(search_results) > 1:
            response += f" Also: **{search_results[1]['title']}**: {search_results[1]['content'][:150]}..."
        
    elif any(word in query_lower for word in ['price', 'cost', 'pricing', 'plan']):
        if 'demo mode cannot access' not in content.lower():
            response = f"For specific pricing, contact Core DNA directly. From documentation: {content[:200]}..."
        else:
            response = "Demo mode cannot access live pricing tools. For current pricing information, please contact Core DNA directly."
        
    elif any(word in query_lower for word in ['integration', 'connect', 'api', 'sync']):
        response = f"Core DNA integration capabilities [{title} → {url}]: {content[:300]}..."
        
    else:
        response = f"From Core DNA's documentation on '{title}': {content[:280]}..."
        if len(search_results) > 1:
            response += f" Related: {search_results[1]['content'][:100]}..."
    
    # Add clarifying question for medium confidence
    action_type = "none"
    if 0.55 <= match_score < 0.72:
        response += "\n\nWould you like more specific information about any particular aspect?"
        action_type = "clarify"
    
    return {
        "text": response,
        "citations": citations,
        "confidence": match_score,
        "actions": [{"type": action_type}]
    }

@app.on_event("startup")
async def startup_event():
    """Load data on startup"""
    print("🚀 Starting Core DNA Smart Demo Server")
    load_scraped_data()

@app.get("/")
async def root():
    return {
        "message": "Core DNA Chatbot API (Smart Demo)",
        "version": "1.0.0",
        "docs": "/docs",
        "note": "Using real scraped Core DNA content with intelligent search",
        "documents_loaded": len(scraped_data)
    }

@app.get("/health")
async def health_check():
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now()
    )

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Smart chat endpoint using real scraped data"""
    try:
        # Search for relevant content
        search_results = search_content(request.message, max_results=3)
        
        # Convert search results to context blocks format
        context_blocks = []
        for result in search_results:
            context_blocks.append({
                'title': result.get('title', 'Core DNA Documentation'),
                'url': result.get('url', ''),
                'last_updated': '',  # Demo mode doesn't track last_updated
                'excerpt': result.get('content', '')
            })
        
        # Calculate match score from search results
        avg_relevance = sum(result.get('relevance_score', 0.5) for result in search_results) / len(search_results) if search_results else 0.0
        match_score = min(1.0, avg_relevance)
        
        # Generate response using strict assembler
        demo_response = assemble_grounded_response(request.message, context_blocks, match_score)
        
        # Extract sources from citations
        sources = [citation['url'] for citation in demo_response.get('citations', [])]
        if not sources:
            sources = [result['url'] for result in search_results if result.get('url')]
        
        conversation_id = request.conversation_id or f"smart_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return ChatResponse(
            response=demo_response['text'],
            conversation_id=conversation_id,
            sources=sources[:3],  # Limit to top 3 sources
            confidence_score=demo_response['confidence'],
            structured_response=demo_response
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@app.get("/search")
async def search_endpoint(q: str, limit: int = 5):
    """Search the scraped content"""
    results = search_content(q, max_results=limit)
    
    return {
        "query": q,
        "results_count": len(results),
        "results": [{
            "title": r.get('title', ''),
            "url": r.get('url', ''),
            "content_preview": r.get('content', '')[:200] + "...",
            "relevance_score": r.get('relevance_score', 0.0)
        } for r in results]
    }

@app.get("/stats")
async def content_stats():
    """Get statistics about the loaded content"""
    if not scraped_data:
        return {"error": "No data loaded"}
    
    # Analyze content types
    content_types = defaultdict(int)
    total_content_length = 0
    
    for doc in scraped_data:
        url = doc.get('url', '')
        content = doc.get('content', '')
        total_content_length += len(content)
        
        if '/blogs/' in url:
            content_types['blog'] += 1
        elif '/all-features/' in url:
            content_types['features'] += 1
        elif '/customers/' in url:
            content_types['case_studies'] += 1
        elif '/guides/' in url:
            content_types['guides'] += 1
        else:
            content_types['other'] += 1
    
    return {
        "total_documents": len(scraped_data),
        "content_types": dict(content_types),
        "total_content_length": total_content_length,
        "average_content_length": total_content_length // len(scraped_data) if scraped_data else 0,
        "indexed_keywords": len(indexed_content)
    }

if __name__ == "__main__":
    print("🚀 Starting Core DNA Smart Demo Server")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("❤️  Health check: http://localhost:8000/health")
    print("💬 Chat endpoint: http://localhost:8000/chat")
    print("📊 Content stats: http://localhost:8000/stats")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)