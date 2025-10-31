"""
WhatsApp Business API Webhook Server
Uses credentials extracted by DevOps Agent
"""

import os
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests
import hmac
import hashlib

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load Meta credentials (auto-extracted by agent)
META_ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')
META_APP_SECRET = os.getenv('META_APP_SECRET')
META_VERIFY_TOKEN = os.getenv('META_VERIFY_TOKEN')
META_PHONE_NUMBER_ID = os.getenv('META_PHONE_NUMBER_ID')
WEBHOOK_PORT = int(os.getenv('META_PORT', 3000))

# Validate required env vars
required_vars = ['META_ACCESS_TOKEN', 'META_VERIFY_TOKEN', 'META_PHONE_NUMBER_ID']
missing = [var for var in required_vars if not os.getenv(var)]
if missing:
    logger.error(f"❌ Missing required environment variables: {missing}")
    logger.info("Run the DevOps Agent to extract these credentials!")
    exit(1)

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """
    Webhook verification endpoint
    Meta calls this to verify your webhook URL
    """
    try:
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        logger.info(f"🔍 Webhook verification attempt - Mode: {mode}")
        
        if mode == 'subscribe' and token == META_VERIFY_TOKEN:
            logger.info("✅ Webhook verified successfully!")
            return challenge, 200
        else:
            logger.warning("❌ Verification failed - token mismatch")
            return 'Verification failed', 403
            
    except Exception as e:
        logger.error(f"Verification error: {e}")
        return 'Error', 500

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Main webhook endpoint for receiving WhatsApp messages
    """
    try:
        # Verify request signature
        signature = request.headers.get('X-Hub-Signature-256', '')
        if not verify_signature(request.get_data(), signature):
            logger.warning("⚠️ Invalid signature - possible unauthorized request")
            return 'Invalid signature', 403
        
        data = request.get_json()
        logger.info(f"📨 Received webhook data")
        
        # Process incoming messages
        if 'entry' in data:
            for entry in data['entry']:
                for change in entry.get('changes', []):
                    value = change.get('value', {})
                    
                    # Handle messages
                    if 'messages' in value:
                        for message in value['messages']:
                            process_message(message, value)
                    
                    # Handle message status updates
                    if 'statuses' in value:
                        for status in value['statuses']:
                            logger.info(f"📊 Message status: {status.get('status')}")
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

def verify_signature(payload, signature):
    """Verify webhook request is from Meta"""
    if not META_APP_SECRET:
        return True  # Skip verification if no secret (dev mode)
    
    expected = hmac.new(
        META_APP_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(f"sha256={expected}", signature)

def process_message(message, value):
    """Process incoming WhatsApp message"""
    try:
        sender = message.get('from')
        message_type = message.get('type')
        
        logger.info(f"💬 New {message_type} message from {sender}")
        
        # Handle text messages
        if message_type == 'text':
            text = message.get('text', {}).get('body', '')
            logger.info(f"   Text: {text}")
            
            # Echo back the message
            reply = f"You said: {text}"
            send_message(sender, reply)
        
        # Handle image messages
        elif message_type == 'image':
            image_id = message.get('image', {}).get('id')
            caption = message.get('image', {}).get('caption', '')
            logger.info(f"   Image ID: {image_id}, Caption: {caption}")
            send_message(sender, "Got your image! 📸")
        
        # Handle location messages
        elif message_type == 'location':
            lat = message.get('location', {}).get('latitude')
            lon = message.get('location', {}).get('longitude')
            logger.info(f"   Location: {lat}, {lon}")
            send_message(sender, "Thanks for sharing your location! 📍")
        
        # Handle interactive messages (buttons, lists)
        elif message_type == 'interactive':
            interactive_type = message.get('interactive', {}).get('type')
            logger.info(f"   Interactive: {interactive_type}")
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")

def send_message(to, text):
    """Send WhatsApp message"""
    try:
        url = f"https://graph.facebook.com/v18.0/{META_PHONE_NUMBER_ID}/messages"
        
        headers = {
            'Authorization': f'Bearer {META_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'messaging_product': 'whatsapp',
            'to': to,
            'type': 'text',
            'text': {'body': text}
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            logger.info(f"✅ Message sent to {to}")
        else:
            logger.error(f"❌ Failed to send: {response.status_code} - {response.text}")
            
    except Exception as e:
        logger.error(f"Error sending message: {e}")

def send_template(to, template_name, language='en'):
    """Send WhatsApp template message"""
    try:
        url = f"https://graph.facebook.com/v18.0/{META_PHONE_NUMBER_ID}/messages"
        
        headers = {
            'Authorization': f'Bearer {META_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'messaging_product': 'whatsapp',
            'to': to,
            'type': 'template',
            'template': {
                'name': template_name,
                'language': {'code': language}
            }
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            logger.info(f"✅ Template sent to {to}")
        else:
            logger.error(f"❌ Failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        logger.error(f"Error sending template: {e}")

def send_interactive_buttons(to, body_text, buttons):
    """
    Send interactive message with buttons
    
    Example:
    send_interactive_buttons(
        to="254712345678",
        body_text="Choose an option:",
        buttons=[
            {"id": "opt1", "title": "Option 1"},
            {"id": "opt2", "title": "Option 2"}
        ]
    )
    """
    try:
        url = f"https://graph.facebook.com/v18.0/{META_PHONE_NUMBER_ID}/messages"
        
        headers = {
            'Authorization': f'Bearer {META_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'messaging_product': 'whatsapp',
            'to': to,
            'type': 'interactive',
            'interactive': {
                'type': 'button',
                'body': {'text': body_text},
                'action': {
                    'buttons': [
                        {'type': 'reply', 'reply': btn} for btn in buttons
                    ]
                }
            }
        }
        
        response = requests.post(url, headers=headers, json=payload)
        logger.info(f"Interactive message: {response.status_code}")
        
    except Exception as e:
        logger.error(f"Error sending interactive: {e}")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'service': 'whatsapp-webhook',
        'credentials_loaded': all([
            META_ACCESS_TOKEN,
            META_VERIFY_TOKEN,
            META_PHONE_NUMBER_ID
        ])
    }), 200

@app.route('/send', methods=['POST'])
def send_endpoint():
    """
    API endpoint to send messages
    POST /send
    {
        "to": "254712345678",
        "message": "Hello from the API!"
    }
    """
    try:
        data = request.get_json()
        to = data.get('to')
        message = data.get('message')
        
        if not to or not message:
            return jsonify({'error': 'Missing to or message'}), 400
        
        send_message(to, message)
        return jsonify({'status': 'sent'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info(f"""
╔══════════════════════════════════════════════════════════════╗
║  WhatsApp Business Webhook Server                            ║
╚══════════════════════════════════════════════════════════════╝

📱 Phone Number ID: {META_PHONE_NUMBER_ID[:20]}...
🔑 Access Token: {META_ACCESS_TOKEN[:20]}... (loaded)
🔐 Verify Token: {META_VERIFY_TOKEN[:20]}...
🚀 Starting server on port {WEBHOOK_PORT}

📡 Webhook URL: http://localhost:{WEBHOOK_PORT}/webhook
🏥 Health check: http://localhost:{WEBHOOK_PORT}/health

⚠️  For production:
   1. Deploy to Render/Railway/etc
   2. Use HTTPS URL in Meta dashboard
   3. Set webhook verify token in Meta to: {META_VERIFY_TOKEN}
""")
    
    app.run(host='0.0.0.0', port=WEBHOOK_PORT, debug=False)