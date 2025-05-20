import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Proje kök dizinini sys.path'e ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from models.user import User
from utils.helpers import hash_password

class TestUserModel(unittest.TestCase):
    
    @patch('models.user.get_mysql_connection')
    def test_find_by_email(self, mock_get_conn):
        # Mock bağlantı ve cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock cursor'un fetchone metodunu yapılandır
        mock_cursor.fetchone.return_value = {
            'id': 1, 
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'hashedpassword'
        }
        
        # Test et
        result = User.find_by_email('test@example.com')
        
        # Assert
        mock_cursor.execute.assert_called_once()
        self.assertEqual(result['email'], 'test@example.com')
        self.assertEqual(result['username'], 'testuser')
    
    @patch('models.user.get_mysql_connection')
    def test_find_by_id(self, mock_get_conn):
        # Mock bağlantı ve cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock cursor'un fetchone metodunu yapılandır
        mock_cursor.fetchone.return_value = {
            'id': 1, 
            'email': 'test@example.com',
            'username': 'testuser'
        }
        
        # Test et
        result = User.find_by_id(1)
        
        # Assert
        mock_cursor.execute.assert_called_once()
        self.assertEqual(result['id'], 1)
    
    @patch('models.user.get_mysql_connection')
    @patch('models.user.hash_password')
    def test_create(self, mock_hash_password, mock_get_conn):
        # Mock bağlantı ve cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock hash_password
        mock_hash_password.return_value = 'hashedpassword'
        
        # Mock cursor'un lastrowid'sini yapılandır
        mock_cursor.lastrowid = 1
        
        # Test verisi
        user_data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'password': 'password123'
        }
        
        # Test et
        result = User.create(user_data)
        
        # Assert
        mock_cursor.execute.assert_called_once()
        mock_hash_password.assert_called_once_with('password123')
        self.assertEqual(result, 1)
    
    @patch('models.user.get_mysql_connection')
    @patch('models.user.check_password')
    @patch('models.user.User.update_last_login')
    def test_verify_password_success(self, mock_update_login, mock_check_password, mock_get_conn):
        # Mock User.find_by_email
        with patch('models.user.User.find_by_email') as mock_find:
            mock_find.return_value = {
                'id': 1,
                'email': 'test@example.com',
                'password': 'hashedpassword'
            }
            
            # Mock check_password
            mock_check_password.return_value = True
            
            # Test et
            result = User.verify_password('test@example.com', 'password123')
            
            # Assert
            mock_find.assert_called_once_with('test@example.com')
            mock_check_password.assert_called_once_with('password123', 'hashedpassword')
            mock_update_login.assert_called_once_with(1)
            self.assertIsNotNone(result)
    
    @patch('models.user.User.find_by_email')
    @patch('models.user.check_password')
    def test_verify_password_failure(self, mock_check_password, mock_find):
        # Mock User.find_by_email
        mock_find.return_value = {
            'id': 1,
            'email': 'test@example.com',
            'password': 'hashedpassword'
        }
        
        # Mock check_password
        mock_check_password.return_value = False
        
        # Test et
        result = User.verify_password('test@example.com', 'wrongpassword')
        
        # Assert
        mock_find.assert_called_once_with('test@example.com')
        mock_check_password.assert_called_once_with('wrongpassword', 'hashedpassword')
        self.assertIsNone(result)
    
    @patch('models.user.get_mysql_connection')
    @patch('models.user.generate_reset_token')
    def test_create_reset_token(self, mock_generate_token, mock_get_conn):
        # Mock bağlantı ve cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock cursor'un rowcount'ını yapılandır
        mock_cursor.rowcount = 1
        
        # Mock generate_reset_token
        mock_generate_token.return_value = 'test-token-123'
        
        # Test et
        result = User.create_reset_token('test@example.com')
        
        # Assert
        mock_cursor.execute.assert_called_once()
        self.assertEqual(result, 'test-token-123')

if __name__ == '__main__':
    unittest.main() 