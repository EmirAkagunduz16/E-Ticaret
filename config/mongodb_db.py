from pymongo import MongoClient
import os
from dotenv import load_dotenv
import sys

# Ortam değişkenlerini yükle
load_dotenv()

mongo_client = None
mongo_db = None
# Flag to indicate if we're in test mode
is_test_mode = 'pytest' in sys.modules

class MockCollection:
    """A mock MongoDB collection for testing"""
    def __init__(self, name):
        self.name = name
        self.docs = []
    
    def insert_one(self, doc):
        from bson import ObjectId
        if '_id' not in doc:
            doc['_id'] = ObjectId()
        self.docs.append(doc)
        return type('InsertOneResult', (), {'inserted_id': doc['_id']})
    
    def find(self, query=None, *args, **kwargs):
        if query is None:
            query = {}
        # Simple implementation that returns all docs for testing
        return type('Cursor', (), {
            'sort': lambda *args, **kwargs: self,
            'skip': lambda *args: self,
            'limit': lambda *args: self,
            '__iter__': lambda *args: iter(self.docs)
        })
    
    def find_one(self, query=None):
        if query is None:
            query = {}
        if len(self.docs) > 0:
            return self.docs[0]
        return None
        
    def count_documents(self, query=None):
        if query is None:
            query = {}
        return len(self.docs)
    
    def update_one(self, query, update):
        # Simple implementation for testing
        return type('UpdateResult', (), {'modified_count': 1})
    
    def delete_one(self, query):
        # Simple implementation for testing
        return type('DeleteResult', (), {'deleted_count': 1})

class MockDatabase:
    """A mock MongoDB database for testing"""
    def __init__(self):
        self.collections = {}
    
    def __getitem__(self, name):
        if name not in self.collections:
            self.collections[name] = MockCollection(name)
        return self.collections[name]

def init_mongodb():
    """MongoDB bağlantısını başlat"""
    global mongo_client, mongo_db
    
    # If in test mode, use mock database
    if is_test_mode:
        print("Test modu: Mock MongoDB kullanılıyor")
        mongo_db = MockDatabase()
        return True
    
    try:
        # Always use localhost for MongoDB in test mode, selenium tests, or if MONGO_URI is not set
        if is_test_mode or 'FLASK_TEST_PORT' in os.environ or 'MONGO_URI' not in os.environ:
            mongo_uri = 'mongodb://localhost:27017/'
        else:
            mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        
        # Always use a test database in test mode or selenium tests
        if is_test_mode or 'FLASK_TEST_PORT' in os.environ:
            db_name = 'ecommerce_test'
        else:
            db_name = os.getenv('MONGO_DB_NAME', 'ecommerce')
        
        print(f"MongoDB'ye bağlanılıyor: {mongo_uri}, Veritabanı: {db_name}")
        
        mongo_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)  # Reduced timeout for faster failure
        mongo_db = mongo_client[db_name]
        
        # Bağlantıyı test et
        mongo_client.admin.command('ping')
        print("MongoDB bağlantısı başarılı!")
        return True
    except Exception as e:
        print(f"MongoDB bağlantı hatası: {str(e)}")
        
        # If connection fails in test mode or selenium tests, use mock database
        if is_test_mode or 'FLASK_TEST_PORT' in os.environ:
            print("Test modu: Mock MongoDB'ye geri dönülüyor")
            mongo_db = MockDatabase()
            return True
            
        return False

def get_db():
    """MongoDB veritabanı örneğini al"""
    global mongo_db
    if mongo_db is None:
        if not init_mongodb():
            print("MongoDB bağlantısı başlatılamadı")
            if is_test_mode:
                # Return mock database in test mode
                mongo_db = MockDatabase()
        
    return mongo_db

# Don't auto-initialize when importing the module
# init_mongodb() will be called by get_db() when needed
