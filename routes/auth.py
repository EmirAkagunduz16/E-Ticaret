from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from config.mongodb_db import get_db
from models.user import User
from utils.helpers import send_email
from config.settings import Config
from datetime import datetime, timedelta
import os

auth_bp = Blueprint('auth', __name__)

# Modül yükleme zamanı yerine istek zamanında şifre sıfırlama jetonlarını oluştur
def get_password_reset_tokens():
    db = get_db()
    if db is not None:  # DB örneğinin doğru şekilde kontrol edilmesi
        return db['password_reset_tokens']
    return None

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Kullanıcının zaten var olup olmadığını kontrol et
    if User.find_by_email(data['email']):
        return jsonify({'message': 'Kullanıcı zaten mevcut'}), 400
    
    # Kullanıcı verilerini oluştur
    user_data = {
        'username': data.get('username', data['email'].split('@')[0]),
        'email': data['email'],
        'password': data['password'],
        'first_name': data.get('first_name', ''),
        'last_name': data.get('last_name', ''),
        'role': data.get('role', 'customer')
    }
    
    # Yeni kullanıcı oluştur
    user_id = User.create(user_data)
    
    if user_id:
        return jsonify({'message': 'Kullanıcı başarıyla oluşturuldu'}), 201
    else:
        return jsonify({'message': 'Kullanıcı oluşturma hatası'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.verify_password(data['email'], data['password'])
    
    if user:
        # Last_login alanı otomatik olarak User.verify_password içinde güncelleniyor
        access_token = create_access_token(identity={'id': user['id'], 'role': user['role']})
        return jsonify({
            'access_token': access_token,
            'role': user['role'],
            'last_login': user.get('last_login')
        }), 200
    
    return jsonify({'message': 'Geçersiz kimlik bilgileri'}), 401

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    user = User.find_by_email(data['email'])
    
    if user:
        # Şifre sıfırlama token'ı oluştur
        token = User.create_reset_token(data['email'])
        if token:
            # Token'ı MongoDB'de sakla
            password_reset_tokens = get_password_reset_tokens()
            if password_reset_tokens is not None:  # Düzeltildi: MongoDB koleksiyonunun var olup olmadığını kontrol etmenin doğru yolu    
                try:
                    password_reset_tokens.insert_one({
                        'email': data['email'],
                        'token': token,
                        'expires': datetime.utcnow() + timedelta(hours=24)
                    })
                except Exception as e:
                    current_app.logger.error(f"Error inserting token into MongoDB: {str(e)}")
                    # Devam etmek, MySQL'de hala token olduğu için
            
            # E-posta gönder
            # Frontend URL'ini konfigürasyondan al
            app_url = Config.APP_URL
            if app_url is None or "localhost" in app_url:
                app_url = "http://localhost:5000"
                
            # Sıfırlama bağlantısı oluştur
            reset_link = f"{app_url}/reset-password?token={token}"
            
            # Reset linkini dosyaya kaydet
            from utils.helpers import email_logger
            email_logger.info(f"Reset linki oluşturuldu: {reset_link}")
            
            # Token ve reset link bilgisini dosyaya kaydet
            reset_tokens_dir = os.path.join(os.getcwd(), 'sent_emails', 'tokens')
            if not os.path.exists(reset_tokens_dir):
                os.makedirs(reset_tokens_dir)
                
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            token_file = os.path.join(reset_tokens_dir, f"{timestamp}_{data['email'].replace('@', '_at_')}_token.txt")
            
            with open(token_file, 'w', encoding='utf-8') as f:
                f.write(f"Email: {data['email']}\n")
                f.write(f"Token: {token}\n")
                f.write(f"Reset Link: {reset_link}\n")
                f.write(f"Expires: {datetime.utcnow() + timedelta(hours=24)}\n")
            
            # Sender email parametresini al (varsa)
            sender_email = data.get('sender_email', None)
            
            # HTML şablonu kullanarak şifre sıfırlama e-postası gönder
            email_sent = send_email(
                "Şifre Sıfırlama İsteği",
                user['email'],
                f"Lütfen aşağıdaki linki tıklayarak şifrenizi sıfırlayın: {reset_link}",
                is_html=True,
                template="emails/password_reset.html",
                template_data={
                    'user_name': f"{user['first_name']} {user['last_name']}",
                    'reset_link': reset_link,
                    'app_url': app_url
                },
                sender=sender_email
            )
            
            # send_email şimdi gerçek email gönderildiğinde True, dosyaya kaydedildiğinde False döndürür
            if email_sent:
                return jsonify({'message': 'Şifre sıfırlama e-postası gönderildi'}), 200
            else:
                # E-posta gönderilemedi ama dosyaya kaydedildi, yine de token oluşturuldu
                return jsonify({
                    'message': 'Şifre sıfırlama e-postası gönderilemedi ancak dosyaya kaydedildi',
                    'info': 'Mail sunucu yapılandırmasını kontrol edin. Token oluşturuldu ve kullanılabilir.'
                }), 200
    
    return jsonify({'message': 'E-posta bulunamadı'}), 404

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('new_password')
    
    # İlk olarak MongoDB'de geçerli token'ı kontrol et
    password_reset_tokens = get_password_reset_tokens()
    if password_reset_tokens is not None:  # Düzeltildi: MongoDB koleksiyonunun var olup olmadığını kontrol etmenin doğru yolu
        try:
            mongo_token = password_reset_tokens.find_one({
                'token': token,
                'expires': {'$gt': datetime.utcnow()}
            })
            
            if mongo_token:
                # MongoDB token'ından e-posta adresine göre kullanıcıyı bul
                user = User.find_by_email(mongo_token['email'])
                if user:
                    # Kullanıcı modelini kullanarak şifreyi sıfırla
                    success = User.reset_password(token, new_password)
                    if success:
                        # Kullanılan token'ı kaldır
                        password_reset_tokens.delete_one({'token': token})
                        return jsonify({'message': 'Şifre sıfırlama başarılı'}), 200
        except Exception as e:
            print(f"Error checking MongoDB token: {str(e)}")
            # MySQL'e geri dönmek için geriye dönüş
    
    # MySQL'e geri dönmek için geriye dönüş
    # Kullanıcı modelini kullanarak şifreyi doğrudan sıfırla
    success = User.reset_password(token, new_password)
    
    if success:
        return jsonify({'message': 'Şifre sıfırlama başarılı'}), 200
    
    return jsonify({'message': 'Geçersiz veya süresi dolmuş token'}), 400

# Frontend'e şifre sıfırlama sayfası sağlayan yeni bir rota
@auth_bp.route('/password/reset', methods=['GET'])
def password_reset_page():
    token = request.args.get('token')
    if not token:
        return jsonify({'message': 'Geçersiz token'}), 400
    
    # Şifre sıfırlama sayfasına yönlendir
    from flask import render_template
    return render_template('reset-password.html', token=token)

# Token doğrulama rotası
@auth_bp.route('/verify-token', methods=['GET'])
def verify_token():
    token = request.args.get('token')
    if not token:
        return jsonify({'valid': False}), 200
    
    # İlk olarak MongoDB'de token'ı kontrol et
    password_reset_tokens = get_password_reset_tokens()
    if password_reset_tokens is not None:
        try:
            mongo_token = password_reset_tokens.find_one({
                'token': token,
                'expires': {'$gt': datetime.utcnow()}
            })
            
            if mongo_token:
                return jsonify({'valid': True}), 200
        except Exception as e:
            print(f"MongoDB token doğrulama hatası: {str(e)}")
    
    # MongoDB'de bulunamadıysa MySQL'de kontrol et
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
    SELECT * FROM users 
    WHERE reset_token = %s AND reset_token_expires > %s
    """
    
    cursor.execute(query, (token, datetime.now()))
    user = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return jsonify({'valid': user is not None}), 200

# Update API routes with correct prefixes
@auth_bp.route('/api/auth/verify-token', methods=['GET'])
def api_verify_token():
    return verify_token() 