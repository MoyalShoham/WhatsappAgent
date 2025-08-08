import uuid
from datetime import datetime
from utils.logger import setup_logger
from utils.message_parser import Intent

logger = setup_logger(__name__)

class OrderAgent:
    """Handles sales order creation, status checks, and cancellations"""
    
    def __init__(self, whatsapp_service, database_service, config):
        self.whatsapp_service = whatsapp_service
        self.database_service = database_service
        self.config = config
        
        # Order creation states for multi-step conversations
        self.pending_orders = {}  # phone_number -> order_data
        
        logger.info("Order Agent initialized")
    
    def handle_message(self, intent: Intent, message: str, sender_number: str, parsed_message: dict) -> str:
        """Handle order-related messages"""
        try:
            if intent == Intent.ORDER_CREATE:
                return self._handle_order_creation(message, sender_number, parsed_message)
            elif intent == Intent.ORDER_STATUS:
                return self._handle_order_status(message, sender_number, parsed_message)
            elif intent == Intent.ORDER_CANCEL:
                return self._handle_order_cancellation(message, sender_number, parsed_message)
            else:
                return self._get_order_help()
                
        except Exception as e:
            logger.error(f"Error in OrderAgent: {e}")
            return "❌ Sorry, I encountered an error processing your order request. Please try again."
    
    def _handle_order_creation(self, message: str, sender_number: str, parsed_message: dict) -> str:
        """Handle order creation process"""
        # Check if customer has pending order creation
        if sender_number in self.pending_orders:
            return self._continue_order_creation(message, sender_number)
        
        # Parse order details from message
        order_details = parsed_message.get('entities', {})
        
        # Check if message contains complete order information
        if self._is_complete_order(message):
            return self._create_order_from_message(message, sender_number)
        else:
            # Start guided order creation
            return self._start_guided_order_creation(message, sender_number)
    
    def _is_complete_order(self, message: str) -> bool:
        """Check if message contains complete order information"""
        required_fields = ['product', 'name', 'phone', 'address']
        message_lower = message.lower()
        
        found_fields = 0
        for field in required_fields:
            if field in message_lower or f"{field}:" in message_lower:
                found_fields += 1
        
        return found_fields >= 3  # At least 3 out of 4 required fields
    
    def _create_order_from_message(self, message: str, sender_number: str) -> str:
        """Create order from complete message"""
        try:
            # Parse order details
            from utils.message_parser import MessageParser
            parser = MessageParser()
            order_details = parser.extract_order_details(message)
            
            # Generate order ID
            order_id = f"ORD-{str(uuid.uuid4())[:8].upper()}"
            
            # Ensure customer exists
            customer = self.database_service.get_customer(sender_number)
            if not customer:
                self.database_service.create_customer(
                    sender_number, 
                    order_details.get('customer_name', 'Unknown'),
                    metadata={'source': 'whatsapp_order'}
                )
            
            # Create order in database
            success = self.database_service.create_order(
                order_id=order_id,
                customer_phone=sender_number,
                product=order_details.get('product', 'Product not specified'),
                quantity=int(order_details.get('quantity', 1)),
                details={
                    'customer_name': order_details.get('customer_name', ''),
                    'customer_phone': order_details.get('customer_phone', sender_number),
                    'address': order_details.get('address', ''),
                    'notes': order_details.get('notes', ''),
                    'created_via': 'whatsapp',
                    'agent_processed': True
                }
            )
            
            if success:
                logger.info(f"Order {order_id} created successfully for {sender_number}")
                return self._get_order_confirmation(order_id, order_details)
            else:
                return "❌ Sorry, there was an error creating your order. Please try again."
                
        except Exception as e:
            logger.error(f"Error creating order from message: {e}")
            return "❌ Sorry, I couldn't process your order. Please check the format and try again."
    
    def _start_guided_order_creation(self, message: str, sender_number: str) -> str:
        """Start guided order creation process"""
        # Initialize pending order
        self.pending_orders[sender_number] = {
            'step': 'product',
            'data': {},
            'started_at': datetime.now()
        }
        
        return """📦 **Let's create your order!**

I'll help you step by step.

**Step 1: What would you like to order?**
Please tell me the product/service you want.

*Examples:*
• 2 laptops
• 1 smartphone
• Office chair
• Custom software development

What would you like to order? 🛍️"""
    
    def _continue_order_creation(self, message: str, sender_number: str) -> str:
        """Continue guided order creation"""
        order_data = self.pending_orders[sender_number]
        current_step = order_data['step']
        
        try:
            if current_step == 'product':
                order_data['data']['product'] = message.strip()
                order_data['step'] = 'name'
                
                return """✅ **Product recorded!**

**Step 2: Your name**
Please provide your full name for the order.

*Example:* John Doe"""
            
            elif current_step == 'name':
                order_data['data']['customer_name'] = message.strip()
                order_data['step'] = 'phone'
                
                return """✅ **Name recorded!**

**Step 3: Contact number**
Please provide your phone number.

*Example:* +1-555-0123"""
            
            elif current_step == 'phone':
                order_data['data']['customer_phone'] = message.strip()
                order_data['step'] = 'address'
                
                return """✅ **Phone recorded!**

**Step 4: Delivery address**
Please provide your complete delivery address.

*Example:* 123 Main St, Apt 4B, New York, NY 10001"""
            
            elif current_step == 'address':
                order_data['data']['address'] = message.strip()
                
                # Create the order
                order_id = f"ORD-{str(uuid.uuid4())[:8].upper()}"
                
                success = self.database_service.create_order(
                    order_id=order_id,
                    customer_phone=sender_number,
                    product=order_data['data']['product'],
                    quantity=1,
                    details={
                        **order_data['data'],
                        'created_via': 'whatsapp_guided',
                        'agent_processed': True
                    }
                )
                
                # Clean up pending order
                del self.pending_orders[sender_number]
                
                if success:
                    return self._get_order_confirmation(order_id, order_data['data'])
                else:
                    return "❌ Sorry, there was an error creating your order. Please try again."
            
        except Exception as e:
            logger.error(f"Error in guided order creation: {e}")
            # Clean up on error
            if sender_number in self.pending_orders:
                del self.pending_orders[sender_number]
            return "❌ Sorry, there was an error. Let's start over. Type *order* to begin again."
    
    def _handle_order_status(self, message: str, sender_number: str, parsed_message: dict) -> str:
        """Handle order status inquiries"""
        # Try to extract order ID from message
        from utils.message_parser import MessageParser
        parser = MessageParser()
        order_id = parser.extract_order_id(message)
        
        if order_id:
            # Look up specific order
            order = self.database_service.get_order(f"ORD-{order_id}")
            if order:
                return self._format_order_status(order)
            else:
                return f"❌ Order ORD-{order_id} not found. Please check the order number and try again."
        else:
            # Show all orders for customer
            orders = self.database_service.get_customer_orders(sender_number)
            if orders:
                return self._format_customer_orders(orders)
            else:
                return """📋 **No orders found**

You don't have any orders yet.

Would you like to:
• Type *order* to place a new order
• Type *help* for more options"""
    
    def _handle_order_cancellation(self, message: str, sender_number: str, parsed_message: dict) -> str:
        """Handle order cancellation requests"""
        # Try to extract order ID
        from utils.message_parser import MessageParser
        parser = MessageParser()
        order_id = parser.extract_order_id(message)
        
        if order_id:
            order_id = f"ORD-{order_id}"
            
            # Verify order belongs to customer
            order = self.database_service.get_order(order_id)
            if not order:
                return f"❌ Order {order_id} not found."
            
            if order['customer_phone'] != sender_number:
                return "❌ You can only cancel your own orders."
            
            # Extract cancellation reason if provided
            reason = "Customer request via WhatsApp"
            if "reason:" in message.lower():
                reason = message.lower().split("reason:")[1].strip()
            
            # Attempt cancellation
            success, message_result = self.database_service.cancel_order(order_id, reason)
            
            if success:
                return f"""✅ **Order Cancelled**

**Order ID:** {order_id}
**Status:** Cancelled
**Reason:** {reason}

If you need assistance, type *contact* for support.
Need to place a new order? Type *order*"""
            else:
                return f"❌ **Cannot Cancel Order**\n\n{message_result}"
        else:
            # Show cancellable orders
            orders = self.database_service.get_customer_orders(sender_number)
            cancellable_orders = [o for o in orders if o['status'] not in ['delivered', 'cancelled']]
            
            if cancellable_orders:
                order_list = "\n".join([f"• {o['order_id']} - {o['product']} ({o['status']})" 
                                      for o in cancellable_orders[:5]])
                
                return f"""❌ **Cancel Order**

Your cancellable orders:
{order_list}

To cancel, reply with:
*cancel ORD-XXXXX*

*Example:* cancel ORD-12345

⚠️ Orders can only be cancelled within 24 hours."""
            else:
                return "❌ You don't have any orders that can be cancelled."
    
    def _get_order_confirmation(self, order_id: str, order_details: dict) -> str:
        """Generate order confirmation message"""
        return f"""✅ **Order Created Successfully!**

**Order ID:** {order_id}
**Product:** {order_details.get('product', 'N/A')}
**Customer:** {order_details.get('customer_name', 'N/A')}
**Phone:** {order_details.get('customer_phone', 'N/A')}
**Address:** {order_details.get('address', 'N/A')}

**Status:** Processing
**Estimated Delivery:** 2-3 business days

📱 You'll receive updates via WhatsApp
📧 Confirmation email will be sent if provided

**Need help?**
• Type *status {order_id.replace('ORD-', '')}* to check status
• Type *contact* for support

Thank you for your order! 🎉"""
    
    def _format_order_status(self, order: dict) -> str:
        """Format single order status"""
        status_emoji = {
            'pending': '⏳',
            'processing': '🔄',
            'shipped': '🚚',
            'delivered': '✅',
            'cancelled': '❌'
        }
        
        emoji = status_emoji.get(order['status'], '📦')
        
        return f"""{emoji} **Order Status**

**Order ID:** {order['order_id']}
**Product:** {order['product']}
**Quantity:** {order['quantity']}
**Status:** {order['status'].title()}
**Created:** {order['created_at'][:10]}

Need help? Type *contact* or *help*"""
    
    def _format_customer_orders(self, orders: list) -> str:
        """Format multiple orders for customer"""
        if not orders:
            return "📋 No orders found."
        
        order_list = []
        for order in orders[:5]:  # Show last 5 orders
            status_emoji = {
                'pending': '⏳',
                'processing': '🔄', 
                'shipped': '🚚',
                'delivered': '✅',
                'cancelled': '❌'
            }
            emoji = status_emoji.get(order['status'], '📦')
            
            order_list.append(f"{emoji} {order['order_id']} - {order['product']} ({order['status']})")
        
        orders_text = "\n".join(order_list)
        
        return f"""📋 **Your Orders**

{orders_text}

**To check specific order:**
Type *status* + order number
*Example:* status 12345

**Need help?** Type *help* or *contact*"""
    
    def _get_order_help(self) -> str:
        """Get order help message"""
        return """📦 **Order Help**

**Create Order:**
• Type *order* and follow the guided process
• Or send complete details in one message

**Check Status:**
• Type *status* + order number
• Type *status* to see all your orders

**Cancel Order:**
• Type *cancel* + order number
• Orders can be cancelled within 24 hours

**Need more help?** Type *contact*"""
