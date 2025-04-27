from config.mysql_db import get_mysql_connection

class Order:
    @staticmethod
    def create(user_id, total_amount, shipping_address):
        """Yeni bir sipariş oluştur"""
        conn = get_mysql_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO orders (user_id, total_amount, shipping_address, status) 
        VALUES (%s, %s, %s, %s)
        """
        
        cursor.execute(query, (
            user_id,
            total_amount,
            shipping_address,
            'pending'
        ))
        
        order_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        return order_id
    
    @staticmethod
    def get_by_id(order_id):
        """ID'ye göre sipariş getir"""
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT * FROM orders WHERE id = %s"
        cursor.execute(query, (order_id,))
        
        order = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return order
    
    @staticmethod
    def get_by_user(user_id):
        """Kullanıcının tüm siparişlerini getir"""
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT * FROM orders WHERE user_id = %s ORDER BY created_at DESC"
        cursor.execute(query, (user_id,))
        
        orders = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return orders
    
    @staticmethod
    def update_status(order_id, status):
        """Sipariş durumunu güncelle"""
        conn = get_mysql_connection()
        cursor = conn.cursor()
        
        query = "UPDATE orders SET status = %s WHERE id = %s"
        cursor.execute(query, (status, order_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        cursor.close()
        conn.close()
        
        return success


class OrderItem:
    @staticmethod
    def create(order_id, product_id, quantity, price):
        """Yeni bir sipariş öğesi oluştur"""
        conn = get_mysql_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO order_items (order_id, product_id, quantity, price) 
        VALUES (%s, %s, %s, %s)
        """
        
        cursor.execute(query, (
            order_id,
            product_id,
            quantity,
            price
        ))
        
        item_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        return item_id
    
    @staticmethod
    def get_by_order(order_id):
        """Siparişe ait tüm ürünleri getir"""
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT * FROM order_items WHERE order_id = %s"
        cursor.execute(query, (order_id,))
        
        items = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return items
