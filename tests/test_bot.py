import unittest
from src.bot.handlers import MessageHandler
from src.services.order_service import OrderService
from src.services.customer_service import CustomerService

class TestMessageHandler(unittest.TestCase):
    def setUp(self):
        self.order_service = OrderService()
        self.customer_service = CustomerService()
        self.message_handler = MessageHandler(self.order_service, self.customer_service)

    def test_handle_message_inquiry(self):
        response = self.message_handler.handle_message("What is my order status?")
        self.assertIn("Your order status is", response)

    def test_handle_message_create_order(self):
        response = self.message_handler.handle_message("I want to place an order for 2 items.")
        self.assertIn("Your order has been created", response)

    def test_handle_order_creation(self):
        order_data = {"customer_id": 1, "items": ["item1", "item2"]}
        order = self.order_service.create_order(order_data)
        self.assertIsNotNone(order)
        self.assertEqual(order.customer_id, 1)

if __name__ == '__main__':
    unittest.main()