import os
from datetime import timedelta
from dotenv import load_dotenv

# Ortam değişkenlerini yükle
load_dotenv()

class Config:
    """Temel konfigürasyon"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    SERVER_NAME = os.environ.get('SERVER_NAME')
    
    # JWT Konfigürasyonu
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'default-jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 86400))
    
    # E-posta Konfigürasyonu
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # MongoDB Konfigürasyonu
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
    MONGO_DB_NAME = os.environ.get('MONGO_DB_NAME', 'ecommerce')
    
    # MySQL Konfigürasyonu
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'ecommerce')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    
    # Yükleme klasörü
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    
    # Uygulama URL'si
    APP_URL = os.environ.get('APP_URL', 'http://localhost:5000')

class TestConfig(Config):
    """Test konfigürasyonu"""
    TESTING = True
    DEBUG = True
    SECRET_KEY = 'test-secret-key'
    JWT_SECRET_KEY = 'test-jwt-secret-key'
    
    # Test için bellek içi SQLite veritabanı kullan
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Test için gerçek e-posta gönderme
    MAIL_SUPPRESS_SEND = True
    
    # Test için MongoDB kullanma - localhost'u kullan
    MONGO_URI = 'mongodb://localhost:27017/'
    MONGO_DB_NAME = 'ecommerce_test'
    
    # Test için MySQL kullanma - localhost'u kullan
    MYSQL_HOST = 'localhost'
    MYSQL_DATABASE = 'ecommerce_test'
    
    # Test için geçici yükleme klasörü
    UPLOAD_FOLDER = 'uploads/test'
