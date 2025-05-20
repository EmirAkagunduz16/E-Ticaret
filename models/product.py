from config.mongodb_db import get_db
from config.mysql_db import get_mysql_connection
from bson import ObjectId
from datetime import datetime

class Product:
    @staticmethod
    def create(supplier_id, name, description, price, stock):
        """Yeni bir ürün oluştur"""
        db = get_db()
        products_collection = db.products
        
        product = {
            'supplier_id': supplier_id,
            'name': name,
            'description': description,
            'price': float(price),
            'stock': int(stock),
            'created_at': datetime.utcnow(),
            'is_deleted': False
        }
        
        result = products_collection.insert_one(product)
        return str(result.inserted_id)
    
    @staticmethod
    def get_by_id(product_id):
        """Ürünü ID'ye göre getir"""
        db = get_db()
        products_collection = db.products
        
        try:
            product = products_collection.find_one({
                '_id': ObjectId(product_id),
                'is_deleted': False
            })
            
            if product:
                product['_id'] = str(product['_id'])
            
            return product
        except:
            return None
    
    @staticmethod
    def get_all(limit=20, skip=0):
        """Tüm ürünleri getir"""
        db = get_db()
        products_collection = db.products
        
        products = list(products_collection.find(
            {'is_deleted': False}
        ).sort('created_at', -1).skip(skip).limit(limit))
        
        # ObjectId'yi string'e çevir
        for product in products:
            product['_id'] = str(product['_id'])
        
        return products
    
    @staticmethod
    def get_by_supplier(supplier_id):
        """Tedarikçi ID'sine göre ürünleri getir"""
        db = get_db()
        products_collection = db.products
        
        products = list(products_collection.find({
            'supplier_id': supplier_id,
            'is_deleted': False
        }))
        
        # ObjectId'yi string'e çevir
        for product in products:
            product['_id'] = str(product['_id'])
        
        return products
    
    @staticmethod
    def update(product_id, update_data):
        """Ürün bilgilerini güncelle"""
        db = get_db()
        products_collection = db.products
        
        try:
            result = products_collection.update_one(
                {'_id': ObjectId(product_id)},
                {'$set': update_data}
            )
            
            return result.modified_count > 0
        except:
            return False
    
    @staticmethod
    def delete(product_id):
        """Ürünü yumuşak şekilde sil (soft delete)"""
        db = get_db()
        products_collection = db.products
        
        try:
            result = products_collection.update_one(
                {'_id': ObjectId(product_id)},
                {'$set': {'is_deleted': True}}
            )
            
            return result.modified_count > 0
        except:
            return False

    # MySQL methods for testing
    @staticmethod
    def get_all_products():
        """Tüm ürünleri getir (MySQL)"""
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT * FROM products WHERE is_deleted = 0 ORDER BY created_at DESC"
        cursor.execute(query)
        
        products = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return products
    
    @staticmethod
    def get_product_by_id(product_id):
        """ID'ye göre ürün getir (MySQL)"""
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT * FROM products WHERE id = %s AND is_deleted = 0"
        cursor.execute(query, (product_id,))
        
        product = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return product
    
    @staticmethod
    def create_product(product_data):
        """Yeni ürün oluştur (MySQL)"""
        conn = get_mysql_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO products (name, price, description, image, category_id) 
        VALUES (%s, %s, %s, %s, %s)
        """
        
        cursor.execute(query, (
            product_data['name'],
            product_data['price'],
            product_data['description'],
            product_data['image'],
            product_data['category_id']
        ))
        
        product_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        return product_id
    
    @staticmethod
    def update_product(product_id, product_data):
        """Ürün güncelle (MySQL)"""
        conn = get_mysql_connection()
        cursor = conn.cursor()
        
        query = """
        UPDATE products 
        SET name = %s, price = %s, description = %s, image = %s, category_id = %s
        WHERE id = %s
        """
        
        cursor.execute(query, (
            product_data['name'],
            product_data['price'],
            product_data['description'],
            product_data['image'],
            product_data['category_id'],
            product_id
        ))
        
        success = cursor.rowcount > 0
        conn.commit()
        cursor.close()
        conn.close()
        
        return success
    
    @staticmethod
    def delete_product(product_id):
        """Ürün sil (MySQL)"""
        conn = get_mysql_connection()
        cursor = conn.cursor()
        
        query = "UPDATE products SET is_deleted = 1 WHERE id = %s"
        cursor.execute(query, (product_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        cursor.close()
        conn.close()
        
        return success
