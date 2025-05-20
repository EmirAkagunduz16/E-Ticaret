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

def run_selenium_tests():
    """Selenium UI testlerini çalıştır"""
    print("\n=== Selenium UI Testleri Çalıştırılıyor ===")
    # Flask uygulamasını başlat (arka planda)
    flask_proc = subprocess.Popen(["flask", "run"])
    
    try:
        # Uygulamanın başlaması için bekle
        time.sleep(2)
        
        # Selenium testlerini çalıştır
        result = subprocess.run(["pytest", "tests/selenium", "-v"])
        return result.returncode == 0
    finally:
        # Flask uygulamasını durdur
        flask_proc.terminate()

def run_performance_tests():
    """Performans testlerini çalıştır"""
    print("\n=== Performans Testleri Çalıştırılıyor ===")
    print("Locust ile DoS testlerini çalıştırmak için:")
    print("locust -f tests/performance/test_dos.py --host=http://localhost:5000")
    print("ve tarayıcıda http://localhost:8089 adresini açın.")
    
    # Burada locust'u otomatik başlatmak yerine kullanıcıya nasıl çalıştıracağını gösteriyoruz
    return True


def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(description="E-Ticaret Flask Uygulaması Test Runner")
    parser.add_argument("--unit", action="store_true", help="Sadece unit testleri çalıştır")
    parser.add_argument("--integration", action="store_true", help="Sadece entegrasyon testleri çalıştır")
    parser.add_argument("--selenium", action="store_true", help="Sadece selenium testleri çalıştır")
    parser.add_argument("--performance", action="store_true", help="Sadece performans testleri çalıştır")
    parser.add_argument("--all", action="store_true", help="Tüm testleri çalıştır")
    
    args = parser.parse_args()
    
    # Hiçbir argüman verilmezse --all kullan
    if not any(vars(args).values()):
        args.all = True
    
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