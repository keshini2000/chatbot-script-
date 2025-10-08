import { NextRequest, NextResponse } from 'next/server';
import { getRagService } from '@/lib/rag-service';

export async function GET(request: NextRequest) {
  try {
    const ragService = await getRagService();
    const vectorStoreInfo = await ragService.getVectorStoreInfo();
    
    return NextResponse.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      version: '2.0.0-typescript',
      vector_store: vectorStoreInfo,
      framework: 'Next.js + LlamaIndex.TS'
    });
    
  } catch (error) {
    console.error('Health check error:', error);
    return NextResponse.json(
      { 
        status: 'unhealthy', 
        error: 'Vector store initialization failed',
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    );
  }
}