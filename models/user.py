from config.mysql_db import get_mysql_connection
from datetime import datetime, timedelta
from utils.helpers import generate_reset_token, hash_password, check_password

class User:
    @staticmethod
    def find_by_email(email):
        """E-posta adresine göre kullanıcıyı bul"""
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return user
    
    @staticmethod
    def find_by_id(user_id):
        """ID'ye göre kullanıcıyı bul"""
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT * FROM users WHERE id = %s"
        cursor.execute(query, (user_id,))
        
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return user
    
    @staticmethod
    def create(user_data):
        """Yeni bir kullanıcı oluştur"""
        conn = get_mysql_connection()
        cursor = conn.cursor()
        
        # Şifreyi hash'le
        hashed_password = hash_password(user_data['password'])
        
        query = """
        INSERT INTO users (username, first_name, last_name, email, password, role) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(query, (
            user_data['username'],
            user_data['first_name'],
            user_data['last_name'],
            user_data['email'],
            hashed_password,
            user_data.get('role', 'customer')
        ))
        
        user_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        return user_id
    
    @staticmethod
    def update(user_id, user_data):
        """Kullanıcı bilgilerini güncelle"""
        conn = get_mysql_connection()
        cursor = conn.cursor()
        
        # Eğer şifre güncelleniyor ise
        if 'password' in user_data:
            query = """
            UPDATE users 
            SET username = %s, first_name = %s, last_name = %s, email = %s, password = %s
            WHERE id = %s
            """
            
            cursor.execute(query, (
                user_data['username'],
                user_data['first_name'],
                user_data['last_name'],
                user_data['email'],
                user_data['password'],
                user_id
            ))
        else:
            query = """
            UPDATE users 
            SET username = %s, first_name = %s, last_name = %s, email = %s
            WHERE id = %s
            """
            
            cursor.execute(query, (
                user_data['username'],
                user_data['first_name'],
                user_data['last_name'],
                user_data['email'],
                user_id
            ))
        
        success = cursor.rowcount > 0
        conn.commit()
        cursor.close()
        conn.close()
        
        return success
    
    @staticmethod
    def verify_password(email, password):
        """Kullanıcının şifresini doğrula"""
        user = User.find_by_email(email)
        if not user:
            return None
        
        if check_password(password, user['password']):
            return user
        
        return None
    
    @staticmethod
    def create_reset_token(email):
        """Şifre sıfırlama token'ı oluştur"""
        conn = get_mysql_connection()
        cursor = conn.cursor()
        
        token = generate_reset_token()
        expires = datetime.now() + timedelta(hours=24)
        
        query = "UPDATE users SET reset_token = %s, reset_token_expires = %s WHERE email = %s"
        cursor.execute(query, (token, expires, email))
        
        success = cursor.rowcount > 0
        conn.commit()
        cursor.close()
        conn.close()
        
        return token if success else None

    @staticmethod
    def reset_password(token, new_password):
        """Şifreyi sıfırla"""
        conn = get_mysql_connection()
        cursor = conn.cursor()
        
        hashed_password = hash_password(new_password)
        
        query = "UPDATE users SET password = %s, reset_token = NULL, reset_token_expires = NULL WHERE reset_token = %s"
        cursor.execute(query, (hashed_password, token))
        
        success = cursor.rowcount > 0 
        conn.commit()
        cursor.close()
        conn.close()
        
        return success