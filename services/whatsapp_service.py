from twilio.rest import Client
from twilio.base.exceptions import TwilioException
from utils.logger import setup_logger

logger = setup_logger(__name__)

class WhatsAppService:
    """Handles all WhatsApp API interactions using Twilio"""
    
    def __init__(self, config):
        self.config = config
        try:
            self.client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
            self.whatsapp_number = config.WHATSAPP_NUMBER
            logger.info("WhatsApp service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Twilio client: {e}")
            raise
    
    def send_message(self, to_number: str, message: str) -> bool:
        """Send a WhatsApp message to a specific number"""
        try:
            # Ensure the number is in WhatsApp format
            if not to_number.startswith('whatsapp:'):
                to_number = f"whatsapp:{to_number}"
            
            sent_message = self.client.messages.create(
                body=message,
                from_=self.whatsapp_number,
                to=to_number
            )
            logger.info(f"Message sent successfully. SID: {sent_message.sid} to {to_number}")
            return True
        except TwilioException as e:
            logger.error(f"Twilio error sending message to {to_number}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending message to {to_number}: {e}")
            return False
    
    def send_template_message(self, to_number: str, template_name: str, variables: dict = None) -> bool:
        """Send a template-based message (for future WhatsApp Business API integration)"""
        # For now, this is a placeholder for future template functionality
        logger.info(f"Template message feature not yet implemented: {template_name}")
        return False
    
    def get_message_body(self, request) -> str:
        """Extract message body from webhook request"""
        return request.form.get('Body', '').strip()
    
    def get_sender_number(self, request) -> str:
        """Extract sender number from webhook request"""
        return request.form.get('From', '').replace('whatsapp:', '')
    
    def get_message_id(self, request) -> str:
        """Extract message ID from webhook request"""
        return request.form.get('MessageSid', '')
    
    def get_sender_name(self, request) -> str:
        """Extract sender name from webhook request (if available)"""
        return request.form.get('ProfileName', 'Unknown')
    
    def get_media_url(self, request) -> str:
        """Extract media URL from webhook request (if message contains media)"""
        return request.form.get('MediaUrl0', '')
    
    def get_media_type(self, request) -> str:
        """Extract media type from webhook request"""
        return request.form.get('MediaContentType0', '')
    
    def validate_webhook(self, request) -> bool:
        """Validate incoming webhook request"""
        try:
            # Basic validation - check if required fields are present
            required_fields = ['From', 'Body']
            for field in required_fields:
                if not request.form.get(field):
                    logger.warning(f"Missing required field: {field}")
                    return False
            return True
        except Exception as e:
            logger.error(f"Error validating webhook: {e}")
            return False
    
    def format_number(self, phone_number: str) -> str:
        """Format phone number for WhatsApp"""
        # Remove any existing whatsapp: prefix
        clean_number = phone_number.replace('whatsapp:', '')
        
        # Add + if not present
        if not clean_number.startswith('+'):
            clean_number = '+' + clean_number
        
        return clean_number
    
    def is_valid_number(self, phone_number: str) -> bool:
        """Basic phone number validation"""
        clean_number = self.format_number(phone_number)
        # Basic validation - should start with + and be 10-15 digits
        import re
        pattern = r'^\+\d{10,15}$'
        return bool(re.match(pattern, clean_number))
