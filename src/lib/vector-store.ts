import { ChromaClient, OpenAIEmbeddingFunction } from 'chromadb';
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
  distance: number;
  metadata?: any;
}

export class ChromaVectorStore {
  private client: ChromaClient;
  private collection: any;
  private collectionName: string;
  private embedFunction: OpenAIEmbeddingFunction;

  constructor(collectionName: string = 'coredna_docs') {
    this.collectionName = collectionName;
    
    // Initialize ChromaDB client pointing to existing database
    this.client = new ChromaClient({
      path: join(process.cwd(), 'chatbot-backend', 'data', 'vector_db')
    });

    // Initialize OpenAI embedding function (same as Python backend)
    this.embedFunction = new OpenAIEmbeddingFunction({
      openai_api_key: process.env.OPENAI_API_KEY!,
      openai_model: 'text-embedding-ada-002'
    });
  }

  async initialize(): Promise<void> {
    try {
      // Try to get existing collection
      this.collection = await this.client.getCollection({
        name: this.collectionName,
        embeddingFunction: this.embedFunction
      });
      console.log(`Loaded existing collection: ${this.collectionName}`);
    } catch (error) {
      // Collection doesn't exist, create it
      this.collection = await this.client.createCollection({
        name: this.collectionName,
        embeddingFunction: this.embedFunction,
        metadata: { description: 'Core DNA website content for RAG' }
      });
      console.log(`Created new collection: ${this.collectionName}`);
    }
  }

  async addDocuments(chunks: DocumentChunk[]): Promise<boolean> {
    try {
      const documents: string[] = [];
      const metadatas: any[] = [];
      const ids: string[] = [];

      chunks.forEach((chunk, index) => {
        const url = chunk.metadata.source_url;
        const chunkId = chunk.metadata.chunk_id || 0;
        const docId = `${this.hashString(url)}_${chunkId}`;

        documents.push(chunk.text);
        metadatas.push(chunk.metadata);
        ids.push(docId);
      });

      // Add documents in batches
      const batchSize = 100;
      for (let i = 0; i < documents.length; i += batchSize) {
        const batchDocs = documents.slice(i, i + batchSize);
        const batchMetadata = metadatas.slice(i, i + batchSize);
        const batchIds = ids.slice(i, i + batchSize);

        await this.collection.add({
          documents: batchDocs,
          metadatas: batchMetadata,
          ids: batchIds
        });

        console.log(`Added batch ${Math.floor(i / batchSize) + 1}: ${i + batchDocs.length}/${documents.length} documents`);
      }

      console.log(`Successfully added ${documents.length} documents to vector store`);
      return true;
    } catch (error) {
      console.error('Error adding documents to vector store:', error);
      return false;
    }
  }

  async query(queryText: string, nResults: number = 5): Promise<SearchResult[]> {
    try {
      const results = await this.collection.query({
        queryTexts: [queryText],
        nResults,
        include: ['documents', 'distances', 'metadatas']
      });

      const formattedResults: SearchResult[] = [];
      for (let i = 0; i < results.documents[0].length; i++) {
        formattedResults.push({
          text: results.documents[0][i],
          distance: results.distances[0][i],
          metadata: results.metadatas?.[0]?.[i]
        });
      }

      console.log(`Query returned ${formattedResults.length} results`);
      return formattedResults;
    } catch (error) {
      console.error('Error querying vector store:', error);
      return [];
    }
  }

  async getCollectionInfo(): Promise<any> {
    try {
      const count = await this.collection.count();
      return {
        name: this.collectionName,
        document_count: count,
        created_at: new Date().toISOString()
      };
    } catch (error) {
      console.error('Error getting collection info:', error);
      return {};
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

// Utility function to load existing chunks
export function loadExistingChunks(): DocumentChunk[] {
  try {
    const chunksPath = join(process.cwd(), 'chatbot-backend', 'data', 'processed', 'coredna_chunks.json');
    const chunksData = readFileSync(chunksPath, 'utf-8');
    return JSON.parse(chunksData);
  } catch (error) {
    console.error('Error loading chunks:', error);
    return [];
  }
}