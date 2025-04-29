import os
import re
import secrets
import bcrypt
from flask import current_app
from datetime import datetime, timedelta
import jwt
from flask import render_template
import logging
import io
import smtplib
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

# SMTP loglarını yakalamak için özel sınıf
class SMTPHandlerCapture:
    def __init__(self, log_file_path):
        self.log_file = log_file_path
        self.original_smtp_connect = smtplib.SMTP.connect
        self.original_smtp_send = smtplib.SMTP.send
        
        # Metotları değiştir
        smtplib.SMTP.connect = self._patched_connect
        smtplib.SMTP.send = self._patched_send
    
    def _patched_connect(self, host='localhost', port=0, source_address=None):
        """SMTP bağlantı metodu için yama - tüm iletişimi logla"""
        result = self.original_smtp_connect(self, host, port, source_address)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - SMTP Connect - Host: {host}, Port: {port}\n")
        return result
    
    def _patched_send(self, s):
        """SMTP gönderme metodu için yama - tüm gönderilen verileri logla"""
        result = self.original_smtp_send(self, s)
        # Binary verileri güvenli şekilde loglamaya çalış
        log_content = s
        if isinstance(s, bytes):
            try:
                log_content = s.decode('utf-8')
            except UnicodeDecodeError:
                log_content = f"<Binary data {len(s)} bytes>"
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - SMTP Send: {log_content}\n")
        return result

# Loglama için özellikleri yapılandır
def configure_email_logging():
    # E-posta logları için dizinleri oluştur
    base_dir = os.path.join(os.getcwd(), 'sent_emails')
    log_dir = os.path.join(base_dir, 'logs')
    messages_dir = os.path.join(base_dir, 'messages')
    tokens_dir = os.path.join(base_dir, 'tokens')
    smtp_dir = os.path.join(base_dir, 'smtp')
    
    for dir_path in [log_dir, messages_dir, tokens_dir, smtp_dir]:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
    
    # E-posta logları için dosya yolunu belirle
    log_file = os.path.join(log_dir, 'email.log')
    
    # SMTP logları için dosya yolu
    smtp_log_file = os.path.join(smtp_dir, 'smtp.log')
    
    # Loglamayı yapılandır
    email_logger = logging.getLogger('email_logger')
    email_logger.setLevel(logging.INFO)
    
    # Dosya işleyicisini ekle
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    
    # Biçimlendiriciyi oluştur
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    # İşleyiciyi log nesnesi için ata
    if not email_logger.handlers:
        email_logger.addHandler(file_handler)
    
    # SMTP loglarını yakalamak için SMTPHandlerCapture'ı başlat
    smtp_handler = SMTPHandlerCapture(smtp_log_file)
    
    return email_logger

# E-posta loglaması için logger oluştur
email_logger = configure_email_logging()

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
                email_logger.error(f"Error rendering email template {template}: {str(e)}")
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
            email_logger.info(f"Gerçek e-posta gönderildi: {recipient} (Gönderen: {email_sender})")
            return True
        except Exception as e:
            email_logger.error(f"Gerçek e-posta gönderimi hatası: {str(e)}")
            # Hata durumunda geliştirme modundaki gibi dosyaya kaydet
            email_logger.info("Dosyaya kaydetme yöntemine geri dönülüyor...")
        
        # Detaylı e-posta bilgilerini logla
        email_logger.info(f"E-posta gönderildi {recipient}: {subject}")
        email_logger.info(f"Gönderici: {email_sender}")
        email_logger.info(f"HTML: {is_html}")
        if len(body) > 200:
            email_logger.info(f"İçerik: {body[:200]}...")
        else:
            email_logger.info(f"İçerik: {body}")
        email_logger.info(f"Current APP_URL: {Config.APP_URL}")
        
        # Geliştirme için, e-postayı bir dosyaya kaydet
        email_dir = os.path.join(os.getcwd(), 'sent_emails', 'messages')
        if not os.path.exists(email_dir):
            os.makedirs(email_dir)
        
        timestamp = __import__('datetime').datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"{email_dir}/{timestamp}_{recipient.replace('@', '_at_')}.html" if is_html else f"{email_dir}/{timestamp}_{recipient.replace('@', '_at_')}.txt"
        
        # E-posta içeriğini dosyaya kaydet
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Subject: {subject}\n")
            f.write(f"To: {recipient}\n")
            f.write(f"From: {email_sender}\n")
            f.write(f"Content-Type: {'text/html' if is_html else 'text/plain'}\n\n")
            f.write(body)
        
        email_logger.info(f"E-posta dosyasına kaydedildi: {filename}")
        return False  # Gerçek e-posta gönderilemedi, dosyaya kaydedildi
    except Exception as e:
        email_logger.error(f"E-posta gönderimi hatası: {str(e)}")
        return False 