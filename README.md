# 🤖 Core DNA Chatbot - Complete Integration Solution

[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com/)
[![LlamaIndex](https://img.shields.io/badge/LlamaIndex-000000?style=for-the-badge&logo=llamaindex&logoColor=white)](https://www.llamaindex.ai/)

> An intelligent chatbot widget for Core DNA's website, powered by 793 indexed documents and advanced RAG technology.

## 🚀 Quick Start

### For Core DNA Website Integration
```bash
# 1. Deploy your API server
npm install && npm run build && npm start

# 2. Upload widget to your web server
cp public/coredna-chatbot.js /path/to/your/webserver/

# 3. Add embed code to your website
# Copy from integration-package/embed-code.html
```

### For Development & Testing
```bash
git clone https://github.com/keshini2000/chatbot-script-.git
cd chatbot-script-
npm install
npm run dev
# Visit http://localhost:3000
```

## 📋 What's Included

### 🎯 **Complete Chatbot Solution**
- **TypeScript API** with Next.js backend
- **Embeddable Widget** - Vanilla JavaScript, no dependencies
- **793 Indexed Documents** from Core DNA website
- **Contact Integration** with real Core DNA sales info
- **Mobile Responsive** design

### 🛠️ **Integration Tools**
- **Deployment Scripts** for multiple environments
- **Embed Code Generator** with customization options
- **Test Environment** for validation before going live
- **Complete Documentation** with troubleshooting guides

### 🎨 **Demo Environments**
- **Core DNA Website Replica** - Authentic branding demo
- **Widget Embed Demo** - Integration instructions
- **Full-Screen Chat** - Complete feature testing
- **Integration Test Page** - Localhost validation

## 🏗️ Project Structure

```
coredna-chatbot/
├── src/
│   ├── app/
│   │   ├── api/chat/           # Chat API endpoint
│   │   ├── demo/               # Core DNA website replica
│   │   └── page.tsx            # Demo selection page
│   ├── components/
│   │   ├── ChatBot.tsx         # Full-screen chat interface
│   │   └── FloatingChatWidget.tsx
│   └── lib/
│       ├── rag-service.ts      # RAG implementation
│       └── vector-store-llamaindex.ts
├── public/
│   ├── coredna-chatbot.js      # Embeddable widget
│   ├── embed-demo.html         # Integration demo
│   └── test-integration.html   # Localhost test page
├── scripts/
│   ├── deploy-widget.sh        # Deployment automation
│   └── generate-embed-code.js  # Multi-environment embed generator
├── integration-package/        # Production-ready files
├── chatbot-backend/            # Original Python data (793 documents)
└── docs/
    ├── CORE_DNA_INTEGRATION.md
    └── PRODUCTION_DEPLOYMENT.md
```

## 🎯 Integration Methods

### Method 1: Direct Integration (Recommended)
```html
<!-- Add before </body> tag -->
<script>
  window.COREDNA_CHATBOT_API = 'https://your-api.com/api/chat';
</script>
<script src="https://coredna.com/coredna-chatbot.js" async></script>
```

### Method 2: Google Tag Manager
1. Create Custom HTML tag in GTM
2. Paste embed code from `integration-package/embed-code.html`
3. Set trigger to "All Pages"
4. Publish container

### Method 3: WordPress/CMS
- Add to theme's footer template
- Use "Insert Headers and Footers" plugin
- Or add via theme customizer

## 🔧 Configuration Options

```javascript
window.COREDNA_CHATBOT_CONFIG = {
  brandColor: '#dc2626',           // Core DNA red
  position: 'bottom-right',        // Widget position
  autoOpen: false,                 // Auto-open behavior
  welcomeMessage: 'Custom text',   // Greeting message
  contactInfo: {                   // Sales contact details
    email: 'sales@coredna.com',
    phone: { us: '+1 617 274 6660', au: '+61 3 8563 9100' }
  },
  suggestedQuestions: [            // Quick-start questions
    'What is Core DNA?',
    'Tell me about pricing'
  ]
};
```

## 🚀 Deployment

### Quick Deployment
```bash
# Generate production package
./scripts/deploy-widget.sh https://your-production-api.com

# Upload files to your server
scp dist/coredna-chatbot.js user@server:/var/www/html/
```

### Environment-Specific Deployment
```bash
# Development
node scripts/generate-embed-code.js development

# Staging  
node scripts/generate-embed-code.js staging

# Production
node scripts/generate-embed-code.js production
```

## 🧪 Testing

### Local Testing
```bash
npm run dev
# Visit http://localhost:3000/test-integration.html
```

### Production Testing Checklist
- [ ] Widget appears in bottom-right corner
- [ ] Chat functionality works
- [ ] Contact modal triggers correctly
- [ ] Mobile responsive behavior
- [ ] No console errors
- [ ] API health check passes

## 📊 Features

### 🧠 **AI-Powered**
- **LlamaIndex.TS** for advanced RAG implementation
- **OpenAI GPT-3.5** for intelligent responses
- **793 Core DNA Documents** indexed and searchable
- **Source Citations** for transparency

### 📱 **User Experience**
- **Mobile Responsive** design
- **Floating Widget** with notification system
- **Contact Detection** auto-shows sales info
- **Conversation Persistence** across page reloads

### ⚡ **Performance**
- **3-5 Second** first response time
- **1-2 Second** subsequent responses
- **50KB Compressed** widget size
- **Zero Dependencies** for widget

### 🔒 **Security & Privacy**
- **CORS Protection** for domain restrictions
- **No Personal Data** stored in widget
- **Temporary Session IDs** only
- **HTTPS Required** for production

## 📞 Support & Customization

### Common Issues
- **Widget not appearing**: Check console for errors, verify file paths
- **API connection failed**: Check CORS settings, verify endpoint URL
- **Contact modal not working**: Verify configuration object

### Customization Services
The chatbot can be customized for:
- Custom branding and colors
- Additional contact methods
- Custom welcome messages
- Industry-specific knowledge bases

### Technical Requirements
- **Server**: Node.js 18+, TypeScript support
- **Database**: Vector index with document embeddings
- **APIs**: OpenAI GPT-3.5 + text-embedding-ada-002
- **Frontend**: Modern browser with ES6 support

## 🎉 Success Metrics

Once deployed, expect:
- **Instant Customer Support** - 24/7 availability
- **Reduced Support Burden** - Automated common questions
- **Higher Engagement** - Interactive website experience
- **Lead Generation** - Built-in contact integration
- **Brand Consistency** - Matches Core DNA design

## 📄 License

This project is proprietary software developed for Core DNA. All rights reserved.

## 🤝 Contributing

This is a private repository for Core DNA's chatbot integration. For technical support or feature requests, please contact the development team.

---

**🚀 Ready to deploy?** Follow the [Production Deployment Guide](./PRODUCTION_DEPLOYMENT.md) for step-by-step instructions.

**🧪 Want to test first?** Check out the [Integration Guide](./CORE_DNA_INTEGRATION.md) for demo environments.

**🔧 Need customization?** Review the [Configuration Options](#-configuration-options) section above.
