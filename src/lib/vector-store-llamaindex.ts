import {
  VectorStoreIndex,
  Document,
  Settings,
  storageContextFromDefaults,
  SimpleVectorStore,
} from 'llamaindex';
import { OpenAI, OpenAIEmbedding } from '@llamaindex/openai';
import { readFileSync } from 'fs';
import { join } from 'path';

export interface DocumentChunk {
  text: string;
  metadata: {
    source_url: string;
    title?: string;
    chunk_id: number;
    total_chunks: number;
  };
}

export interface SearchResult {
  text: string;
  score: number;
  metadata?: any;
}

export class LlamaIndexVectorStore {
  private index: VectorStoreIndex | null = null;
  private llm: OpenAI;
  private embedModel: OpenAIEmbedding;

  constructor() {
    // Configure LlamaIndex settings
    this.llm = new OpenAI({
      model: 'gpt-3.5-turbo',
      apiKey: process.env.OPENAI_API_KEY!,
    });

    this.embedModel = new OpenAIEmbedding({
      model: 'text-embedding-ada-002',
      apiKey: process.env.OPENAI_API_KEY!,
    });

    // Set global settings
    Settings.llm = this.llm;
    Settings.embedModel = this.embedModel;
  }

  async initialize(): Promise<void> {
    try {
      // Load existing chunks
      const chunks = this.loadExistingChunks();
      
      if (chunks.length === 0) {
        throw new Error('No chunks found to index');
      }

      // Convert chunks to LlamaIndex Documents
      const documents = chunks.map((chunk, index) => {
        return new Document({
          text: chunk.text,
          metadata: {
            ...chunk.metadata,
            doc_id: `${this.hashString(chunk.metadata.source_url)}_${chunk.metadata.chunk_id}`
          }
        });
      });

      console.log(`Converting ${documents.length} documents to vector index...`);

      // Create vector store index
      this.index = await VectorStoreIndex.fromDocuments(documents);
      
      console.log(`Successfully created vector index with ${documents.length} documents`);
    } catch (error) {
      console.error('Error initializing vector store:', error);
      throw error;
    }
  }

  async query(queryText: string, topK: number = 5): Promise<SearchResult[]> {
    if (!this.index) {
      throw new Error('Vector store not initialized');
    }

    try {
      // Create query engine
      const queryEngine = this.index.asQueryEngine({
        similarityTopK: topK,
      });

      // Execute query
      const response = await queryEngine.query({
        query: queryText,
      });

      // Extract source nodes for results
      const results: SearchResult[] = [];
      
      if (response.sourceNodes) {
        for (const sourceNode of response.sourceNodes) {
          results.push({
            text: sourceNode.node.getText(),
            score: sourceNode.score || 0,
            metadata: sourceNode.node.metadata
          });
        }
      }

      console.log(`Query returned ${results.length} results`);
      return results;
    } catch (error) {
      console.error('Error querying vector store:', error);
      return [];
    }
  }

  async chat(queryText: string, conversationHistory: string = ''): Promise<string> {
    if (!this.index) {
      throw new Error('Vector store not initialized');
    }

    try {
      // Create chat engine with context
      const chatEngine = this.index.asChatEngine({
        chatMode: 'context',
        systemPrompt: `You are a helpful assistant for Core DNA, an ecommerce platform company. Use the provided context to answer questions about Core DNA's products, features, and services.

${conversationHistory ? `Recent conversation context:\n${conversationHistory}\n` : ''}

Guidelines:
- Answer based primarily on the provided context
- Be helpful and informative
- If the context doesn't contain relevant information, say so politely
- Keep responses concise but complete
- Maintain a professional tone
- Focus on Core DNA's ecommerce platform capabilities`
      });

      const response = await chatEngine.chat({
        message: queryText,
      });

      return response.response;
    } catch (error) {
      console.error('Error in chat:', error);
      throw error;
    }
  }

  getInfo(): any {
    return {
      framework: 'LlamaIndex.TS',
      model: 'gpt-3.5-turbo',
      embedding_model: 'text-embedding-ada-002',
      initialized: this.index !== null,
      created_at: new Date().toISOString()
    };
  }

  private loadExistingChunks(): DocumentChunk[] {
    try {
      const chunksPath = join(process.cwd(), 'chatbot-backend', 'data', 'processed', 'coredna_chunks.json');
      const chunksData = readFileSync(chunksPath, 'utf-8');
      const chunks = JSON.parse(chunksData);
      console.log(`Loaded ${chunks.length} chunks from ${chunksPath}`);
      return chunks;
    } catch (error) {
      console.error('Error loading chunks:', error);
      return [];
    }
  }

  private hashString(str: string): string {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return hash.toString();
  }
}