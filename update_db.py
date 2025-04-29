from config.mysql_db import get_mysql_connection
import sys

def update_database():
    """Veritabanı yapısını güncelle (last_login ekle)"""
    print("Veritabanı yapısı güncelleniyor...")
    
    # MySQL'e bağlan
    conn = get_mysql_connection()
    if not conn:
        print("MySQL veritabanına bağlanılamadı")
        return False
    
    cursor = conn.cursor()
    
    # last_login kolonunu users tablosuna ekle
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN last_login DATETIME NULL")
        print("last_login kolonu users tablosuna eklendi")
    except Exception as e:
        error_msg = str(e)
        if "Duplicate column name" in error_msg:
            print("last_login kolonu zaten mevcut")
        else:
            print(f"Hata: {error_msg}")
    
    # Tabloyu kontrol et
    cursor.execute("DESCRIBE users")
    columns = cursor.fetchall()
    print("\nUsers tablosu yapısı:")
    for column in columns:
        print(f"  {column[0]} ({column[1]}) {column[3]}")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("\nVeri tabanı güncellemesi tamamlandı.")
    return True

if __name__ == "__main__":
    update_database() 