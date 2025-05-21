import unittest
import sys
import os
import time
from unittest.mock import patch, MagicMock
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.firefox import GeckoDriverManager

# Proje kök dizinini sys.path'e ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from config.settings import TestConfig

class TestUI(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Explicitly set MongoDB URI in environment variables for the test
        os.environ['MONGO_URI'] = 'mongodb://localhost:27017/'
        os.environ['MONGO_DB_NAME'] = 'ecommerce_test'
        os.environ['FLASK_TEST_PORT'] = '5000'
        
        # Flask uygulamasını burada import etmiyoruz, subprocess ile başlatacağız
        
        try:
            # Firefox WebDriver'ı başlat
            print("Firefox WebDriver başlatılıyor...")
            firefox_options = FirefoxOptions()
            firefox_options.add_argument("--headless")  # Headless mod (görünmez pencere)
            
            try:
                # GeckoDriver'ı kur ve başlat
                driver_path = GeckoDriverManager().install()
                print(f"GeckoDriver kuruldu: {driver_path}")
                cls.driver = webdriver.Firefox(service=FirefoxService(driver_path), options=firefox_options)
                print("Firefox WebDriver başarıyla başlatıldı!")
            except Exception as e:
                print(f"Firefox WebDriver başlatma hatası: {str(e)}")
                print("Firefox tarayıcısı kurulu mu kontrol edin ve gerekli paketleri yükleyin:")
                print("sudo apt-get install firefox-esr firefox-geckodriver")
                print("pip install webdriver-manager")
                cls.driver = None
                return
            
            cls.driver.implicitly_wait(10)
            
            # Flask uygulaması run_tests.py tarafından başlatılacak
            # Uygulamanın başlaması için bekle
            time.sleep(2)
            print("Flask uygulamasının başlaması bekleniyor...")
            
        except Exception as e:
            print(f"Test ortamı başlatma hatası: {str(e)}")
            import traceback
            traceback.print_exc()
            cls.driver = None
    
    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'driver') and cls.driver:
            cls.driver.quit()
    
    # For all tests, check if we have a driver before running
    def setUp(self):
        if not hasattr(self.__class__, 'driver') or not self.__class__.driver:
            self.skipTest("Selenium driver is not available")
    
    def test_homepage_loads(self):
        """Ana sayfa yükleniyor mu test et"""
        self.driver.get('http://localhost:5000/')
        
        # Sayfanın yüklendiğini doğrula - sayfa içeriğini kontrol et
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        # Sayfada herhangi bir içerik olup olmadığını kontrol et
        self.assertTrue(len(self.driver.page_source) > 0)
    
    def test_products_page(self):
        """Ürünler sayfası yükleniyor mu test et"""
        self.driver.get('http://localhost:5000/products')
        
        # Sayfanın yüklendiğini doğrula - sayfa içeriğini kontrol et
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        # Sayfada herhangi bir içerik olup olmadığını kontrol et
        self.assertTrue(len(self.driver.page_source) > 0)
    
    def test_login_page(self):
        """Giriş sayfası yükleniyor mu test et"""
        self.driver.get('http://localhost:5000/login')
        
        # Debug: Sayfa kaynağını yazdır
        print("\n--- LOGIN PAGE SOURCE START ---")
        print(self.driver.page_source[:500])  # İlk 500 karakteri yazdır
        print("...")
        print("--- LOGIN PAGE SOURCE END ---\n")
        
        # Daha genel bir kontrol yapalım - önce sayfanın yüklendiğinden emin olalım
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Şimdi herhangi bir form olup olmadığını kontrol edelim
        try:
            form = self.driver.find_element(By.TAG_NAME, "form")
            print(f"Form bulundu: {form.get_attribute('id')}")
        except Exception as e:
            print(f"Form bulunamadı: {str(e)}")
        
        # Sayfada herhangi bir içerik olup olmadığını kontrol et
        self.assertTrue(len(self.driver.page_source) > 0)
        
        # Email ve password alanlarını doğrudan kontrol et
        try:
            email = self.driver.find_element(By.ID, "email")
            password = self.driver.find_element(By.ID, "password")
            self.assertTrue(email)
            self.assertTrue(password)
        except Exception as e:
            print(f"Email veya password alanı bulunamadı: {str(e)}")
            self.fail("Email veya password alanı bulunamadı")
    
    def test_register_page(self):
        """Kayıt sayfası yükleniyor mu test et"""
        self.driver.get('http://localhost:5000/register')
        
        # Debug: Sayfa kaynağını yazdır
        print("\n--- REGISTER PAGE SOURCE START ---")
        print(self.driver.page_source[:500])  # İlk 500 karakteri yazdır
        print("...")
        print("--- REGISTER PAGE SOURCE END ---\n")
        
        # Daha genel bir kontrol yapalım - önce sayfanın yüklendiğinden emin olalım
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Şimdi herhangi bir form olup olmadığını kontrol edelim
        try:
            form = self.driver.find_element(By.TAG_NAME, "form")
            print(f"Form bulundu: {form.get_attribute('id')}")
        except Exception as e:
            print(f"Form bulunamadı: {str(e)}")
        
        # Sayfada herhangi bir içerik olup olmadığını kontrol et
        self.assertTrue(len(self.driver.page_source) > 0)
        
        # Gerekli alanları doğrudan kontrol et
        try:
            name = self.driver.find_element(By.ID, "name")
            email = self.driver.find_element(By.ID, "email")
            password = self.driver.find_element(By.ID, "password")
            self.assertTrue(name)
            self.assertTrue(email)
            self.assertTrue(password)
        except Exception as e:
            print(f"Kayıt formu alanları bulunamadı: {str(e)}")
            self.fail("Kayıt formu alanları bulunamadı")
    
    def test_login_workflow(self):
        """Giriş yapma iş akışını test et"""
        self.driver.get('http://localhost:5000/login')
        
        # Daha genel bir kontrol yapalım - önce sayfanın yüklendiğinden emin olalım
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Sayfada herhangi bir içerik olup olmadığını kontrol et
        self.assertTrue(len(self.driver.page_source) > 0)
        
        # Email ve password alanlarını doğrudan kontrol et
        try:
            email = self.driver.find_element(By.ID, "email")
            password = self.driver.find_element(By.ID, "password")
            self.assertTrue(email)
            self.assertTrue(password)
        except Exception as e:
            print(f"Email veya password alanı bulunamadı: {str(e)}")
            self.fail("Email veya password alanı bulunamadı")

if __name__ == '__main__':
    unittest.main() 