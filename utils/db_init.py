from config.mysql_db import get_mysql_connection, is_test_mode
from config.mongodb_db import get_db
import os

def init_tables():
    """Veritabanı tablolarını başlat"""
    print("Veritabanı tabloları başlatılıyor...")
    
    # MySQL tablolarını başlat
    conn = get_mysql_connection()
    if not conn:
        print("MySQL veritabanına bağlanılamadı")
        # If we're in test mode, we can continue without MySQL
        if is_test_mode or 'FLASK_TEST_PORT' in os.environ:
            print("Test modu: MySQL olmadan devam ediliyor")
        else:
            return False
    else:
        cursor = conn.cursor()
        
        # Users tablosu
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(20) NOT NULL DEFAULT 'customer',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login DATETIME NULL,
            reset_token VARCHAR(100),
            reset_token_expires DATETIME
        )
        ''')
        
        # last_login kolonunu eklemek için (eğer yoksa)
        try:
            cursor.execute('''
            ALTER TABLE users ADD COLUMN last_login DATETIME NULL
            ''')
            print("last_login kolonu eklendi veya zaten vardı")
        except Exception as e:
            # Kolon zaten var olabilir, bu hata görmezden gelinebilir
            print(f"Not: {str(e)}")
        
        # Orders tablosu
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            total_amount DECIMAL(10, 2) NOT NULL,
            shipping_address TEXT NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # Order items tablosu
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            order_id INT NOT NULL,
            product_id VARCHAR(24) NOT NULL,
            quantity INT NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES orders(id)
        )
        ''')
        
        conn.commit()
        cursor.close()
        conn.close()
    
    # MongoDB toplamlarını başlat
    db = get_db()
    
    # MongoDB toplamlarını başlat
    if hasattr(db, 'list_collection_names'):
        if 'products' not in db.list_collection_names():
            db.create_collection('products')
            db.products.create_index('supplier_id')
            db.products.create_index('name')
        
        if 'carts' not in db.list_collection_names():
            db.create_collection('carts')
            db.carts.create_index('user_id')
            db.carts.create_index('product_id')
    
    print("Veritabanı tabloları başarıyla başlatıldı!")
    return True 