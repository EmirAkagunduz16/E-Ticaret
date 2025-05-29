# E-Ticaret

## Kurulum ve Çalıştırma

### Hızlı Başlangıç
```bash
# Sanal ortam oluştur ve aktifleştir
python3 -m venv venv
source venv/bin/activate

# Bağımlılıkları yükle
pip install -r requirements.txt
pip install -r test-requirements.txt

# .env dosyasını oluştur
cp env.example .env
# .env dosyasını düzenleyin

# Veritabanını başlat
python init_db.py

# Uygulamayı çalıştır (testler otomatik başlar)
flask run
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

Uygulama kapsamlı test altyapısı içerir ve testler Flask uygulaması çalışırken otomatik olarak başlatılır.

### Test Türleri
- **Unit Testler**: Model ve temel işlevsellik testleri
- **Entegrasyon Testleri**: API endpoint'leri için testler
  - Auth API testleri (kayıt, giriş, şifre sıfırlama)
  - Products API testleri (ürün CRUD işlemleri)
  - Cart API testleri (sepet işlemleri, checkout)
- **UI Testleri**: Selenium ile otomatik arayüz testleri
- **Performans Testleri**: Locust ile DoS dayanıklılık testleri

### Otomatik Test Çalıştırma
Flask uygulaması başlatıldığında (`flask run`) testler otomatik olarak çalışır. Ayrıca admin panelinden de testleri manuel olarak çalıştırabilirsiniz.

### Manuel Test Çalıştırma
Flask uygulaması çalışırken ayrı bir terminalden testleri manuel olarak çalıştırmak için:

```bash
# Yeni terminal açın ve proje dizinine gidin
cd ~/Desktop/E-Ticaret-flask
source venv/bin/activate

# Tüm testleri çalıştır
python run_tests.py

# Sadece unit testleri
python run_tests.py --unit

# Sadece entegrasyon testleri
python run_tests.py --integration

# Sadece selenium testleri
python run_tests.py --selenium
```

### Test Gereksinimleri
Testleri çalıştırmak için gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
pip install -r test-requirements.txt
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
   ```bash
   python run_tests.py --selenium
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
   ```bash
   python run_tests.py --selenium
   ```

Eğer ChromeDriver hataları alıyorsanız, şu komutla ChromeDriver'ı manuel olarak yüklemeyi deneyebilirsiniz:
```
CHROMEDRIVER_PATH=$(which chromium) python -c "from webdriver_manager.chrome import ChromeDriverManager; from webdriver_manager.core.utils import ChromeType; print(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())"
```

### Önemli Notlar
- Uygulama başlatıldığında testler otomatik olarak çalışır
- Admin paneline erişim: `http://localhost:5000/admin` (admin/admin123)
- Ana site: `http://localhost:5000`

``` 
