import unittest
from unittest.mock import Mock, patch
from services.whatsapp_service import WhatsAppService
from config import Config

class TestWhatsAppService(unittest.TestCase):
    """Unit tests for WhatsApp service"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = Mock()
        self.config.TWILIO_ACCOUNT_SID = "test_sid"
        self.config.TWILIO_AUTH_TOKEN = "test_token"
        self.config.WHATSAPP_NUMBER = "whatsapp:+14155238886"
    
    @patch('services.whatsapp_service.Client')
    def test_whatsapp_service_initialization(self, mock_client):
        """Test WhatsApp service initialization"""
        service = WhatsAppService(self.config)
        
        self.assertIsNotNone(service)
        self.assertEqual(service.whatsapp_number, "whatsapp:+14155238886")
        mock_client.assert_called_once_with("test_sid", "test_token")
    
    def test_format_number(self):
        """Test phone number formatting"""
        with patch('services.whatsapp_service.Client'):
            service = WhatsAppService(self.config)
            
            # Test cases
            test_cases = [
                ("1234567890", "+1234567890"),
                ("+1234567890", "+1234567890"),
                ("whatsapp:+1234567890", "+1234567890")
            ]
            
            for input_number, expected in test_cases:
                result = service.format_number(input_number)
                self.assertEqual(result, expected)
    
    def test_is_valid_number(self):
        """Test phone number validation"""
        with patch('services.whatsapp_service.Client'):
            service = WhatsAppService(self.config)
            
            # Valid numbers
            valid_numbers = ["+1234567890", "+12345678901", "+123456789012"]
            for number in valid_numbers:
                self.assertTrue(service.is_valid_number(number))
            
            # Invalid numbers
            invalid_numbers = ["123", "+123", "not_a_number", ""]
            for number in invalid_numbers:
                self.assertFalse(service.is_valid_number(number))
    
    @patch('services.whatsapp_service.Client')
    def test_send_message_success(self, mock_client):
        """Test successful message sending"""
        # Mock the Twilio client
        mock_message = Mock()
        mock_message.sid = "test_message_sid"
        mock_client.return_value.messages.create.return_value = mock_message
        
        service = WhatsAppService(self.config)
        result = service.send_message("+1234567890", "Test message")
        
        self.assertTrue(result)
        mock_client.return_value.messages.create.assert_called_once_with(
            body="Test message",
            from_="whatsapp:+14155238886",
            to="whatsapp:+1234567890"
        )
    
    @patch('services.whatsapp_service.Client')
    def test_send_message_failure(self, mock_client):
        """Test message sending failure"""
        # Mock Twilio exception
        from twilio.base.exceptions import TwilioException
        mock_client.return_value.messages.create.side_effect = TwilioException("Test error")
        
        service = WhatsAppService(self.config)
        result = service.send_message("+1234567890", "Test message")
        
        self.assertFalse(result)
    
    def test_get_message_data_from_request(self):
        """Test extracting message data from webhook request"""
        with patch('services.whatsapp_service.Client'):
            service = WhatsAppService(self.config)
            
            # Mock request object
            mock_request = Mock()
            mock_request.form = {
                'Body': 'Test message',
                'From': 'whatsapp:+1234567890',
                'MessageSid': 'test_sid',
                'ProfileName': 'Test User'
            }
            
            self.assertEqual(service.get_message_body(mock_request), 'Test message')
            self.assertEqual(service.get_sender_number(mock_request), '+1234567890')
            self.assertEqual(service.get_message_id(mock_request), 'test_sid')
            self.assertEqual(service.get_sender_name(mock_request), 'Test User')

if __name__ == '__main__':
    unittest.main()
