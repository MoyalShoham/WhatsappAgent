import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from utils.logger import setup_logger

logger = setup_logger(__name__)

class DatabaseService:
    """Manages database interactions for orders and customers"""
    
    def __init__(self, db_path: str = "whatsapp_agent.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create customers table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS customers (
                        phone_number TEXT PRIMARY KEY,
                        name TEXT,
                        email TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        metadata TEXT  -- JSON field for additional data
                    )
                ''')
                
                # Create orders table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS orders (
                        order_id TEXT PRIMARY KEY,
                        customer_phone TEXT,
                        product TEXT,
                        quantity INTEGER DEFAULT 1,
                        status TEXT DEFAULT 'pending',
                        details TEXT,  -- JSON field for order details
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (customer_phone) REFERENCES customers (phone_number)
                    )
                ''')
                
                # Create conversation history table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        customer_phone TEXT,
                        message_type TEXT,  -- 'incoming' or 'outgoing'
                        message_body TEXT,
                        intent TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (customer_phone) REFERENCES customers (phone_number)
                    )
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    # Customer operations
    def create_customer(self, phone_number: str, name: str = None, email: str = None, metadata: Dict = None) -> bool:
        """Create a new customer"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO customers 
                    (phone_number, name, email, metadata, updated_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (phone_number, name, email, json.dumps(metadata or {})))
                conn.commit()
                logger.info(f"Customer created/updated: {phone_number}")
                return True
        except Exception as e:
            logger.error(f"Error creating customer {phone_number}: {e}")
            return False
    
    def get_customer(self, phone_number: str) -> Optional[Dict]:
        """Get customer by phone number"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT phone_number, name, email, created_at, updated_at, metadata
                    FROM customers WHERE phone_number = ?
                ''', (phone_number,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'phone_number': row[0],
                        'name': row[1],
                        'email': row[2],
                        'created_at': row[3],
                        'updated_at': row[4],
                        'metadata': json.loads(row[5] or '{}')
                    }
                return None
        except Exception as e:
            logger.error(f"Error getting customer {phone_number}: {e}")
            return None
    
    def update_customer(self, phone_number: str, **kwargs) -> bool:
        """Update customer information"""
        try:
            # Get current customer data
            customer = self.get_customer(phone_number)
            if not customer:
                return False
            
            # Update fields
            for key, value in kwargs.items():
                if key in ['name', 'email']:
                    customer[key] = value
                else:
                    customer['metadata'][key] = value
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE customers 
                    SET name = ?, email = ?, metadata = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE phone_number = ?
                ''', (customer['name'], customer['email'], json.dumps(customer['metadata']), phone_number))
                conn.commit()
                logger.info(f"Customer updated: {phone_number}")
                return True
        except Exception as e:
            logger.error(f"Error updating customer {phone_number}: {e}")
            return False
    
    # Order operations
    def create_order(self, order_id: str, customer_phone: str, product: str, 
                    quantity: int = 1, details: Dict = None) -> bool:
        """Create a new order"""
        try:
            # Ensure customer exists
            if not self.get_customer(customer_phone):
                self.create_customer(customer_phone)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO orders 
                    (order_id, customer_phone, product, quantity, details)
                    VALUES (?, ?, ?, ?, ?)
                ''', (order_id, customer_phone, product, quantity, json.dumps(details or {})))
                conn.commit()
                logger.info(f"Order created: {order_id} for {customer_phone}")
                return True
        except Exception as e:
            logger.error(f"Error creating order {order_id}: {e}")
            return False
    
    def get_order(self, order_id: str) -> Optional[Dict]:
        """Get order by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT order_id, customer_phone, product, quantity, status, details, created_at, updated_at
                    FROM orders WHERE order_id = ?
                ''', (order_id,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'order_id': row[0],
                        'customer_phone': row[1],
                        'product': row[2],
                        'quantity': row[3],
                        'status': row[4],
                        'details': json.loads(row[5] or '{}'),
                        'created_at': row[6],
                        'updated_at': row[7]
                    }
                return None
        except Exception as e:
            logger.error(f"Error getting order {order_id}: {e}")
            return None
    
    def get_customer_orders(self, customer_phone: str) -> List[Dict]:
        """Get all orders for a customer"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT order_id, customer_phone, product, quantity, status, details, created_at, updated_at
                    FROM orders WHERE customer_phone = ? ORDER BY created_at DESC
                ''', (customer_phone,))
                
                orders = []
                for row in cursor.fetchall():
                    orders.append({
                        'order_id': row[0],
                        'customer_phone': row[1],
                        'product': row[2],
                        'quantity': row[3],
                        'status': row[4],
                        'details': json.loads(row[5] or '{}'),
                        'created_at': row[6],
                        'updated_at': row[7]
                    })
                return orders
        except Exception as e:
            logger.error(f"Error getting orders for {customer_phone}: {e}")
            return []
    
    def update_order_status(self, order_id: str, status: str, details: Dict = None) -> bool:
        """Update order status"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get current order details
                current_order = self.get_order(order_id)
                if not current_order:
                    return False
                
                # Merge details
                updated_details = current_order['details']
                if details:
                    updated_details.update(details)
                
                cursor.execute('''
                    UPDATE orders 
                    SET status = ?, details = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE order_id = ?
                ''', (status, json.dumps(updated_details), order_id))
                conn.commit()
                logger.info(f"Order {order_id} status updated to {status}")
                return True
        except Exception as e:
            logger.error(f"Error updating order {order_id}: {e}")
            return False
    
    def cancel_order(self, order_id: str, reason: str = None) -> Tuple[bool, str]:
        """Cancel an order"""
        try:
            order = self.get_order(order_id)
            if not order:
                return False, "Order not found"
            
            if order['status'] in ['delivered', 'cancelled']:
                return False, f"Cannot cancel order with status: {order['status']}"
            
            # Check if order is within cancellation period (24 hours)
            created_at = datetime.fromisoformat(order['created_at'].replace('Z', '+00:00'))
            time_diff = datetime.now() - created_at
            if time_diff.days >= 1:
                return False, "Order cannot be cancelled after 24 hours"
            
            # Update order with cancellation details
            cancel_details = order['details']
            cancel_details['cancellation_reason'] = reason or "Customer request"
            cancel_details['cancelled_at'] = datetime.now().isoformat()
            
            success = self.update_order_status(order_id, 'cancelled', cancel_details)
            return success, "Order cancelled successfully" if success else "Error cancelling order"
            
        except Exception as e:
            logger.error(f"Error cancelling order {order_id}: {e}")
            return False, "Error cancelling order"
    
    # Conversation history
    def log_conversation(self, customer_phone: str, message_type: str, message_body: str, intent: str = None) -> bool:
        """Log conversation message"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO conversations (customer_phone, message_type, message_body, intent)
                    VALUES (?, ?, ?, ?)
                ''', (customer_phone, message_type, message_body, intent))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error logging conversation for {customer_phone}: {e}")
            return False
    
    def get_conversation_history(self, customer_phone: str, limit: int = 50) -> List[Dict]:
        """Get conversation history for a customer"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT message_type, message_body, intent, timestamp
                    FROM conversations 
                    WHERE customer_phone = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (customer_phone, limit))
                
                conversations = []
                for row in cursor.fetchall():
                    conversations.append({
                        'message_type': row[0],
                        'message_body': row[1],
                        'intent': row[2],
                        'timestamp': row[3]
                    })
                return conversations
        except Exception as e:
            logger.error(f"Error getting conversation history for {customer_phone}: {e}")
            return []
    
    # Analytics and reporting
    def get_order_stats(self) -> Dict:
        """Get order statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total orders
                cursor.execute('SELECT COUNT(*) FROM orders')
                total_orders = cursor.fetchone()[0]
                
                # Orders by status
                cursor.execute('SELECT status, COUNT(*) FROM orders GROUP BY status')
                status_counts = dict(cursor.fetchall())
                
                # Recent orders (last 7 days)
                cursor.execute('''
                    SELECT COUNT(*) FROM orders 
                    WHERE created_at >= datetime('now', '-7 days')
                ''')
                recent_orders = cursor.fetchone()[0]
                
                return {
                    'total_orders': total_orders,
                    'status_distribution': status_counts,
                    'recent_orders': recent_orders
                }
        except Exception as e:
            logger.error(f"Error getting order stats: {e}")
            return {}
    
    def cleanup_old_conversations(self, days_to_keep: int = 30) -> bool:
        """Clean up old conversation logs"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM conversations 
                    WHERE timestamp < datetime('now', '-{} days')
                '''.format(days_to_keep))
                deleted_count = cursor.rowcount
                conn.commit()
                logger.info(f"Cleaned up {deleted_count} old conversation records")
                return True
        except Exception as e:
            logger.error(f"Error cleaning up conversations: {e}")
            return False
