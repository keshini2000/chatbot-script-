'use client';

import { useState, useRef, useEffect } from 'react';

// Types for our chat system
interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
  sources?: string[];
  confidence?: number;
}

interface ChatResponse {
  response: string;
  conversation_id: string;
  sources: string[];
  confidence_score?: number;
  show_contact?: boolean;
}

export default function FloatingChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: "Hi! I'm the Core DNA assistant. I can help you learn about Core DNA's ecommerce platform, features, and capabilities. What would you like to know?",
      isUser: false,
      timestamp: new Date(),
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [showContactModal, setShowContactModal] = useState(false);
  const [hasNewMessage, setHasNewMessage] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages are added
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Send message to our API
  const sendMessage = async (text: string) => {
    if (!text.trim()) return;

    // Add user message immediately
    const userMessage: Message = {
      id: Date.now().toString(),
      text: text.trim(),
      isUser: true,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      // Call our TypeScript chatbot API
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: text.trim(),
          conversation_id: conversationId,
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data: ChatResponse = await response.json();

      // Update conversation ID
      if (data.conversation_id && !conversationId) {
        setConversationId(data.conversation_id);
      }

      // Auto-show contact modal if backend suggests it
      if (data.show_contact) {
        setTimeout(() => setShowContactModal(true), 1000);
      }

      // Add bot response
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: data.response,
        isUser: false,
        timestamp: new Date(),
        sources: data.sources,
        confidence: data.confidence_score,
      };

      setMessages(prev => [...prev, botMessage]);

      // Show notification if chat is closed
      if (!isOpen) {
        setHasNewMessage(true);
      }

    } catch (error) {
      console.error('Chat error:', error);
      
      // Add error message
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: "Sorry, I'm having trouble connecting to my knowledge base. Please try again or refresh the page.",
        isUser: false,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(inputText);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(inputText);
    }
  };

  // Open chat and clear notification
  const openChat = () => {
    setIsOpen(true);
    setIsMinimized(false);
    setHasNewMessage(false);
  };

  // Suggested questions
  const suggestedQuestions = [
    "What is Core DNA?",
    "What ecommerce features does Core DNA offer?",
    "How can I contact the sales team?",
  ];

  const askSuggestedQuestion = (question: string) => {
    sendMessage(question);
  };

  // Contact modal component
  const ContactModal = () => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Contact Core DNA Sales</h3>
          <button
            onClick={() => setShowContactModal(false)}
            className="text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        </div>
        
        <div className="space-y-4">
          <div>
            <h4 className="font-medium text-gray-900 mb-2">📧 Email Sales Team</h4>
            <a
              href="mailto:sales@coredna.com"
              className="text-blue-600 hover:underline"
            >
              sales@coredna.com
            </a>
          </div>
          
          <div>
            <h4 className="font-medium text-gray-900 mb-2">📞 Call Sales Team</h4>
            <div className="space-y-1">
              <div>
                <span className="text-sm text-gray-600">🇺🇸 US/Canada: </span>
                <a href="tel:+16172746660" className="text-blue-600 hover:underline">
                  +1 617 274 6660
                </a>
              </div>
              <div>
                <span className="text-sm text-gray-600">🇦🇺 Australia/NZ: </span>
                <a href="tel:+61385639100" className="text-blue-600 hover:underline">
                  +61 3 8563 9100
                </a>
              </div>
            </div>
          </div>
          
          <div>
            <h4 className="font-medium text-gray-900 mb-2">🏢 Office Locations</h4>
            <div className="text-sm text-gray-600 space-y-1">
              <div>📍 Melbourne: 348 High Street, Prahran, VIC 3181</div>
              <div>📍 Boston: 55 Court St, Level 2, Boston, MA 02108</div>
              <div>📍 Berlin: Belziger Str. 71, Berlin 10823</div>
            </div>
          </div>
          
          <div className="pt-2">
            <button
              onClick={() => setShowContactModal(false)}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  // Chat button (when closed)
  if (!isOpen) {
    return (
      <>
        <div className="fixed bottom-6 right-6 z-40">
          <button
            onClick={openChat}
            className="bg-blue-600 hover:bg-blue-700 text-white rounded-full p-4 shadow-lg transition-all duration-300 flex items-center gap-3 group"
          >
            <div className="relative">
              💬
              {hasNewMessage && (
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
              )}
            </div>
            <span className="hidden group-hover:block whitespace-nowrap">
              Chat with Core DNA Assistant
            </span>
          </button>
        </div>
        {showContactModal && <ContactModal />}
      </>
    );
  }

  // Chat window (when open)
  return (
    <>
      <div className="fixed bottom-6 right-6 w-96 h-[500px] bg-white rounded-lg shadow-2xl border z-40 flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 rounded-t-lg">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="font-semibold">Core DNA Assistant</h3>
              <p className="text-blue-100 text-xs">Ask me about our platform</p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setShowContactModal(true)}
                className="bg-white/20 hover:bg-white/30 text-white px-2 py-1 rounded text-xs"
              >
                📞 Contact
              </button>
              <button
                onClick={() => setIsMinimized(true)}
                className="text-white hover:bg-white/20 w-6 h-6 rounded flex items-center justify-center text-sm"
              >
                −
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="text-white hover:bg-white/20 w-6 h-6 rounded flex items-center justify-center text-sm"
              >
                ✕
              </button>
            </div>
          </div>
        </div>

        {/* Messages Area */}
        {!isMinimized && (
          <>
            <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs px-3 py-2 rounded-lg text-sm ${
                      message.isUser
                        ? 'bg-blue-600 text-white'
                        : 'bg-white text-gray-800 shadow-sm'
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{message.text}</p>
                    
                    {/* Show sources for bot messages */}
                    {!message.isUser && message.sources && message.sources.length > 0 && (
                      <div className="mt-2 pt-2 border-t border-gray-200">
                        <p className="text-xs text-gray-600 mb-1">Sources:</p>
                        {message.sources.slice(0, 2).map((source, index) => (
                          <a
                            key={index}
                            href={source}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-blue-600 hover:underline block truncate"
                          >
                            {source.replace('https://www.coredna.com', '').substring(0, 30)}...
                          </a>
                        ))}
                      </div>
                    )}

                    <p className="text-xs opacity-70 mt-1">
                      {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                </div>
              ))}

              {/* Loading indicator */}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-white rounded-lg px-3 py-2 shadow-sm">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Suggested Questions (show only initially) */}
            {messages.length === 1 && (
              <div className="px-4 py-2 bg-white border-t">
                <div className="flex flex-wrap gap-1">
                  {suggestedQuestions.map((question, index) => (
                    <button
                      key={index}
                      onClick={() => askSuggestedQuestion(question)}
                      className="text-xs bg-gray-100 hover:bg-blue-50 text-gray-700 rounded-full px-2 py-1 transition-colors"
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Input Area */}
            <div className="border-t p-3 bg-white rounded-b-lg">
              <form onSubmit={handleSubmit} className="flex gap-2">
                <textarea
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Ask about Core DNA..."
                  className="flex-1 border border-gray-300 rounded-lg px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  rows={1}
                  disabled={isLoading}
                />
                <button
                  type="submit"
                  disabled={isLoading || !inputText.trim()}
                  className="bg-blue-600 text-white px-3 py-1 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm"
                >
                  Send
                </button>
              </form>
            </div>
          </>
        )}
      </div>

      {/* Contact Modal */}
      {showContactModal && <ContactModal />}
    </>
  );
}