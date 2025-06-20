#!/bin/bash

# Test Resend MCP Email Sending
echo "🚀 Testing Resend MCP Email Sending"
echo "==================================="

# Check if API key is provided
if [ -z "$RESEND_API_KEY" ]; then
    echo "❌ Please set RESEND_API_KEY environment variable"
    echo "💡 Usage: RESEND_API_KEY='your_key' SENDER_EMAIL_ADDRESS='your_email' ./scripts/test_resend_mcp.sh"
    exit 1
fi

if [ -z "$SENDER_EMAIL_ADDRESS" ]; then
    echo "❌ Please set SENDER_EMAIL_ADDRESS environment variable"
    echo "💡 Usage: RESEND_API_KEY='your_key' SENDER_EMAIL_ADDRESS='your_email' ./scripts/test_resend_mcp.sh"
    exit 1
fi

echo "📧 Sending test email..."
echo "   From: $SENDER_EMAIL_ADDRESS"
echo "   To: pmannion@whiskeyhouse.com"
echo "   Subject: this is in ccccccursor chat test test 123"
echo ""

# Create MCP request for sending email
MCP_REQUEST=$(cat <<EOF
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "send_email",
    "arguments": {
      "from": "$SENDER_EMAIL_ADDRESS",
      "to": ["pmannion@whiskeyhouse.com"],
      "subject": "this is in ccccccursor chat test test 123",
      "html": "<div style='font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;'><h2 style='color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px;'>🤖 Cursor Chat Test Email</h2><p style='color: #666; font-size: 16px; line-height: 1.6;'>Hello! This is a test email sent from <strong>Cursor Chat</strong> using the Resend MCP integration.</p><div style='background-color: #f8f9fa; border-left: 4px solid #007bff; padding: 15px; margin: 20px 0;'><h3 style='color: #007bff; margin-top: 0;'>Test Details:</h3><ul style='color: #666;'><li><strong>Subject:</strong> this is in ccccccursor chat test test 123</li><li><strong>Sent via:</strong> Resend MCP through Docker</li><li><strong>Timestamp:</strong> $(date -u +"%Y-%m-%dT%H:%M:%SZ")</li><li><strong>Test ID:</strong> cursor-chat-$(date +%s)</li></ul></div><p style='color: #666; font-size: 14px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;'>This email was sent automatically from the IGN Scripts project using Cursor AI and Resend.</p></div>",
      "text": "Cursor Chat Test Email\\n\\nHello! This is a test email sent from Cursor Chat using the Resend MCP integration.\\n\\nTest Details:\\n- Subject: this is in ccccccursor chat test test 123\\n- Sent via: Resend MCP through Docker\\n- Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")\\n- Test ID: cursor-chat-$(date +%s)\\n\\nThis email was sent automatically from the IGN Scripts project using Cursor AI and Resend."
    }
  }
}
EOF
)

echo "🔄 Sending MCP request..."

# Send the MCP request to the Resend server
echo "$MCP_REQUEST" | docker run --rm -i \
  -e RESEND_API_KEY="$RESEND_API_KEY" \
  -e SENDER_EMAIL_ADDRESS="$SENDER_EMAIL_ADDRESS" \
  mcp/resend

echo ""
echo "📋 MCP request completed!" 