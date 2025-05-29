import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock

# Proje kök dizinini sys.path'e ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app import create_app
from config.settings import TestConfig

class TestAuthAPI(unittest.TestCase):
    
    @patch('config.mongodb_db.init_mongodb')
    @patch('utils.db_init.init_tables')
    @patch('config.mysql_db.get_mysql_connection')
    def setUp(self, mock_mysql, mock_init_tables, mock_init_mongodb):
        # MongoDB ve MySQL bağlantılarını mockla
        mock_init_mongodb.return_value = True
        mock_init_tables.return_value = True
        mock_mysql.return_value = MagicMock()
        
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        self.app_context.pop()
    
    @patch('routes.auth.User')
    def test_register_success(self, mock_user):
        # Mock User.find_by_email
        mock_user.find_by_email.return_value = None
        
        # Mock User.create
        mock_user.create.return_value = 1
        
        # Test verisi - yeni format (name kullanıyor)
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'Password123!'
        }
        
        # Test isteği
        response = self.client.post(
            '/api/auth/register',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Assert
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['message'], 'User registered successfully')
    
    @patch('routes.auth.User')
    def test_register_existing_email(self, mock_user):
        # Mock User.find_by_email - e-posta zaten var
        mock_user.find_by_email.return_value = {'id': 1, 'email': 'test@example.com'}
        
        # Test verisi - yeni format (name kullanıyor)
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'Password123!'
        }
        
        # Test isteği
        response = self.client.post(
            '/api/auth/register',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Assert
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['message'], 'Email already in use')
    
    @patch('routes.auth.User')
    @patch('routes.auth.create_access_token')
    def test_login_success(self, mock_create_token, mock_user):
        # Mock User.verify_password
        mock_user.verify_password.return_value = {
            'id': 1,
            'username': 'testuser',
            'email': 'test@example.com',
            'role': 'customer'
        }
        
        # Mock create_access_token
        mock_create_token.return_value = 'fake-jwt-token'
        
        # Test verisi
        data = {
            'email': 'test@example.com',
            'password': 'Password123!'
        }
        
        # Test isteği
        response = self.client.post(
            '/api/auth/login',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['message'], 'Giriş başarılı')
        self.assertEqual(response_data['token'], 'fake-jwt-token')
        self.assertEqual(response_data['user']['email'], 'test@example.com')
    
    @patch('routes.auth.User')
    def test_login_invalid_credentials(self, mock_user):
        # Mock User.verify_password - geçersiz kimlik bilgileri
        mock_user.verify_password.return_value = None
        
        # Test verisi
        data = {
            'email': 'test@example.com',
            'password': 'WrongPassword'
        }
        
        # Test isteği
        response = self.client.post(
            '/api/auth/login',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Assert
        self.assertEqual(response.status_code, 401)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['message'], 'Geçersiz e-posta veya şifre')
    
    @patch('routes.auth.User')
    @patch('routes.auth.send_email')
    def test_forgot_password_success(self, mock_send_email, mock_user):
        # Mock email sending to return True (successful)
        mock_send_email.return_value = True
        
        # Mock User.find_by_email
        mock_user.find_by_email.return_value = {
            'id': 1,
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        # Mock User.create_reset_token
        mock_user.create_reset_token.return_value = 'reset-token-123'
        
        # Test verisi
        data = {'email': 'test@example.com'}
        
        # Test isteği
        response = self.client.post(
            '/api/auth/forgot-password',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['message'], 'Şifre sıfırlama bağlantısı e-posta adresinize gönderildi')
        mock_send_email.assert_called_once()

if __name__ == '__main__':
    unittest.main() 