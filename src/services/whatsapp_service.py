class WhatsAppService:
    def __init__(self, api_client):
        self.api_client = api_client

    def send_message(self, recipient, message):
        response = self.api_client.send_message(recipient, message)
        return response

    def receive_message(self):
        message = self.api_client.receive_message()
        return message

    def get_chat_history(self, chat_id):
        history = self.api_client.get_chat_history(chat_id)
        return history

    def delete_message(self, message_id):
        response = self.api_client.delete_message(message_id)
        return response

    def update_message_status(self, message_id, status):
        response = self.api_client.update_message_status(message_id, status)
        return response