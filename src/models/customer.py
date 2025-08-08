class Customer:
    def __init__(self, name, phone_number):
        self.name = name
        self.phone_number = phone_number
        self.order_history = []

    def add_order(self, order):
        self.order_history.append(order)

    def get_order_history(self):
        return self.order_history

    def __str__(self):
        return f"Customer(name={self.name}, phone_number={self.phone_number})"