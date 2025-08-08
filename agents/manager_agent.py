from flask import Response
from utils.logger import setup_logger
from utils.message_parser import MessageParser, Intent
from services.database_service import DatabaseService
from agents.order_agent import OrderAgent
from agents.faq_agent import FAQAgent
from agents.reject_agent import RejectAgent

logger = setup_logger(__name__)

class ManagerAgent:
    """Main agent that routes tasks to specialized sub-agents"""
    
    def __init__(self, whatsapp_service, config):
        self.whatsapp_service = whatsapp_service
        self.config = config
        self.message_parser = MessageParser()
        self.database_service = DatabaseService()
        
        # Initialize sub-agents
        self.order_agent = OrderAgent(whatsapp_service, self.database_service, config)
        self.faq_agent = FAQAgent(whatsapp_service, config)
        self.reject_agent = RejectAgent(whatsapp_service, config)
        
        logger.info("Manager Agent initialized with sub-agents")
    
    def handle_incoming_message(self, request):
        """Main handler for incoming WhatsApp messages"""
        try:
            # Validate webhook
            if not self.whatsapp_service.validate_webhook(request):
                logger.warning("Invalid webhook request")
                return Response(status=400)
            
            # Extract message data
            message_body = self.whatsapp_service.get_message_body(request)
            sender_number = self.whatsapp_service.get_sender_number(request)
            message_id = self.whatsapp_service.get_message_id(request)
            sender_name = self.whatsapp_service.get_sender_name(request)
            
            logger.info(f"Received message from {sender_number} ({sender_name}): {message_body}")
            
            # Parse message to determine intent
            parsed_message = self.message_parser.parse_message(message_body)
            intent = parsed_message['intent']
            confidence = parsed_message['confidence']
            
            logger.info(f"Detected intent: {intent.value} (confidence: {confidence:.2f})")
            
            # Log conversation
            self.database_service.log_conversation(
                sender_number, 'incoming', message_body, intent.value
            )
            
            # Route to appropriate agent
            response_message = self._route_to_agent(intent, message_body, sender_number, parsed_message)
            
            # Send response
            if response_message:
                success = self.whatsapp_service.send_message(sender_number, response_message)
                if success:
                    # Log outgoing message
                    self.database_service.log_conversation(
                        sender_number, 'outgoing', response_message
                    )
                else:
                    logger.error(f"Failed to send response to {sender_number}")
            
            return Response(status=200)
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            return Response(status=500)
    
    def _route_to_agent(self, intent: Intent, message: str, sender_number: str, parsed_message: dict) -> str:
        """Route message to appropriate specialized agent"""
        try:
            # Order-related intents
            if intent in [Intent.ORDER_CREATE, Intent.ORDER_STATUS, Intent.ORDER_CANCEL]:
                return self.order_agent.handle_message(intent, message, sender_number, parsed_message)
            
            # FAQ and information intents
            elif intent in [Intent.FAQ_GENERAL, Intent.FAQ_HOURS, Intent.FAQ_CONTACT, Intent.HELP]:
                return self.faq_agent.handle_message(intent, message, sender_number, parsed_message)
            
            # Reject responses
            elif intent == Intent.REJECT_RESPONSE:
                return self.reject_agent.handle_message(intent, message, sender_number, parsed_message)
            
            # Greeting
            elif intent == Intent.GREETING:
                return self._handle_greeting(sender_number)
            
            # Unknown intent
            else:
                return self._handle_unknown_intent(message, sender_number)
                
        except Exception as e:
            logger.error(f"Error routing message to agent: {e}")
            return self._get_error_response()
    
    def _handle_greeting(self, sender_number: str) -> str:
        """Handle greeting messages"""
        # Check if returning customer
        customer = self.database_service.get_customer(sender_number)
        
        if customer and customer.get('name'):
            return f"""👋 Hello {customer['name']}! Welcome back to {self.config.BOT_NAME}!

How can I assist you today?

💡 **Quick options:**
• Type *order* - Place a new order
• Type *status* - Check order status
• Type *help* - See all commands"""
        else:
            return f"""👋 Hello! Welcome to {self.config.BOT_NAME}!

I'm your virtual assistant here to help with:
📦 Orders and order status
ℹ️ Product information
📞 Contact details
🕒 Business hours

Type *help* to see all available commands or just tell me what you need! 😊"""
    
    def _handle_unknown_intent(self, message: str, sender_number: str) -> str:
        """Handle messages with unknown intent"""
        logger.info(f"Unknown intent for message: {message}")
        
        # Try to provide helpful suggestions based on keywords
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['price', 'cost', 'how much']):
            return """💰 **Pricing Information**

For product pricing and quotes, please:
• Type *contact* to speak with our sales team
• Call us directly during business hours
• Type *help* for more options

How else can I assist you?"""
        
        elif any(word in message_lower for word in ['delivery', 'shipping', 'when']):
            return """🚚 **Delivery Information**

For delivery details:
• Type *status* + your order number to track existing orders
• New orders typically take 2-3 business days
• Type *contact* for specific delivery questions

Anything else I can help with?"""
        
        else:
            return """🤔 I didn't quite understand that.

Here's what I can help you with:
• *order* - Place a new order
• *status* - Check order status
• *contact* - Get contact information
• *help* - See all commands

Just type one of these keywords or describe what you need! 😊"""
    
    def _get_error_response(self) -> str:
        """Get a generic error response"""
        return """❌ I encountered an issue processing your request.

Please try again, or:
• Type *help* for available commands
• Type *contact* to reach our support team

Sorry for the inconvenience! 🙏"""
    
    def get_agent_status(self) -> dict:
        """Get status of all agents"""
        return {
            'manager_agent': 'active',
            'order_agent': 'active',
            'faq_agent': 'active',
            'reject_agent': 'active',
            'database_connection': 'connected' if self.database_service else 'disconnected',
            'whatsapp_service': 'active' if self.whatsapp_service else 'inactive'
        }
