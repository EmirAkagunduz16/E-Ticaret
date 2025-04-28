# E-Ticaret

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
