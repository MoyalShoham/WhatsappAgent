class CustomerService:
    def __init__(self):
        self.customers = {}

    def add_customer(self, customer_id, customer_data):
        self.customers[customer_id] = customer_data

    def get_customer(self, customer_id):
        return self.customers.get(customer_id, None)

    def handle_inquiry(self, customer_id, inquiry):
        # Logic to handle customer inquiries
        response = f"Thank you for your inquiry, {customer_id}. We will get back to you shortly."
        return response

    def collect_feedback(self, customer_id, feedback):
        # Logic to collect customer feedback
        response = f"Thank you for your feedback, {customer_id}!"
        return response