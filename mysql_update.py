import mysql.connector
import os
from dotenv import load_dotenv

# Ortam değişkenlerini yükle
load_dotenv()

def main():
    try:
        # MySQL bağlantısını kur
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            database=os.getenv('MYSQL_DATABASE', 'ecommerce'),
            port=int(os.getenv('MYSQL_PORT', 3306))
        )
        
        print("MySQL veritabanına bağlandı")
        
        cursor = connection.cursor()
        
        # Kolon var mı kontrol et
        cursor.execute("SHOW COLUMNS FROM users LIKE 'last_login'")
        result = cursor.fetchone()
        
        if not result:
            # Kolon yoksa ekle
            sql = "ALTER TABLE users ADD COLUMN last_login DATETIME NULL"
            cursor.execute(sql)
            connection.commit()
            print("last_login kolonu eklendi")
        else:
            print("last_login kolonu zaten mevcut")
        
        # Tabloyu görüntüle
        cursor.execute("DESCRIBE users")
        table_structure = cursor.fetchall()
        
        print("\nUsers tablosu yapısı:")
        for column in table_structure:
            print(f"  {column[0]} - {column[1]} - {column[2]} - {column[3]}")
        
    except mysql.connector.Error as error:
        print(f"MySQL bağlantı hatası: {error}")
    
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL bağlantısı kapatıldı")

if __name__ == "__main__":
    main() 