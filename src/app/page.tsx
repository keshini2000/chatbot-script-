export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <div className="text-center">
            <div className="flex items-center justify-center mb-4">
              <span className="text-3xl font-bold text-black">Core</span>
              <span className="text-3xl font-bold text-red-600 ml-1">dna</span>
              <span className="ml-3 text-lg text-gray-600">Chatbot Demos</span>
            </div>
            <p className="text-gray-600">
              Experience the AI-powered chatbot in action with different demo environments
            </p>
          </div>
        </div>
      </div>

      {/* Demo Options */}
      <div className="max-w-6xl mx-auto px-4 py-16">
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          
          {/* Core DNA Website Demo */}
          <div className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
            <div className="bg-gradient-to-r from-red-500 to-red-600 p-6 text-white">
              <div className="text-3xl mb-2">🌐</div>
              <h3 className="text-xl font-bold mb-2">Core DNA Website Demo</h3>
              <p className="text-red-100 text-sm">
                Experience the chatbot on a replica of the actual Core DNA website
              </p>
            </div>
            <div className="p-6">
              <div className="space-y-3 text-sm text-gray-600 mb-6">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>Authentic Core DNA branding and design</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>Embedded chatbot widget (bottom-right)</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>Real Core DNA contact integration</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>Production-ready experience</span>
                </div>
              </div>
              <a 
                href="/demo" 
                className="block w-full bg-red-600 text-white text-center py-3 px-4 rounded-lg font-medium hover:bg-red-700 transition-colors"
              >
                View Core DNA Demo
              </a>
            </div>
          </div>

          {/* Widget Embed Demo */}
          <div className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
            <div className="bg-gradient-to-r from-blue-500 to-blue-600 p-6 text-white">
              <div className="text-3xl mb-2">🔧</div>
              <h3 className="text-xl font-bold mb-2">Widget Embed Demo</h3>
              <p className="text-blue-100 text-sm">
                See how to integrate the chatbot widget into any website
              </p>
            </div>
            <div className="p-6">
              <div className="space-y-3 text-sm text-gray-600 mb-6">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>Copy-paste embed code</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>Integration instructions</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>Technical documentation</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>Live widget testing</span>
                </div>
              </div>
              <a 
                href="/embed-demo.html" 
                className="block w-full bg-blue-600 text-white text-center py-3 px-4 rounded-lg font-medium hover:bg-blue-700 transition-colors"
              >
                View Embed Demo
              </a>
            </div>
          </div>

          {/* Full-Screen Chat Demo */}
          <div className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
            <div className="bg-gradient-to-r from-purple-500 to-purple-600 p-6 text-white">
              <div className="text-3xl mb-2">💬</div>
              <h3 className="text-xl font-bold mb-2">Full-Screen Chat Demo</h3>
              <p className="text-purple-100 text-sm">
                Test the chatbot in a dedicated full-screen interface
              </p>
            </div>
            <div className="p-6">
              <div className="space-y-3 text-sm text-gray-600 mb-6">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>Full chatbot interface</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>All features visible</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>Source citations</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>Contact modal testing</span>
                </div>
              </div>
              <a 
                href="/chat" 
                className="block w-full bg-purple-600 text-white text-center py-3 px-4 rounded-lg font-medium hover:bg-purple-700 transition-colors"
              >
                View Chat Demo
              </a>
            </div>
          </div>
        </div>

        {/* Features Overview */}
        <div className="mt-16 bg-white rounded-xl shadow-lg p-8">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              🤖 Chatbot Features Overview
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Experience an intelligent chatbot powered by 793 indexed Core DNA documents 
              using advanced RAG (Retrieval Augmented Generation) technology.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="text-center p-4">
              <div className="text-3xl mb-3">🧠</div>
              <h3 className="font-semibold text-gray-900 mb-2">AI-Powered</h3>
              <p className="text-sm text-gray-600">
                Uses TypeScript + LlamaIndex for intelligent responses
              </p>
            </div>

            <div className="text-center p-4">
              <div className="text-3xl mb-3">📚</div>
              <h3 className="font-semibold text-gray-900 mb-2">Knowledge Base</h3>
              <p className="text-sm text-gray-600">
                793 documents scraped from Core DNA website
              </p>
            </div>

            <div className="text-center p-4">
              <div className="text-3xl mb-3">📞</div>
              <h3 className="font-semibold text-gray-900 mb-2">Sales Integration</h3>
              <p className="text-sm text-gray-600">
                Real contact info with auto-detection
              </p>
            </div>

            <div className="text-center p-4">
              <div className="text-3xl mb-3">⚡</div>
              <h3 className="font-semibold text-gray-900 mb-2">Fast & Reliable</h3>
              <p className="text-sm text-gray-600">
                3-5 second response times with source citations
              </p>
            </div>
          </div>
        </div>

        {/* API Status */}
        <div className="mt-8 bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">System Status</h3>
              <p className="text-sm text-gray-600">All demos are powered by the live TypeScript API</p>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm font-medium text-green-600">Online</span>
            </div>
          </div>
          <div className="mt-4 text-xs text-gray-500">
            <p>🚀 TypeScript Backend • 📊 793 Documents Indexed • 💬 Real-time Responses</p>
          </div>
        </div>
      </div>
    </div>
  );
}
