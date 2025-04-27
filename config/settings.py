import os
from datetime import timedelta
from dotenv import load_dotenv

# Ortam değişkenlerini yükle
load_dotenv()

class Config:
    # Flask Konfigürasyonu
    SECRET_KEY = os.getenv('SECRET_KEY', '1d023839bc76ee137a7de4c56aae13d8')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    SERVER_NAME = os.getenv('SERVER_NAME')
    
    # JWT Konfigürasyonu
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', '415c4d0c2324ebd0a38fe728b0ca0726')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 86400)))
    
    # E-posta Konfigürasyonu
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
    
    # MongoDB Konfigürasyonu
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'ecommerce')
    
    # MySQL Konfigürasyonu
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'password')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'ecommerce')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    
    # Yükleme klasörü
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    
    # Uygulama Konfigürasyonu
    APP_URL = os.getenv('APP_URL', 'http://localhost:5000')
