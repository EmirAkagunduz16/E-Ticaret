import mysql.connector
import os
from dotenv import load_dotenv

# Ortam değişkenlerini yükle
load_dotenv()

def get_mysql_connection():
    """MySQL veritabanına bağlantı al"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', 'password'),
            database=os.getenv('MYSQL_DATABASE', 'ecommerce'),
            port=int(os.getenv('MYSQL_PORT', 3306))
        )
        return connection
    except Exception as e:
        print(f"MySQL bağlantı hatası: {str(e)}")
        return None
