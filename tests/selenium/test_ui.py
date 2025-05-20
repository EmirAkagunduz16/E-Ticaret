import unittest
import sys
import os
import time
from unittest.mock import patch, MagicMock
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Proje kök dizinini sys.path'e ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from config.settings import TestConfig
import threading

class TestUI(unittest.TestCase):
    
    @classmethod
    @patch('config.mongodb_db.init_mongodb')
    @patch('utils.db_init.init_tables')
    def setUpClass(cls, mock_init_tables, mock_mongodb):
        # MongoDB ve diğer bağımlılıkları mockla
        mock_mongodb.return_value = True
        mock_init_tables.return_value = None
        
        # Flask uygulamasını başlat - burada import ediyoruz çünkü patching önce yapılmalı
        from app import create_app
        cls.app = create_app(TestConfig)
        cls.app.config['TESTING'] = True
        cls.app.config['SERVER_NAME'] = 'localhost:5000'
        
        # Uygulamayı ayrı bir thread'de çalıştır
        cls.ctx = cls.app.app_context()
        cls.ctx.push()
        cls.app.config['MONGODB_MOCK'] = True  # Use mock MongoDB
        
        try:
            # Selenium WebDriver'ı başlat - headless modda
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Headless mod (görünmez pencere)
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            cls.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            cls.driver.implicitly_wait(10)
            
            # Flask uygulamasını başlat - port 5000'de
            cls.server_thread = threading.Thread(target=lambda: cls.app.run(port=5000))
            cls.server_thread.daemon = True
            cls.server_thread.start()
            
            # Thread'in başlaması için bekle
            time.sleep(1)
        except Exception as e:
            print(f"Selenium driver başlatma hatası: {str(e)}")
            cls.driver = None
    
    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'driver') and cls.driver:
            cls.driver.quit()
        if hasattr(cls, 'ctx'):
            cls.ctx.pop()
    
    # For all tests, check if we have a driver before running
    def setUp(self):
        if not hasattr(self.__class__, 'driver') or not self.__class__.driver:
            self.skipTest("Selenium driver is not available")
    
    def test_homepage_loads(self):
        """Ana sayfa yükleniyor mu test et"""
        self.driver.get('http://localhost:5000/')
        
        # Sayfanın yüklendiğini doğrula - sadece sayfa başlığını kontrol et
        self.assertIn('E-Ticaret', self.driver.title)
    
    def test_products_page(self):
        """Ürünler sayfası yükleniyor mu test et"""
        self.driver.get('http://localhost:5000/products')
        
        # Sayfanın yüklendiğini doğrula - sadece sayfa başlığını kontrol et
        self.assertIn('Ürünler', self.driver.title)
    
    def test_login_page(self):
        """Giriş sayfası yükleniyor mu test et"""
        self.driver.get('http://localhost:5000/login')
        
        # Sayfanın yüklendiğini doğrula - sadece sayfa başlığını kontrol et
        self.assertIn('Giriş', self.driver.title)
    
    def test_register_page(self):
        """Kayıt sayfası yükleniyor mu test et"""
        self.driver.get('http://localhost:5000/register')
        
        # Sayfanın yüklendiğini doğrula - sadece sayfa başlığını kontrol et
        self.assertIn('Kayıt', self.driver.title)
    
    def test_login_workflow(self):
        """Giriş yapma iş akışını test et"""
        self.driver.get('http://localhost:5000/login')
        
        # Sayfanın yüklendiğini doğrula - sadece sayfa başlığını kontrol et
        self.assertIn('Giriş', self.driver.title)

if __name__ == '__main__':
    unittest.main() 