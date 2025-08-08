import unittest
from unittest.mock import Mock, patch
from agents.manager_agent import ManagerAgent
from agents.order_agent import OrderAgent
from agents.faq_agent import FAQAgent
from agents.reject_agent import RejectAgent
from utils.message_parser import Intent

class TestManagerAgent(unittest.TestCase):
    """Unit tests for Manager Agent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_whatsapp_service = Mock()
        self.mock_config = Mock()
        self.mock_config.BOT_NAME = "Test Bot"
        self.mock_config.BUSINESS_HOURS = "9:00-17:00"
        
        with patch('agents.manager_agent.DatabaseService'):
            self.manager_agent = ManagerAgent(self.mock_whatsapp_service, self.mock_config)
    
    def test_manager_agent_initialization(self):
        """Test manager agent initialization"""
        self.assertIsNotNone(self.manager_agent)
        self.assertIsInstance(self.manager_agent.order_agent, OrderAgent)
        self.assertIsInstance(self.manager_agent.faq_agent, FAQAgent)
        self.assertIsInstance(self.manager_agent.reject_agent, RejectAgent)
    
    def test_route_to_order_agent(self):
        """Test routing to order agent"""
        with patch.object(self.manager_agent.order_agent, 'handle_message') as mock_handle:
            mock_handle.return_value = "Order response"
            
            result = self.manager_agent._route_to_agent(
                Intent.ORDER_CREATE, "I want to order", "+1234567890", {}
            )
            
            self.assertEqual(result, "Order response")
            mock_handle.assert_called_once()
    
    def test_route_to_faq_agent(self):
        """Test routing to FAQ agent"""
        with patch.object(self.manager_agent.faq_agent, 'handle_message') as mock_handle:
            mock_handle.return_value = "FAQ response"
            
            result = self.manager_agent._route_to_agent(
                Intent.FAQ_HOURS, "What are your hours", "+1234567890", {}
            )
            
            self.assertEqual(result, "FAQ response")
            mock_handle.assert_called_once()
    
    def test_route_to_reject_agent(self):
        """Test routing to reject agent"""
        with patch.object(self.manager_agent.reject_agent, 'handle_message') as mock_handle:
            mock_handle.return_value = "Reject response"
            
            result = self.manager_agent._route_to_agent(
                Intent.REJECT_RESPONSE, "No thanks", "+1234567890", {}
            )
            
            self.assertEqual(result, "Reject response")
            mock_handle.assert_called_once()

class TestOrderAgent(unittest.TestCase):
    """Unit tests for Order Agent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_whatsapp_service = Mock()
        self.mock_database_service = Mock()
        self.mock_config = Mock()
        
        self.order_agent = OrderAgent(
            self.mock_whatsapp_service, 
            self.mock_database_service, 
            self.mock_config
        )
    
    def test_order_agent_initialization(self):
        """Test order agent initialization"""
        self.assertIsNotNone(self.order_agent)
        self.assertEqual(self.order_agent.pending_orders, {})
    
    def test_handle_order_creation(self):
        """Test order creation handling"""
        result = self.order_agent.handle_message(
            Intent.ORDER_CREATE, "I want to order laptops", "+1234567890", {}
        )
        
        self.assertIsInstance(result, str)
        self.assertIn("order", result.lower())
    
    def test_handle_order_status(self):
        """Test order status handling"""
        # Mock database response
        self.mock_database_service.get_customer_orders.return_value = []
        
        result = self.order_agent.handle_message(
            Intent.ORDER_STATUS, "Check my order status", "+1234567890", {}
        )
        
        self.assertIsInstance(result, str)
        self.assertIn("order", result.lower())

class TestFAQAgent(unittest.TestCase):
    """Unit tests for FAQ Agent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_whatsapp_service = Mock()
        self.mock_config = Mock()
        self.mock_config.BOT_NAME = "Test Bot"
        self.mock_config.BUSINESS_HOURS = "9:00-17:00"
        
        self.faq_agent = FAQAgent(self.mock_whatsapp_service, self.mock_config)
    
    def test_faq_agent_initialization(self):
        """Test FAQ agent initialization"""
        self.assertIsNotNone(self.faq_agent)
        self.assertIsInstance(self.faq_agent.faqs, dict)
    
    def test_handle_business_hours(self):
        """Test business hours response"""
        result = self.faq_agent.handle_message(
            Intent.FAQ_HOURS, "What are your hours", "+1234567890", {}
        )
        
        self.assertIsInstance(result, str)
        self.assertIn("hours", result.lower())
        self.assertIn("business", result.lower())
    
    def test_handle_contact_info(self):
        """Test contact information response"""
        result = self.faq_agent.handle_message(
            Intent.FAQ_CONTACT, "How can I contact you", "+1234567890", {}
        )
        
        self.assertIsInstance(result, str)
        self.assertIn("contact", result.lower())
    
    def test_search_faq(self):
        """Test FAQ search functionality"""
        result = self.faq_agent.search_faq("delivery information")
        
        self.assertIsInstance(result, str)
        self.assertIn("delivery", result.lower())

class TestRejectAgent(unittest.TestCase):
    """Unit tests for Reject Agent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_whatsapp_service = Mock()
        self.mock_config = Mock()
        
        self.reject_agent = RejectAgent(self.mock_whatsapp_service, self.mock_config)
    
    def test_reject_agent_initialization(self):
        """Test reject agent initialization"""
        self.assertIsNotNone(self.reject_agent)
        self.assertIsInstance(self.reject_agent.rejection_responses, dict)
    
    def test_analyze_rejection_not_interested(self):
        """Test analyzing 'not interested' rejection"""
        result = self.reject_agent._analyze_rejection("I'm not interested")
        self.assertEqual(result, "not_interested")
    
    def test_analyze_rejection_too_expensive(self):
        """Test analyzing 'too expensive' rejection"""
        result = self.reject_agent._analyze_rejection("This is too expensive")
        self.assertEqual(result, "too_expensive")
    
    def test_analyze_rejection_wrong_timing(self):
        """Test analyzing 'wrong timing' rejection"""
        result = self.reject_agent._analyze_rejection("Not now, I'm busy")
        self.assertEqual(result, "wrong_timing")
    
    def test_handle_rejection_response(self):
        """Test handling rejection response"""
        result = self.reject_agent.handle_message(
            Intent.REJECT_RESPONSE, "No thanks", "+1234567890", {}
        )
        
        self.assertIsInstance(result, str)
        self.assertIn("thank", result.lower())

if __name__ == '__main__':
    unittest.main()
