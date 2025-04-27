from config.mongodb_db import get_db
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
