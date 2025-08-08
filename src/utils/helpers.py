def format_message(message: str) -> str:
    """Format a message for sending to the user."""
    return message.strip().capitalize()

def validate_phone_number(phone_number: str) -> bool:
    """Validate the format of a phone number."""
    return phone_number.isdigit() and len(phone_number) in [10, 11]

def extract_order_id(message: str) -> str:
    """Extract order ID from a message."""
    # Assuming order ID is a numeric value in the message
    words = message.split()
    for word in words:
        if word.isdigit():
            return word
    return None

def is_valid_order_status(status: str) -> bool:
    """Check if the provided order status is valid."""
    valid_statuses = ['pending', 'confirmed', 'shipped', 'delivered', 'canceled']
    return status.lower() in valid_statuses