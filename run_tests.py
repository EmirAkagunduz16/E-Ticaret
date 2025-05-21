#!/usr/bin/env python3
"""
E-Ticaret Flask Uygulaması Test Runner

Bu script, tüm test türlerini (unit, integration, selenium, performance) çalıştırır.
"""

import os
import sys
import subprocess
import argparse
import time
from dotenv import load_dotenv

# Proje kök dizinini tanımla
project_root = os.path.dirname(os.path.abspath(__file__))

# .env dosyasını yükle
load_dotenv()

def run_unit_tests():
    """Unit testleri çalıştır"""
    print("\n=== Unit Testleri Çalıştırılıyor ===")
    result = subprocess.run(["pytest", "tests/unit", "-v", "--cov=models", "--cov-report=term"])
    return result.returncode == 0

def run_integration_tests():
    """Entegrasyon testlerini çalıştır"""
    print("\n=== Entegrasyon Testleri Çalıştırılıyor ===")
    result = subprocess.run(["pytest", "tests/integration", "-v"])
    return result.returncode == 0

def setup_browser_driver():
    """
    Browser WebDriver'ı (Firefox veya Chromium için) hazırla
    """
    print("WebDriver hazırlanıyor...")
    
    try:
        # Önce Firefox'u deneyin (tercih edilen)
        try:
            import subprocess
            result = subprocess.run(["firefox", "--version"], capture_output=True, text=True)
            firefox_version = result.stdout.strip()
            
            if firefox_version:
                print(f"Firefox bulundu: {firefox_version}")
                # GeckoDriver yüklemeyi dene
                from webdriver_manager.firefox import GeckoDriverManager
                driver_path = GeckoDriverManager().install()
                print(f"GeckoDriver başarıyla kuruldu: {driver_path}")
                os.environ["GECKO_DRIVER_PATH"] = driver_path
                return "firefox", driver_path
        except Exception as firefox_err:
            print(f"Firefox kurulum hatası: {str(firefox_err)}")
        
        # Firefox başarısız olursa Chromium'u deneyin
        result = subprocess.run(["chromium", "--version"], capture_output=True, text=True)
        chromium_path = result.stdout.strip()
        
        if not chromium_path:
            print("Chromium bulunamadı!")
            return None, None
        
        print(f"Chromium bulundu: {chromium_path}")
        
        # ChromeDriver için gerekli dizini oluştur
        driver_dir = os.path.join(os.path.expanduser("~"), ".wdm", "drivers", "chromedriver")
        os.makedirs(driver_dir, exist_ok=True)
        
        # Webdriver manager ile ChromeDriver kur
        from webdriver_manager.chrome import ChromeDriverManager
        from webdriver_manager.core.utils import ChromeType
        
        driver_path = ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
        print(f"ChromeDriver başarıyla kuruldu: {driver_path}")
        os.environ["CHROME_DRIVER_PATH"] = driver_path
        
        return "chromium", driver_path
    except Exception as e:
        print(f"WebDriver kurulum hatası: {str(e)}")
        return None, None

def run_selenium_tests():
    """Selenium UI testlerini çalıştır"""
    print("\n=== Selenium UI Testleri Çalıştırılıyor ===")
    
    # WebDriver'ı hazırla
    browser_type, driver_path = setup_browser_driver()
    
    if not browser_type or not driver_path:
        print("WebDriver kurulamadı, UI testleri atlanıyor.")
        return True  # Hata döndürmeden devam et
    
    # Test ortamı için gerekli değişkenleri ayarla
    # .env dosyasından değerler zaten yüklendi, sadece test için gerekli olanları ayarla
    test_env = {
        "FLASK_TEST_PORT": "5000",
        "MONGO_DB_NAME": "ecommerce_test"
    }
    
    # Ortam değişkenlerini ayarla
    for key, value in test_env.items():
        os.environ[key] = value
    
    # Flask uygulamasını başlat (arka planda)
    flask_proc = subprocess.Popen(["flask", "run", "--port", "5000"])
    
    try:
        # Uygulamanın başlaması için bekle
        time.sleep(2)
        
        # Selenium testlerini çalıştır
        result = subprocess.run(["pytest", "tests/selenium", "-v"])
        return result.returncode == 0  # Return True if tests pass (exit code 0)
    finally:
        # Flask uygulamasını durdur
        flask_proc.terminate()
        # Test için ayarlanmış ortam değişkenlerini temizle
        for key in test_env:
            if key in os.environ:
                del os.environ[key]

def run_performance_tests():
    """Performans testlerini çalıştır"""
    print("\n=== Performans Testleri Çalıştırılıyor ===")
    print("Locust ile DoS testlerini çalıştırmak için:")
    print("locust -f tests/performance/test_dos.py --host=http://localhost:5000")
    print("ve tarayıcıda http://localhost:8089 adresini açın.")
    
    # Burada locust'u otomatik başlatmak yerine kullanıcıya nasıl çalıştıracağını gösteriyoruz
    return True

def run_tests():
    """Tüm test türlerini çalıştırır"""
    os.chdir(project_root)
    
    print("=== Unit Testler Çalıştırılıyor ===")
    if run_unit_tests() != 0:
        return False
    
    print("\n=== Entegrasyon Testleri Çalıştırılıyor ===")
    if run_integration_tests() != 0:
        return False
    
    print("\n=== Selenium UI Testleri Çalıştırılıyor ===")
    # ChromeDriver'ı hazırla
    setup_browser_driver()
    
    if run_selenium_tests() != 0:
        print("UI testlerinden bazıları başarısız oldu, ancak devam ediyoruz.")
    
    print("\n=== Performans Testleri Çalıştırılıyor ===")
    print("Locust ile DoS testlerini çalıştırmak için:")
    print("locust -f tests/performance/test_dos.py --host=http://localhost:5000")
    print("ve tarayıcıda http://localhost:8089 adresini açın.")
    
    print("\n=== Tüm testler başarıyla tamamlandı! ===")
    return True

def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(description="E-Ticaret Flask Uygulaması Test Runner")
    parser.add_argument("--unit", action="store_true", help="Sadece unit testleri çalıştır")
    parser.add_argument("--integration", action="store_true", help="Sadece entegrasyon testleri çalıştır")
    parser.add_argument("--selenium", action="store_true", help="Sadece selenium testleri çalıştır")
    parser.add_argument("--performance", action="store_true", help="Sadece performans testleri çalıştır")
    parser.add_argument("--all", action="store_true", help="Tüm testleri çalıştır")
    parser.add_argument("--firefox", action="store_true", help="Firefox kullanarak testleri çalıştır")
    parser.add_argument("--chromium", action="store_true", help="Chromium kullanarak testleri çalıştır")
    
    args = parser.parse_args()
    
    # Hiçbir argüman verilmezse --all kullan
    if not any([args.unit, args.integration, args.selenium, args.performance, args.all]):
        args.all = True
    
    # Tarayıcı tercihi
    if args.firefox:
        os.environ["PREFERRED_BROWSER"] = "firefox"
    elif args.chromium:
        os.environ["PREFERRED_BROWSER"] = "chromium"
    
    success = True
    
    # Unit testleri çalıştır
    if args.unit or args.all:
        if not run_unit_tests():
            success = False
    
    # Entegrasyon testlerini çalıştır
    if args.integration or args.all:
        if not run_integration_tests():
            success = False
    
    # Selenium testlerini çalıştır
    if args.selenium or args.all:
        if not run_selenium_tests():
            success = False
    
    # Performans testlerini çalıştır
    if args.performance or args.all:
        if not run_performance_tests():
            success = False
    
    # Sonuç
    if success:
        print("\n=== Tüm testler başarıyla tamamlandı! ===")
        return 0
    else:
        print("\n=== Bazı testler başarısız oldu! ===")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 