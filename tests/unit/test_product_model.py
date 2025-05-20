import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Proje kök dizinini sys.path'e ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from models.product import Product

class TestProductModel(unittest.TestCase):
    
    @patch('models.product.get_mysql_connection')
    def test_get_all_products(self, mock_get_conn):
        # Mock bağlantı ve cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock cursor'un fetchall metodunu yapılandır
        mock_cursor.fetchall.return_value = [
            {
                'id': 1, 
                'name': 'Test Product 1',
                'price': 99.99,
                'description': 'Test Description 1',
                'image': 'test1.jpg'
            },
            {
                'id': 2, 
                'name': 'Test Product 2',
                'price': 149.99,
                'description': 'Test Description 2',
                'image': 'test2.jpg'
            }
        ]
        
        # Test et
        result = Product.get_all_products()
        
        # Assert
        mock_cursor.execute.assert_called_once()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'Test Product 1')
        self.assertEqual(result[1]['name'], 'Test Product 2')
    
    @patch('models.product.get_mysql_connection')
    def test_get_product_by_id(self, mock_get_conn):
        # Mock bağlantı ve cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock cursor'un fetchone metodunu yapılandır
        mock_cursor.fetchone.return_value = {
            'id': 1, 
            'name': 'Test Product',
            'price': 99.99,
            'description': 'Test Description',
            'image': 'test.jpg'
        }
        
        # Test et
        result = Product.get_product_by_id(1)
        
        # Assert
        mock_cursor.execute.assert_called_once()
        self.assertEqual(result['id'], 1)
        self.assertEqual(result['name'], 'Test Product')
    
    @patch('models.product.get_mysql_connection')
    def test_create_product(self, mock_get_conn):
        # Mock bağlantı ve cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock cursor'un lastrowid'sini yapılandır
        mock_cursor.lastrowid = 1
        
        # Test verisi
        product_data = {
            'name': 'New Product',
            'price': 199.99,
            'description': 'New Description',
            'image': 'new.jpg',
            'category_id': 1
        }
        
        # Test et
        result = Product.create_product(product_data)
        
        # Assert
        mock_cursor.execute.assert_called_once()
        self.assertEqual(result, 1)
    
    @patch('models.product.get_mysql_connection')
    def test_update_product(self, mock_get_conn):
        # Mock bağlantı ve cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock cursor'un rowcount'ını yapılandır
        mock_cursor.rowcount = 1
        
        # Test verisi
        product_data = {
            'name': 'Updated Product',
            'price': 249.99,
            'description': 'Updated Description',
            'image': 'updated.jpg',
            'category_id': 2
        }
        
        # Test et
        result = Product.update_product(1, product_data)
        
        # Assert
        mock_cursor.execute.assert_called_once()
        self.assertTrue(result)
    
    @patch('models.product.get_mysql_connection')
    def test_delete_product(self, mock_get_conn):
        # Mock bağlantı ve cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock cursor'un rowcount'ını yapılandır
        mock_cursor.rowcount = 1
        
        # Test et
        result = Product.delete_product(1)
        
        # Assert
        mock_cursor.execute.assert_called_once()
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main() 