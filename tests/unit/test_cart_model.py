import unittest
import sys
import os
from unittest.mock import patch, MagicMock
from bson import ObjectId

# Proje kök dizinini sys.path'e ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from models.cart import Cart

class TestCartModel(unittest.TestCase):
    
    @patch('models.cart.get_db')
    def test_add_item(self, mock_get_db):
        """MongoDB add_item metodunu test et"""
        # Mock MongoDB database ve collection
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.carts = mock_collection
        
        # Mock find_one - ürün sepette yok
        mock_collection.find_one.return_value = None
        
        # Mock insert_one
        mock_insert_result = MagicMock()
        mock_insert_result.inserted_id = ObjectId()
        mock_collection.insert_one.return_value = mock_insert_result
        
        # Test et
        result = Cart.add_item(1, "product123", 2, 99.99)
        
        # Assert
        mock_collection.find_one.assert_called_once()
        mock_collection.insert_one.assert_called_once()
        self.assertIsNotNone(result)
    
    @patch('models.cart.get_db')
    def test_get_user_cart(self, mock_get_db):
        """MongoDB get_user_cart metodunu test et"""
        # Mock MongoDB database ve collection
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.carts = mock_collection
        
        # Mock find
        mock_collection.find.return_value = [
            {
                '_id': ObjectId(),
                'user_id': 1,
                'product_id': 'product123',
                'quantity': 2,
                'price': 99.99,
                'is_checked_out': False
            }
        ]
        
        # Test et
        result = Cart.get_user_cart(1)
        
        # Assert
        mock_collection.find.assert_called_once()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['user_id'], 1)
    
    @patch('models.cart.get_db')
    def test_get_items_with_product_details(self, mock_get_db):
        """MongoDB get_items metodunu test et"""
        # Mock MongoDB database ve collections
        mock_db = MagicMock()
        mock_carts_collection = MagicMock()
        mock_products_collection = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.carts = mock_carts_collection
        mock_db.products = mock_products_collection
        
        # Mock cart items
        mock_carts_collection.find.return_value = [
            {
                '_id': ObjectId(),
                'user_id': 1,
                'product_id': ObjectId(),
                'quantity': 2,
                'price': 99.99,
                'is_checked_out': False
            }
        ]
        
        # Mock product details
        mock_products_collection.find_one.return_value = {
            '_id': ObjectId(),
            'name': 'Test Product',
            'image': 'test.jpg',
            'is_deleted': False
        }
        
        # Test et
        result = Cart.get_items(1)
        
        # Assert
        mock_carts_collection.find.assert_called_once()
        mock_products_collection.find_one.assert_called()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['product_name'], 'Test Product')
    
    @patch('models.cart.get_db')
    def test_update_quantity(self, mock_get_db):
        """MongoDB update_quantity metodunu test et"""
        # Mock MongoDB database ve collection
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.carts = mock_collection
        
        # Mock update_one
        mock_update_result = MagicMock()
        mock_update_result.modified_count = 1
        mock_collection.update_one.return_value = mock_update_result
        
        # Test et
        result = Cart.update_quantity(str(ObjectId()), 5)
        
        # Assert
        mock_collection.update_one.assert_called_once()
        self.assertTrue(result)
    
    @patch('models.cart.get_db')
    def test_remove_item(self, mock_get_db):
        """MongoDB remove_item metodunu test et"""
        # Mock MongoDB database ve collection
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.carts = mock_collection
        
        # Mock delete_one
        mock_delete_result = MagicMock()
        mock_delete_result.deleted_count = 1
        mock_collection.delete_one.return_value = mock_delete_result
        
        # Test et
        result = Cart.remove_item(str(ObjectId()))
        
        # Assert
        mock_collection.delete_one.assert_called_once()
        self.assertTrue(result)
    
    @patch('models.cart.get_db')
    def test_checkout(self, mock_get_db):
        """MongoDB checkout metodunu test et"""
        # Mock MongoDB database ve collection
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.carts = mock_collection
        
        # Mock update_many
        mock_update_result = MagicMock()
        mock_update_result.modified_count = 2
        mock_collection.update_many.return_value = mock_update_result
        
        # Test et
        result = Cart.checkout(1)
        
        # Assert
        mock_collection.update_many.assert_called_once()
        self.assertEqual(result, 2)
    
    @patch('models.cart.get_db')
    def test_clear(self, mock_get_db):
        """MongoDB clear metodunu test et"""
        # Mock MongoDB database ve collection
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.carts = mock_collection
        
        # Mock delete_many
        mock_delete_result = MagicMock()
        mock_delete_result.deleted_count = 3
        mock_collection.delete_many.return_value = mock_delete_result
        
        # Test et
        result = Cart.clear(1)
        
        # Assert
        mock_collection.delete_many.assert_called_once()
        self.assertEqual(result, 3)

    # MySQL methodları için testler (geriye dönük uyumluluk)
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