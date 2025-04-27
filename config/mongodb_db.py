from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Ortam değişkenlerini yükle
load_dotenv()

mongo_client = None
mongo_db = None

def init_mongodb():
    """MongoDB bağlantısını başlat"""
    global mongo_client, mongo_db
    
    try:
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        db_name = os.getenv('MONGO_DB_NAME', 'ecommerce')
        
        print(f"MongoDB'ye bağlanılıyor: {mongo_uri}, Veritabanı: {db_name}")
        
        mongo_client = MongoClient(mongo_uri)
        mongo_db = mongo_client[db_name]
        
        # Bağlantıyı test et
        mongo_client.admin.command('ping')
        print("MongoDB bağlantısı başarılı!")
        return True
    except Exception as e:
        print(f"MongoDB bağlantı hatası: {str(e)}")
        return False

def get_db():
    """MongoDB veritabanı örneğini al"""
    global mongo_db
    if mongo_db is None:
        if not init_mongodb():
            print("MongoDB bağlantısı başlatılamadı")
        
    return mongo_db

# Modül import edildiğinde MongoDB'yi başlat
init_mongodb()
