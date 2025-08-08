import re
from enum import Enum
from typing import Dict, List, Optional, Tuple

class Intent(Enum):
    """Message intent classification"""
    ORDER_CREATE = "order_create"
    ORDER_STATUS = "order_status"
    ORDER_CANCEL = "order_cancel"
    FAQ_GENERAL = "faq_general"
    FAQ_HOURS = "faq_hours"
    FAQ_CONTACT = "faq_contact"
    REJECT_RESPONSE = "reject_response"
    HELP = "help"
    GREETING = "greeting"
    UNKNOWN = "unknown"

class MessageParser:
    """Extract intents and entities from WhatsApp messages"""
    
    def __init__(self):
        # Intent patterns
        self.intent_patterns = {
            Intent.ORDER_CREATE: [
                r'\b(order|buy|purchase|want|need)\b',
                r'\b(create.*order|new.*order|place.*order)\b',
                r'\b(i want|i need|looking for)\b'
            ],
            Intent.ORDER_STATUS: [
                r'\b(status|track|where.*order|order.*status)\b',
                r'\b(check.*order|find.*order)\b',
                r'\bord[-\s]*\d+\b'  # Order ID pattern
            ],
            Intent.ORDER_CANCEL: [
                r'\b(cancel|delete|remove).*order\b',
                r'\b(cancel|stop)\b'
            ],
            Intent.FAQ_HOURS: [
                r'\b(hours|time|open|close|when)\b',
                r'\b(working.*hours|business.*hours)\b'
            ],
            Intent.FAQ_CONTACT: [
                r'\b(contact|phone|email|address)\b',
                r'\b(reach|call|write)\b'
            ],
            Intent.HELP: [
                r'\b(help|assist|support)\b',
                r'\b(what.*can|how.*work)\b'
            ],
            Intent.GREETING: [
                r'\b(hello|hi|hey|good morning|good afternoon)\b',
                r'\b(greetings|welcome)\b'
            ],
            Intent.REJECT_RESPONSE: [
                r'\b(no|not|reject|decline|refuse)\b',
                r'\b(don\'t want|not interested)\b'
            ]
        }
        
        # Entity patterns
        self.entity_patterns = {
            'order_id': r'\b(ord|order)[-\s]*(\d+)\b',
            'phone_number': r'\+?[\d\s\-\(\)]{10,15}',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'quantity': r'\b(\d+)\s*(piece|pieces|item|items)?\b',
            'product': r'\b(laptop|phone|computer|tablet|monitor|keyboard|mouse)\w*\b'
        }
    
    def parse_message(self, message: str) -> Dict:
        """
        Parse a WhatsApp message and extract intent and entities
        
        Args:
            message (str): The incoming message text
            
        Returns:
            Dict: Parsed message with intent, entities, and confidence
        """
        message_lower = message.lower().strip()
        
        # Detect intent
        intent, confidence = self._detect_intent(message_lower)
        
        # Extract entities
        entities = self._extract_entities(message)
        
        return {
            'original_message': message,
            'intent': intent,
            'confidence': confidence,
            'entities': entities,
            'message_length': len(message),
            'word_count': len(message.split())
        }
    
    def _detect_intent(self, message: str) -> Tuple[Intent, float]:
        """Detect the intent of the message"""
        intent_scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, message, re.IGNORECASE))
                score += matches
            
            if score > 0:
                intent_scores[intent] = score
        
        if not intent_scores:
            return Intent.UNKNOWN, 0.0
        
        # Get the intent with highest score
        best_intent = max(intent_scores, key=intent_scores.get)
        max_score = intent_scores[best_intent]
        
        # Calculate confidence (simple scoring)
        confidence = min(max_score * 0.3, 1.0)  # Cap at 1.0
        
        return best_intent, confidence
    
    def _extract_entities(self, message: str) -> Dict[str, List[str]]:
        """Extract entities from the message"""
        entities = {}
        
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, message, re.IGNORECASE)
            if matches:
                if entity_type == 'order_id':
                    # Extract just the number part
                    entities[entity_type] = [match[1] if isinstance(match, tuple) else match for match in matches]
                else:
                    entities[entity_type] = [match if isinstance(match, str) else match[0] for match in matches]
        
        return entities
    
    def extract_order_details(self, message: str) -> Dict[str, str]:
        """Extract structured order details from message"""
        lines = message.strip().split('\n')
        
        order_details = {
            'product': '',
            'quantity': '1',
            'customer_name': '',
            'customer_phone': '',
            'address': '',
            'notes': ''
        }
        
        for line in lines:
            line_lower = line.strip().lower()
            
            if 'name:' in line_lower:
                order_details['customer_name'] = line.split(':')[1].strip()
            elif 'phone:' in line_lower:
                order_details['customer_phone'] = line.split(':')[1].strip()
            elif 'address:' in line_lower:
                order_details['address'] = line.split(':')[1].strip()
            elif 'quantity:' in line_lower or 'qty:' in line_lower:
                qty_match = re.search(r'\d+', line)
                if qty_match:
                    order_details['quantity'] = qty_match.group()
            elif any(word in line_lower for word in ['want', 'order', 'buy', 'need']):
                order_details['product'] = line.strip()
            else:
                # Add to notes if it doesn't match other fields
                if line.strip() and not any(field in line_lower for field in ['name:', 'phone:', 'address:', 'quantity:']):
                    order_details['notes'] += line.strip() + ' '
        
        # Clean up notes
        order_details['notes'] = order_details['notes'].strip()
        
        return order_details
    
    def is_greeting(self, message: str) -> bool:
        """Check if message is a greeting"""
        parsed = self.parse_message(message)
        return parsed['intent'] == Intent.GREETING
    
    def is_order_related(self, message: str) -> bool:
        """Check if message is order-related"""
        parsed = self.parse_message(message)
        return parsed['intent'] in [Intent.ORDER_CREATE, Intent.ORDER_STATUS, Intent.ORDER_CANCEL]
    
    def extract_order_id(self, message: str) -> Optional[str]:
        """Extract order ID from message"""
        entities = self._extract_entities(message)
        order_ids = entities.get('order_id', [])
        return order_ids[0] if order_ids else None
