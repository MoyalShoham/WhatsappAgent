from flask import Flask, request
from bot.handlers import MessageHandler

app = Flask(__name__)
message_handler = MessageHandler()

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    response = message_handler.handle_message(data)
    return response, 200

if __name__ == '__main__':
    app.run(port=5000)