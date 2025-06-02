#!/usr/bin/env python3
"""
Cart API Integration Tests

Bu dosya sepet (cart) API endpoint'lerinin entegrasyon testlerini içerir.
"""

import json
import os
import sys
from unittest.mock import patch, MagicMock
from bson import ObjectId

# Proje kök dizinini sys.path'e ekle
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from app import create_app
from config.settings import TestConfig
from flask_jwt_extended import create_access_token

class TestCartAPI:
    """Cart API integration tests"""
    
    @classmethod
    def setup_class(cls):
        """Test sınıfı için kurulum"""
        # Test uygulamasını oluştur
        cls.app = create_app(TestConfig)
        cls.client = cls.app.test_client()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        
        # Test verileri
        cls.test_user_data = {
            'id': 1,
            'email': 'carttest@example.com',
            'role': 'customer'
        }
    
    @classmethod
    def teardown_class(cls):
        """Test sınıfı için temizlik"""
        cls.app_context.pop()
    
    def get_auth_token(self):
        """Kimlik doğrulama token'ı al"""
        with self.app.app_context():
            return create_access_token(identity=self.test_user_data)
    
    @patch('routes.cart.get_cart_collection')
    @patch('routes.cart.get_products_collection')
    def test_add_to_cart_success(self, mock_products_collection, mock_cart_collection):
        """Sepete ürün ekleme - başarılı"""
        token = self.get_auth_token()
        
        # Mock collections
        mock_cart_collection.return_value.find_one.return_value = None  # Sepette ürün yok
        mock_cart_collection.return_value.insert_one.return_value = MagicMock()
        mock_cart_collection.return_value.find.return_value = []
        
        mock_products_collection.return_value.find_one.return_value = {
            '_id': ObjectId(),
            'name': 'Test Product',
            'price': 99.99,
            'stock': 10
        }
        
        response = self.client.post('/api/cart/add',
            data=json.dumps({
                'product_id': str(ObjectId()),
                'quantity': 2
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'message' in data
        assert 'başarıyla eklendi' in data['message']
    
    @patch('routes.cart.get_cart_collection')
    @patch('routes.cart.get_products_collection')
    def test_add_to_cart_invalid_product(self, mock_products_collection, mock_cart_collection):
        """Sepete geçersiz ürün ekleme"""
        token = self.get_auth_token()
        
        # Mock collections - ürün bulunamadı
        mock_products_collection.return_value.find_one.return_value = None
        
        response = self.client.post('/api/cart/add',
            data=json.dumps({
                'product_id': str(ObjectId()),
                'quantity': 1
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'Ürün bulunamadı' in data['message']
    
    def test_add_to_cart_unauthorized(self):
        """Yetkisiz sepete ürün ekleme"""
        response = self.client.post('/api/cart/add',
            data=json.dumps({
                'product_id': str(ObjectId()),
                'quantity': 1
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 401
    
    @patch('routes.cart.get_cart_collection')
    @patch('routes.cart.get_products_collection')
    def test_get_cart_success(self, mock_products_collection, mock_cart_collection):
        """Sepet görüntüleme - başarılı"""
        token = self.get_auth_token()
        
        # Mock cart items
        mock_cart_items = [
            {
                '_id': ObjectId(),
                'user_id': 1,
                'product_id': str(ObjectId()),
                'quantity': 2,
                'is_checked_out': False
            }
        ]
        
        mock_cart_collection.return_value.find.return_value = mock_cart_items
        mock_products_collection.return_value.find_one.return_value = {
            '_id': ObjectId(),
            'is_deleted': False
        }
        
        response = self.client.get('/api/cart',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'items' in data
    
    def test_get_cart_unauthorized(self):
        """Yetkisiz sepet görüntüleme"""
        response = self.client.get('/api/cart')
        
        assert response.status_code == 401
    
    @patch('routes.cart.get_cart_collection')
    def test_get_cart_count_success(self, mock_cart_collection):
        """Sepet sayısı alma - başarılı"""
        token = self.get_auth_token()
        
        # Mock cart count
        mock_cart_collection.return_value.count_documents.return_value = 3
        
        response = self.client.get('/api/cart/count',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'count' in data
        assert data['count'] == 3
    
    @patch('routes.cart.get_cart_collection')
    def test_get_cart_count_unauthorized(self, mock_cart_collection):
        """Yetkisiz sepet sayısı alma"""
        mock_cart_collection.return_value = None
        
        response = self.client.get('/api/cart/count')
        
        # Yetkisiz isteklerde 0 dönmeli
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['count'] == 0
    
    @patch('routes.cart.get_cart_collection')
    def test_update_cart_item_success(self, mock_cart_collection):
        """Sepet öğesi güncelleme - başarılı"""
        token = self.get_auth_token()
        cart_id = str(ObjectId())
        
        # Mock cart item
        mock_cart_collection.return_value.find_one.return_value = {
            '_id': ObjectId(cart_id),
            'user_id': 1,
            'is_checked_out': False
        }
        mock_cart_collection.return_value.update_one.return_value = MagicMock(modified_count=1)
        
        response = self.client.put(f'/api/cart/update/{cart_id}',
            data=json.dumps({
                'quantity': 5
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'güncellendi' in data['message']
    
    @patch('routes.cart.get_cart_collection')
    def test_update_cart_item_invalid_quantity(self, mock_cart_collection):
        """Sepet öğesi güncelleme - geçersiz miktar"""
        token = self.get_auth_token()
        cart_id = str(ObjectId())
        
        response = self.client.put(f'/api/cart/update/{cart_id}',
            data=json.dumps({
                'quantity': 0
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert '1 veya daha fazla olmalıdır' in data['message']
    
    @patch('routes.cart.get_cart_collection')
    def test_remove_cart_item_success(self, mock_cart_collection):
        """Sepet öğesi kaldırma - başarılı"""
        token = self.get_auth_token()
        cart_id = str(ObjectId())
        
        # Mock cart item
        mock_cart_collection.return_value.find_one.return_value = {
            '_id': ObjectId(cart_id),
            'user_id': 1,
            'is_checked_out': False
        }
        mock_cart_collection.return_value.delete_one.return_value = MagicMock(deleted_count=1)
        
        response = self.client.delete(f'/api/cart/remove/{cart_id}',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'kaldırıldı' in data['message']
    
    @patch('routes.cart.get_cart_collection')
    def test_remove_cart_item_not_found(self, mock_cart_collection):
        """Sepet öğesi kaldırma - bulunamadı"""
        token = self.get_auth_token()
        cart_id = str(ObjectId())
        
        # Mock cart item not found
        mock_cart_collection.return_value.find_one.return_value = None
        
        response = self.client.delete(f'/api/cart/remove/{cart_id}',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'bulunamadı' in data['message']
    
    @patch('routes.cart.get_cart_collection')
    @patch('routes.cart.get_products_collection')
    def test_checkout_cart_success(self, mock_products_collection, mock_cart_collection):
        """Sepet checkout - başarılı"""
        token = self.get_auth_token()
        
        # Mock cart items
        mock_cart_items = [
            {
                '_id': ObjectId(),
                'user_id': 1,
                'product_id': str(ObjectId()),
                'quantity': 2,
                'is_checked_out': False
            }
        ]
        
        mock_cart_collection.return_value.find.return_value = mock_cart_items
        mock_cart_collection.return_value.update_many.return_value = MagicMock()
        
        response = self.client.post('/api/cart/checkout',
            data=json.dumps({
                'shipping_address': 'Test Address, Test City, 12345'
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'başarıyla oluşturuldu' in data['message']
        assert 'order_id' in data
    
    @patch('routes.cart.get_cart_collection')
    def test_checkout_empty_cart(self, mock_cart_collection):
        """Boş sepet checkout"""
        token = self.get_auth_token()
        
        # Mock empty cart
        mock_cart_collection.return_value.find.return_value = []
        
        response = self.client.post('/api/cart/checkout',
            data=json.dumps({
                'shipping_address': 'Test Address, Test City, 12345'
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Sepet boş' in data['message']

if __name__ == '__main__':
    import unittest
    unittest.main() 