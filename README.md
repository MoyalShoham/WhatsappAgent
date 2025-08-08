# WhatsApp Support Bot

This project is a WhatsApp bot designed to serve as a first-level customer support agent. It can handle customer inquiries and create new sales orders, providing a seamless experience for users.

## Features

- Responds to customer inquiries with predefined responses.
- Allows customers to create new sales orders.
- Integrates with the WhatsApp API for message handling.

## Project Structure

```
whatsapp-support-bot
├── src
│   ├── main.py                # Entry point of the application
│   ├── bot
│   │   ├── __init__.py        # Initializes the bot package
│   │   ├── handlers.py         # Message handling logic
│   │   └── responses.py        # Predefined responses for inquiries
│   ├── services
│   │   ├── __init__.py        # Initializes the services package
│   │   ├── whatsapp_service.py  # Handles WhatsApp API communication
│   │   ├── order_service.py    # Manages sales orders
│   │   └── customer_service.py  # Handles customer-related operations
│   ├── models
│   │   ├── __init__.py        # Initializes the models package
│   │   ├── customer.py         # Defines the Customer class
│   │   └── order.py            # Defines the Order class
│   ├── utils
│   │   ├── __init__.py        # Initializes the utils package
│   │   └── helpers.py          # Utility functions
│   └── config
│       ├── __init__.py        # Initializes the config package
│       └── settings.py         # Configuration settings
├── tests
│   ├── __init__.py            # Initializes the tests package
│   ├── test_bot.py            # Unit tests for bot functionality
│   ├── test_services.py       # Unit tests for service classes
│   └── test_models.py         # Unit tests for model classes
├── requirements.txt           # Project dependencies
├── .env.example               # Example environment variables
├── .gitignore                 # Files to ignore in version control
└── README.md                  # Project documentation
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd whatsapp-support-bot
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your environment variables by copying `.env.example` to `.env` and filling in the necessary values.

## Usage

To start the bot, run the following command:
```
python src/main.py
```

The bot will begin listening for incoming messages on WhatsApp and respond accordingly.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.