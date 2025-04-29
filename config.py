import os
from datetime import timedelta
from dotenv import load_dotenv

# Ortam değişkenlerini yükle
load_dotenv()

class Config:
    # Flask Yapılandırması
    SECRET_KEY = os.getenv('SECRET_KEY')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    SERVER_NAME = os.getenv('SERVER_NAME')
    
    # MySQL Yapılandırması
    SQLALCHEMY_DATABASE_URI = os.getenv('MYSQL_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Yapılandırması
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 86400)))
    
    # Email Yapılandırması
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
    
    # MongoDB Yapılandırması
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    MONGO_DB_NAME = 'ecommerce'
    
    # Uygulama Yapılandırması
    APP_URL = os.getenv('APP_URL', 'http://localhost:5000') 