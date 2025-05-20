import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Proje kök dizinini sys.path'e ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from models.cart import Cart

class TestCartModel(unittest.TestCase):
    
    @patch('models.cart.get_mysql_connection')
    def test_get_cart_by_user_id(self, mock_get_conn):
        # Mock bağlantı ve cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock cursor'un fetchall metodunu yapılandır
        mock_cursor.fetchall.return_value = [
            {
                'id': 1, 
                'user_id': 1,
                'product_id': 1,
                'quantity': 2,
                'product_name': 'Test Product 1',
                'product_price': 99.99,
                'product_image': 'test1.jpg'
            },
            {
                'id': 2, 
                'user_id': 1,
                'product_id': 2,
                'quantity': 1,
                'product_name': 'Test Product 2',
                'product_price': 149.99,
                'product_image': 'test2.jpg'
            }
        ]
        
        # Test et
        result = Cart.get_cart_by_user_id(1)
        
        # Assert
        mock_cursor.execute.assert_called_once()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['product_name'], 'Test Product 1')
        self.assertEqual(result[1]['product_name'], 'Test Product 2')
    
    @patch('models.cart.get_mysql_connection')
    def test_add_to_cart_new_item(self, mock_get_conn):
        # Mock bağlantı ve cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock cursor'un fetchone metodunu yapılandır - ürün sepette yok
        mock_cursor.fetchone.return_value = None
        
        # Mock cursor'un lastrowid'sini yapılandır
        mock_cursor.lastrowid = 1
        
        # Test et
        result = Cart.add_to_cart(1, 1, 2)
        
        # Assert
        self.assertEqual(mock_cursor.execute.call_count, 2)  # Bir kez kontrol, bir kez ekleme
        self.assertEqual(result, {'cart_id': 1, 'status': 'added'})
    
    @patch('models.cart.get_mysql_connection')
    def test_add_to_cart_existing_item(self, mock_get_conn):
        # Mock bağlantı ve cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock cursor'un fetchone metodunu yapılandır - ürün sepette var
        mock_cursor.fetchone.return_value = {
            'id': 1,
            'user_id': 1,
            'product_id': 1,
            'quantity': 1
        }
        
        # Test et
        result = Cart.add_to_cart(1, 1, 2)
        
        # Assert
        self.assertEqual(mock_cursor.execute.call_count, 2)  # Bir kez kontrol, bir kez güncelleme
        self.assertEqual(result, {'cart_id': 1, 'status': 'updated'})
    
    @patch('models.cart.get_mysql_connection')
    def test_update_cart_item(self, mock_get_conn):
        # Mock bağlantı ve cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock cursor'un rowcount'ını yapılandır
        mock_cursor.rowcount = 1
        
        # Test et
        result = Cart.update_cart_item(1, 1, 3)
        
        # Assert
        mock_cursor.execute.assert_called_once()
        self.assertTrue(result)
    
    @patch('models.cart.get_mysql_connection')
    def test_remove_from_cart(self, mock_get_conn):
        # Mock bağlantı ve cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock cursor'un rowcount'ını yapılandır
        mock_cursor.rowcount = 1
        
        # Test et
        result = Cart.remove_from_cart(1, 1)
        
        # Assert
        mock_cursor.execute.assert_called_once()
        self.assertTrue(result)
    
    @patch('models.cart.get_mysql_connection')
    def test_clear_cart(self, mock_get_conn):
        # Mock bağlantı ve cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock cursor'un rowcount'ını yapılandır
        mock_cursor.rowcount = 2
        
        # Test et
        result = Cart.clear_cart(1)
        
        # Assert
        mock_cursor.execute.assert_called_once()
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main() 