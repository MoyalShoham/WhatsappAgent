import unittest
from src.services.order_service import OrderService
from src.services.customer_service import CustomerService

class TestOrderService(unittest.TestCase):
    def setUp(self):
        self.order_service = OrderService()
    
    def test_create_order(self):
        order_data = {
            'customer_id': 1,
            'items': [{'product_id': 101, 'quantity': 2}],
            'total_amount': 200.0
        }
        order = self.order_service.create_order(order_data)
        self.assertIsNotNone(order)
        self.assertEqual(order.customer_id, order_data['customer_id'])
        self.assertEqual(order.total_amount, order_data['total_amount'])

class TestCustomerService(unittest.TestCase):
    def setUp(self):
        self.customer_service = CustomerService()
    
    def test_get_customer(self):
        customer = self.customer_service.get_customer(1)
        self.assertIsNotNone(customer)
        self.assertEqual(customer.id, 1)

if __name__ == '__main__':
    unittest.main()