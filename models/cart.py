from config.mongodb_db import get_db
from config.mysql_db import get_mysql_connection
from bson import ObjectId
from datetime import datetime

class Cart:
    @staticmethod
    def add_item(user_id, product_id, quantity, price):
        """Sepete ürün ekle veya güncelle"""
        db = get_db()
        carts_collection = db.carts
        
        # Ürün sepette zaten var mı kontrol et
        existing_item = carts_collection.find_one({
            'user_id': user_id,
            'product_id': product_id,
            'is_checked_out': False
        })
        
        if existing_item:
            # Ürün zaten varsa miktarı güncelle
            result = carts_collection.update_one(
                {'_id': existing_item['_id']},
                {
                    '$set': {
                        'quantity': existing_item['quantity'] + quantity,
                        'price': price
                    }
                }
            )
            return str(existing_item['_id'])
        else:
            # Sepete yeni ürün ekle
            cart_item = {
                'user_id': user_id,
                'product_id': product_id,
                'quantity': quantity,
                'price': float(price),
                'added_at': datetime.utcnow(),
                'is_checked_out': False,
                'checked_out_at': None
            }
            
            result = carts_collection.insert_one(cart_item)
            return str(result.inserted_id)
    
    @staticmethod
    def get_user_cart(user_id):
        """Kullanıcının sepetindeki tüm ürünleri getir"""
        db = get_db()
        carts_collection = db.carts
        
        cart_items = list(carts_collection.find({
            'user_id': user_id,
            'is_checked_out': False
        }))
        
        # ObjectId'yi stringe çevir
        for item in cart_items:
            item['_id'] = str(item['_id'])
        
        return cart_items
    
    @staticmethod
    def get_items(user_id):
        """Kullanıcının sepetindeki ürünleri, ürün bilgileriyle birlikte getir"""
        db = get_db()
        carts_collection = db.carts
        
        # Get cart items
        cart_items = list(carts_collection.find({
            'user_id': user_id,
            'is_checked_out': False
        }))
        
        # Get product details for each item
        result = []
        for item in cart_items:
            # Convert MongoDB ObjectId to string
            item_id = str(item['_id'])
            
            # Get product details from MySQL
            conn = get_mysql_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT * FROM products WHERE id = %s"
            cursor.execute(query, (item['product_id'],))
            
            product = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if product:
                result.append({
                    'id': item_id,
                    'product_id': item['product_id'],
                    'quantity': item['quantity'],
                    'price': float(item['price']),
                    'product_name': product['name'],
                    'product_image': product['image']
                })
        
        return result
    
    @staticmethod
    def update_quantity(cart_id, quantity):
        """Sepetteki ürünün miktarını güncelle"""
        db = get_db()
        carts_collection = db.carts
        
        try:
            result = carts_collection.update_one(
                {'_id': ObjectId(cart_id)},
                {'$set': {'quantity': quantity}}
            )
            
            return result.modified_count > 0
        except:
            return False
    
    @staticmethod
    def remove_item(cart_id):
        """Sepetten ürün kaldır"""
        db = get_db()
        carts_collection = db.carts
        
        try:
            result = carts_collection.delete_one({'_id': ObjectId(cart_id)})
            return result.deleted_count > 0
        except:
            return False
    
    @staticmethod
    def checkout(user_id):
        """Kullanıcının sepetindeki ürünleri satın alınmış olarak işaretle"""
        db = get_db()
        carts_collection = db.carts
        
        result = carts_collection.update_many(
            {'user_id': user_id, 'is_checked_out': False},
            {
                '$set': {
                    'is_checked_out': True,
                    'checked_out_at': datetime.utcnow()
                }
            }
        )
        
        return result.modified_count
    
    @staticmethod
    def clear(user_id):
        """Kullanıcının sepetini temizle"""
        db = get_db()
        carts_collection = db.carts
        
        result = carts_collection.delete_many({
            'user_id': user_id,
            'is_checked_out': False
        })
        
        return result.deleted_count

    # MySQL methods for testing
    @staticmethod
    def get_cart_by_user_id(user_id):
        """Kullanıcının sepetindeki tüm ürünleri getir (MySQL)"""
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
        SELECT c.*, p.name as product_name, p.price as product_price, p.image as product_image
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = %s
        """
        cursor.execute(query, (user_id,))
        
        cart_items = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return cart_items
    
    @staticmethod
    def add_to_cart(user_id, product_id, quantity):
        """Sepete ürün ekle (MySQL)"""
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Ürün sepette var mı kontrol et
        check_query = "SELECT * FROM cart WHERE user_id = %s AND product_id = %s"
        cursor.execute(check_query, (user_id, product_id))
        
        existing_item = cursor.fetchone()
        
        if existing_item:
            # Ürün varsa miktarı güncelle
            update_query = "UPDATE cart SET quantity = quantity + %s WHERE id = %s"
            cursor.execute(update_query, (quantity, existing_item['id']))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return {'cart_id': existing_item['id'], 'status': 'updated'}
        else:
            # Yeni ürün ekle
            insert_query = "INSERT INTO cart (user_id, product_id, quantity) VALUES (%s, %s, %s)"
            cursor.execute(insert_query, (user_id, product_id, quantity))
            
            cart_id = cursor.lastrowid
            conn.commit()
            cursor.close()
            conn.close()
            
            return {'cart_id': cart_id, 'status': 'added'}
    
    @staticmethod
    def update_cart_item(cart_id, user_id, quantity):
        """Sepet öğesini güncelle (MySQL)"""
        conn = get_mysql_connection()
        cursor = conn.cursor()
        
        query = "UPDATE cart SET quantity = %s WHERE id = %s AND user_id = %s"
        cursor.execute(query, (quantity, cart_id, user_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        cursor.close()
        conn.close()
        
        return success
    
    @staticmethod
    def remove_from_cart(cart_id, user_id):
        """Sepetten ürün kaldır (MySQL)"""
        conn = get_mysql_connection()
        cursor = conn.cursor()
        
        query = "DELETE FROM cart WHERE id = %s AND user_id = %s"
        cursor.execute(query, (cart_id, user_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        cursor.close()
        conn.close()
        
        return success
    
    @staticmethod
    def clear_cart(user_id):
        """Kullanıcının sepetini temizle (MySQL)"""
        conn = get_mysql_connection()
        cursor = conn.cursor()
        
        query = "DELETE FROM cart WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        cursor.close()
        conn.close()
        
        return success
