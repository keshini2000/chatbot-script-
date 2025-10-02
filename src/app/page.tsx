import ChatBot from '@/components/ChatBot';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-500 to-purple-600 p-4">
      <div className="container mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-white mb-4">
            Core DNA Chatbot
          </h1>
          <p className="text-xl text-white/80 mb-4">
            Intelligent Assistant Powered by RAG Technology
          </p>
          <div className="flex justify-center space-x-4 text-sm text-white/70">
            <span>✅ 200+ Pages Scraped</span>
            <span>✅ Vector Database Ready</span>
            <span>✅ FastAPI Backend</span>
            <span>✅ Real-time Chat</span>
          </div>
        </div>

        {/* Chat Interface */}
        <ChatBot />

        {/* Footer Info */}
        <div className="mt-8 text-center">
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 max-w-2xl mx-auto">
            <p className="text-white/80 text-sm">
              🚀 This chatbot uses advanced RAG (Retrieval Augmented Generation) technology 
              to answer questions about Core DNA's platform using real data scraped from their website.
            </p>
            <p className="text-white/60 text-xs mt-2">
              Backend API running on localhost:8000 • Frontend on localhost:3000
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
