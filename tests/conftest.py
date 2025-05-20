import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Proje kök dizinini sys.path'e ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from config.settings import TestConfig

@pytest.fixture
def app():
    """Flask uygulaması için pytest fixture"""
    app = create_app(TestConfig)
    app.config['TESTING'] = True
    app.config['SERVER_NAME'] = 'localhost:5000'
    
    # Veritabanı bağlantılarını mockla
    with patch('config.mysql_db.get_mysql_connection') as mock_mysql:
        # MySQL bağlantısını mockla
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_mysql.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        with patch('config.mongodb_db.init_mongodb') as mock_mongo:
            # MongoDB bağlantısını mockla
            mock_mongo.return_value = True
            
            with app.app_context():
                yield app

@pytest.fixture
def client(app):
    """Flask test client için pytest fixture"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Flask CLI test runner için pytest fixture"""
    return app.test_cli_runner()

@pytest.fixture
def mock_db():
    """Veritabanı mock'ları için pytest fixture"""
    with patch('config.mysql_db.get_mysql_connection') as mock_mysql:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_mysql.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        with patch('config.mongodb_db.init_mongodb') as mock_mongo:
            mock_mongo.return_value = True
            
            yield {
                'mysql_conn': mock_conn,
                'mysql_cursor': mock_cursor,
                'mysql_get_conn': mock_mysql,
                'mongo_init': mock_mongo
            }

@pytest.fixture
def auth_token():
    """Test için JWT token oluşturan pytest fixture"""
    with patch('flask_jwt_extended.create_access_token') as mock_create_token:
        mock_create_token.return_value = 'test-jwt-token'
        yield mock_create_token.return_value 