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
    
    @task(2)
    def homepage(self):
        """Ana sayfaya istek gönder"""
        self.client.get("/")
    
    @task(3)
    def products(self):
        """Ürünler sayfasına istek gönder"""
        self.client.get("/products")
    
    @task(1)
    def single_product(self):
        """Tek bir ürün sayfasına istek gönder"""
        # Rastgele ürün ID'leri dene
        for product_id in range(1, 10):
            self.client.get(f"/api/products/{product_id}")
    
    @task(2)
    def login_attempt(self):
        """Giriş denemesi yap - brute force saldırısı simülasyonu"""
        self.client.post("/api/auth/login", json={
            "email": f"test{self.user_count}@example.com",
            "password": "wrongpassword"
        })
    
    @task(1)
    def register_attempt(self):
        """Kayıt denemesi yap"""
        self.client.post("/api/auth/register", json={
            "username": f"testuser{self.user_count}",
            "email": f"test{self.user_count}@example.com",
            "password": "Password123!",
            "first_name": "Test",
            "last_name": "User"
        })
    
    @task(1)
    def heavy_api_call(self):
        """Ağır API çağrısı - tüm ürünleri getir"""
        self.client.get("/api/products?limit=100")
    
    @task(1)
    def cart_operations(self):
        """Sepet işlemleri - JWT token olmadan deneme"""
        # Sepete ürün eklemeyi dene (başarısız olacak ama yük oluşturacak)
        self.client.post("/api/cart", json={
            "product_id": 1,
            "quantity": 1
        })
        
        # Sepeti görüntülemeyi dene
        self.client.get("/api/cart")
    
    def on_start(self):
        """Kullanıcı başladığında çalışır"""
        # Her kullanıcı için benzersiz bir sayaç
        self.user_count = 0
    
    def on_stop(self):
        """Kullanıcı durduğunda çalışır"""
        pass 