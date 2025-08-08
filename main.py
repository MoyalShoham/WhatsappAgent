from flask import Flask, request, Response
from config import Config
from services.whatsapp_service import WhatsAppService
from agents.manager_agent import ManagerAgent
from utils.logger import setup_logger
import os

# Setup logging
logger = setup_logger(__name__)

app = Flask(__name__)

# Initialize configuration
config = Config()
config.validate()

# Initialize services
whatsapp_service = WhatsAppService(config)
manager_agent = ManagerAgent(whatsapp_service, config)

@app.route("/webhook", methods=["POST"])
def webhook():
    """Handle incoming WhatsApp messages"""
    try:
        return manager_agent.handle_incoming_message(request)
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return Response(status=500)

@app.route("/webhook", methods=["GET"])
def webhook_verification():
    """Verify webhook for WhatsApp Business API"""
    verify_token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    
    if verify_token == config.WEBHOOK_VERIFY_TOKEN:
        return challenge
    return "Verification failed", 403

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "WhatsApp Agent"}, 200

@app.route("/", methods=["GET"])
def home():
    """Home endpoint"""
    return {
        "message": "WhatsApp Agent is running",
        "agent": "Manager Agent with specialized sub-agents"
    }, 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    
    logger.info(f"Starting WhatsApp Agent on port {port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
