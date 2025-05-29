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

## DoS Dayanıklılık Testleri (Performans Testleri)

Uygulama, DoS (Denial of Service) saldırılarına karşı dayanıklılığını test etmek için Locust tabanlı performans testleri içerir.

### DoS Testi Özellikleri

DoS testi şu senaryoları kapsar:
- **Ana sayfa yükü**: Eşzamanlı ana sayfa ziyaretleri
- **Ürün sayfası yükü**: Ürünler sayfasına yoğun trafik
- **API endpoint testleri**: Ürün listeleme, arama ve öne çıkan ürünler API'leri
- **Brute force saldırısı simülasyonu**: Sürekli giriş denemeleri
- **Sepet saldırısı testleri**: Yetkisiz sepet işlemi denemeleri
- **Ağır arama sorguları**: Büyük veri setlerinde arama işlemleri

### DoS Testini Çalıştırma

#### Yöntem 1: Komut Satırı (Headless Mode)

```bash
# Uygulamayı başlat (ayrı terminal)
flask run

# DoS testini çalıştır (ana terminal)
# Temel test - 10 kullanıcı, 30 saniye
locust -f tests/performance/test_dos.py --host=http://localhost:5000 --headless --users 10 --spawn-rate 2 --run-time 30s

# Orta seviye test - 25 kullanıcı, 2 dakika
locust -f tests/performance/test_dos.py --host=http://localhost:5000 --headless --users 25 --spawn-rate 5 --run-time 2m

# Ağır test - 50 kullanıcı, 5 dakika
locust -f tests/performance/test_dos.py --host=http://localhost:5000 --headless --users 50 --spawn-rate 10 --run-time 5m
```

#### Yöntem 2: Web Arayüzü

```bash
# Uygulamayı başlat (ayrı terminal)
flask run

# DoS test web arayüzünü başlat
locust -f tests/performance/test_dos.py --host=http://localhost:5000

# Tarayıcıda http://localhost:8089 adresine git
# Web arayüzünden test parametrelerini ayarla:
# - Number of users: 10-50 arası
# - Spawn rate: 2-10 arası
# - Host: http://localhost:5000
```

### DoS Test Parametreleri

| Parametre | Açıklama | Önerilen Değerler |
|-----------|----------|-------------------|
| `--users` | Eşzamanlı kullanıcı sayısı | 10-50 (başlangıç için 10) |
| `--spawn-rate` | Saniyede eklenen kullanıcı sayısı | 1-10 (users'ın 1/5'i) |
| `--run-time` | Test süresi | 30s-5m (başlangıç için 30s) |
| `--host` | Test edilecek sunucu | http://localhost:5000 |

### DoS Test Sonuçlarını Anlama

#### Başarılı Bir Test:
```
Type     Name    # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|------|-------|-------------|-------|-------|-------|-------|--------|-----------
GET      /           50     0(0.00%) |      5       2      15      4 |    2.50        0.00
GET      /products   45     0(0.00%) |      8       3      25      7 |    2.25        0.00
--------|------|-------|-------------|-------|-------|-------|-------|--------|-----------
         Aggregated  120    5(4.17%) |      6       2      45      5 |    6.00        0.25
```

#### Başarı Kriterleri:
- **✅ 0-10% hata oranı**: Normal (çoğu hata yetkisiz istekler)
- **✅ Yanıt süresi < 100ms**: Çok iyi performans
- **✅ Yanıt süresi < 500ms**: Kabul edilebilir performans
- **✅ Uygulama çökmedi**: DoS dayanıklı

#### Alarm Verilecek Durumlar:
- **❌ %50+ hata oranı**: Ciddi sorun
- **❌ Yanıt süresi > 1000ms**: Performans sorunu
- **❌ Uygulama çöktü**: DoS zafiyeti

### DoS Test Senaryoları

Test dosyası şu senaryoları simüle eder:

1. **Normal Kullanıcı Trafiği**: Ana sayfa ve ürün sayfası ziyaretleri
2. **API Saldırısı**: Yoğun API istekleri
3. **Brute Force Saldırısı**: Sürekli login denemeleri
4. **Kaynak Tüketimi**: Ağır arama sorguları
5. **Yetkisiz Erişim**: Sepet işlemlerine izinsiz erişim

### Güvenlik ve Performans Önerileri

DoS testleri sonrasında şu noktalara dikkat edin:

1. **Rate Limiting**: Gerekirse Flask-Limiter ekleyin
2. **Caching**: Redis veya Memcached kullanın
3. **Database İndeksler**: MongoDB query optimizasyonu
4. **NGINX**: Reverse proxy kullanın
5. **CloudFlare**: DDoS koruması için

### DoS Test Gereksinimleri

```bash
# Locust'u yükleyin
pip install locust

# Veya test-requirements.txt'den
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
