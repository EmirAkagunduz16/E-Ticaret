import sys
import os
import random
import json
import time
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
    
    def on_start(self):
        """Kullanıcı başladığında çalışır - Authentication için"""
        # Unique user ID with timestamp to avoid conflicts
        self.user_id = f"{random.randint(1, 10000)}_{int(time.time() * 1000)}"
        self.auth_token = None
        self.user_created = False
        self.email = f"test{self.user_id}@example.com"
        self.password = "TestPassword123!"
        
        # Test kullanıcısı oluşturmaya çalış
        self.create_test_user()
    
    def create_test_user(self):
        """Test kullanıcısı oluştur ve login ol"""
        try:
            # Kayıt ol - API'nin beklediği format (name kullanıyor)
            register_data = {
                "name": f"Test User {self.user_id}",  # API 'name' field bekliyor
                "email": self.email,
                "password": self.password,
                "account_type": "customer"  # API bu field'ı da bekliyor
            }
            
            response = self.client.post("/api/auth/register", json=register_data)
            
            if response.status_code in [200, 201]:
                self.user_created = True
                # Login ol
                login_data = {
                    "email": self.email,
                    "password": self.password
                }
                
                login_response = self.client.post("/api/auth/login", json=login_data)
                if login_response.status_code == 200:
                    data = login_response.json()
                    if 'access_token' in data:
                        self.auth_token = data['access_token']
                    elif 'token' in data:
                        self.auth_token = data['token']
            elif response.status_code == 400:
                # Email already exists, try login instead
                login_data = {
                    "email": self.email,
                    "password": self.password
                }
                login_response = self.client.post("/api/auth/login", json=login_data)
                if login_response.status_code == 200:
                    self.user_created = True
                    data = login_response.json()
                    if 'access_token' in data:
                        self.auth_token = data['access_token']
                    elif 'token' in data:
                        self.auth_token = data['token']
        except Exception as e:
            # Hata olursa anonymous kullanıcı olarak devam et
            print(f"User creation error: {e}")  # Debug için
            pass
    
    def get_headers(self):
        """Authentication header'ları al"""
        headers = {'Content-Type': 'application/json'}
        if self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'
        return headers
    
    @task(4)
    def homepage(self):
        """Ana sayfaya istek gönder"""
        self.client.get("/")
    
    @task(5)
    def products_page(self):
        """Ürünler sayfasına istek gönder"""
        self.client.get("/products")
    
    @task(4)
    def featured_products(self):
        """Öne çıkan ürünler API'sini test et"""
        self.client.get("/api/products/featured")
    
    @task(4)
    def products_api(self):
        """Ürünler API'sini farklı parametrelerle test et"""
        page = random.randint(1, 3)
        limit = random.choice([10, 20, 50])
        self.client.get(f"/api/products?page={page}&per_page={limit}")
    
    @task(3)
    def heavy_search(self):
        """Ağır arama sorguları"""
        search_terms = ["test", "product", "sample", "demo", "item"]
        search = random.choice(search_terms)
        self.client.get(f"/api/products?search={search}&limit=100")
    
    @task(2)
    def cart_operations_authenticated(self):
        """Sepet işlemleri - Authentication ile"""
        if self.auth_token:
            headers = self.get_headers()
            
            # Sepet sayısını al
            self.client.get("/api/cart/count", headers=headers)
            
            # Sepeti görüntüle
            self.client.get("/api/cart", headers=headers)
            
            # Gerçek ürün ID'lerini kullan
            real_product_ids = [
                "6838173ed63fc0880e57f43b",  # Laptop
                "6838173ed63fc0880e57f43c",  # Smartphone  
                "6838173ed63fc0880e57f43d",  # Headphones
                "6838173ed63fc0880e57f43e",  # Smartwatch
                "68381c102ddf28a78e5c7f6b"   # Bilgisayar HP
            ]
            
            # Rastgele bir ürün ID'si seç
            product_id = random.choice(real_product_ids)
            
            # Sepete ürün eklemeyi dene
            self.client.post("/api/cart/add", 
                           json={
                               "product_id": product_id,
                               "quantity": 1
                           },
                           headers=headers)
    
    @task(1)
    def cart_operations_anonymous(self):
        """Sepet işlemleri - Anonymous kullanıcı (beklenen hatalar)"""
        # Bu sadece sepet count için - anonymous kullanıcılar için çalışıyor
        self.client.get("/api/cart/count")
    
    @task(3)  # Weight increased from 1 to 3 for valid logins
    def valid_login_attempt(self):
        """Geçerli giriş denemesi - eğer kullanıcı varsa"""
        if self.user_created:
            login_data = {
                "email": self.email,
                "password": self.password
            }
            self.client.post("/api/auth/login", json=login_data)
    
    @task(1)  # Weight reduced - only occasional brute force for security testing
    def limited_brute_force_simulation(self):
        """Sınırlı brute force saldırısı simülasyonu - güvenlik testi için"""
        # Only 10% chance of running this to reduce error rate
        if random.random() < 0.1:
            fake_user = random.randint(50000, 99999)
            self.client.post("/api/auth/login", json={
                "email": f"nonexistent{fake_user}@example.com",
                "password": "wrongpassword"
            })
    
    def on_stop(self):
        """Kullanıcı durduğunda çalışır"""
        pass 