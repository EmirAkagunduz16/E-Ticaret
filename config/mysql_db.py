import mysql.connector
import os
import sys
from dotenv import load_dotenv

# Ortam değişkenlerini yükle
load_dotenv()

# Flag to indicate if we're in test mode
is_test_mode = 'pytest' in sys.modules

def get_mysql_connection():
    """MySQL veritabanına bağlantı al"""
    try:
        # Always use localhost for MySQL in test mode or selenium tests
        if is_test_mode or 'FLASK_TEST_PORT' in os.environ:
            host = 'localhost'
            database = os.getenv('MYSQL_DATABASE', 'ecommerce_test')
        else:
            host = os.getenv('MYSQL_HOST', 'localhost')
            database = os.getenv('MYSQL_DATABASE', 'ecommerce')
            
        connection = mysql.connector.connect(
            host=host,
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            database=database,
            port=int(os.getenv('MYSQL_PORT', 3306)),
            connection_timeout=5  # Reduced timeout for faster failure
        )
        return connection
    except Exception as e:
        print(f"MySQL bağlantı hatası: {str(e)}")
        # If we're in test mode, we can continue without MySQL
        if is_test_mode or 'FLASK_TEST_PORT' in os.environ:
            print("Test modu: MySQL olmadan devam ediliyor")
            return None
        return None
