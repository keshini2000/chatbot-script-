# Core DNA Chatbot Integration (PRODUCTION)

## Quick Integration Guide

### Step 1: Add to Your Website
Copy and paste this code before the closing `</body>` tag on any page where you want the chatbot:

```html
<!-- Core DNA Chatbot Widget -->
<script>
  // Core DNA Chatbot Configuration
  window.COREDNA_CHATBOT_API = 'https://chatbot.coredna.com/api/chat';
  window.COREDNA_CHATBOT_CONFIG = {
    // Branding
    brandColor: '#dc2626',
    brandName: 'Core DNA',
    
    // Positioning
    position: 'bottom-right',
    zIndex: 10000,
    
    // Messages
    welcomeMessage: 'Hi! I can help you learn about Core DNA\'s platform. Ask me anything!',
    offlineMessage: 'Our chatbot is currently offline. Please try again later or contact us directly.',
    
    // Suggested questions for quick start
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
    
    // Behavior settings
    autoOpen: false,
    showNotifications: true,
    persistConversation: true,
    
    // Environment
    environment: 'production',
    debug: false
  };
  
  // Error handling for production
  window.addEventListener('error', function(e) {
    if (e.filename && e.filename.includes('coredna-chatbot')) {
      console.warn('Core DNA Chatbot: Widget failed to load. Please check your network connection.');
    }
  });
</script>
<script src="https://coredna.com/coredna-chatbot.js" async onerror="console.warn('Core DNA Chatbot: Failed to load widget from https://coredna.com/coredna-chatbot.js')"></script>
<!-- End Core DNA Chatbot Widget -->
```

### Step 2: CORS Configuration
Ensure your chatbot API (https://chatbot.coredna.com) allows requests from your domain:

```typescript
// Add to your API CORS configuration
const allowedOrigins = [
  'https://coredna.com',
  'https://www.coredna.com',
  'https://staging.coredna.com' // if using staging
];
```

### Step 3: Test Integration
1. Visit your website
2. Look for chat button in bottom-right corner
3. Test with queries like:
   - "What is Core DNA?"
   - "Tell me about pricing"
   - "I want to contact sales"

## Integration Options

### Option A: Direct Integration
Add the embed code directly to your HTML templates.

### Option B: Google Tag Manager
1. Create a new Custom HTML tag in GTM
2. Paste the embed code
3. Set trigger to "All Pages" (or specific pages)
4. Publish the container

### Option C: WordPress Plugin
If using WordPress, you can add the code to:
- Theme's `footer.php` file
- Using a plugin like "Insert Headers and Footers"
- Through the WordPress Customizer

## Customization

The widget can be customized by modifying `window.COREDNA_CHATBOT_CONFIG`:

```javascript
window.COREDNA_CHATBOT_CONFIG = {
  brandColor: '#your-color',        // Change widget colors
  position: 'bottom-left',          // Change position
  autoOpen: true,                   // Auto-open on page load
  welcomeMessage: 'Custom message', // Customize greeting
  // ... other options
};
```

## Deployment Requirements

- **API Server**: Running at https://chatbot.coredna.com
- **Widget File**: Accessible at https://coredna.com/coredna-chatbot.js
- **CORS**: Configured for coredna.com domain
- **HTTPS**: Required for production (secure contexts only)

## Performance

- **Widget Size**: ~50KB compressed
- **Load Time**: <1 second
- **First Response**: 3-5 seconds
- **Subsequent**: 1-2 seconds
- **Browser Support**: All modern browsers (Chrome 60+, Firefox 55+, Safari 12+)

## Troubleshooting

### Widget Not Appearing
1. Check browser console for errors
2. Verify widget URL is accessible
3. Check CORS configuration

### API Not Responding
1. Test API health: https://chatbot.coredna.com/api/health
2. Check network tab in browser dev tools
3. Verify API server is running

### Contact Modal Issues
1. Check contact info configuration
2. Verify email/phone number formats
3. Test with different browsers

For technical support, contact your development team or check the browser console for detailed error messages.
