from app import create_app
from config.mongodb_db import get_db
from models.user import User

from datetime import datetime
from utils.db_init import init_tables

def init_db():
    app = create_app()
    with app.app_context():
        # Tabloları başlat
        init_tables()
        
        # Admin kullanıcı var mı kontrol et
        admin = User.find_by_email('admin@example.com')
        if not admin:
            # Admin kullanıcı oluştur
            admin_data = {
                'username': 'admin',
                'email': 'admin@example.com',
                'password': 'admin123',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'supplier'
            }
            admin_id = User.create(admin_data)
            print("Admin user created with email: admin@example.com and password: admin123")
        
        # Eğer ürün yoksa örnek ürünleri oluştur
        db = get_db()
        products_collection = db['products']
        
        if products_collection.count_documents({}) == 0:
            admin = User.find_by_email('admin@example.com')
            admin_id = admin['id']
            
            sample_products = [
                {
                    'supplier_id': admin_id,
                    'name': 'Laptop',
                    'description': 'High performance laptop with 16GB RAM and SSD',
                    'price': 999.99,
                    'stock': 10,
                    'created_at': datetime.utcnow(),
                    'is_deleted': False
                },
                {
                    'supplier_id': admin_id,
                    'name': 'Smartphone',
                    'description': 'Latest smartphone with high-resolution camera',
                    'price': 699.99,
                    'stock': 20,
                    'created_at': datetime.utcnow(),
                    'is_deleted': False
                },
                {
                    'supplier_id': admin_id,
                    'name': 'Headphones',
                    'description': 'Noise-cancelling wireless headphones',
                    'price': 199.99,
                    'stock': 30,
                    'created_at': datetime.utcnow(),
                    'is_deleted': False
                },
                {
                    'supplier_id': admin_id,
                    'name': 'Smartwatch',
                    'description': 'Fitness tracking smartwatch with heart rate monitor',
                    'price': 249.99,
                    'stock': 15,
                    'created_at': datetime.utcnow(),
                    'is_deleted': False
                },
                {
                    'supplier_id': admin_id,
                    'name': 'Tablet',
                    'description': '10-inch tablet with high-resolution display',
                    'price': 399.99,
                    'stock': 12,
                    'created_at': datetime.utcnow(),
                    'is_deleted': False
                },
                {
                    'supplier_id': admin_id,
                    'name': 'Wireless Mouse',
                    'description': 'Ergonomic wireless mouse with long battery life',
                    'price': 49.99,
                    'stock': 40,
                    'created_at': datetime.utcnow(),
                    'is_deleted': False
                },
                {
                    'supplier_id': admin_id,
                    'name': 'Mechanical Keyboard',
                    'description': 'RGB backlit mechanical gaming keyboard',
                    'price': 129.99,
                    'stock': 25,
                    'created_at': datetime.utcnow(),
                    'is_deleted': False
                },
                {
                    'supplier_id': admin_id,
                    'name': 'External SSD',
                    'description': '1TB portable SSD with USB-C connection',
                    'price': 159.99,
                    'stock': 18,
                    'created_at': datetime.utcnow(),
                    'is_deleted': False
                },
                {
                    'supplier_id': admin_id,
                    'name': 'Gaming Console',
                    'description': 'Next-gen gaming console with 1TB storage',
                    'price': 499.99,
                    'stock': 8,
                    'created_at': datetime.utcnow(),
                    'is_deleted': False
                },
                {
                    'supplier_id': admin_id,
                    'name': 'Bluetooth Speaker',
                    'description': 'Waterproof portable Bluetooth speaker',
                    'price': 89.99,
                    'stock': 22,
                    'created_at': datetime.utcnow(),
                    'is_deleted': False
                }
            ]
            
            products_collection.insert_many(sample_products)
            print(f"{len(sample_products)} örnek ürün oluşturuldu")
        
        print("Veritabanı başlatıldı")

if __name__ == '__main__':
    init_db() 