(function() {
  'use strict';

  // Configuration
  const CHATBOT_API_URL = 'http://localhost:3000/api/chat'; // Change to your domain when deployed
  const WIDGET_ID = 'coredna-chatbot-widget';

  // Prevent multiple widgets
  if (document.getElementById(WIDGET_ID)) return;

  class CoreDNAChatbot {
    constructor() {
      this.isOpen = false;
      this.isMinimized = false;
      this.messages = [
        {
          id: '1',
          text: "Hi! I'm the Core DNA assistant. How can I help you build better and stress less?",
          isUser: false,
          timestamp: new Date(),
        }
      ];
      this.inputText = '';
      this.isLoading = false;
      this.conversationId = null;
      this.showContactModal = false;
      this.hasNewMessage = false;

      this.init();
    }

    init() {
      this.injectStyles();
      this.createWidget();
      this.attachEventListeners();
    }

    injectStyles() {
      const styles = `
        #${WIDGET_ID} {
          position: fixed;
          bottom: 20px;
          right: 20px;
          z-index: 10000;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }

        .coredna-chat-button {
          background: linear-gradient(135deg, #0066cc, #004499);
          color: white;
          border: none;
          border-radius: 50px;
          padding: 16px 20px;
          cursor: pointer;
          box-shadow: 0 4px 12px rgba(0, 102, 204, 0.3);
          transition: all 0.3s ease;
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 14px;
          font-weight: 500;
        }

        .coredna-chat-button:hover {
          background: linear-gradient(135deg, #0052a3, #003d7a);
          transform: translateY(-2px);
          box-shadow: 0 6px 16px rgba(0, 102, 204, 0.4);
        }

        .coredna-chat-window {
          width: 380px;
          height: 500px;
          background: white;
          border-radius: 12px;
          box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
          border: 1px solid #e5e5e5;
          display: flex;
          flex-direction: column;
          overflow: hidden;
        }

        .coredna-chat-header {
          background: linear-gradient(135deg, #0066cc, #004499);
          color: white;
          padding: 16px;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .coredna-chat-title {
          font-weight: 600;
          font-size: 16px;
        }

        .coredna-chat-subtitle {
          font-size: 12px;
          opacity: 0.9;
          margin-top: 2px;
        }

        .coredna-chat-controls {
          display: flex;
          gap: 8px;
        }

        .coredna-chat-btn {
          background: rgba(255, 255, 255, 0.2);
          border: none;
          color: white;
          padding: 4px 8px;
          border-radius: 4px;
          cursor: pointer;
          font-size: 12px;
          transition: background 0.2s;
        }

        .coredna-chat-btn:hover {
          background: rgba(255, 255, 255, 0.3);
        }

        .coredna-chat-messages {
          flex: 1;
          overflow-y: auto;
          padding: 16px;
          background: #f8f9fa;
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .coredna-message {
          display: flex;
        }

        .coredna-message.user {
          justify-content: flex-end;
        }

        .coredna-message-bubble {
          max-width: 280px;
          padding: 10px 14px;
          border-radius: 18px;
          font-size: 14px;
          line-height: 1.4;
        }

        .coredna-message.user .coredna-message-bubble {
          background: #0066cc;
          color: white;
        }

        .coredna-message.bot .coredna-message-bubble {
          background: white;
          color: #333;
          border: 1px solid #e5e5e5;
        }

        .coredna-message-time {
          font-size: 11px;
          opacity: 0.7;
          margin-top: 4px;
        }

        .coredna-message-sources {
          margin-top: 8px;
          padding-top: 8px;
          border-top: 1px solid #eee;
          font-size: 11px;
        }

        .coredna-source-link {
          color: #0066cc;
          text-decoration: none;
          display: block;
          margin-top: 2px;
        }

        .coredna-source-link:hover {
          text-decoration: underline;
        }

        .coredna-typing {
          display: flex;
          gap: 4px;
          padding: 10px 14px;
        }

        .coredna-typing-dot {
          width: 6px;
          height: 6px;
          background: #999;
          border-radius: 50%;
          animation: coredna-bounce 1.4s infinite ease-in-out;
        }

        .coredna-typing-dot:nth-child(1) { animation-delay: -0.32s; }
        .coredna-typing-dot:nth-child(2) { animation-delay: -0.16s; }

        @keyframes coredna-bounce {
          0%, 80%, 100% { transform: scale(0); }
          40% { transform: scale(1); }
        }

        .coredna-chat-input {
          border-top: 1px solid #e5e5e5;
          padding: 12px;
          background: white;
          display: flex;
          gap: 8px;
        }

        .coredna-input-field {
          flex: 1;
          border: 1px solid #ddd;
          border-radius: 20px;
          padding: 8px 12px;
          font-size: 14px;
          outline: none;
          resize: none;
          font-family: inherit;
        }

        .coredna-input-field:focus {
          border-color: #0066cc;
        }

        .coredna-send-btn {
          background: #0066cc;
          color: white;
          border: none;
          border-radius: 20px;
          padding: 8px 16px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
          transition: background 0.2s;
        }

        .coredna-send-btn:hover:not(:disabled) {
          background: #0052a3;
        }

        .coredna-send-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .coredna-suggestions {
          padding: 12px;
          background: white;
          border-top: 1px solid #e5e5e5;
          display: flex;
          flex-wrap: wrap;
          gap: 6px;
        }

        .coredna-suggestion {
          background: #f1f3f4;
          border: none;
          border-radius: 12px;
          padding: 6px 12px;
          font-size: 12px;
          cursor: pointer;
          color: #333;
          transition: background 0.2s;
        }

        .coredna-suggestion:hover {
          background: #e8f0fe;
        }

        .coredna-notification-dot {
          position: absolute;
          top: -2px;
          right: -2px;
          width: 12px;
          height: 12px;
          background: #ff4444;
          border-radius: 50%;
          animation: coredna-pulse 2s infinite;
        }

        @keyframes coredna-pulse {
          0% { transform: scale(1); opacity: 1; }
          50% { transform: scale(1.1); opacity: 0.7; }
          100% { transform: scale(1); opacity: 1; }
        }

        .coredna-contact-modal {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 10001;
        }

        .coredna-contact-content {
          background: white;
          border-radius: 12px;
          padding: 24px;
          max-width: 400px;
          width: 90%;
          max-height: 80vh;
          overflow-y: auto;
        }

        .coredna-contact-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
        }

        .coredna-contact-title {
          font-size: 18px;
          font-weight: 600;
          color: #333;
        }

        .coredna-close-btn {
          background: none;
          border: none;
          font-size: 20px;
          cursor: pointer;
          color: #999;
        }

        .coredna-contact-section {
          margin-bottom: 20px;
        }

        .coredna-contact-section h4 {
          font-size: 14px;
          font-weight: 600;
          color: #333;
          margin-bottom: 8px;
        }

        .coredna-contact-link {
          color: #0066cc;
          text-decoration: none;
          font-size: 14px;
        }

        .coredna-contact-link:hover {
          text-decoration: underline;
        }

        .coredna-office-list {
          font-size: 12px;
          color: #666;
          line-height: 1.5;
        }

        @media (max-width: 480px) {
          .coredna-chat-window {
            width: calc(100vw - 40px);
            height: calc(100vh - 100px);
          }
          
          #${WIDGET_ID} {
            bottom: 10px;
            right: 10px;
          }
        }
      `;

      const styleSheet = document.createElement('style');
      styleSheet.textContent = styles;
      document.head.appendChild(styleSheet);
    }

    createWidget() {
      const widget = document.createElement('div');
      widget.id = WIDGET_ID;
      widget.innerHTML = this.getButtonHTML();
      document.body.appendChild(widget);
      this.widgetElement = widget;
    }

    getButtonHTML() {
      return `
        <button class="coredna-chat-button" onclick="window.coreDNAChatbot.openChat()">
          <span style="font-size: 18px;">💬</span>
          <span>Chat with us</span>
          ${this.hasNewMessage ? '<div class="coredna-notification-dot"></div>' : ''}
        </button>
      `;
    }

    getChatHTML() {
      const suggestedQuestions = [
        "What is Core DNA?",
        "What ecommerce features do you offer?",
        "How can I contact sales?"
      ];

      return `
        <div class="coredna-chat-window">
          <div class="coredna-chat-header">
            <div>
              <div class="coredna-chat-title">Core DNA Assistant</div>
              <div class="coredna-chat-subtitle">Ask about our platform</div>
            </div>
            <div class="coredna-chat-controls">
              <button class="coredna-chat-btn" onclick="window.coreDNAChatbot.showContact()">📞 Contact</button>
              <button class="coredna-chat-btn" onclick="window.coreDNAChatbot.minimizeChat()">−</button>
              <button class="coredna-chat-btn" onclick="window.coreDNAChatbot.closeChat()">✕</button>
            </div>
          </div>

          ${!this.isMinimized ? `
            <div class="coredna-chat-messages" id="coredna-messages">
              ${this.renderMessages()}
            </div>

            ${this.messages.length === 1 ? `
              <div class="coredna-suggestions">
                ${suggestedQuestions.map(q => `
                  <button class="coredna-suggestion" onclick="window.coreDNAChatbot.sendMessage('${q}')">${q}</button>
                `).join('')}
              </div>
            ` : ''}

            <div class="coredna-chat-input">
              <textarea 
                class="coredna-input-field" 
                placeholder="Ask about Core DNA..." 
                rows="1"
                id="coredna-input"
                onkeydown="window.coreDNAChatbot.handleKeyDown(event)"
                ${this.isLoading ? 'disabled' : ''}
              ></textarea>
              <button 
                class="coredna-send-btn" 
                onclick="window.coreDNAChatbot.sendCurrentMessage()"
                ${this.isLoading ? 'disabled' : ''}
              >
                Send
              </button>
            </div>
          ` : ''}
        </div>

        ${this.showContactModal ? this.getContactModalHTML() : ''}
      `;
    }

    getContactModalHTML() {
      return `
        <div class="coredna-contact-modal" onclick="window.coreDNAChatbot.closeContact(event)">
          <div class="coredna-contact-content" onclick="event.stopPropagation()">
            <div class="coredna-contact-header">
              <div class="coredna-contact-title">Contact Core DNA Sales</div>
              <button class="coredna-close-btn" onclick="window.coreDNAChatbot.closeContact()">✕</button>
            </div>
            
            <div class="coredna-contact-section">
              <h4>📧 Email Sales Team</h4>
              <a href="mailto:sales@coredna.com" class="coredna-contact-link">sales@coredna.com</a>
            </div>
            
            <div class="coredna-contact-section">
              <h4>📞 Call Sales Team</h4>
              <div>
                <span style="font-size: 12px; color: #666;">🇺🇸 US/Canada: </span>
                <a href="tel:+16172746660" class="coredna-contact-link">+1 617 274 6660</a>
              </div>
              <div style="margin-top: 4px;">
                <span style="font-size: 12px; color: #666;">🇦🇺 Australia/NZ: </span>
                <a href="tel:+61385639100" class="coredna-contact-link">+61 3 8563 9100</a>
              </div>
            </div>
            
            <div class="coredna-contact-section">
              <h4>🏢 Office Locations</h4>
              <div class="coredna-office-list">
                📍 Melbourne: 348 High Street, Prahran, VIC 3181<br>
                📍 Boston: 55 Court St, Level 2, Boston, MA 02108<br>
                📍 Berlin: Belziger Str. 71, Berlin 10823
              </div>
            </div>
          </div>
        </div>
      `;
    }

    renderMessages() {
      return this.messages.map(message => `
        <div class="coredna-message ${message.isUser ? 'user' : 'bot'}">
          <div class="coredna-message-bubble">
            ${message.text.replace(/\n/g, '<br>')}
            ${message.sources && message.sources.length > 0 ? `
              <div class="coredna-message-sources">
                <strong style="font-size: 11px;">Sources:</strong>
                ${message.sources.slice(0, 2).map(source => `
                  <a href="${source}" target="_blank" class="coredna-source-link">
                    ${source.replace('https://www.coredna.com', '').substring(0, 30)}...
                  </a>
                `).join('')}
              </div>
            ` : ''}
            <div class="coredna-message-time">
              ${message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </div>
          </div>
        </div>
      `).join('') + (this.isLoading ? `
        <div class="coredna-message bot">
          <div class="coredna-message-bubble">
            <div class="coredna-typing">
              <div class="coredna-typing-dot"></div>
              <div class="coredna-typing-dot"></div>
              <div class="coredna-typing-dot"></div>
            </div>
          </div>
        </div>
      ` : '');
    }

    openChat() {
      this.isOpen = true;
      this.isMinimized = false;
      this.hasNewMessage = false;
      this.render();
      setTimeout(() => {
        const input = document.getElementById('coredna-input');
        if (input) input.focus();
        this.scrollToBottom();
      }, 100);
    }

    closeChat() {
      this.isOpen = false;
      this.render();
    }

    minimizeChat() {
      this.isMinimized = true;
      this.render();
    }

    showContact() {
      this.showContactModal = true;
      this.render();
    }

    closeContact(event) {
      if (!event || event.target.classList.contains('coredna-contact-modal')) {
        this.showContactModal = false;
        this.render();
      }
    }

    async sendMessage(text) {
      if (!text || this.isLoading) return;

      const userMessage = {
        id: Date.now().toString(),
        text: text,
        isUser: true,
        timestamp: new Date(),
      };

      this.messages.push(userMessage);
      this.isLoading = true;
      this.render();

      try {
        const response = await fetch(CHATBOT_API_URL, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: text,
            conversation_id: this.conversationId,
          }),
        });

        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();

        if (data.conversation_id && !this.conversationId) {
          this.conversationId = data.conversation_id;
        }

        if (data.show_contact) {
          setTimeout(() => {
            this.showContactModal = true;
            this.render();
          }, 1000);
        }

        const botMessage = {
          id: (Date.now() + 1).toString(),
          text: data.response,
          isUser: false,
          timestamp: new Date(),
          sources: data.sources,
          confidence: data.confidence_score,
        };

        this.messages.push(botMessage);

        if (!this.isOpen) {
          this.hasNewMessage = true;
        }

      } catch (error) {
        console.error('Chat error:', error);
        
        const errorMessage = {
          id: (Date.now() + 1).toString(),
          text: "Sorry, I'm having trouble connecting. Please try again.",
          isUser: false,
          timestamp: new Date(),
        };

        this.messages.push(errorMessage);
      } finally {
        this.isLoading = false;
        this.render();
      }
    }

    sendCurrentMessage() {
      const input = document.getElementById('coredna-input');
      if (input && input.value.trim()) {
        this.sendMessage(input.value.trim());
        input.value = '';
      }
    }

    handleKeyDown(event) {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        this.sendCurrentMessage();
      }
    }

    scrollToBottom() {
      const messagesContainer = document.getElementById('coredna-messages');
      if (messagesContainer) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
      }
    }

    render() {
      if (this.isOpen) {
        this.widgetElement.innerHTML = this.getChatHTML();
        setTimeout(() => this.scrollToBottom(), 100);
      } else {
        this.widgetElement.innerHTML = this.getButtonHTML();
      }
    }

    attachEventListeners() {
      // Make methods globally accessible
      window.coreDNAChatbot = this;
    }
  }

  // Initialize the chatbot
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      new CoreDNAChatbot();
    });
  } else {
    new CoreDNAChatbot();
  }

})();