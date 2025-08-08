class OrderService:
    def __init__(self):
        self.orders = []

    def create_order(self, customer_id, order_details):
        order_id = len(self.orders) + 1
        order = {
            'order_id': order_id,
            'customer_id': customer_id,
            'order_details': order_details,
            'status': 'pending'
        }
        self.orders.append(order)
        return order

    def get_order(self, order_id):
        for order in self.orders:
            if order['order_id'] == order_id:
                return order
        return None

    def list_orders(self):
        return self.orders