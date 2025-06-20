#!/bin/bash

# Cursor Chat Test Email Sender
# This script sends a test email via Resend MCP

echo "🚀 Cursor Chat Test Email Sender"
echo "=================================="

# Check if required environment variables are set
if [ -z "$RESEND_API_KEY" ]; then
    echo "❌ RESEND_API_KEY environment variable is not set"
    echo "💡 Please set your Resend API key:"
    echo "   export RESEND_API_KEY=\"your_api_key_here\""
    echo "   Get your API key from: https://resend.com/api-keys"
    exit 1
fi

if [ -z "$SENDER_EMAIL_ADDRESS" ]; then
    echo "❌ SENDER_EMAIL_ADDRESS environment variable is not set"
    echo "💡 Please set your verified sender email:"
    echo "   export SENDER_EMAIL_ADDRESS=\"your_verified_sender@yourdomain.com\""
    echo "   Or use Resend's test domain: \"onboarding@resend.dev\""
    exit 1
fi

# Set default reply-to if not provided
if [ -z "$REPLY_TO_EMAIL_ADDRESSES" ]; then
    REPLY_TO_EMAIL_ADDRESSES="$SENDER_EMAIL_ADDRESS"
fi

echo "📧 Sending email with the following details:"
echo "   From: $SENDER_EMAIL_ADDRESS"
echo "   To: pmannion@whiskeyhouse.com"
echo "   Subject: this is in ccccccursor chat test test 123"
echo "   Reply-To: $REPLY_TO_EMAIL_ADDRESSES"
echo ""

# Create email payload
EMAIL_PAYLOAD=$(cat <<EOF
{
  "from": "$SENDER_EMAIL_ADDRESS",
  "to": ["pmannion@whiskeyhouse.com"],
  "subject": "this is in ccccccursor chat test test 123",
  "reply_to": ["$REPLY_TO_EMAIL_ADDRESSES"],
  "html": "<div style='font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;'><h2 style='color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px;'>🤖 Cursor Chat Test Email</h2><p style='color: #666; font-size: 16px; line-height: 1.6;'>Hello! This is a test email sent from <strong>Cursor Chat</strong> using the Resend MCP integration.</p><div style='background-color: #f8f9fa; border-left: 4px solid #007bff; padding: 15px; margin: 20px 0;'><h3 style='color: #007bff; margin-top: 0;'>Test Details:</h3><ul style='color: #666;'><li><strong>Subject:</strong> this is in ccccccursor chat test test 123</li><li><strong>Sent via:</strong> Resend MCP through Docker</li><li><strong>Timestamp:</strong> $(date -u +"%Y-%m-%dT%H:%M:%SZ")</li><li><strong>Test ID:</strong> cursor-chat-$(date +%s)</li></ul></div><p style='color: #666; font-size: 14px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;'>This email was sent automatically from the IGN Scripts project using Cursor AI and Resend.</p></div>",
  "text": "Cursor Chat Test Email\n\nHello! This is a test email sent from Cursor Chat using the Resend MCP integration.\n\nTest Details:\n- Subject: this is in ccccccursor chat test test 123\n- Sent via: Resend MCP through Docker\n- Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")\n- Test ID: cursor-chat-$(date +%s)\n\nThis email was sent automatically from the IGN Scripts project using Cursor AI and Resend."
}
EOF
)

echo "🔄 Sending email via Resend MCP..."

# Send the email using Resend MCP Docker container
docker run --rm -i \
  -e RESEND_API_KEY="$RESEND_API_KEY" \
  -e SENDER_EMAIL_ADDRESS="$SENDER_EMAIL_ADDRESS" \
  -e REPLY_TO_EMAIL_ADDRESSES="$REPLY_TO_EMAIL_ADDRESSES" \
  mcp/resend \
  send-email \
  --from "$SENDER_EMAIL_ADDRESS" \
  --to "pmannion@whiskeyhouse.com" \
  --subject "this is in ccccccursor chat test test 123" \
  --html "<div style='font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;'><h2 style='color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px;'>🤖 Cursor Chat Test Email</h2><p style='color: #666; font-size: 16px; line-height: 1.6;'>Hello! This is a test email sent from <strong>Cursor Chat</strong> using the Resend MCP integration.</p><div style='background-color: #f8f9fa; border-left: 4px solid #007bff; padding: 15px; margin: 20px 0;'><h3 style='color: #007bff; margin-top: 0;'>Test Details:</h3><ul style='color: #666;'><li><strong>Subject:</strong> this is in ccccccursor chat test test 123</li><li><strong>Sent via:</strong> Resend MCP through Docker</li><li><strong>Timestamp:</strong> $(date -u +"%Y-%m-%dT%H:%M:%SZ")</li><li><strong>Test ID:</strong> cursor-chat-$(date +%s)</li></ul></div><p style='color: #666; font-size: 14px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;'>This email was sent automatically from the IGN Scripts project using Cursor AI and Resend.</p></div>" \
  --text "Cursor Chat Test Email\n\nHello! This is a test email sent from Cursor Chat using the Resend MCP integration.\n\nTest Details:\n- Subject: this is in ccccccursor chat test test 123\n- Sent via: Resend MCP through Docker\n- Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")\n- Test ID: cursor-chat-$(date +%s)\n\nThis email was sent automatically from the IGN Scripts project using Cursor AI and Resend."

if [ $? -eq 0 ]; then
    echo "✅ Email sent successfully!"
    echo "📬 Check pmannion@whiskeyhouse.com for the test email"
else
    echo "❌ Failed to send email"
    echo "💡 Please check your API key and sender email address"
fi 