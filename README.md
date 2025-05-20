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

### Alternatif Çalıştırma (Make Olmadan)
Make komutu olmayan sistemlerde `run.sh` script'i kullanılabilir:
```bash
# Script'i çalıştırılabilir yap
chmod +x run.sh

# Projeyi kurmak için
./run.sh setup

# .env dosyasını oluşturmak için
cp env.example .env
# .env dosyasını düzenleyin

# Veritabanını başlatmak için
./run.sh init-db

# Testleri çalıştırmak için
./run.sh test

# Uygulamayı çalıştırmak için
./run.sh run
```

### Docker ile Çalıştırma
Docker ve Docker Compose ile projeyi çalıştırmak için:
```bash
# .env dosyasını oluşturmak için
cp env.example .env
# .env dosyasındaki Docker yorumlarını etkinleştirin

# Uygulamayı başlatmak için
docker-compose up -d

# Testleri çalıştırmak için
docker-compose run test

# Uygulamayı durdurmak için
docker-compose down
```

### Tüm Komutlar
Makefile ile kullanılabilecek tüm komutları görmek için:
```bash
make help
```

veya shell script ile:
```bash
./run.sh
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
- **API Testleri**: Postman koleksiyonu ile API testleri

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

``` 
