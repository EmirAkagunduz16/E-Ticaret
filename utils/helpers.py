import os
import re
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

def send_email(subject, recipient, body, is_html=False, template=None, template_data=None):
    """Bir e-posta gönder"""
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
        
        # Bu, gerçek e-posta gönderme uygulamasının yerine koyulacak
        # Üretim ortamında, SMTP gibi bir uygun e-posta hizmeti kullanılacak
        print(f"E-posta gönderildi {recipient}: {subject}")
        print(f"HTML: {is_html}")
        print(f"İçerik: {body[:200]}..." if len(body) > 200 else f"İçerik: {body}")
        
        # Hata ayıklama: APP_URL'in doğru şekilde ayarlandığını kontrol et
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
            f.write(f"Content-Type: {'text/html' if is_html else 'text/plain'}\n\n")
            f.write(body)
        
        print(f"E-posta dosyasına kaydedildi: {filename}")
        return True
    except Exception as e:
        print(f"E-posta gönderimi hatası: {str(e)}")
        return False 