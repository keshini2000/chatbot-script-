import { LlamaIndexVectorStore, SearchResult } from './vector-store-llamaindex';

export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

export interface ChatResponse {
  response: string;
  conversation_id: string;
  sources: string[];
  confidence_score?: number;
  show_contact?: boolean;
}

export class RAGService {
  private vectorStore: LlamaIndexVectorStore;
  private conversations: Map<string, Array<{ role: string; content: string }>> = new Map();

  constructor() {
    this.vectorStore = new LlamaIndexVectorStore();
  }

  async initialize(): Promise<void> {
    await this.vectorStore.initialize();
  }

  async chat(request: ChatRequest): Promise<ChatResponse> {
    try {
      // Generate conversation ID if not provided
      const conversationId = request.conversation_id || this.generateConversationId();

      // Get or create conversation history
      if (!this.conversations.has(conversationId)) {
        this.conversations.set(conversationId, []);
      }
      const conversation = this.conversations.get(conversationId)!;

      // Build conversation context for LlamaIndex
      const conversationContext = conversation
        .slice(-6) // Last 3 exchanges (6 messages)
        .map(msg => `${msg.role}: ${msg.content}`)
        .join('\n');

      // Check if user is asking about contact/sales
      const contactKeywords = ['contact', 'sales', 'phone', 'email', 'call', 'reach', 'speak', 'talk', 'demo', 'meeting'];
      const isContactQuery = contactKeywords.some(keyword => 
        request.message.toLowerCase().includes(keyword)
      );

      // Use LlamaIndex chat function or provide direct contact response
      let response;
      
      if (isContactQuery) {
        // Provide direct helpful response for contact queries
        response = "I'd be happy to help you connect with Core DNA's sales team! Our sales specialists can provide personalized demos, discuss pricing, and help you understand how Core DNA's platform can meet your specific business needs.\n\n📞 **Ready to connect with our sales team?** Click the 'Contact Sales' button above to get direct access to our sales team's phone numbers, email, and office locations!";
      } else {
        // Use LlamaIndex for regular queries
        response = await this.vectorStore.chat(request.message, conversationContext);
      }

      // Get search results for sources and confidence
      const searchResults = await this.vectorStore.query(request.message, 3);
      
      // Calculate confidence score from search results
      const avgScore = searchResults.length > 0 
        ? searchResults.reduce((sum, result) => sum + (result.score || 0), 0) / searchResults.length
        : 0;
      const confidenceScore = Math.max(0, Math.min(1, avgScore));

      // Prepare sources
      const sources = searchResults
        .filter(result => result.metadata?.source_url)
        .map(result => result.metadata.source_url)
        .filter((url, index, array) => array.indexOf(url) === index) // Remove duplicates
        .slice(0, 3); // Limit to 3 sources

      // Update conversation history
      conversation.push(
        { role: 'user', content: request.message },
        { role: 'assistant', content: response }
      );

      // Keep conversation history manageable (last 10 exchanges)
      if (conversation.length > 20) {
        conversation.splice(0, conversation.length - 20);
      }

      return {
        response,
        conversation_id: conversationId,
        sources,
        confidence_score: confidenceScore,
        show_contact: isContactQuery
      };

    } catch (error) {
      console.error('Error in RAG service:', error);
      throw new Error('Failed to process chat request');
    }
  }

  async getVectorStoreInfo(): Promise<any> {
    return this.vectorStore.getInfo();
  }

  private generateConversationId(): string {
    return `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

// Singleton instance
let ragServiceInstance: RAGService | null = null;

export async function getRagService(): Promise<RAGService> {
  if (!ragServiceInstance) {
    ragServiceInstance = new RAGService();
    await ragServiceInstance.initialize();
  }
  return ragServiceInstance;
}