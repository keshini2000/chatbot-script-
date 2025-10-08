#!/bin/bash

# Core DNA Chatbot Widget Deployment Script
# This script helps deploy the chatbot widget to production

set -e

echo "🚀 Core DNA Chatbot Widget Deployment"
echo "======================================"

# Configuration
PRODUCTION_DOMAIN=${1:-"https://your-chatbot-api.com"}
BUILD_DIR="./dist"
WIDGET_FILE="coredna-chatbot.js"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📋 Deployment Checklist:${NC}"
echo "1. Build production-ready widget"
echo "2. Update API endpoints"
echo "3. Generate embed code"
echo "4. Create deployment package"
echo ""

# Create build directory
echo -e "${YELLOW}📁 Creating build directory...${NC}"
mkdir -p $BUILD_DIR

# Copy and update the widget file
echo -e "${YELLOW}🔧 Preparing widget for production...${NC}"
cp public/coredna-chatbot.js $BUILD_DIR/

# Update API URL in the widget file for production
if [ "$PRODUCTION_DOMAIN" != "https://your-chatbot-api.com" ]; then
    echo -e "${YELLOW}🔗 Updating API URL to: $PRODUCTION_DOMAIN${NC}"
    sed -i.bak "s|http://localhost:3000|$PRODUCTION_DOMAIN|g" $BUILD_DIR/$WIDGET_FILE
    rm $BUILD_DIR/$WIDGET_FILE.bak 2>/dev/null || true
fi

# Generate embed code
echo -e "${YELLOW}📝 Generating embed code...${NC}"
cat > $BUILD_DIR/embed-code.html << EOF
<!-- Core DNA Chatbot Widget -->
<script>
  // Core DNA Chatbot Configuration
  window.COREDNA_CHATBOT_API = '$PRODUCTION_DOMAIN/api/chat';
  window.COREDNA_CHATBOT_CONFIG = {
    brandColor: '#dc2626', // Core DNA red
    position: 'bottom-right',
    welcomeMessage: 'Hi! I can help you learn about Core DNA\'s platform. Ask me anything!',
    contactInfo: {
      email: 'sales@coredna.com',
      phone: {
        us: '+1 617 274 6660',
        au: '+61 3 8563 9100'
      }
    }
  };
</script>
<script src="$PRODUCTION_DOMAIN/coredna-chatbot.js" async></script>
<!-- End Core DNA Chatbot Widget -->
EOF

# Generate integration instructions
echo -e "${YELLOW}📋 Creating integration instructions...${NC}"
cat > $BUILD_DIR/INTEGRATION_INSTRUCTIONS.md << EOF
# Core DNA Chatbot Integration Instructions

## Quick Start

1. **Upload the widget file to your web server:**
   - Upload \`coredna-chatbot.js\` to your website's public directory
   - Ensure it's accessible at: \`https://coredna.com/coredna-chatbot.js\`

2. **Add the embed code to your website:**
   - Copy the content from \`embed-code.html\`
   - Paste it before the closing \`</body>\` tag on every page where you want the chatbot

3. **Update your server configuration:**
   - Ensure your chatbot API is running at: \`$PRODUCTION_DOMAIN\`
   - Configure CORS to allow requests from \`coredna.com\`

## Integration Steps

### Step 1: Server Setup
\`\`\`bash
# Deploy your chatbot API to production
# Example using PM2:
pm2 start npm --name "coredna-chatbot" -- start

# Or using Docker:
docker build -t coredna-chatbot .
docker run -d -p 3000:3000 coredna-chatbot
\`\`\`

### Step 2: CORS Configuration
Update your API to allow requests from coredna.com:

\`\`\`typescript
// In your API route (src/app/api/chat/route.ts)
const corsHeaders = {
  'Access-Control-Allow-Origin': 'https://coredna.com',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};
\`\`\`

### Step 3: Widget Integration
Add this code to your website template (before \`</body>\`):

\`\`\`html
$(cat $BUILD_DIR/embed-code.html)
\`\`\`

### Step 4: Testing
1. Visit your website and look for the chat button in the bottom-right corner
2. Test conversations with queries like:
   - "What is Core DNA?"
   - "Tell me about your ecommerce features"
   - "I want to contact sales"
3. Verify the contact modal works correctly

## Customization Options

The widget can be customized by modifying \`window.COREDNA_CHATBOT_CONFIG\`:

\`\`\`javascript
window.COREDNA_CHATBOT_CONFIG = {
  brandColor: '#dc2626',        // Widget color theme
  position: 'bottom-right',     // Widget position
  welcomeMessage: '...',        // Initial message
  suggestedQuestions: [         // Quick start questions
    'What is Core DNA?',
    'Tell me about pricing',
    'How do I get started?'
  ]
};
\`\`\`

## Support

- Widget loads in ~50KB compressed
- First response: 3-5 seconds
- Subsequent responses: 1-2 seconds
- Supports all modern browsers
- Mobile responsive

For technical support, check the browser console for any errors.
EOF

# Create deployment package info
cat > $BUILD_DIR/deployment-info.txt << EOF
Core DNA Chatbot Widget - Production Package
Generated: $(date)
API Endpoint: $PRODUCTION_DOMAIN
Files included:
- coredna-chatbot.js (production widget)
- embed-code.html (copy-paste integration)
- INTEGRATION_INSTRUCTIONS.md (detailed setup guide)

Next steps:
1. Upload coredna-chatbot.js to your web server
2. Copy embed code to your website template
3. Test the integration on coredna.com
EOF

echo ""
echo -e "${GREEN}✅ Deployment package ready!${NC}"
echo -e "${GREEN}📦 Files created in: $BUILD_DIR${NC}"
echo ""
echo -e "${BLUE}📋 Contents:${NC}"
ls -la $BUILD_DIR/
echo ""
echo -e "${YELLOW}🔗 Next steps:${NC}"
echo "1. Upload coredna-chatbot.js to your web server"
echo "2. Copy the embed code from embed-code.html"
echo "3. Add it to coredna.com before the closing </body> tag"
echo "4. Test the integration"
echo ""
echo -e "${GREEN}🎉 Ready to deploy to Core DNA website!${NC}"