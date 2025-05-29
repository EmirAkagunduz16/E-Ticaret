import sys
import os
from locust import HttpUser, task, between

# Proje kök dizinini sys.path'e ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

class DoSUser(HttpUser):
    """
    DoS saldırı testi için kullanıcı sınıfı
    
    Bu test, uygulamanın DoS saldırılarına karşı dayanıklılığını test eder.
    Çalıştırmak için:
    
    locust -f tests/performance/test_dos.py --host=http://localhost:5000
    
    Web arayüzü: http://localhost:8089
    """
    
    # Kullanıcıların istekler arasında 1-3 saniye beklemesi
    wait_time = between(1, 3)
    
    @task(3)
    def homepage(self):
        """Ana sayfaya istek gönder"""
        self.client.get("/")
    
    @task(4)
    def products_page(self):
        """Ürünler sayfasına istek gönder"""
        self.client.get("/products")
    
    @task(3)
    def featured_products(self):
        """Öne çıkan ürünler API'sini test et"""
        self.client.get("/api/products/featured")
    
    @task(3)
    def products_api(self):
        """Ürünler API'sini farklı parametrelerle test et"""
        # Farklı sayfa ve limit parametreleri ile test et
        import random
        page = random.randint(1, 3)
        limit = random.choice([10, 20, 50])
        self.client.get(f"/api/products?page={page}&per_page={limit}")
    
    @task(2)
    def login_attempt(self):
        """Giriş denemesi yap - brute force saldırısı simülasyonu"""
        import random
        user_num = random.randint(1, 1000)
        self.client.post("/api/auth/login", json={
            "email": f"test{user_num}@example.com",
            "password": "wrongpassword"
        })
    
    @task(1)
    def register_attempt(self):
        """Kayıt denemesi yap"""
        import random
        user_num = random.randint(1, 1000)
        self.client.post("/api/auth/register", json={
            "username": f"testuser{user_num}",
            "email": f"test{user_num}@example.com",
            "password": "Password123!",
            "first_name": "Test",
            "last_name": "User"
        })
    
    @task(2)
    def heavy_search(self):
        """Ağır arama sorguları"""
        import random
        search_terms = ["test", "product", "sample", "demo", "item"]
        search = random.choice(search_terms)
        self.client.get(f"/api/products?search={search}&limit=100")
    
    @task(1)
    def cart_operations(self):
        """Sepet işlemleri - JWT token olmadan deneme (beklenen hata)"""
        # Sepete ürün eklemeyi dene (başarısız olacak ama yük oluşturacak)
        self.client.post("/api/cart/add", json={
            "product_id": "507f1f77bcf86cd799439011",  # Örnek MongoDB ObjectId
            "quantity": 1
        })
        
        # Sepeti görüntülemeyi dene
        self.client.get("/api/cart")
        
        # Sepet sayısını almaya çalış
        self.client.get("/api/cart/count")
    
    def on_start(self):
        """Kullanıcı başladığında çalışır"""
        pass
    
    def on_stop(self):
        """Kullanıcı durduğunda çalışır"""
        pass 