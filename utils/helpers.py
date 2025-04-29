import os
import secrets
import bcrypt
from flask import current_app
from datetime import datetime, timedelta
import jwt
from flask import render_template
try:
    from config.settings import Config
except ImportError:
    try:
        # Try relative import for when running as a module
        from ..config.settings import Config
    except ImportError:
        # Fallback for when running directly
        import sys
        import os.path as path
        sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
        from config.settings import Config

# Flask-Mail'i içe aktar
from flask_mail import Message
from app import mail

def hash_password(password):
    """Şifreyi bcrypt kullanarak hashle"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed_password):
    """Şifrenin hashlenmiş şifreyle eşleşip eşleşmediğini kontrol et"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def generate_token(user_id, expires_delta=None):
    """Kimlik doğrulama için JWT token oluştur"""
    if expires_delta is None:
        expires_delta = timedelta(days=1)
    
    expires = datetime.utcnow() + expires_delta
    
    payload = {
        'exp': expires,
        'iat': datetime.utcnow(),
        'sub': user_id
    }
    
    return jwt.encode(
        payload,
        current_app.config['JWT_SECRET_KEY'],
        algorithm='HS256'
    )

def generate_reset_token():
    """Güvenli bir şifre sıfırlama token oluştur"""
    return secrets.token_urlsafe(32)

def send_email(subject, recipient, body, is_html=False, template=None, template_data=None, sender=None):
    """Bir e-posta gönder
    
    Args:
        subject: Email konusu
        recipient: Alıcı email adresi
        body: Email içeriği
        is_html: İçerik HTML ise True
        template: Kullanılacak şablon dosyası
        template_data: Şablona gönderilecek veriler
        sender: Gönderici email adresi (None ise varsayılan gönderici kullanılır)
    """
    try:
        # Eğer bir şablon sağlanmışsa, sağlanan verilerle onu oluştur
        if template and template_data:
            try:
                html_content = render_template(template, **template_data)
                is_html = True
                body = html_content
            except Exception as e:
                print(f"Error rendering email template {template}: {str(e)}")
                # Sağlanan gövdeye geri dön
        
        # Göndericiyi belirle: ya belirtilen gönderici ya da varsayılan gönderici
        email_sender = sender or Config.MAIL_DEFAULT_SENDER
        
        # Her zaman gerçek e-posta göndermeyi dene
        try:
            msg = Message(
                subject=subject,
                recipients=[recipient],
                body=None if is_html else body,
                html=body if is_html else None,
                sender=email_sender
            )
            mail.send(msg)
            print(f"Gerçek e-posta gönderildi: {recipient} (Gönderen: {email_sender})")
            return True
        except Exception as e:
            print(f"Gerçek e-posta gönderimi hatası: {str(e)}")
            # Hata durumunda geliştirme modundaki gibi dosyaya kaydet
            print("Dosyaya kaydetme yöntemine geri dönülüyor...")
        
        # E-posta gönderimi başarısız olduysa veya DEBUG modundaysa dosyaya kaydet
        # Hata ayıklama bilgileri
        print(f"E-posta gönderildi {recipient}: {subject}")
        print(f"Gönderici: {email_sender}")
        print(f"HTML: {is_html}")
        print(f"İçerik: {body[:200]}..." if len(body) > 200 else f"İçerik: {body}")
        print(f"Current APP_URL: {Config.APP_URL}")
        
        # Geliştirme için, e-postayı bir dosyaya kaydet
        email_dir = os.path.join(os.getcwd(), 'sent_emails')
        if not os.path.exists(email_dir):
            os.makedirs(email_dir)
        
        timestamp = __import__('datetime').datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"{email_dir}/{timestamp}_{recipient.replace('@', '_at_')}.html" if is_html else f"{email_dir}/{timestamp}_{recipient.replace('@', '_at_')}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Subject: {subject}\n")
            f.write(f"To: {recipient}\n")
            f.write(f"From: {email_sender}\n")
            f.write(f"Content-Type: {'text/html' if is_html else 'text/plain'}\n\n")
            f.write(body)
        
        print(f"E-posta dosyasına kaydedildi: {filename}")
        return False  # Gerçek e-posta gönderilemedi, dosyaya kaydedildi
    except Exception as e:
        print(f"E-posta gönderimi hatası: {str(e)}")
        return False 