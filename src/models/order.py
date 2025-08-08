class Order:
    def __init__(self, order_id, customer_id, status="Pending"):
        self.order_id = order_id
        self.customer_id = customer_id
        self.status = status

    def update_status(self, new_status):
        self.status = new_status

    def get_order_details(self):
        return {
            "order_id": self.order_id,
            "customer_id": self.customer_id,
            "status": self.status
        }