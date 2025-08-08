from datetime import datetime
from utils.logger import setup_logger
from utils.message_parser import Intent

logger = setup_logger(__name__)

class FAQAgent:
    """Handles FAQs and general queries"""
    
    def __init__(self, whatsapp_service, config):
        self.whatsapp_service = whatsapp_service
        self.config = config
        
        # FAQ database
        self.faqs = {
            'hours': {
                'keywords': ['hours', 'time', 'open', 'close', 'when', 'working'],
                'response': self._get_business_hours_response()
            },
            'contact': {
                'keywords': ['contact', 'phone', 'email', 'address', 'reach', 'call'],
                'response': self._get_contact_response()
            },
            'delivery': {
                'keywords': ['delivery', 'shipping', 'ship', 'deliver', 'how long'],
                'response': self._get_delivery_response()
            },
            'payment': {
                'keywords': ['payment', 'pay', 'price', 'cost', 'money', 'credit'],
                'response': self._get_payment_response()
            },
            'returns': {
                'keywords': ['return', 'refund', 'exchange', 'warranty'],
                'response': self._get_returns_response()
            },
            'products': {
                'keywords': ['products', 'catalog', 'items', 'sell', 'available'],
                'response': self._get_products_response()
            }
        }
        
        logger.info("FAQ Agent initialized")
    
    def handle_message(self, intent: Intent, message: str, sender_number: str, parsed_message: dict) -> str:
        """Handle FAQ and information requests"""
        try:
            if intent == Intent.FAQ_HOURS:
                return self._get_business_hours_response()
            elif intent == Intent.FAQ_CONTACT:
                return self._get_contact_response()
            elif intent == Intent.HELP:
                return self._get_help_response()
            elif intent == Intent.FAQ_GENERAL:
                return self._handle_general_faq(message)
            else:
                return self._get_help_response()
                
        except Exception as e:
            logger.error(f"Error in FAQAgent: {e}")
            return "❌ Sorry, I encountered an error. Please try again or type *contact* for support."
    
    def _handle_general_faq(self, message: str) -> str:
        """Handle general FAQ by keyword matching"""
        message_lower = message.lower()
        
        # Score each FAQ category
        category_scores = {}
        for category, faq_data in self.faqs.items():
            score = 0
            for keyword in faq_data['keywords']:
                if keyword in message_lower:
                    score += 1
            if score > 0:
                category_scores[category] = score
        
        # Return the highest scoring FAQ
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            return self.faqs[best_category]['response']
        else:
            return self._get_help_response()
    
    def _get_business_hours_response(self) -> str:
        """Get business hours information"""
        current_time = datetime.now()
        is_business_hours = self._is_business_hours(current_time)
        status = "🟢 We're Open!" if is_business_hours else "🔴 Currently Closed"
        
        return f"""🕒 **Business Hours**

**{self.config.BOT_NAME}**
📅 Monday - Friday: {self.config.BUSINESS_HOURS}
📅 Saturday: 10:00 AM - 2:00 PM
📅 Sunday: Closed

**Current Status:** {status}

**Weekend Support:**
Limited support available
Response time: 24-48 hours

**Holiday Hours:**
We may have special hours during holidays.
Check our website or call for updates.

💡 **Note:** You can send messages anytime - we'll respond during business hours!

**Need immediate help?** Type *contact* for emergency contact info."""
    
    def _get_contact_response(self) -> str:
        """Get contact information"""
        return f"""📞 **Contact Information**

**{self.config.BOT_NAME}**

📧 **Email:** support@company.com
📱 **Phone:** +1-555-0123
📍 **Address:** 123 Business St, Suite 100, City, State 12345
🌐 **Website:** www.company.com

**For urgent matters:**
📞 Call us directly during business hours
📧 Email for non-urgent inquiries

**Support Channels:**
• 💬 WhatsApp (here!) - Fastest response
• 📧 Email - Within 24 hours
• 📞 Phone - Immediate during business hours

**Business Hours:** {self.config.BUSINESS_HOURS}

**What can we help you with today?** 😊"""
    
    def _get_delivery_response(self) -> str:
        """Get delivery information"""
        return """🚚 **Delivery Information**

**Standard Delivery:**
📦 2-3 business days (most items)
🆓 Free shipping on orders over $50

**Express Delivery:**
⚡ Next business day available
💰 Additional charges apply

**Delivery Areas:**
🌍 We deliver nationwide
🏙️ Same-day delivery in select cities

**Tracking:**
📱 Real-time updates via WhatsApp
📧 Email notifications
🔍 Track with your order number

**Delivery Times:**
🕘 9:00 AM - 6:00 PM (weekdays)
🕘 10:00 AM - 4:00 PM (Saturdays)

**Special Instructions:**
💬 Add delivery notes when ordering
📞 We'll call before delivery

**Questions?** Type *status* + order number to track your order!"""
    
    def _get_payment_response(self) -> str:
        """Get payment information"""
        return """💳 **Payment Information**

**Accepted Payment Methods:**
💳 Credit Cards (Visa, MasterCard, Amex)
💰 Debit Cards
🏦 Bank Transfer
📱 Digital Wallets (PayPal, Apple Pay, Google Pay)
💵 Cash on Delivery (select areas)

**Payment Security:**
🔒 SSL encrypted transactions
🛡️ PCI DSS compliant
✅ Secure payment processing

**Pricing:**
💲 Competitive prices
🎯 No hidden fees
📊 Transparent pricing

**Payment Terms:**
✅ Payment required at order
🔄 Refunds processed within 5-7 business days
📄 Digital receipts provided

**Need a Quote?**
📞 Call or email for custom pricing
💬 Type *contact* for sales team

**Questions about billing?** Our support team is here to help!"""
    
    def _get_returns_response(self) -> str:
        """Get returns and warranty information"""
        return """🔄 **Returns & Warranty**

**Return Policy:**
📅 30-day return window
📦 Items must be in original condition
🆓 Free returns on defective items
💰 Return shipping may apply

**Return Process:**
1️⃣ Contact support for return authorization
2️⃣ Pack item securely with original packaging
3️⃣ Ship using provided return label
4️⃣ Refund processed within 5-7 business days

**Warranty Coverage:**
🛡️ 1-year manufacturer warranty
⚡ Extended warranty options available
🔧 Repair or replacement for defects

**Warranty Claims:**
📞 Contact support with order number
📋 Proof of purchase required
🔍 Quick warranty verification

**What's Not Covered:**
❌ Normal wear and tear
❌ Damage from misuse
❌ Items modified or repaired elsewhere

**Need to return something?** Type *contact* to start the process!"""
    
    def _get_products_response(self) -> str:
        """Get product information"""
        return """🛍️ **Our Products**

**Categories:**
💻 Electronics & Computers
📱 Mobile Devices & Accessories
🏠 Home & Office Equipment
⌚ Smart Devices & Wearables
🎮 Gaming & Entertainment

**Featured Products:**
⭐ Laptops & Computers
⭐ Smartphones & Tablets
⭐ Audio & Video Equipment
⭐ Smart Home Devices
⭐ Office Furniture

**Product Information:**
📋 Detailed specifications available
📸 High-quality product images
⭐ Customer reviews and ratings
💰 Competitive pricing

**Customization:**
🎨 Custom configurations available
💼 Business solutions
🏢 Bulk order discounts

**New Arrivals:**
🆕 Latest models and technologies
📅 Updated weekly
🔔 Subscribe for notifications

**Browse Products:**
🌐 Visit our website
📞 Call for product consultation
💬 Type *order* to start shopping!

**Questions about specific products?** Our team is here to help!"""
    
    def _get_help_response(self) -> str:
        """Get comprehensive help information"""
        return f"""🤖 **{self.config.BOT_NAME} - How I Can Help**

**📦 Order Management:**
• *order* - Create a new order
• *status* - Check order status
• *cancel* - Cancel an order

**ℹ️ Information:**
• *hours* - Business hours
• *contact* - Contact details
• *delivery* - Shipping information
• *payment* - Payment options
• *returns* - Return policy

**💡 Quick Commands:**
Just type any of these keywords and I'll help you instantly!

**🔍 Smart Search:**
Ask me questions like:
• "What are your business hours?"
• "How do I return an item?"
• "What payment methods do you accept?"
• "How long does delivery take?"

**🆘 Need Human Help?**
Type *contact* to reach our support team

**🚀 Getting Started:**
New here? Type *order* to place your first order!

**What would you like to know?** 😊"""
    
    def _is_business_hours(self, current_time: datetime) -> bool:
        """Check if current time is within business hours"""
        # Simple business hours check (9 AM - 5 PM, Mon-Fri)
        weekday = current_time.weekday()  # 0-6, Monday is 0
        hour = current_time.hour
        
        # Monday to Friday
        if 0 <= weekday <= 4:
            return 9 <= hour < 17
        # Saturday (limited hours)
        elif weekday == 5:
            return 10 <= hour < 14
        # Sunday
        else:
            return False
    
    def search_faq(self, query: str) -> str:
        """Search FAQ database for relevant information"""
        query_lower = query.lower()
        matches = []
        
        for category, faq_data in self.faqs.items():
            score = 0
            for keyword in faq_data['keywords']:
                if keyword in query_lower:
                    score += 1
            
            if score > 0:
                matches.append((category, score, faq_data['response']))
        
        if matches:
            # Sort by score and return the best match
            matches.sort(key=lambda x: x[1], reverse=True)
            return matches[0][2]
        else:
            return self._get_help_response()
    
    def get_faq_categories(self) -> list:
        """Get list of available FAQ categories"""
        return list(self.faqs.keys())
