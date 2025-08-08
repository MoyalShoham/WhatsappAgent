from utils.logger import setup_logger
from utils.message_parser import Intent

logger = setup_logger(__name__)

class RejectAgent:
    """Handles reject responses and negative feedback"""
    
    def __init__(self, whatsapp_service, config):
        self.whatsapp_service = whatsapp_service
        self.config = config
        
        # Response strategies for different rejection scenarios
        self.rejection_responses = {
            'not_interested': [
                "No problem! Thanks for letting me know.",
                "That's perfectly fine! We're here if you change your mind.",
                "Understood! Feel free to reach out anytime in the future."
            ],
            'too_expensive': [
                "I understand pricing is important. Would you like information about our current promotions?",
                "We occasionally have special offers. Would you like me to notify you about upcoming deals?",
                "I appreciate the feedback! We strive to offer competitive pricing."
            ],
            'wrong_timing': [
                "No worries! Would you like me to follow up with you at a better time?",
                "That's completely understandable. When might be a better time to connect?",
                "Thanks for letting me know! Feel free to reach out when you're ready."
            ],
            'need_to_think': [
                "Of course! Take all the time you need to decide.",
                "That's wise! Would you like me to send you some information to review?",
                "Absolutely! I'm here whenever you're ready to discuss further."
            ],
            'general_no': [
                "I understand. Thank you for your time!",
                "No problem at all! Is there anything else I can help you with?",
                "That's perfectly fine! Thanks for being direct with me."
            ]
        }
        
        logger.info("Reject Agent initialized")
    
    def handle_message(self, intent: Intent, message: str, sender_number: str, parsed_message: dict) -> str:
        """Handle rejection responses and negative feedback"""
        try:
            # Analyze the type of rejection
            rejection_type = self._analyze_rejection(message)
            
            # Get appropriate response
            response = self._get_rejection_response(rejection_type, message)
            
            # Log the rejection for analytics
            self._log_rejection(sender_number, message, rejection_type)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in RejectAgent: {e}")
            return "Thank you for your feedback. Is there anything else I can help you with?"
    
    def _analyze_rejection(self, message: str) -> str:
        """Analyze the type of rejection from the message"""
        message_lower = message.lower()
        
        # Check for specific rejection patterns
        if any(phrase in message_lower for phrase in ['not interested', 'don\'t want', 'not looking']):
            return 'not_interested'
        
        elif any(phrase in message_lower for phrase in ['too expensive', 'too much', 'can\'t afford', 'cost', 'price']):
            return 'too_expensive'
        
        elif any(phrase in message_lower for phrase in ['not now', 'bad timing', 'busy', 'later']):
            return 'wrong_timing'
        
        elif any(phrase in message_lower for phrase in ['think about', 'consider', 'decide', 'maybe']):
            return 'need_to_think'
        
        else:
            return 'general_no'
    
    def _get_rejection_response(self, rejection_type: str, original_message: str) -> str:
        """Get appropriate response based on rejection type"""
        base_responses = self.rejection_responses.get(rejection_type, self.rejection_responses['general_no'])
        
        # Select response based on rejection type
        if rejection_type == 'not_interested':
            return f"""{base_responses[0]}

🤝 **We respect your decision**

If circumstances change, we're always here to help:
• Type *help* - For any questions
• Type *contact* - To reach our team

Thank you for your time! 😊"""
        
        elif rejection_type == 'too_expensive':
            return f"""{base_responses[0]}

💰 **Money-Saving Options:**
• 🎯 Current promotions and discounts
• 📅 Seasonal sales notifications
• 💳 Flexible payment plans
• 📦 Bundle deals for better value

Would you like to:
• Hear about current promotions? 
• Be notified of future deals?
• Explore budget-friendly alternatives?

Type *contact* if you'd like to discuss pricing options! 💬"""
        
        elif rejection_type == 'wrong_timing':
            return f"""{base_responses[0]}

⏰ **We understand timing is everything**

Options for later:
• 📅 Schedule a follow-up reminder
• 📧 Join our mailing list for updates
• 💬 Reach out anytime you're ready

**When would be better for you?**
• In a few weeks?
• Next month?
• Next quarter?

Just let me know and I can follow up then! 🕒"""
        
        elif rejection_type == 'need_to_think':
            return f"""{base_responses[0]}

🤔 **Take your time!**

To help with your decision:
• 📋 Detailed product information
• 💭 Customer testimonials
• 🔍 Comparison guides
• 💬 FAQ and support

**Resources available:**
• Type *help* - For quick questions
• Type *contact* - To speak with our team
• Visit our website for detailed specs

**No pressure** - we're here when you're ready! 😊"""
        
        else:  # general_no
            return f"""{base_responses[0]}

🙏 **Thank you for being direct**

We appreciate honest feedback! 

**Still here to help:**
• Questions about anything? Type *help*
• Need support? Type *contact*
• Changed your mind? Type *order*

**Your feedback matters** - it helps us improve!

Have a great day! 😊"""
    
    def _log_rejection(self, sender_number: str, message: str, rejection_type: str):
        """Log rejection for analytics and follow-up"""
        try:
            # Log to database or analytics system
            logger.info(f"Rejection logged - Customer: {sender_number}, Type: {rejection_type}, Message: {message[:50]}...")
            
            # Here you could add database logging, analytics tracking, etc.
            # For now, just log to file
            
        except Exception as e:
            logger.error(f"Error logging rejection: {e}")
    
    def handle_complaint(self, message: str, sender_number: str) -> str:
        """Handle customer complaints specifically"""
        return """😔 **We're sorry to hear about your experience**

Your feedback is very important to us.

**Immediate Actions:**
• 📞 Priority support escalation
• 🔍 Investigation of your concern  
• 📋 Follow-up within 24 hours

**To help us resolve this:**
• Type *contact* to speak with a supervisor
• Provide your order number if applicable
• Share specific details about the issue

**We're committed to making this right** 🤝

Our customer satisfaction team will personally review your case and respond promptly.

Thank you for giving us the opportunity to improve! 🙏"""
    
    def handle_negative_feedback(self, message: str, sender_number: str) -> str:
        """Handle general negative feedback"""
        return """📝 **Thank you for your feedback**

We take all feedback seriously and use it to improve our service.

**Your input helps us:**
• 🎯 Improve our products and services
• 📈 Enhance customer experience
• 🔧 Fix any issues you've encountered

**Next Steps:**
• Your feedback has been noted
• We'll review and take appropriate action
• You may be contacted for follow-up

**Need immediate assistance?**
Type *contact* to speak with our team.

We appreciate you taking the time to share your thoughts! 🙏"""
    
    def get_feedback_statistics(self) -> dict:
        """Get statistics about rejections and feedback (for analytics)"""
        # This would connect to your analytics system
        return {
            'total_rejections': 0,
            'rejection_types': {
                'not_interested': 0,
                'too_expensive': 0,
                'wrong_timing': 0,
                'need_to_think': 0,
                'general_no': 0
            },
            'resolution_rate': 0.0
        }
    
    def suggest_alternatives(self, rejection_type: str) -> str:
        """Suggest alternatives based on rejection type"""
        if rejection_type == 'too_expensive':
            return """💡 **Alternative Options:**

• 🆓 Free tier or trial versions
• 📦 Smaller packages or bundles
• 💳 Payment plans available
• 🎯 Current promotions and discounts
• 🔄 Refurbished or previous models

Would any of these work better for you?"""
        
        elif rejection_type == 'not_interested':
            return """💭 **Perhaps you might be interested in:**

• 🆕 Different product categories
• 🎯 Related services we offer
• 📧 Industry insights and tips
• 🎁 Exclusive member benefits

Type *help* to explore other options!"""
        
        else:
            return """🤝 **We understand!**

Feel free to reach out anytime if:
• Your needs change
• You have questions
• You'd like updates on new offerings

We're here whenever you're ready! 😊"""
