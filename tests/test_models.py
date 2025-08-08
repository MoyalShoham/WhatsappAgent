import unittest
from src.models.customer import Customer
from src.models.order import Order

class TestCustomerModel(unittest.TestCase):
    def test_customer_creation(self):
        customer = Customer(name="John Doe", phone_number="1234567890")
        self.assertEqual(customer.name, "John Doe")
        self.assertEqual(customer.phone_number, "1234567890")
        self.assertEqual(customer.order_history, [])

class TestOrderModel(unittest.TestCase):
    def test_order_creation(self):
        order = Order(order_id=1, customer_id=1, status="Pending")
        self.assertEqual(order.order_id, 1)
        self.assertEqual(order.customer_id, 1)
        self.assertEqual(order.status, "Pending")

if __name__ == '__main__':
    unittest.main()