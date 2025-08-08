class MessageHandler:
    def __init__(self, whatsapp_service, order_service, customer_service):
        self.whatsapp_service = whatsapp_service
        self.order_service = order_service
        self.customer_service = customer_service

    def handle_message(self, message):
        # Process incoming message and determine the appropriate response
        if "order" in message.lower():
            return self.handle_order(message)
        elif "inquiry" in message.lower():
            return self.handle_inquiry(message)
        else:
            return "I'm sorry, I didn't understand that."

    def handle_order(self, message):
        # Extract order details from the message and create a new order
        order_details = self.extract_order_details(message)
        order = self.order_service.create_order(order_details)
        return f"Your order has been created with ID: {order.id}"

    def handle_inquiry(self, message):
        # Process customer inquiries
        response = self.customer_service.handle_inquiry(message)
        return response

    def extract_order_details(self, message):
        # Placeholder for extracting order details from the message
        return {}  # Return a dictionary with order details