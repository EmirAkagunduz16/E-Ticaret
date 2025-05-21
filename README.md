# E-Ticaret

## Kurulum ve Çalıştırma

### Hızlı Başlangıç
```bash
# Projeyi kurmak için
make setup

# .env dosyasını oluşturmak için
cp env.example .env
# .env dosyasını düzenleyin

# Veritabanını başlatmak için
make init-db

# Testleri çalıştırmak için
make test

# Uygulamayı çalıştırmak için
make run
```


### Tüm Komutlar
Makefile ile kullanılabilecek tüm komutları görmek için:
```bash
make help
```

## E-posta Yapılandırması

Uygulama şu özellikleri destekler:
1. Sepet güncellemeleri için e-posta bildirimleri
2. Şifre sıfırlama için e-posta bildirimleri
3. Sipariş onayı için e-posta bildirimleri

### Gerçek E-posta Gönderimi

Uygulama artık gerçek e-posta gönderimi için yapılandırılmıştır. E-postalar, SMTP sunucusu üzerinden doğrudan kullanıcı e-posta adreslerine gönderilecektir.

Gmail ile kullanım için:
1. Gmail hesabınızda "Uygulama Şifreleri" oluşturun:
   - "Hesap" > "Güvenlik" > "2 Adımlı Doğrulama" etkinleştirin
   - "Hesap" > "Güvenlik" > "Uygulama Şifreleri" seçin
   - Yeni bir uygulama şifresi oluşturun
2. `.env` dosyasındaki SMTP yapılandırmasını ayarlayın:
   ```
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   MAIL_DEFAULT_SENDER=your-email@gmail.com
   ```

### Dinamik E-posta Gönderici

Uygulama ayrıca dinamik e-posta gönderici desteği sunar. API isteklerinde `sender_email` parametresi kullanarak gönderici e-posta adresini ayarlayabilirsiniz.

Örnek kullanım:
```json
{
  "email": "user@example.com",
  "sender_email": "custom-sender@example.com"
}
```

Bu özelliği kullanmak için:
1. `.env` dosyasında SMTP yapılandırmasını doğru şekilde ayarlayın
2. Gmail kullanıyorsanız, bir "Uygulama Şifresi" oluşturun
3. API isteklerinde isteğe bağlı olarak `sender_email` parametresi ekleyin

Desteklenen API'ler:
- `/api/auth/forgot-password`
- `/api/cart/add`
- `/api/cart/checkout`

### E-posta Hata Ayıklama

Eğer e-posta gönderilemezse (örneğin SMTP yapılandırması yanlışsa), sistem halen e-posta içeriğini `sent_emails/` dizininde HTML veya TXT dosyaları olarak kaydedecektir. Bu, geliştirme sürecinde faydalıdır.

## Test Yapılandırması

Uygulama kapsamlı test altyapısı içerir:

### Test Türleri
- **Unit Testler**: Model ve temel işlevsellik testleri
- **Entegrasyon Testleri**: API endpoint'leri için testler
- **UI Testleri**: Selenium ile otomatik arayüz testleri
- **Performans Testleri**: Locust ile DoS dayanıklılık testleri

### Test Çalıştırma
Testleri çalıştırmak için:
```
make test          # Tüm testleri çalıştırır
make test-unit     # Sadece unit testleri çalıştırır
make test-selenium # Sadece UI testleri çalıştırır
```


### Test Gereksinimleri
Testleri çalıştırmak için gerekli paketleri yükleyin:
```
make install
```

## UI Testleri için Selenium Kurulumu

Selenium UI testlerini çalıştırmak için aşağıdaki adımları izleyin:

### Firefox ile Kullanım (Önerilen)

1. Python bağımlılıklarını yükleyin:
   ```
   pip install -r test-requirements.txt
   pip install webdriver-manager selenium
   ```

2. GeckoDriver'ı yükleyin:
   ```bash
   # Debian/Ubuntu sistemlerde:
   sudo apt-get install firefox-geckodriver
   # Veya webdriver-manager ile:
   python -c "from webdriver_manager.firefox import GeckoDriverManager; print(GeckoDriverManager().install())"
   ```

3. Testleri çalıştırın:
   ```
   python -m pytest tests/selenium/test_ui.py
   ```

### Chromium ile Kullanım

1. Chromium tarayıcısını yükleyin (eğer zaten kurulu değilse):
   ```
   sudo apt-get install chromium
   ```

2. Python bağımlılıklarını yükleyin:
   ```
   pip install -r test-requirements.txt
   pip install webdriver-manager selenium
   ```

3. ChromeDriver'ı manuel olarak ayarlamak için:
   ```python
   from webdriver_manager.chrome import ChromeDriverManager
   from webdriver_manager.core.utils import ChromeType
   
   # Chromium için ChromeDriver'ı indir
   driver_path = ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
   print(f"ChromeDriver yüklendi: {driver_path}")
   ```

4. Testleri çalıştırın:
   ```
   python run_tests.py
   ```

Eğer ChromeDriver hataları alıyorsanız, şu komutla ChromeDriver'ı manuel olarak yüklemeyi deneyebilirsiniz:
```
CHROMEDRIVER_PATH=$(which chromium) python -c "from webdriver_manager.chrome import ChromeDriverManager; from webdriver_manager.core.utils import ChromeType; print(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())"
```

``` 
