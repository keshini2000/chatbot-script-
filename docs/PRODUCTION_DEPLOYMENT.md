# 🚀 Core DNA Chatbot - Production Deployment Guide

## Overview
This guide provides everything needed to deploy the Core DNA chatbot widget to the live coredna.com website.

## 📦 What You Get

### 1. Integration Scripts
- `scripts/deploy-widget.sh` - Automated deployment script
- `scripts/generate-embed-code.js` - Embed code generator for different environments
- `integration-package/` - Ready-to-use integration files

### 2. Production-Ready Files
- `coredna-chatbot.js` - Standalone widget (no dependencies)
- `embed-code.html` - Copy-paste integration code
- Complete integration documentation

## 🎯 Quick Integration (2 Steps)

### Step 1: Upload Widget File
Upload `public/coredna-chatbot.js` to your web server so it's accessible at:
```
https://coredna.com/coredna-chatbot.js
```

### Step 2: Add Embed Code
Add this code before the closing `</body>` tag on coredna.com:

```html
<!-- Core DNA Chatbot Widget -->
<script>
  window.COREDNA_CHATBOT_API = 'https://your-chatbot-api.com/api/chat';
  window.COREDNA_CHATBOT_CONFIG = {
    brandColor: '#dc2626',
    brandName: 'Core DNA',
    position: 'bottom-right',
    welcomeMessage: 'Hi! I can help you learn about Core DNA\'s platform. Ask me anything!',
    contactInfo: {
      email: 'sales@coredna.com',
      phone: { us: '+1 617 274 6660', au: '+61 3 8563 9100' }
    }
  };
</script>
<script src="https://coredna.com/coredna-chatbot.js" async></script>
<!-- End Core DNA Chatbot Widget -->
```

## 🔧 Automated Deployment

### Generate Integration Package
```bash
# Generate production-ready package
./scripts/deploy-widget.sh https://your-production-api.com

# Or generate for different environments
node scripts/generate-embed-code.js production
node scripts/generate-embed-code.js staging
```

## 📋 Production Checklist

### Before Deployment
- [ ] API server deployed and running
- [ ] API accessible at production URL
- [ ] CORS configured for coredna.com
- [ ] OpenAI API keys configured
- [ ] 793 documents indexed and working

### During Deployment
- [ ] Upload `coredna-chatbot.js` to web server
- [ ] Add embed code to website template
- [ ] Update API URL in embed code
- [ ] Test on staging environment first

### After Deployment
- [ ] Verify widget appears in bottom-right corner
- [ ] Test chat functionality
- [ ] Test contact modal
- [ ] Verify on mobile devices
- [ ] Monitor for errors in browser console

## 🌐 Integration Methods

### Method 1: Direct HTML
Add embed code directly to your HTML templates.

### Method 2: Google Tag Manager
1. Create Custom HTML tag in GTM
2. Paste embed code
3. Set trigger to "All Pages"
4. Publish container

### Method 3: Content Management System
- **WordPress**: Add to theme's `footer.php` or use "Insert Headers and Footers" plugin
- **Drupal**: Add to theme template or use Block system
- **Custom CMS**: Add to global footer template

## ⚙️ Configuration Options

### Basic Configuration
```javascript
window.COREDNA_CHATBOT_CONFIG = {
  brandColor: '#dc2626',           // Core DNA red
  position: 'bottom-right',        // Widget position
  autoOpen: false,                 // Don't auto-open
  showNotifications: true,         // Show new message notifications
  persistConversation: true       // Remember conversation on page refresh
};
```

### Advanced Configuration
```javascript
window.COREDNA_CHATBOT_CONFIG = {
  // Suggested quick-start questions
  suggestedQuestions: [
    'What is Core DNA?',
    'Tell me about your ecommerce features',
    'How does Core DNA compare to other platforms?',
    'What are your pricing options?',
    'Can I schedule a demo?'
  ],
  
  // Contact information
  contactInfo: {
    email: 'sales@coredna.com',
    phone: {
      us: '+1 617 274 6660',
      au: '+61 3 8563 9100'
    },
    offices: ['Melbourne', 'Boston', 'Berlin']
  },
  
  // Behavior
  zIndex: 10000,                   // Ensure widget appears above other content
  debug: false                     // Set to true for troubleshooting
};
```

## 🔒 Security & Performance

### CORS Configuration
Update your API to allow requests from coredna.com:

```typescript
// In your API route
const corsHeaders = {
  'Access-Control-Allow-Origin': 'https://coredna.com',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};
```

### Performance Metrics
- **Widget Load**: ~50KB compressed (~200KB uncompressed)
- **First Response**: 3-5 seconds (includes AI processing)
- **Subsequent Responses**: 1-2 seconds
- **Browser Support**: Chrome 60+, Firefox 55+, Safari 12+, Edge 80+

### Security Features
- No personal data stored in widget
- Temporary conversation IDs only
- HTTPS required for production
- Content Security Policy compatible

## 🔍 Troubleshooting

### Widget Not Appearing
1. Check browser console for JavaScript errors
2. Verify `coredna-chatbot.js` is accessible via direct URL
3. Check network tab for failed requests
4. Ensure embed code is before `</body>` tag

### API Connection Issues
1. Test API health endpoint: `GET /api/health`
2. Check CORS headers in network tab
3. Verify API server is running and accessible
4. Check firewall/security group settings

### Contact Modal Issues
1. Verify contact info in configuration
2. Check for JavaScript errors in console
3. Test on different browsers/devices

### Performance Issues
1. Check API response times in network tab
2. Monitor server logs for errors
3. Verify vector index is loaded properly
4. Check OpenAI API rate limits

## 📞 Support

### Technical Requirements
- **Server**: Node.js 18+, TypeScript support
- **Database**: Vector index with 793 Core DNA documents
- **APIs**: OpenAI GPT-3.5 + Embeddings
- **Frontend**: Modern browser with ES6 support

### Monitoring
Monitor these key metrics:
- Widget load success rate
- API response times
- Error rates in browser console
- User engagement (conversations started)

### Getting Help
1. Check browser console for detailed errors
2. Test API endpoints directly
3. Review integration-package/INTEGRATION_GUIDE.md
4. Contact development team with specific error messages

## 🎉 Go Live!

Once deployed, the chatbot will:
- ✅ Appear as a floating widget in bottom-right corner
- ✅ Answer questions about Core DNA platform using 793 indexed documents
- ✅ Automatically detect contact requests and show sales info
- ✅ Provide source citations for transparency
- ✅ Work seamlessly on desktop and mobile

Your customers can now get instant, intelligent answers about Core DNA's platform 24/7!