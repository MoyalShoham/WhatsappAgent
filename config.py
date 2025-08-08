import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Centralized configuration management"""
    
    # Twilio/WhatsApp API settings
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    WHATSAPP_NUMBER = os.getenv('WHATSAPP_NUMBER', 'whatsapp:+14155238886')
    
    # Webhook settings
    WEBHOOK_URL = os.getenv('WEBHOOK_URL', 'https://placeholder.ngrok.io/webhook')
    WEBHOOK_VERIFY_TOKEN = os.getenv('WEBHOOK_VERIFY_TOKEN', 'your_verify_token')
    
    # Bot settings
    BOT_NAME = os.getenv('BOT_NAME', 'Customer Support Bot')
    BUSINESS_HOURS = os.getenv('BUSINESS_HOURS', '9:00-17:00')
    
    # Database settings
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    
    # Flask settings
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    PORT = int(os.getenv('PORT', 5000))
    
    # Agent settings
    AGENT_TIMEOUT = int(os.getenv('AGENT_TIMEOUT', 30))  # seconds
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
    
    def validate(self):
        """Validate that required environment variables are set"""
        required_vars = [
            'TWILIO_ACCOUNT_SID',
            'TWILIO_AUTH_TOKEN'
        ]
        
        missing_vars = [var for var in required_vars if not getattr(self, var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
